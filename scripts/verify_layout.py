#!/usr/bin/env python3
"""Check Typora theme geometry in a small, representative browser fixture.

This is an early regression check, not a replacement for testing in Typora.
It includes the Typora base rules relevant to image wrappers, source mode,
and tables, then loads the generated theme CSS after them. Run with:

    python3 scripts/verify_layout.py
    python3 scripts/verify_layout.py --css theme/hekouwang.css
"""

import argparse
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent.parent
WIDTHS = (320, 480, 760, 900, 1440, 1800, 2048)
# The reading column may grow on desktop, but it should remain a reading
# column rather than stretching across the full technical canvas.
MAX_READING_REM = 60
MIN_DESKTOP_GROWTH_PX = 96
CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome"),
    shutil.which("chromium"),
)

# These are the relevant parts of Typora's base.css and base-control.css.
# In particular, :only-child ignores text nodes, so an image embedded between
# two pieces of text still matches Typora's 100%-wide image wrapper rule.
TYPORA_BASE = """
*,:before,:after { box-sizing: border-box; }
body { margin: 0; }
content { display: block; width: 100%; min-height: 100vh; }
img { max-width: 100%; vertical-align: middle; }
p > .md-image:only-child:not(.md-img-error) img,
p > img:only-child { display: block; margin: auto; }
p > .md-image:only-child { display: inline-block; width: 100%; }
figure { overflow-x: auto; margin: 1.2em 0; max-width: calc(100% + 16px); padding: 0; }
figure > table { margin: 0; }
table { border-collapse: collapse; width: 100%; }
.CodeMirror { position: relative; overflow: hidden; }
.CodeMirror-scroll { overflow-x: auto; overflow-y: hidden; }
#typora-source .CodeMirror-lines {
  padding: 30px 30px 60px 60px;
  max-width: 800px;
  margin: 0 auto;
}
"""

IMAGE = (
    "data:image/svg+xml,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22"
    "%20width=%2220%22%20height=%2220%22%3E%3Crect%20width=%2220%22"
    "%20height=%2220%22%20fill=%22red%22/%3E%3C/svg%3E"
)

PROBE_JS = """
(() => {
  const element = id => document.getElementById(id);
  const box = id => {
    const el = element(id), r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return {left:r.left, top:r.top, right:r.right, bottom:r.bottom, width:r.width,
            clientWidth:el.clientWidth, scrollWidth:el.scrollWidth,
            paddingLeft:parseFloat(s.paddingLeft),
            paddingRight:parseFloat(s.paddingRight), overflowX:s.overflowX,
            display:s.display};
  };
  const mixed = element('mixed');
  const textBox = node => {
    const range = document.createRange();
    range.selectNodeContents(node);
    const r = range.getBoundingClientRect();
    return {left:r.left, top:r.top, right:r.right};
  };
  const out = {viewport:window.innerWidth,
    documentWidth:document.documentElement.scrollWidth,
    rootSize:parseFloat(getComputedStyle(document.documentElement).fontSize),
    letterSpacing:getComputedStyle(element('prose')).letterSpacing,
    write:box('write'), prose:box('prose'), heading:box('heading'),
    topbar:box('qa-topbar'), list:box('list'), quote:box('quote'),
    code:box('code'), bareCode:box('bare-code'),
    longCode:box('long-code'), codeScroll:box('code-scroll'),
    wideFigure:box('wide-figure'), wideTable:box('wide-table'),
    sparseTable:box('sparse-table'), fourFigure:box('four-figure'),
    fourTable:box('four-table'), sixFigure:box('six-figure'),
    sixTable:box('six-table'), directFourTable:box('direct-four-table'),
    denseFigure:box('dense-figure'),
    denseTable:box('dense-table'), mixed:box('mixed'),
    denseFourFigure:box('dense-four-figure'),
    denseFourTable:box('dense-four-table'),
    denseFourCell:box('dense-four-cell'),
    denseCodeCell:box('dense-code-cell'),
    imageWrapper:box('image-wrapper'), inlineImage:box('inline-image'),
    sourceLines:box('source-lines'),
    beforeImage:textBox(mixed.firstChild),
    afterImage:textBox(mixed.lastChild)};
  element('__LAYOUT__').textContent = JSON.stringify(out);
})();
"""


