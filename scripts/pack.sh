#!/usr/bin/env bash
#
# hekouwang · 打付费主题包 zip（给你私发买家用）
#
#   ./scripts/pack.sh                         # → Desktop
#   ./scripts/pack.sh ~/Desktop/foo.zip
#
# 清单单一真相源：PAID_FILES 数组。打完逐项验货，缺件即删包 exit 1。
# 需要本机有 scripts/palettes.paid.json（不进公开仓）。
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck disable=SC1091
. "$SCRIPT_DIR/links.sh"

PAID_CSS=(
  hekouwang-v1.css hekouwang-v1-dark.css
  hekouwang-v3.css hekouwang-v3-dark.css
  hekouwang-v4.css hekouwang-v4-dark.css
  hekouwang-v5.css hekouwang-v5-dark.css
  hekouwang-v6.css hekouwang-v6-dark.css
)

STAMP="$(date +%Y%m%d)"
OUT="${1:-$HOME/Desktop/hekouwang-typora-theme-pack-$STAMP.zip}"
STAGE="$(mktemp -d "${TMPDIR:-/tmp}/hkw-typora-pack-stage.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT

g='\033[1;32m'; r='\033[1;31m'; b='\033[1;34m'; o='\033[0m'
ok()  { printf "  ${g}✓${o} %s\n" "$*"; }
bad() { printf "  ${r}✗${o} %s\n" "$*"; }

echo -e "${b}hekouwang · pack paid zip${o}"
echo "────────────────────────────────────────"

[ -f "$SCRIPT_DIR/palettes.paid.json" ] || {
  bad "缺少 scripts/palettes.paid.json（付费色板不进公开仓）"
  exit 1
}
[ -f "$SCRIPT_DIR/craft_paid.py" ] || {
  bad "缺少 scripts/craft_paid.py（付费工艺不进公开仓）"
  exit 1
}
ok "palettes.paid.json + craft_paid.py 在位"

echo "  building paid CSS…"
python3 "$SCRIPT_DIR/build.py" --tier paid
ok "build --tier paid"

TOP="hekouwang-typora-theme-pack-$STAMP"
DEST="$STAGE/$TOP"
mkdir -p "$DEST/theme" "$DEST/scripts"

for f in "${PAID_CSS[@]}"; do
  [ -f "$ROOT/theme/$f" ] || { bad "缺 theme/$f"; exit 1; }
  cp "$ROOT/theme/$f" "$DEST/theme/$f"
done
ok "拷贝 10 份付费 CSS"

cp "$SCRIPT_DIR/palettes.paid.json" "$DEST/scripts/palettes.paid.json"
cp "$SCRIPT_DIR/craft_paid.py" "$DEST/scripts/craft_paid.py"
cp "$SCRIPT_DIR/unlock.sh" "$DEST/unlock.sh"
cp "$SCRIPT_DIR/links.sh" "$DEST/scripts/links.sh"
cp "$ROOT/LICENSE-PRO.txt" "$DEST/LICENSE-PRO.txt"
cp "$ROOT/VERSION" "$DEST/VERSION"
chmod +x "$DEST/unlock.sh"

cat > "$DEST/README.txt" <<EOF
hekouwang Typora 主题包 · V1 / V3–V6（各含 Dark）
版本 $(tr -d '[:space:]' < "$ROOT/VERSION") · 打包日 $STAMP

怎么装（macOS）
--------------
完整图文手册（推荐先看）：
  https://huiyonghkw.github.io/hekouwang-typora-theme/#unlock

1. 若还没装免费默认：先 clone 公开仓，跑 ./scripts/install.sh
   $HKW_URL_REPO
2. 本目录执行：
     ./unlock.sh
   或把本 zip 丢给公开仓脚本：
     ./scripts/unlock.sh /path/to/本文件.zip
3. Cmd+Q 完全退出 Typora，再开 → 主题菜单选 Hekouwang V1…V6

买到什么
--------
- skill 对齐的 V1 科技 / V3 财经 / V4 玻璃 / V5 紫 / V6 焰彩
- 浅色 + 深色各一份（共 10 个 CSS）
- 与免费 V2 同一套阅读指标：1rem · 1.65 · 52em · 纸感

授权：见 LICENSE-PRO.txt（个人使用，请勿二次分发）
落地页 / 更新：$HKW_URL_BUY
微信：hekouwang（备注「Typora主题」）
EOF
ok "包内 README / LICENSE-PRO / unlock.sh"

rm -f "$OUT"
(
  cd "$STAGE"
  # 不用 -y：保留 UTF-8 文件名标记；macOS 列表模式仍可能乱，解压是好的
  zip -rq "$OUT" "$TOP"
)

# 验货：PAID_CSS 每一项都在 zip
python3 - "$OUT" "$TOP" "${PAID_CSS[@]}" <<'PY'
import sys, zipfile
out, top = sys.argv[1], sys.argv[2]
need = [f"{top}/theme/{n}" for n in sys.argv[3:]]
need += [
    f"{top}/unlock.sh",
    f"{top}/LICENSE-PRO.txt",
    f"{top}/VERSION",
    f"{top}/scripts/palettes.paid.json",
    f"{top}/scripts/craft_paid.py",
]
z = zipfile.ZipFile(out)
names = set(z.namelist())
missing = [n for n in need if n not in names]
if missing:
    print("MISSING:")
    for m in missing:
        print(" ", m)
    sys.exit(1)
print(len(need), "required entries ok")
PY
ok "验包通过 → $OUT"
printf "\n${g}发给买家：微信传这个 zip，让对方跑 ./unlock.sh${o}\n"
printf "  大小：%s\n" "$(du -h "$OUT" | cut -f1 | tr -d ' ')"
