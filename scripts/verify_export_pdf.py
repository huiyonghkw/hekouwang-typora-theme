#!/usr/bin/env python3
"""Exercise generated export CSS in A4/A5 PDF fixtures.

This uses the Typora 1.14 print rules relevant to code fences and macOS
tables, then loads a generated theme. Chrome PDF verifies full text, table
pagination, custom margins, and CSS page headers/footers. Typora's native
export dialog still needs a manual check.

    python3 scripts/verify_export_pdf.py --css theme/hekouwang.css
"""

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from xml.etree import ElementTree


BASE = """
* { box-sizing: border-box; }
body { margin: 0; }
body.typora-export { padding-left: 30px; padding-right: 30px; }
#write { margin: 0 auto; overflow-x: visible; }
.md-fences { display: block; white-space: pre; overflow: visible;
             page-break-inside: avoid; }
#write .md-fences.mock-cm { white-space: pre-wrap; }
figure { overflow-x: auto; margin: 1.2em 0; padding: 0; }
figure > table { margin: 0; }
table { width: 100%; page-break-inside: auto; }
.is-mac table { page-break-inside: avoid; }
@media print { figure { overflow-x: visible; } }
"""


def page(css: Path, paper: str, content: str) -> str:
    # The late @page rule models chosen paper/margins and user header/footer.
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            f"<style>{BASE}</style>"
            f"<link rel='stylesheet' href='{css.as_uri()}'>"
            f"<style>@page {{ size: {paper}; margin: 20mm; "
            "@top-center { content: 'HK_EXPORT_HEADER'; font: 8pt sans-serif; } "
            "@bottom-center { content: 'HK_EXPORT_FOOTER'; font: 8pt sans-serif; } "
            "}</style>"
            "</head><body class='typora-export is-mac'>"
            f"<div class='typora-export-content'><div id='write'>{content}"
            "</div></div></body></html>")


def run_pdf(chrome: str, html_path: Path, pdf_path: Path, profile: Path) -> None:
    command = [
        chrome, "--headless", "--disable-gpu", "--incognito",
        "--allow-file-access-from-files", f"--user-data-dir={profile}",
        f"--print-to-pdf={pdf_path}", "--no-pdf-header-footer",
        html_path.as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    if result.returncode or not pdf_path.is_file():
        raise RuntimeError(f"Chrome PDF failed: {result.stderr[-800:]}")


def pdf_text(pdf_path: Path) -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True, text=True, check=True,
    )
    return [part for part in result.stdout.split("\f") if part.strip()]


def paper_size(pdf_path: Path) -> tuple[float, float]:
    info = subprocess.run(
        ["pdfinfo", str(pdf_path)], capture_output=True, text=True, check=True,
    ).stdout
    match = re.search(r"^Page size:\s*([\d.]+) x ([\d.]+) pts", info, re.M)
    if not match:
        raise AssertionError(f"pdfinfo did not report page size: {pdf_path}")
    return float(match.group(1)), float(match.group(2))


def first_heading_position(pdf_path: Path, title: str) -> tuple[float, float]:
    xml = subprocess.run(
        ["pdftotext", "-bbox", str(pdf_path), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    root = ElementTree.fromstring(xml)
    first_word = title.split()[0]
    for word in root.iter():
        if word.tag.endswith("}word") and word.text == first_word:
            return float(word.attrib["xMin"]), float(word.attrib["yMin"])
    raise AssertionError(f"heading {title!r} missing from PDF: {pdf_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--css", type=Path, default=Path("theme/hekouwang.css"))
    parser.add_argument("--chrome", type=Path)
    args = parser.parse_args()
    css = args.css.resolve()
    if not css.is_file():
        parser.error(f"CSS not found: {css}")
    chrome = str(args.chrome or next(
        (Path(p) for p in (
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            shutil.which("google-chrome"), shutil.which("chromium"),
        ) if p and Path(p).is_file()), ""))
    if not chrome or not shutil.which("pdftotext") or not shutil.which("pdfinfo"):
        parser.error("Chrome, pdftotext, and pdfinfo are required")

    long_line = "ABC123xyz_" * 28
    code_html = (
        "<h1>Code export fixture</h1>"
        f"<pre class='md-fences'><code>{long_line}CODE_PLAIN_END_67211</code></pre>"
        f"<pre class='md-fences mock-cm'><code>{long_line}CODE_MOCK_END_67212</code></pre>"
    )
    rows = "".join(
        f"<tr><td>ROW_{i:03d}</td><td>Content for row {i:03d}</td></tr>"
        for i in range(1, 56)
    )
    table_html = (
        "<h1>Table pagination fixture</h1>"
        "<p>Introduction before the table. It should share the first page with "
        "the first table rows.</p>"
        "<figure class='table-figure md-table-fig'><table class='md-table'>"
        f"<thead><tr><th>Index</th><th>Description</th></tr></thead><tbody>{rows}"
        "</tbody></table></figure>"
    )

    expected_sizes = {"A4": (595.28, 841.89), "A5": (419.53, 595.28)}
    with tempfile.TemporaryDirectory(prefix="typora-export-qa-") as dirname:
        directory = Path(dirname)
        for paper, expected in expected_sizes.items():
            for kind, content in (("code", code_html), ("table", table_html)):
                html_path = directory / f"{paper}-{kind}.html"
                pdf_path = directory / f"{paper}-{kind}.pdf"
                html_path.write_text(page(css, paper, content), encoding="utf-8")
                run_pdf(chrome, html_path, pdf_path, directory / f"profile-{paper}-{kind}")
                size = paper_size(pdf_path)
                if any(abs(actual - wanted) > 1 for actual, wanted in zip(size, expected)):
                    raise AssertionError(f"{paper} paper size changed: {size}")
                pages = pdf_text(pdf_path)
                all_text = "".join(pages)
                if not all("HK_EXPORT_HEADER" in part and "HK_EXPORT_FOOTER" in part
                           for part in pages):
                    raise AssertionError(f"{paper} dropped user header/footer on a {kind} page")
                title = "Code export fixture" if kind == "code" else "Table pagination fixture"
                heading_x, heading_y = first_heading_position(pdf_path, title)
                if heading_x < 54 or heading_y < 54:
                    raise AssertionError(
                        f"{paper} ignored 20mm page margins: heading at "
                        f"({heading_x:.1f}, {heading_y:.1f})pt"
                    )
                if kind == "code":
                    # A wrap can split the marker itself across PDF text lines.
                    compact_text = re.sub(r"\s+", "", all_text)
                    for marker in ("CODE_PLAIN_END_67211", "CODE_MOCK_END_67212"):
                        if long_line + marker not in compact_text:
                            raise AssertionError(f"{paper} clipped a long code line: {marker}")
                else:
                    if len(pages) < 2 or "ROW_001" not in pages[0] or "ROW_055" not in all_text:
                        raise AssertionError(
                            f"{paper} table did not paginate by row: "
                            f"pages={len(pages)}, first={pages[0][:250]!r}"
                        )
                print(f"PASS {paper} {kind}: {len(pages)} page(s), {size[0]:.1f}x{size[1]:.1f}pt")


if __name__ == "__main__":
    main()