def fixture(css: Path, extra_css: str = "") -> str:
    wide_header = "".join(
        f'<th style="min-width:8rem">指标 {i}</th>' for i in range(1, 9)
    )
    wide_row = "".join(f"<td>数据 {i}</td>" for i in range(1, 9))
    def short_table(cols: int) -> str:
        head = "".join(f"<th>列 {i}</th>" for i in range(1, cols + 1))
        row = "".join(f"<td>值 {i}</td>" for i in range(1, cols + 1))
        return f"<thead><tr>{head}</tr></thead><tbody><tr>{row}</tr></tbody>"

    dense_header = "".join(
        f'<th style="min-width:8rem">Technical {i}</th>' for i in range(1, 13)
    )
    dense_row = "".join(f"<td>value_{i:02d}</td>" for i in range(1, 13))
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>{TYPORA_BASE}</style>
<link rel="stylesheet" href="{css.as_uri()}">
<style>{extra_css}</style>
</head><body><div id="qa-topbar" style="height:40px"></div><content><div id="write">
<h2 id="heading">主题宽屏布局验收</h2>
<p id="prose">{'中文长文需要稳定的阅读行宽，技术内容则可以使用更宽的画布。' * 5}</p>
<ul id="list"><li>列表保持在阅读列，序号和内容都应清晰。</li></ul>
<blockquote id="quote"><p>引用也属于连续阅读内容。</p></blockquote>
<pre id="code" class="md-fences"><code id="bare-code">const longLine = 'code and tables use the wide canvas and long lines must stay within the paper';</code></pre>
<pre id="long-code" class="md-fences"><div class="CodeMirror"><div class="CodeMirror-scroll" id="code-scroll"><div class="CodeMirror-sizer"><div class="CodeMirror-lines"><div class="CodeMirror-code"><div class="CodeMirror-line" style="display:inline-block;white-space:pre">{'const very_long_identifier_1234567890 = "Typora code should scroll locally"; ' * 20}</div></div></div></div></div></div></pre>
<figure id="wide-figure"><table id="wide-table"><thead><tr>{wide_header}</tr></thead>
<tbody><tr>{wide_row}</tr></tbody></table></figure>
<figure id="sparse-figure"><table id="sparse-table"><thead><tr><th>项目</th><th>状态</th></tr></thead>
<tbody><tr><td>A</td><td>完成</td></tr></tbody></table></figure>
<figure class="md-table-fig table-figure" id="four-figure"><table class="md-table" id="four-table">{short_table(4)}</table></figure>
<figure class="md-table-fig table-figure" id="six-figure"><table class="md-table" id="six-table">{short_table(6)}</table></figure>
<table class="md-table" id="direct-four-table">{short_table(4)}</table>
<figure id="dense-figure"><table id="dense-table"><thead><tr>{dense_header}</tr></thead>
<tbody><tr>{dense_row}</tr></tbody></table></figure>
<figure class="md-table-fig table-figure" id="dense-four-figure"><table class="md-table" id="dense-four-table">
<thead><tr><th>阶段</th><th>典型场景</th><th>关键行动</th><th>长代码</th></tr></thead>
<tbody><tr><td id="dense-four-cell">内部工具的需求验证与持续交付，需要完整保留中文词组。</td>
<td>周报、知识库、自动报告和客户支持草稿，都需要可读的单元格宽度。</td>
<td>先接入现有流程，再逐步扩展到更多团队。</td>
<td id="dense-code-cell"><code>https://example.com/a/very_long_identifier_that_must_remain_readable_in_a_table</code></td></tr></tbody></table></figure>
<p id="mixed">前文<span class="md-image" id="image-wrapper"><img id="inline-image"
  width="20" height="20" src="{IMAGE}" alt="图标"></span>后文继续阅读。</p>
</div></content>
<div id="typora-source"><div class="CodeMirror"><div class="CodeMirror-lines" id="source-lines">
  # heading\nA representative source-mode line.
