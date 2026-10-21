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
MAX_READING_REM = 96
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
    sixTable:box('six-table'), sevenFigure:box('seven-figure'),
    sevenTable:box('seven-table'), tierFigure:box('tier-figure'), directFourTable:box('direct-four-table'),
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
        f'<th style="min-width:8rem">Technical {i}</th>' for i in range(1, 21)
    )
    dense_row = "".join(f"<td>value_{i:02d}</td>" for i in range(1, 21))
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>{TYPORA_BASE}</style>
<link rel="stylesheet" href="{css.as_uri()}">
<style>{extra_css}</style>
</head><body class="pin-outline"><div id="qa-topbar" style="height:40px"></div><content><div id="write">
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
<figure class="md-table-fig table-figure" id="tier-figure"><table class="md-table" id="tier-table">
<thead><tr><th>档次</th>{''.join(f'<th>{v}</th>' for v in (200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 6400, 10190))}</tr></thead>
<tbody><tr><td>政府补贴</td>{''.join(f'<td>{v}</td>' for v in (40, 45, 50, 60, 60, 65, 70, 75, 80, 100, 120, 160, 200, 240, 280, 280, 280))}</tr></tbody></table></figure>
<figure class="md-table-fig table-figure" id="seven-figure"><table class="md-table" id="seven-table">{short_table(7)}</table></figure>
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


