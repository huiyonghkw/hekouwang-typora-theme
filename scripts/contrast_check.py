#!/usr/bin/env python3
"""Audit the *generated* Typora CSS against practical WCAG contrast targets.

This module deliberately has no dependency on build.py at import time, so the
builder can call ``audit_css(css, label)`` before writing a theme.  The CLI
imports the builder only when it needs to generate every palette in memory.

The audit checks foregrounds against the least favourable stop of the editor's
paper gradient, as well as code, sidebar, button, and tinted alert surfaces.
Ratios are mathematical CSS-colour estimates; Typora's actual rendering still
needs visual review, especially for antialiasing and overlays.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable


HERE = Path(__file__).resolve().parent
CSS_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^()]*\)")
VAR = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]+))?\)")
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
COMMENT = re.compile(r"/\*.*?\*/", re.S)


@dataclass(frozen=True)
class Color:
    r: float
    g: float
    b: float
    a: float = 1.0

    def hex(self) -> str:
        return "#" + "".join(f"{round(x * 255):02x}" for x in (self.r, self.g, self.b))


@dataclass(frozen=True)
class Result:
    label: str
    ratio: float
    minimum: float
    foreground: str
    background: str

    @property
    def passed(self) -> bool:
        return self.ratio + 1e-9 >= self.minimum

    def line(self, theme: str) -> str:
        return (f"{theme}: {self.label}: {self.ratio:.2f}:1 < {self.minimum:g}:1 "
                f"({self.foreground} on {self.background})")


def parse_color(value: str) -> Color:
    """Parse opaque/alpha hex and CSS rgb(a) colour literals."""
    value = value.strip().lower()
    if value.startswith("#"):
        h = value[1:]
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        if len(h) not in (6, 8):
            raise ValueError(f"unsupported hex colour: {value}")
        values = [int(h[i:i + 2], 16) / 255 for i in range(0, len(h), 2)]
        return Color(*values) if len(values) == 4 else Color(*values, 1.0)
    m = re.fullmatch(r"rgba?\(([^)]*)\)", value)
    if not m:
        raise ValueError(f"unsupported CSS colour: {value}")
    parts = [p.strip() for p in m.group(1).replace("/", ",").split(",")]
    if len(parts) not in (3, 4):
        # Support modern ``rgb(31 30 29 / .5)`` as well as comma syntax.
        parts = [p for p in re.split(r"\s+", m.group(1).replace("/", " ")) if p]
    if len(parts) not in (3, 4):
        raise ValueError(f"unsupported RGB colour: {value}")
    rgb = [float(p[:-1]) / 100 if p.endswith("%") else float(p) / 255
           for p in parts[:3]]
    alpha = (float(parts[3][:-1]) / 100 if parts[3].endswith("%")
             else float(parts[3])) if len(parts) == 4 else 1.0
    if any(x < 0 or x > 1 for x in (*rgb, alpha)):
        raise ValueError(f"out-of-range RGB colour: {value}")
    return Color(*rgb, alpha)


def composite(top: Color, bottom: Color) -> Color:
    """Place an alpha colour over an opaque CSS background."""
    if bottom.a != 1:
        raise ValueError("background must be opaque")
    return Color(*(top.a * x + (1 - top.a) * y
                   for x, y in zip((top.r, top.g, top.b),
                                   (bottom.r, bottom.g, bottom.b))))


def luminance(color: Color) -> float:
    def linear(channel: float) -> float:
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
    return (0.2126 * linear(color.r) + 0.7152 * linear(color.g)
            + 0.0722 * linear(color.b))


def contrast(foreground: Color, background: Color) -> float:
    fg = composite(foreground, background) if foreground.a < 1 else foreground
    hi, lo = sorted((luminance(fg), luminance(background)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def parse_rules(css: str) -> dict[str, dict[str, str]]:
    """Extract simple declarations; later editor rules override earlier ones.

    This is intentionally a small parser for our generated CSS, not a generic
    CSS parser.  Print/export overrides are excluded by the caller.
    """
    rules: dict[str, dict[str, str]] = {}
    for match in RULE.finditer(COMMENT.sub("", css)):
        declarations: dict[str, str] = {}
        for item in match.group(2).split(";"):
            if ":" not in item:
                continue
            key, value = item.split(":", 1)
            declarations[key.strip()] = value.strip()
        for selector in match.group(1).split(","):
            rules.setdefault(selector.strip(), {}).update(declarations)
    return rules


def expand_vars(value: str, variables: dict[str, str]) -> str:
    """Resolve the concrete :root tokens used in colour declarations."""
    for _ in range(12):
        new = VAR.sub(lambda m: variables.get(m.group(1), m.group(2) or m.group(0)), value)
        if new == value:
            break
        value = new
    if "var(" in value:
        raise ValueError(f"unresolved CSS variable in: {value}")
    return value


def color_from(value: str, variables: dict[str, str]) -> Color:
    value = expand_vars(value, variables)
    match = CSS_COLOR.search(value)
    if not match:
        raise ValueError(f"no colour literal in: {value}")
    return parse_color(match.group())


def paint_colors(value: str, variables: dict[str, str]) -> list[Color]:
    """Return every gradient stop, or the one solid background colour."""
    value = expand_vars(value, variables)
    colors = [parse_color(m.group()) for m in CSS_COLOR.finditer(value)]
    if not colors:
        raise ValueError(f"no colour stops in background: {value}")
    return colors


def assess(label: str, foreground: Color, backgrounds: Iterable[Color],
           minimum: float) -> Result:
    tested = [(contrast(foreground, bg), bg) for bg in backgrounds]
    if not tested:
        raise ValueError(f"no backgrounds supplied for {label}")
    ratio, worst = min(tested, key=lambda item: item[0])
    effective = composite(foreground, worst) if foreground.a < 1 else foreground
    return Result(label, ratio, minimum, effective.hex(), worst.hex())


def audit_css_results(css: str, label: str) -> list[Result]:
    """Audit the CSS Typora will load; return pass and failure measurements."""
    editor_css = css.split("导出 / 打印", 1)[0]
    rules = parse_rules(editor_css)
    all_rules = parse_rules(css)
    root = rules.get(":root")
    if not root:
        raise ValueError(f"{label}: no :root colour tokens found")

    def prop(selector: str, key: str) -> str:
        try:
            return rules[selector][key]
        except KeyError as exc:
            raise ValueError(f"{label}: missing {selector} {{{key}}} for contrast audit") from exc

    def color(selector: str, key: str = "color") -> Color:
        return color_from(prop(selector, key), root)

    def token(name: str) -> Color:
        return color_from(root[name], root)

    paper_value = rules.get("#write", {}).get("background", root["--bg-color"])
    paper = paint_colors(paper_value, root)
    # Generated paper gradients run between these stops.  A fixed foreground's
    # smallest contrast can occur between stops if its luminance lies in range.
    # Include interpolation samples to avoid an endpoint-only false pass.
    if len(paper) > 1:
        paper = [Color(*(a * (1 - i / 20) + b * (i / 20)
                         for a, b in zip((left.r, left.g, left.b),
                                         (right.r, right.g, right.b))))
                 for left, right in zip(paper, paper[1:]) for i in range(21)]
    sidebar = token("--side-bar-bg-color")
    hover_bg = token("--item-hover-bg-color")
    raised = token("--hk-raised")
    code_bg = color("#write pre.md-fences", "background")
    source_style = {**rules.get("#typora-source", {}),
                    **rules.get("#typora-source .CodeMirror", {})}
    source_bg = color_from(source_style.get("background", source_style.get(
        "background-color", root["--bg-color"])), root)
    button_bg = color(".btn-primary", "background")
    checkbox_bg = color("#write .md-task-list-item > input", "background")
    checkbox_checked = color("#write .md-task-list-item > input:checked", "background")
    inline_bg = color("#write code", "background")
    results: list[Result] = []

    def check(name: str, fg: Color, bgs: Iterable[Color], minimum: float = 4.5) -> None:
        results.append(assess(name, fg, bgs, minimum))

    # Editor paper, reading text and links.  Muted/faint text appears in bylines,
    # footnotes, Markdown syntax markers, sidebar timestamps and line numbers.
    for name, token_name in (("body text / paper", "--text-color"),
                             ("soft text / paper", "--hk-soft"),
                             ("muted text / paper", "--hk-muted"),
                             ("faint metadata / paper", "--hk-faint")):
        check(name, token(token_name), paper)
    check("link / paper", color("#write a"), paper)
    check("link hover / paper", color("#write a:hover"), paper)
    check("Markdown syntax / paper", color("#write .md-meta"), paper)
    focus_ring = color_from(prop("#write a:focus-visible", "outline"), root)
    check("keyboard focus ring / paper", focus_ring, paper, 3.0)
    check("outline active / sidebar", color("#outline-content .outline-active > .outline-item"),
          (sidebar, hover_bg))
    check("inline code / tinted paper", color("#write code"),
          (composite(inline_bg, bg) for bg in paper))
    footnote_bg = color("#write sup.md-footnote", "background")
    check("footnote marker / tinted paper", color("#write sup.md-footnote"),
          (composite(footnote_bg, bg) for bg in paper))

    # Actual code editor colours, including export's raised code fence.
    code_surfaces = [code_bg]
    export_fence = all_rules.get("body.typora-export #write pre.md-fences", {})
    if "background" in export_fence:
        code_surfaces.extend(paint_colors(export_fence["background"], root))
    for syntax, selector in (
        ("comment", ".cm-s-inner .cm-comment"),
        ("keyword", ".cm-s-inner .cm-keyword"),
        ("definition", ".cm-s-inner .cm-def"),
        ("string", ".cm-s-inner .cm-string"),
        ("number", ".cm-s-inner .cm-number"),
        ("error", ".cm-s-inner .cm-error"),
        ("link", ".cm-s-inner .cm-link"),
        ("meta", ".cm-s-inner .cm-meta"),
    ):
        check(f"code {syntax} / fence", color(selector), code_surfaces)
    check("code line number / fence", color(".cm-s-inner .CodeMirror-linenumber"),
          code_surfaces)
    for syntax, selector in (
        ("comment", ".cm-s-typora-default .cm-comment"),
        ("string", ".cm-s-typora-default .cm-string"),
        ("link", ".cm-s-typora-default .cm-link"),
        ("variable", ".cm-s-typora-default .cm-variable-2"),
    ):
        check(f"source {syntax} / editor", color(selector), (source_bg,))

    # Sidebar labels and primary actions.  Button/checkbox glyphs are text;
    # their outlines and fills are essential non-text UI cues (3:1).
    check("sidebar file label", color("#typora-sidebar .file-list-item"),
          (sidebar, hover_bg))
    check("sidebar faint timestamp", color(".file-list-item-time"),
          (sidebar, hover_bg))
    check("primary button text", color(".btn-primary"), (button_bg,))
    check("Typora primary button token", token("--primary-btn-text-color"),
          (token("--primary-color"),))
    check("primary button fill / nearby surface", button_bg, (raised, sidebar), 3.0)
    checkbox_style = rules["#write .md-task-list-item > input"]
    checkbox_border = checkbox_style.get("border-color", checkbox_style.get("border"))
    if checkbox_border is None:
        raise ValueError(f"{label}: no unchecked checkbox border colour")
    check("unchecked checkbox border", color_from(checkbox_border, root),
          (checkbox_bg,), 3.0)
    check("checked checkbox fill / paper", checkbox_checked, paper, 3.0)
    check("checkbox tick / checked fill",
          color_from(prop("#write .md-task-list-item > input:checked::after", "border"), root),
          (checkbox_checked,), 3.0)
    check("active file marker / sidebar", token("--active-file-border-color"),
          (sidebar, hover_bg), 3.0)

    # Alert labels sit on semi-transparent tinted backgrounds, not directly on
    # the paper.  Check every paper stop under that translucent layer.
    for kind in ("note", "important", "warning", "tip", "caution"):
        fg = color(f"#write .md-alert-text-{kind}")
        tint = color(f"#write .md-alert-{kind}", "background")
        check(f"alert {kind} label / tint", fg,
              (composite(tint, bg) for bg in paper))

    return results


def audit_css(css: str, label: str) -> list[str]:
    """Builder-facing API: return human-readable failures (empty means pass)."""
    return [result.line(label) for result in audit_css_results(css, label)
            if not result.passed]


def _variants(tier: str):
    # This import stays inside the CLI.  build.py can import audit_css safely.
    import build

    tokens = json.loads((HERE / "tokens.json").read_text(encoding="utf-8"))
    themes = build.load_themes(tier)
    built = tokens["_meta"].get("presets_built") or [tokens["_meta"].get("preset", "work")]
    for theme in themes:
        for preset_name in built:
            # 用 build.resolve_theme —— 与 build.main 同一份合并实现。
            # 以前这里另写了一份副本，两边漂移，审计对象和出货 CSS 会对不上。
            variant, _ = build.resolve_theme(tokens, theme, preset_name)
            for is_dark in (False, True):
                label = f"{theme['id']}/{preset_name}/{'dark' if is_dark else 'light'}"
                css = build.build(variant, dark=is_dark,
                                  premium=(theme.get("tier") == "paid"),
                                  flavor=theme.get("id", ""))
                yield label, css


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", choices=("free", "paid", "all"), default="all")
    parser.add_argument("--all", action="store_true", help="include passing checks")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--report-only", action="store_true",
                        help="show failures without failing the process")
    args = parser.parse_args()
    results = [(name, audit_css_results(css, name)) for name, css in _variants(args.tier)]
    failures = sum(not result.passed for _, checks in results for result in checks)
    if args.json:
        print(json.dumps([
            {"variant": name, "checks": [
                {"label": r.label, "ratio": round(r.ratio, 3),
                 "minimum": r.minimum, "foreground": r.foreground,
                 "background": r.background, "passed": r.passed}
                for r in checks if args.all or not r.passed]}
            for name, checks in results], ensure_ascii=False, indent=2))
    else:
        for name, checks in results:
            bad = [r for r in checks if not r.passed]
            print(f"{name}: {len(checks) - len(bad)}/{len(checks)} checks pass")
            for result in checks if args.all else bad:
                prefix = "PASS" if result.passed else "FAIL"
                print(f"  {prefix} {result.label}: {result.ratio:.2f}:1 / {result.minimum:g}:1 "
                      f"({result.foreground} on {result.background})")
        print(f"Total: {failures} failing checks across {len(results)} variants")
    return 0 if args.report_only or failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