</div></div></div>
<pre id="__LAYOUT__" style="display:none">pending</pre>
<script>{PROBE_JS}</script></body></html>"""


def find_chrome() -> str:
    for path in CHROME_CANDIDATES:
        if path and os.path.exists(path):
            return path
    raise SystemExit("Chrome/Chromium not found; pass --chrome /path/to/browser")


def measure(chrome: str, css: Path, width: int, extra_css: str = "",
            scale: int = 1) -> dict:
    # Like verify_render.py, put the temporary page next to the stylesheet so
    # file URLs and relative font assets are resolved in the same way.
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", prefix="layout-probe-", delete=False,
        dir=css.parent, encoding="utf-8"
    ) as page:
        page.write(fixture(css, extra_css))
        page_path = Path(page.name)
    outer_path = None
    try:
        # Chrome headless enforces a 500px minimum top-level window. A same-
        # origin iframe gives narrow fixtures their actual 320/480px CSS
        # viewport; at scale 2 it emulates 200% zoom in a 640px display area.
        target = page_path
        if width < 500 or scale != 1:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".html", prefix="layout-frame-", delete=False,
                dir=css.parent, encoding="utf-8"
            ) as outer:
                outer.write(
                    '<!doctype html><meta charset="utf-8">'
                    '<pre id="__LAYOUT__">pending</pre>'
                    '<script>function collect(){const page=document.getElementById("view")'
                    '.contentDocument;const report=page&&page.getElementById("__LAYOUT__");'
                    'if(report&&report.textContent!=="pending")'
                    'document.getElementById("__LAYOUT__").textContent=report.textContent;'
                    'else setTimeout(collect,20)}</script>'
                    f'<iframe id="view" src="{page_path.as_uri()}" onload="collect()" '
                    f'style="border:0;width:{width}px;height:1800px;'
                    f'transform:scale({scale});transform-origin:top left"></iframe>'
                )
                outer_path = Path(outer.name)
            target = outer_path
        with tempfile.TemporaryDirectory(prefix="typora-layout-profile-") as profile:
            result = subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--incognito",
                 "--allow-file-access-from-files", f"--user-data-dir={profile}",
                 "--virtual-time-budget=10000",
                 f"--window-size={max(500, width * scale)},1200",
                 "--dump-dom", target.as_uri()],
                capture_output=True, text=True, timeout=60,
            )
        match = re.search(r'<pre id="__LAYOUT__"[^>]*>(.*?)</pre>', result.stdout, re.S)
        if not match or match.group(1).strip() == "pending":
            raise RuntimeError(
                f"Chrome did not return geometry ({css.name}, {width}px): "
                f"{result.stderr[-500:]}"
            )
        return json.loads(html.unescape(match.group(1)))
    finally:
        page_path.unlink(missing_ok=True)
        if outer_path is not None:
            outer_path.unlink(missing_ok=True)


def validate(data: dict, css_name: str, requested_width: int,
             max_reading_rem: int = MAX_READING_REM) -> list[str]:
    errors = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{css_name} @ {requested_width}px: {message}")

    viewport = data["viewport"]
    content_width = (data["write"]["width"] - data["write"]["paddingLeft"]
                     - data["write"]["paddingRight"])
    prose_limit = data["rootSize"] * max_reading_rem
    need(abs(viewport - requested_width) <= 2,
         f"browser viewport is {viewport}px (expected {requested_width}px)")
    need(data["documentWidth"] <= viewport + 2,
         f"page scrolls horizontally ({data['documentWidth']:.0f} > {viewport:.0f}px)")
    paper_gap = data["write"]["top"] - data["topbar"]["bottom"]
    need(data["rootSize"] * 0.75 <= paper_gap <= data["rootSize"] * 1.5,
         f"paper/topbar gutter is {paper_gap:.0f}px (expected about 1rem)")

    for label in ("prose", "heading", "list", "quote", "mixed"):
        need(data[label]["width"] <= prose_limit + 3,
             f"{label} width {data[label]['width']:.0f}px exceeds "
             f"{max_reading_rem}rem ({prose_limit:.0f}px)")

    need(data["code"]["width"] >= content_width - 4,
         f"code is not using the wide canvas ({data['code']['width']:.0f}/{content_width:.0f}px)")
    need(data["code"]["scrollWidth"] <= data["code"]["clientWidth"] + 2,
         "bare pre > code extends outside its paper box")
    need(data["longCode"]["width"] >= content_width - 4,
         "long code fence is not using the wide canvas")
    need(data["codeScroll"]["overflowX"] in ("auto", "scroll")
         and data["codeScroll"]["scrollWidth"] >= data["codeScroll"]["clientWidth"] + 100,
         "long code does not scroll inside its CodeMirror container")
    need(data["wideTable"]["width"] >= content_width * 0.85 - 4,
         f"eight-column table is not using the wide canvas "
         f"({data['wideTable']['width']:.0f}/{content_width:.0f}px)")
    need(data["wideFigure"]["width"] <= content_width + 17,
         "table figure escapes the paper content box")
    need(data["sourceLines"]["width"] <= data["prose"]["width"] + data["rootSize"] * 6 + 3,
         f"source mode is too wide ({data['sourceLines']['width']:.0f}px)")
    if requested_width == 2048:
        need(data["prose"]["width"] >= data["rootSize"] * 58,
             f"prose does not use the wide desktop ({data['prose']['width']:.0f}px)")

    # Typora wraps edited tables in figure.md-table-fig. Four and six column
    # tables should use the same responsive reading width as adjacent prose.
    # The direct table checks the exported/plain HTML fallback.
    for label in ("fourFigure", "sixFigure", "denseFourFigure",
                  "directFourTable"):
        need(abs(data[label]["left"] - data["prose"]["left"]) <= 3,
             f"{label} starts at {data[label]['left']:.0f}px, "
             f"prose at {data['prose']['left']:.0f}px")
        need(abs(data[label]["width"] - data["prose"]["width"]) <= 3,
             f"{label} width {data[label]['width']:.0f}px does not fill "
             f"prose width {data['prose']['width']:.0f}px")
    for table_name, figure_name in (("fourTable", "fourFigure"),
                                    ("sixTable", "sixFigure"),
                                    ("denseFourTable", "denseFourFigure")):
        table, figure = data[table_name], data[figure_name]
        need(abs(table["left"] - figure["left"]) <= 3,
             f"{table_name} is not aligned with its scroll container")
        need(table["width"] + 3 >= figure["width"],
             f"{table_name} does not fill its reading column")
        if table["width"] > figure["width"] + 3:
            need(figure["overflowX"] in ("auto", "scroll")
                 and figure["scrollWidth"] > figure["clientWidth"] + 3,
                 f"{table_name} overflows without local scrolling")
    need(data["denseFourCell"]["width"] >= data["rootSize"] * 6.75,
         "long Chinese cell was squeezed into an unreadable strip")
    need(data["denseCodeCell"]["width"] >= data["rootSize"] * 11.75,
         "long code cell was squeezed into excessive short lines")
    if requested_width <= 480:
        need(data["denseFourFigure"]["scrollWidth"]
             > data["denseFourFigure"]["clientWidth"] + 10,
             "dense four-column table should scroll locally in a narrow window")

    if requested_width == 1800:
        need(data["code"]["width"] >= data["prose"]["width"] + 80,
             "wide code has not gained meaningful width beyond prose")
        need(data["sparseTable"]["width"] <= data["prose"]["width"] + 3,
             f"sparse table exceeds the reading column "
             f"({data['sparseTable']['width']:.0f}/{data['prose']['width']:.0f}px)")
        need(abs(data["sparseTable"]["left"] - data["prose"]["left"]) <= 3,
             f"sparse table starts at {data['sparseTable']['left']:.0f}px, "
             f"prose at {data['prose']['left']:.0f}px")
    before, after = data["beforeImage"], data["afterImage"]
    image = data["inlineImage"]
    need(data["imageWrapper"]["width"] <= 50,
         f"inline image wrapper is {data['imageWrapper']['width']:.0f}px wide")
    need(abs(before["top"] - after["top"]) <= 2
         and after["left"] >= image["right"] - 1,
         "text before and after the inline image is not on one line")

    dense = data["denseFigure"]
    need(dense["overflowX"] in ("auto", "scroll"),
         "dense table wrapper has no local horizontal scrolling")
    need(dense["scrollWidth"] >= dense["clientWidth"] + 10,
         "dense table did not exercise local horizontal scrolling")
    need(data["denseTable"]["width"] > dense["clientWidth"] + 10,
         "dense table was compressed instead of scrolling inside its wrapper")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--css", action="append", type=Path,
                        help="Theme CSS; repeat to check multiple variants")
    parser.add_argument("--all", action="store_true",
                        help="Check every generated theme variant in theme/")
    parser.add_argument("--chrome", help="Chrome/Chromium executable path")
    args = parser.parse_args()
    if args.css and args.all:
        parser.error("use either --css or --all")
    if args.all:
        css_paths = sorted((ROOT / "theme").glob("hekouwang*.css"))
    elif args.css:
        css_paths = args.css
    else:
        css_paths = [ROOT / "theme/hekouwang.css",
                     ROOT / "theme/hekouwang-dark.css"]
    if not css_paths:
        parser.error("no generated theme CSS found in theme/")
    css_paths = [path.resolve() for path in css_paths]
    for path in css_paths:
        if not path.is_file():
            parser.error(f"CSS not found: {path}")
    chrome = args.chrome or find_chrome()

    failures = []
    for css in css_paths:
        previous = None
        for width in WIDTHS:
            data = measure(chrome, css, width)
            failures.extend(validate(data, css.name, width))
            print(f"{css.name:26} {width:4}px | #write {data['write']['width']:6.0f}px "
                  f"prose {data['prose']['width']:6.0f}px "
                  f"code {data['code']['width']:6.0f}px "
                  f"sparse {data['sparseTable']['width']:6.0f}px "
                  f"source {data['sourceLines']['width']:6.0f}px")
            if previous is not None and width == 1800:
                if data["write"]["width"] < previous["write"]["width"] + 150:
                    failures.append(f"{css.name}: #write did not expand on a wide screen")
                # A wider paper alone is insufficient: the actual prose and
                # normal tables must use some of the extra desktop space.
                for label in ("prose", "fourTable", "sixTable",
                              "directFourTable", "sparseTable"):
                    growth = data[label]["width"] - previous[label]["width"]
                    if growth < MIN_DESKTOP_GROWTH_PX:
                        failures.append(
                            f"{css.name}: {label} gained only {growth:.0f}px "
                            f"from 1440px to 1800px (need {MIN_DESKTOP_GROWTH_PX}px)"
                        )
            previous = data

        # A 320px CSS viewport scaled into 640px of physical display area
        # exercises the same responsive breakpoints as browser zoom at 200%.
        # Text-spacing overrides follow WCAG's user-style stress case.
        for label, width, extra_css, max_rem, scale in (
            ("200% zoom", 320, "", MAX_READING_REM, 2),
            ("text spacing", 320,
             "#write { line-height: 1.5; letter-spacing: 0.12em; "
             "word-spacing: 0.16em; } #write p { margin-bottom: 2em; }",
             MAX_READING_REM, 1),
            ("40rem override", 1800,
             ":root { --hk-reading-measure: 40rem; }", 40, 1),
        ):
            data = measure(chrome, css, width, extra_css, scale=scale)
            failures.extend(validate(data, f"{css.name} [{label}]", width,
                                     max_reading_rem=max_rem))
            if label == "text spacing" and data["letterSpacing"] == "normal":
                failures.append(f"{css.name}: text-spacing override was ignored")
            if label == "40rem override":
                expected = 40 * data["rootSize"]
                if abs(data["prose"]["width"] - expected) > 3:
                    failures.append(
                        f"{css.name}: user reading-width override gave "
                        f"{data['prose']['width']:.0f}px (expected {expected:.0f}px)"
                    )
            print(f"{css.name:26} {label:15} | viewport {width:4}px "
                  f"prose {data['prose']['width']:6.0f}px "
                  f"table {data['fourFigure']['width']:6.0f}px")

    if failures:
        print(f"\n{len(failures)} layout regression(s):")
        for error in failures:
            print(f"  - {error}")
        raise SystemExit(1)
    print("\nLayout geometry passed. Confirm editing and PDF export in Typora.")


if __name__ == "__main__":
    main()
