#!/usr/bin/env python3
"""
渲染验证探针 —— 让"字体没上屏""色值没生效"这类静默失败当场暴露。

为什么需要这个：做这套主题时，headless 探针报「字体已上屏 true、字重宽度单调递增」全绿，
但在 Typora 里字体压根没加载（`format("truetype-variations")` 被老 Chromium 丢弃，
整条 src 作废后悄悄 fallback 到系统字体）。全绿的验证给了假结论。
后来发现探针本身还有第二个 bug：@font-face 是懒加载，没 await document.fonts.load()
就测量，三种字体会量到同一个 fallback 值。

所以这个脚本做两件事：
  1. 显式 load 并 await 之后再测量；
  2. 永远带一个「不存在的字体」作为 fallback 基准 —— 任何字体只要量出来等于基准，
     就说明它没生效，只是悄悄用了系统字体。没有基准的宽度数字毫无意义。

⚠️ 但请记住：本脚本跑在系统 Chrome 里，而主题的目标宿主是 Typora 内嵌的 Chromium
（通常老得多）。**这里全绿不等于 Typora 里对**，最终验收必须在 Typora 里看。
本脚本只能筛掉低级错误，不能签收。

用法：
    python3 verify_render.py --css hekouwang.css --fonts "Hekouwang Sans,Hekouwang Sans Fb"
    python3 verify_render.py --css hekouwang.css --vars bg-color,text-color,hk-code
    python3 verify_render.py --css hekouwang.css --screenshot out.png
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]

PROBE_JS = r"""
(async () => {
  const out = {fonts: [], vars: {}, notes: []};
  const FONTS = __FONTS__;
  // @font-face 是懒加载：声明 ≠ 下载。不显式 load 就测量，量到的全是 fallback。
  for (const f of FONTS) {
    for (const w of [400, 700]) {
      try { await document.fonts.load(`${w} 48px "${f}"`); } catch (e) {}
    }
  }
  await document.fonts.ready;

  const meas = (family, weight) => {
    const s = document.createElement('span');
    s.style.cssText = `position:absolute;visibility:hidden;white-space:nowrap;`
                    + `font-size:48px;font-weight:${weight};font-family:${family}`;
    s.textContent = 'Handgloves 2026 mixed 中文';
    document.body.appendChild(s);
    const w = s.getBoundingClientRect().width;
    s.remove();
    return +w.toFixed(2);
  };

  // 基准：一个必然不存在的字体族，量出的就是系统 fallback 的宽度
  const BASE = meas('"__no_such_font_xyz__"', 400);
  out.baseline = BASE;

  for (const f of FONTS) {
    const w400 = meas(`"${f}"`, 400);
    const w700 = meas(`"${f}"`, 700);
    out.fonts.push({
      family: f,
      loaded: document.fonts.check(`48px "${f}"`),
      width400: w400,
      width700: w700,
      distinctFromBaseline: w400 !== BASE,
      weightVaries: w400 !== w700,
    });
  }

  const VARS = __VARS__;
  if (VARS.length) {
    const cs = getComputedStyle(document.documentElement);
    for (const v of VARS) out.vars[v] = cs.getPropertyValue(v).trim();
  }

  const el = document.querySelector('#write');
  if (el) {
    const s = getComputedStyle(el);
    out.write = {fontFamily: s.fontFamily.split(',')[0], fontSize: s.fontSize,
                 lineHeight: s.lineHeight, color: s.color, background: s.backgroundColor};
  }
  document.getElementById('__PROBE__').textContent = JSON.stringify(out);
})();
"""


def find_chrome():
    for p in CHROME_CANDIDATES:
        if p and os.path.exists(p):
            return p
    sys.exit("找不到 Chrome/Chromium，请手动指定 --chrome")


def build_page(css_path, fonts, variables, body_class=""):
    css_url = "file://" + os.path.abspath(css_path)
    js = (PROBE_JS
          .replace("__FONTS__", json.dumps(fonts))
          .replace("__VARS__", json.dumps(variables)))
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{css_url}"></head>
<body class="{body_class}"><div id="write"><p>probe 中文 mixed</p>
<pre id="__PROBE__">pending</pre>
<script>{js}</script></div></body></html>"""


