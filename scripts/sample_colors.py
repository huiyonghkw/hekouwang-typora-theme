#!/usr/bin/env python3
"""
从参照截图采样真实色值 —— 别猜配色。

为什么需要这个：做这套主题时，我笃定页面底色是 Anthropic 的品牌米色 #faf9f5，
采样后发现对话区其实是 #fdfdfc，#faf9f5 是窗口/侧边栏的颜色 —— 两者角色搞反了。
深色版更极端：深色下侧边栏比正文区**更亮**，与浅色模式的关系完全相反，
靠"把浅色取反"推演一定会做错。

用法：
    python3 sample_colors.py <图片>                      # 交互式：给出常见区域的候选
    python3 sample_colors.py <图片> --box 700,640,1700,700 --label 正文背景
    python3 sample_colors.py <图片> --text-box 690,300,1500,345 --label 正文文字
    python3 sample_colors.py <图片> --solve-alpha 1f1f1e 272725 ffffff,d97757

三种模式：
    --box         取区域众数 → 适合大片背景色
    --text-box    取亮/暗像素的众数 → 适合文字笔画色（避开抗锯齿峰值）
    --solve-alpha 反解叠加色：给底色、结果色、若干候选叠加色，
                  算出每个候选在三通道上各自需要的 alpha。
                  三通道解出的 alpha 一致 → 就是它；差异大 → 不是它。
"""
import argparse
import sys
from collections import Counter

try:
    from PIL import Image
except ImportError:
    sys.exit("需要 Pillow：pip3 install pillow")


def hexs(rgb):
    return "#%02x%02x%02x" % rgb


def sample_box(im, box, label):
    x0, y0, x1, y1 = box
    W, H = im.size
    c = Counter()
    for y in range(y0, min(y1, H), 2):
        for x in range(x0, min(x1, W), 2):
            c[im.getpixel((x, y))] += 1
    if not c:
        print(f"  {label}: 区域为空")
        return None
    total = sum(c.values())
    top = c.most_common(3)
    rgb, n = top[0]
    print(f"  {label:16s} {hexs(rgb)}   占比 {100*n/total:.0f}%")
    if 100 * n / total < 60:
        alts = "  ".join(f"{hexs(r)}({100*k/total:.0f}%)" for r, k in top[1:])
        print(f"    ⚠️ 占比偏低，区域可能不纯。次选: {alts}")
    return rgb


def sample_text(im, box, label, dark_text=None):
    """
    取文字笔画主色。抗锯齿会产生大量中间色，最亮/最暗的极值点通常是溢出峰值，
    不可信；取「排除背景后的众数」才是真实笔画色。
    dark_text=None 时自动判断：区域均值偏亮 → 深色文字，反之浅色文字。
    """
    x0, y0, x1, y1 = box
    W, H = im.size
    px = [im.getpixel((x, y)) for y in range(y0, min(y1, H)) for x in range(x0, min(x1, W))]
    if not px:
        print(f"  {label}: 区域为空")
        return None
    mean = sum(sum(p) / 3 for p in px) / len(px)
    if dark_text is None:
        dark_text = mean > 128
    keep = [p for p in px if (sum(p) / 3 < mean - 30) if dark_text] or \
           [p for p in px if (sum(p) / 3 > mean + 30)]
    if not keep:
        print(f"  {label}: 没有与背景区分明显的像素，换个区域")
        return None
    c = Counter(keep)
    rgb, n = c.most_common(1)[0]
    kind = "深色文字" if dark_text else "浅色文字"
    print(f"  {label:16s} {hexs(rgb)}   ({kind}，占笔画像素 {100*n/len(keep):.0f}%)")
    return rgb


def solve_alpha(base_hex, result_hex, candidates):
    """
    反解：result = base 上叠加了某个颜色的 alpha。
    对每个候选色，在 R/G/B 三通道分别解 alpha。三者接近 → 就是这个叠加色。
    这是判断「代码底是品牌色浅铺还是中性叠加」的可靠方法，比肉眼准。
    """
    def to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    base, result = to_rgb(base_hex), to_rgb(result_hex)
    print(f"  底色 #{base_hex.lstrip('#')} → 结果 #{result_hex.lstrip('#')}"
          f"   通道差 {tuple(r-b for r, b in zip(result, base))}\n")
    best = None
    for cand in candidates:
        c = to_rgb(cand)
        alphas = []
        for b, r, cc in zip(base, result, c):
            if cc == b:
                alphas.append(None)
            else:
                alphas.append((r - b) / (cc - b))
        valid = [a for a in alphas if a is not None and 0 <= a <= 1]
        if len(valid) < 2:
            print(f"  #{cand.lstrip('#')}: 无法解出合理 alpha")
            continue
        spread = max(valid) - min(valid)
        txt = " / ".join("—" if a is None else f"{a:.3f}" for a in alphas)
        verdict = "✅ 三通道一致 → 就是它" if spread < 0.02 else \
                  ("△ 尚可" if spread < 0.05 else "❌ 通道间差异大 → 不是它")
        print(f"  #{cand.lstrip('#'):<8} alpha(R/G/B) = {txt}   离散度 {spread:.3f}   {verdict}")
        if best is None or spread < best[1]:
            best = (cand, spread, sum(valid) / len(valid))
    if best:
        print(f"\n  结论：叠加色 #{best[0].lstrip('#')}，alpha ≈ {best[2]:.3f}")


PRESETS = [
    ("正文/内容区背景", "box", (0.35, 0.45, 0.85, 0.50)),
    ("侧边栏背景",      "box", (0.07, 0.35, 0.25, 0.40)),
    ("窗口最外层",      "box", (0.01, 0.20, 0.04, 0.80)),
    ("正文文字",        "text", (0.35, 0.20, 0.75, 0.24)),
    ("次级/侧边栏文字",  "text", (0.08, 0.42, 0.21, 0.46)),
]


def main():
    ap = argparse.ArgumentParser(description="从参照截图采样真实色值")
    ap.add_argument("image", nargs="?", help="截图路径")
    ap.add_argument("--box", help="x0,y0,x1,y1 —— 取区域众数（背景色）")
    ap.add_argument("--text-box", help="x0,y0,x1,y1 —— 取文字笔画色")
    ap.add_argument("--label", default="采样", help="这次采样的名字")
    ap.add_argument("--solve-alpha", nargs=3, metavar=("BASE", "RESULT", "CANDIDATES"),
                    help="反解叠加色：底色 结果色 候选色(逗号分隔)")
    args = ap.parse_args()

    if args.solve_alpha:
        base, result, cands = args.solve_alpha
        solve_alpha(base, result, cands.split(","))
        return

    if not args.image:
        ap.error("需要图片路径（除非用 --solve-alpha）")

    im = Image.open(args.image).convert("RGB")
    W, H = im.size
    print(f"{args.image}  {W}×{H}\n")

    if args.box:
        sample_box(im, tuple(int(v) for v in args.box.split(",")), args.label)
    elif args.text_box:
        sample_text(im, tuple(int(v) for v in args.text_box.split(",")), args.label)
    else:
        print("按常见布局猜的区域（比例定位，不一定准，请用 --box 精确指定）：\n")
        for label, kind, (rx0, ry0, rx1, ry1) in PRESETS:
            box = (int(rx0 * W), int(ry0 * H), int(rx1 * W), int(ry1 * H))
            (sample_box if kind == "box" else sample_text)(im, box, label)
        print("\n提示：占比 <60% 说明区域不纯，换一块干净的空白处重采。")


if __name__ == "__main__":
    main()
