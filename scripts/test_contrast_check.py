"""Small tests for the generated-CSS contrast audit.

跑法（两种都行）：

    python3 scripts/test_contrast_check.py
    python3 -m unittest scripts.test_contrast_check

之前这文件只能 python3 -m scripts.test_contrast_check 跑 —— 直接跑会报
ModuleNotFoundError: No module named 'scripts'。那意味着它实际上从来没人跑过。
"""

import json
from pathlib import Path
import re
import sys
import unittest

# 允许从仓库根或 scripts/ 目录直接运行本文件
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build  # noqa: E402
from contrast_check import (  # noqa: E402
    Color,
    assess,
    audit_css,
    audit_css_results,
    composite,
    contrast,
    parse_color,
    parse_rules,
)


class ContrastMathTest(unittest.TestCase):
    def test_wcag_reference_colours(self):
        self.assertAlmostEqual(contrast(parse_color("#000"), parse_color("#fff")), 21.0)
        self.assertLess(contrast(parse_color("#777"), parse_color("#fff")), 4.5)
        self.assertGreater(contrast(parse_color("#767676"), parse_color("#fff")), 4.5)

    def test_alpha_compositing_and_worst_surface(self):
        mid = composite(parse_color("rgba(255,255,255,.5)"), parse_color("#000"))
        self.assertEqual(mid.hex(), "#808080")
        result = assess("test", parse_color("#777"),
                        [parse_color("#000"), parse_color("#fff")], 4.5)
        self.assertEqual(result.background, "#ffffff")
        self.assertFalse(result.passed)

    def test_modern_rgb_and_alpha_hex(self):
        modern = parse_color("rgb(31 30 29 / 50%)")
        hexa = parse_color("#1f1e1d80")
        self.assertEqual((modern.r, modern.g, modern.b),
                         (hexa.r, hexa.g, hexa.b))
        self.assertAlmostEqual(modern.a, 0.5)
        self.assertAlmostEqual(hexa.a, 128 / 255)


class GeneratedCssTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tokens = json.loads((HERE / "tokens.json").read_text(encoding="utf-8"))
        # 必须走与 build.main 相同的合并路径（resolve_theme）。
        # 以前这里用裸 tokens 直接 build()，构建出来的是一份不存在的 CSS ——
        # 圆角是 6px 而出货是 0，语法色也全是另一套。测试绿灯，出货却是错的。
        theme = build.load_themes("free")[0]
        resolved, _ = build.resolve_theme(tokens, theme, "work")
        cls.css = build.build(resolved, dark=False)

    def test_css_parser_keeps_editor_rules(self):
        editor = self.css.split("导出 / 打印", 1)[0]
        rules = parse_rules(editor)
        self.assertIn(":root", rules)
        self.assertIn("#write a:hover", rules)
        self.assertIn("radial-gradient", rules["#write"]["background"])

    def test_builder_api_finds_low_contrast_link(self):
        # The probe forces a poor link colour without changing any files.
        bad = re.sub(r"(--hk-link:\s*)#[0-9a-fA-F]+", r"\g<1>#ffffff", self.css)
        failures = audit_css(bad, "probe")
        self.assertTrue(any("link / paper" in failure for failure in failures))

    def test_cli_variants_include_theme_syntax_colours(self):
        # The audit must build the same CSS as build.main: palette syntax
        # overrides are part of the shipped theme, not just the defaults.
        from contrast_check import _variants

        theme = build.load_themes("free")[0]
        keyword = theme["syntax"]["light"]["syn_keyword"]
        variants = dict(_variants("free"))
        self.assertIn(f"color: {keyword};", variants["v2/work/light"])

    def test_gradient_interpolation_catches_interior_minimum(self):
        # A #777 link is near a #777 interior point of a black-to-white paper
        # gradient; checking endpoints alone would miss its ~1:1 contrast.
        css = re.sub(r"(--hk-link:\s*)#[0-9a-fA-F]+", r"\g<1>#777777", self.css)
        css, count = re.subn(
            r"(#write\s*\{[^{}]*?background:\s*)radial-gradient\([^;]+\)",
            r"\g<1>radial-gradient(#000000 0%, #777777 48%, #ffffff 100%)",
            css, count=1, flags=re.S)
        self.assertEqual(count, 1)
        link = next(result for result in audit_css_results(css, "probe")
                    if result.label == "link / paper")
        self.assertLess(link.ratio, 1.02)


if __name__ == "__main__":
    unittest.main()
