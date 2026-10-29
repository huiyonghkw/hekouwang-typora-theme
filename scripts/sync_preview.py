#!/usr/bin/env python3
"""
hekouwang · 在线体验页资源同步
theme/hekouwang.css · theme/hekouwang-dark.css · theme/hekouwang/fonts
    → docs/live/theme/

体验页 docs/live/index.html 直接吃这份拷贝，浏览器里渲染的就是构建产物本身，
不做二次包装。主题重新生成后需重跑本脚本，--check 用于 CI 防止演示页悄悄过期。
"""
import filecmp
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "theme")
DST = os.path.join(ROOT, "docs", "live", "theme")
FILES = ["hekouwang.css", "hekouwang-dark.css"]
FONTS_SRC = os.path.join(SRC, "hekouwang", "fonts")
FONTS_DST = os.path.join(DST, "hekouwang", "fonts")


def plan():
    for name in FILES:
        yield os.path.join(SRC, name), os.path.join(DST, name)
    for name in sorted(os.listdir(FONTS_SRC)):
        yield os.path.join(FONTS_SRC, name), os.path.join(FONTS_DST, name)


def main():
    check = "--check" in sys.argv
    stale = []
    for src, dst in plan():
        if os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False):
            continue
        stale.append(os.path.relpath(dst, ROOT))
        if not check:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    if check and stale:
        print("❌ docs/live/theme 与 theme/ 不一致，请运行 python3 scripts/sync_preview.py")
        for path in stale:
            print("   " + path)
        return 1
    if stale:
        print("✅ 已同步 %d 个文件到 docs/live/theme" % len(stale))
    else:
        print("✅ docs/live/theme 已是最新")
    return 0


if __name__ == "__main__":
    sys.exit(main())