def run(chrome, html_path, screenshot=None):
    tmp = tempfile.mkdtemp(prefix="typora-theme-verify-")
    args = [chrome, "--headless", "--disable-gpu", "--incognito",
            "--allow-file-access-from-files", f"--user-data-dir={tmp}",
            "--virtual-time-budget=10000"]
    if screenshot:
        args += [f"--screenshot={screenshot}", "--force-device-scale-factor=2",
                 "--window-size=900,1200"]
    else:
        args += ["--dump-dom"]
    args.append("file://" + html_path)
    r = subprocess.run(args, capture_output=True, text=True, timeout=90)
    shutil.rmtree(tmp, ignore_errors=True)
    return r.stdout


def main():
    ap = argparse.ArgumentParser(description="Typora 主题渲染验证探针")
    ap.add_argument("--css", required=True, help="要验证的主题 CSS")
    ap.add_argument("--fonts", default="", help="逗号分隔的字体族名")
    # 变量名可省略 -- 前缀。写 --vars "--bg-color" 会被 argparse 当成另一个选项，
    # 所以这里接受 "bg-color" 并自动补前缀（带前缀时也要用 --vars=--bg-color 形式）。
    ap.add_argument("--vars", default="",
                    help="逗号分隔的 CSS 变量名，可省略 -- 前缀，如 bg-color,text-color")
    ap.add_argument("--screenshot", help="同时出一张截图")
    ap.add_argument("--chrome", help="Chrome 可执行文件路径")
    ap.add_argument("--windows", action="store_true",
                    help="用 body.os-windows 预检 Windows 字体栈与排版规则")
    args = ap.parse_args()

    if not os.path.exists(args.css):
        sys.exit(f"找不到 CSS: {args.css}")

    chrome = args.chrome or find_chrome()
    fonts = [f.strip() for f in args.fonts.split(",") if f.strip()]
    variables = ["--" + v.strip().lstrip("-") for v in args.vars.split(",") if v.strip()]

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False,
                                     dir=os.path.dirname(os.path.abspath(args.css)),
                                     encoding="utf-8") as f:
        f.write(build_page(args.css, fonts, variables,
                           "os-windows" if args.windows else ""))
        html = f.name

    try:
        if args.screenshot:
            run(chrome, html, args.screenshot)
            print(f"截图 → {args.screenshot}")
        dom = run(chrome, html)
    finally:
        os.unlink(html)

    m = re.search(r'<pre id="__PROBE__">(.*?)</pre>', dom, re.S)
    if not m or m.group(1).strip() == "pending":
        sys.exit("探针未返回结果（页面可能报错或超时）")
    data = json.loads(m.group(1))

    platform = " · Windows 预检" if args.windows else ""
    print(f"\n渲染验证 · {os.path.basename(args.css)}{platform}")
    print("─" * 56)

    if data.get("write"):
        w = data["write"]
        print(f"#write  字体 {w['fontFamily']}  字号 {w['fontSize']}  行高 {w['lineHeight']}")
        print(f"        前景 {w['color']}   背景 {w['background']}")

    if data["fonts"]:
        base = data["baseline"]
        print(f"\n字体（fallback 基准宽度 = {base}px，等于它就说明没生效）")
        bad = 0
        for f in data["fonts"]:
            if f["distinctFromBaseline"]:
                mark, note = "✅", ""
            else:
                mark, note = "❌", "  ← 与基准相同，实际用的是系统字体"
                bad += 1
            wv = "可变" if f["weightVaries"] else "无字重差异"
            print(f"  {mark} {f['family']:<24} {f['width400']:>8.2f}px  "
                  f"check={str(f['loaded']):<5} {wv}{note}")
        if bad:
            print(f"\n  ⚠️ {bad} 个字体未真实生效。常见原因："
                  "\n     · @font-face 的 src 路径不对（相对路径基准是 CSS 文件所在目录）"
                  "\n     · format() 用了 truetype-variations 等非标准值，整条 src 被丢弃"
                  "\n     · 字体栈里的族名与 @font-face 的 font-family 不一致（改名时最常见）")

    if data["vars"]:
        print("\nCSS 变量")
        for k, v in data["vars"].items():
            print(f"  {k:<28} {v or '(空 —— 变量未定义)'}")

    print("\n⚠️ 这里全绿只代表在系统 Chrome 里没问题。")
    print("   目标宿主 Typora 用的是更老的内嵌 Chromium，最终验收必须在 Typora 里看。")
    if args.windows:
        print("   Windows 真机还须验收：编辑/源码/专注、表格/代码/Mermaid，以及 PDF/HTML/图片导出。")


if __name__ == "__main__":
    main()