def measure_many(chrome: str, css: Path, jobs) -> dict:
    """一次 Chrome 启动，测完全部宽度。

    以前每个宽度都要冷启一次 Chrome（3 秒 x 11 档 x 14 套 = 6 分钟）。
    现在把 N 个宽度打包进同一个页面，用 N 个 iframe 并排跑，
    Chrome 冷启只发生一次 —— 单套从 30 秒降到 3 秒。

    jobs: [(key, width, extra_css, scale), ...]
    返回 {key: geometry dict}
    """
    jobs = list(jobs)
    if not jobs:
        return {}

    # 临时页面建在系统临时目录，不落在 theme/ 里：
    # 以前建在 theme/ 下，进程被中断就会留下 layout-probe-*.html 垃圾
    # （theme/ 是产物目录，脏了会让 git status 出现未跟踪文件）。
    # 字体等相对资源由 <link> 指向的 CSS 自己解析，与页面位置无关。
    workdir = Path(tempfile.mkdtemp(prefix="typora-layout-"))
    try:
        pages = []
        for index, (_key, width, extra_css, scale) in enumerate(jobs):
            page_path = workdir / ("probe-%d.html" % index)
            page_path.write_text(fixture(css, extra_css), encoding="utf-8")
            pages.append(page_path)

        frames = []
        for index, (_key, width, extra_css, scale) in enumerate(jobs):
            # Chrome headless 强制 500px 最小顶层窗口，所以窄屏一律用
            # 同源 iframe 拿到真实的 320/480 CSS 视口；scale=2 模拟 200% 缩放。
            transform = ""
            if scale != 1:
                transform = "transform:scale(%d);transform-origin:top left;" % scale
            frames.append(
                '<iframe id="f%d" src="%s" style="border:0;width:%dpx;'
                'height:1800px;%s"></iframe>'
                % (index, pages[index].as_uri(), width, transform)
            )

        outer = workdir / "outer.html"
        # 顺序很关键：iframe 必须先写进 DOM，收集脚本再跑；
        # 且首次轮询要延迟，等子文档把几何数据算完。
        outer.write_text(
            '<!doctype html><meta charset="utf-8">'
            '<pre id="__BATCH__">pending</pre>'
            + "".join(frames)
            + "<script>"
            "const IDS=" + json.dumps(["f%d" % i for i in range(len(jobs))]) + ";"
            "const got={};"
            "function poll(){"
            "  for(const id of IDS){"
            "    if(got[id]!==undefined) continue;"
            "    const fr=document.getElementById(id);"
            "    const doc=fr&&fr.contentDocument;"
            "    const rep=doc&&doc.getElementById('__LAYOUT__');"
            "    if(rep&&rep.textContent&&rep.textContent!=='pending'){"
            "      got[id]=rep.textContent;"
            "    }"
            "  }"
            "  if(Object.keys(got).length===IDS.length){"
            "    document.getElementById('__BATCH__').textContent=JSON.stringify(got);"
            "    return;"
            "  }"
            "  setTimeout(poll,50);"
            "}"
            "setTimeout(poll,200);"
            "</script>",
            encoding="utf-8",
        )

        widest = max(max(500, width * scale) for _k, width, _e, scale in jobs)
        with tempfile.TemporaryDirectory(prefix="typora-layout-profile-") as profile:
            result = subprocess.run(
                [chrome, "--headless", "--disable-gpu", "--incognito",
                 "--allow-file-access-from-files", f"--user-data-dir={profile}",
                 "--virtual-time-budget=10000",
                 f"--window-size={widest},1200",
                 "--dump-dom", outer.as_uri()],
                capture_output=True, text=True, timeout=120,
            )
        match = re.search(r'<pre id="__BATCH__"[^>]*>(.*?)</pre>', result.stdout, re.S)
        if not match or match.group(1).strip() == "pending":
            raise RuntimeError(
                f"Chrome did not return geometry for {css.name}: "
                f"{result.stderr[-500:]}"
            )
        raw = json.loads(html.unescape(match.group(1)))
        return {
            job[0]: json.loads(html.unescape(raw["f%d" % index]))
            for index, job in enumerate(jobs)
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def measure(chrome: str, css: Path, width: int, extra_css: str = "",
            scale: int = 1) -> dict:
    """单宽度测量（保留给需要单独调用的场景）。"""
    key = "%d:%d:%s" % (width, scale, extra_css)
    return measure_many(chrome, css, [(key, width, extra_css, scale)])[key]


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

    for label in ("code", "longCode"):
        need(abs(data[label]["width"] - data["prose"]["width"]) <= 3
             and abs(data[label]["left"] - data["prose"]["left"]) <= 3,
             f"{label} is not aligned with the reading column "
             f"({data[label]['width']:.0f}/{data['prose']['width']:.0f}px)")
    need(data["code"]["scrollWidth"] <= data["code"]["clientWidth"] + 2,
         "bare pre > code extends outside its paper box")
    need(data["codeScroll"]["overflowX"] in ("auto", "scroll")
         and data["codeScroll"]["scrollWidth"] >= data["codeScroll"]["clientWidth"] + 100,
         "long code does not scroll inside its CodeMirror container")
    # Wide tables start at the reading column and grow toward the canvas
    # only as far as their content requires.
    need(data["wideTable"]["width"] >= min(data["prose"]["width"], content_width) - 3,
         f"eight-column table is narrower than the reading column "
         f"({data['wideTable']['width']:.0f}/{data['prose']['width']:.0f}px)")
    need(data["wideTable"]["width"] > data["prose"]["width"] + 3
         or data["wideTable"]["width"] >= content_width - 4
         or abs(data["wideFigure"]["left"] - data["prose"]["left"]) <= 3,
         "wide table is not centered on the reading column")
    need(data["wideFigure"]["width"] <= content_width + 17,
         "table figure escapes the paper content box")
    need(data["sourceLines"]["width"] <= data["prose"]["width"] + data["rootSize"] * 7 + 3,
         f"source mode is too wide ({data['sourceLines']['width']:.0f}px)")
    if requested_width >= 1440:
        need(data["sparseTable"]["width"] <= data["rootSize"] * 48 + 2,
             f"small table exceeded the 48rem cap "
             f"({data['sparseTable']['width']:.0f}px)")
    if requested_width == 2048:
        need(data["prose"]["width"] >= data["rootSize"] * 64,
             f"prose does not use the wide desktop ({data['prose']['width']:.0f}px)")

    # Typora wraps edited tables in figure.md-table-fig. Four and six column
    # tables should use the same responsive reading width as adjacent prose.
    # The direct table checks the exported/plain HTML fallback.
    # A short seven-column table fits the reading column, so it must align
    # with prose instead of jumping to the wide canvas.
    for label in ("fourFigure", "sixFigure", "sevenFigure", "denseFourFigure",
                  "directFourTable"):
        need(abs(data[label]["left"] - data["prose"]["left"]) <= 3,
             f"{label} starts at {data[label]['left']:.0f}px, "
             f"prose at {data['prose']['left']:.0f}px")
        need(abs(data[label]["width"] - data["prose"]["width"]) <= 3,
             f"{label} width {data[label]['width']:.0f}px does not fill "
             f"prose width {data['prose']['width']:.0f}px")
    for table_name, figure_name in (("fourTable", "fourFigure"),
                                    ("sixTable", "sixFigure"),
                                    ("sevenTable", "sevenFigure"),
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

    if requested_width >= 1800 and max_reading_rem == MAX_READING_REM:
        tier = data["tierFigure"]
        need(tier["scrollWidth"] <= tier["clientWidth"] + 2,
             f"17-column numeric table scrolls on a wide screen "
             f"({tier['scrollWidth']:.0f}/{tier['clientWidth']:.0f}px)")
    if requested_width == 1800:
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
        # 一次 Chrome 启动测完全部档位（以前每档冷启一次，14 套要 6 分钟）
        jobs = [(str(width), width, "", 1) for width in WIDTHS]
        zoom_css = ("#write { line-height: 1.5; letter-spacing: 0.12em; "
                    "word-spacing: 0.16em; } #write p { margin-bottom: 2em; }")
        extras = [
            ("zoom", 320, "", MAX_READING_REM, 2),
            ("text spacing", 320, zoom_css, MAX_READING_REM, 1),
            ("40rem override", 1800, ":root { --hk-reading-measure: 40rem; }", 40, 1),
        ]
        for label, width, extra_css, _max_rem, scale in extras:
            jobs.append((label, width, extra_css, scale))
        measured = measure_many(chrome, css, jobs)

        for width in WIDTHS:
            data = measured[str(width)]
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
                              "directFourTable"):
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
        for label, width, extra_css, max_rem, scale in extras:
            data = measured[label]
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
