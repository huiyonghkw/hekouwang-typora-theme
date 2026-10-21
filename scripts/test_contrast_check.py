"""Small tests for the generated-CSS contrast audit."""

import json
from pathlib import Path
import re
import unittest

from scripts import build
from scripts.contrast_check import (
    Color,
    assess,
    audit_css,
    audit_css_results,
    composite,
    contrast,
    parse_color,
    parse_rules,
)


HERE = Path(__file__).resolve().parent


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
        cls.css = build.build(tokens, dark=False)

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
        from scripts.contrast_check import _variants

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
