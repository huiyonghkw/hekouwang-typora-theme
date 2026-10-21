#!/usr/bin/env bash
# ============================================================
# 预览图刷新 —— 在 Typora 里实拍，浅色 + 深色各一张
#
# 用法：./scripts/shoot_previews.sh [输出目录]
#
# 为什么不能用 headless 拍：docs/previews/*.webp 是 Typora 应用窗口
# 截图（含侧边栏、工具栏、真实字体渲染），不是纯 CSS 渲染。
# 仓库里已有 verify_render.py 那种 headless 探针，但产物形态不同。
# ============================================================
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
OUT_DIR="${1:-$ROOT/docs/previews}"
SAMPLE="$ROOT/demo/acceptance-sample.md"
PREF="abnerworks.Typora"
THEME_DIR="$HOME/Library/Application Support/abnerworks.Typora/themes"

ok()  { printf '\033[38;2;55;141;239m  ✅ %s\033[0m\n' "$*"; }
warn() { printf '  ⚠️  %s\n' "$*"; }
bad()  { printf '  ❌ %s\n' "$*"; }

[ -f "$SAMPLE" ] || { bad "找不到样张：$SAMPLE"; exit 1; }
mkdir -p "$OUT_DIR"

# ⚠️ 不要让 Typora 打开仓库里的样张本身。
# Typora 打开带 frontmatter 的 md 时会把 theme: 键改名（ctheme:），
# 退出时写回 —— 仓库里的样张就这样被改坏了，而且中断时连 trap 都救不回来。
# 所以给它一份临时副本打开，仓库里的文件根本不碰。
WORK="$(mktemp -d -t hekouwang-shoot)"
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT INT TERM
cp "$SAMPLE" "$WORK/sample.md"

# 屏幕分辨率与缩放 —— 截图要按物理像素，retina 下是 2 倍
read -r SCR_W SCR_H <<< "$(osascript -e 'tell application "Finder" to get bounds of window of desktop' | tr ',' ' ')"
SCALE=2

# ------------------------------------------------------------
# 切主题并重启 Typora（改完 CSS 必须完全退出重开，否则加载的是旧版）
# ------------------------------------------------------------
set_theme() {
  local theme="$1" dark="$2"
  defaults write "$PREF" theme -string "$theme"
  defaults write "$PREF" useSeparateDarkTheme -bool "$dark"
  defaults write "$PREF" useDarkTheme -bool false
  defaults write "$PREF" darkTheme -string "$theme"
}

restart_typora() {
  osascript -e 'tell application "Typora" to quit' >/dev/null 2>&1
  sleep 2
  pkill -x Typora >/dev/null 2>&1
  sleep 1
  # 打开临时副本，不碰仓库里的样张（见上方说明）
  open -a Typora "$WORK/sample.md"
  sleep 5
}

# 把 Typora 窗口摆到左上角并放到目标尺寸（1920x1154 逻辑像素）
place_window() {
  osascript <<'APPLESCRIPT' >/dev/null 2>&1
tell application "System Events" to tell process "Typora"
  set frontmost to true
  delay 0.4
  try
    set {x, y} to position of front window
    set {ww, hh} to size of front window
    set position of front window to {0, 0}
    set size of front window to {960, 577}
  end try
end tell
APPLESCRIPT
  sleep 1.5
}

shoot() {
  local outfile="$1"
  local geo x y w h
  # 用 | 分隔取几何：AppleScript 把 position/size 转字符串时会粘连
  # （{0,33} 与 {960,577} 会变成 "033,960,577"），按空格切会切错。
  geo="$(osascript <<'APPLESCRIPT' 2>/dev/null
tell application "System Events" to tell process "Typora"
  set {x, y} to position of front window
  set {ww, hh} to size of front window
  return "GEOM " & x & "|" & y & "|" & ww & "|" & hh
end tell
APPLESCRIPT
)"
  # 用 | 分隔再按行切成四段（AppleScript 的 list 转字符串会粘连，
  # 空格分割会切错；tr 转成一行后按 | 切最稳）
  # 直接按 | 切成四段（tr 会把 | 换成空格，IFS 又按 | 切，两边打架）
  local parts
  parts="$(echo "$geo" | tr '\n' ' ' | tr -s '[:space:]' ' ')"
  IFS='|' read -r _gx _gy _gw _gh <<< "$parts"
  x="${_gx#GEOM }"
  y="${_gy}"
  w="${_gw}"
  h="${_gh}"
  # read 会把分隔符后的空白留在最后一个变量里（h="577 "），
  # 拼进 screencapture -R 会让坐标串多一个尾随空格而截图失败。
  x="${x// /}"; y="${y// /}"; w="${w// /}"; h="${h// /}"
  if [ -z "$w" ] || [ "$w" = "0" ]; then
    bad "拿不到窗口几何"
    return 1
  fi
  local pw ph
  pw=$(( w * SCALE ))
  ph=$(( h * SCALE ))
  screencapture -x -R "$x,$y,$w,$h" /tmp/_hkw_shot.png 2>/dev/null
  # 裁到目标尺寸
  sips --cropToHeightWidth "$ph" "$pw" /tmp/_hkw_shot.png --out "$outfile" >/dev/null 2>&1
  # 转 webp（质量 82，体积与历史一致）
  cwebp -q 82 -quiet "$outfile" -o "${outfile%.png}.webp" 2>/dev/null
  rm -f /tmp/_hkw_shot.png
  ok "$(${outfile%.png}.webp)  ${pw}x${ph}"
}

# 主题清单：菜单名 → 输出文件名
# 免费 V2 永远拍；付费六套若已装进 Typora（themes/ 下有对应 CSS）也一起拍。
ALL_THEMES=(
  "Hekouwang:v2"
  "Hekouwang V1:v1"
  "Hekouwang V2 Pro:v2-pro"
  "Hekouwang V3:v3"
  "Hekouwang V4:v4"
  "Hekouwang V5:v5"
  "Hekouwang V6:v6"
)

echo "hekouwang · 预览图刷新"
echo "────────────────────────────────────────"

for entry in "${ALL_THEMES[@]}"; do
  menu="${entry%%:*}"
  slug="${entry##*:}"
  for variant in light dark; do
    if [ "$variant" = "dark" ]; then
      theme="$menu Dark"
    else
      theme="$menu"
    fi
    # 主题没装进 Typora 就跳过（付费档没解锁时跳过，不报错）
    css_name="hekouwang-$slug.css"
    [ "$slug" = "v2" ] && css_name="hekouwang.css"
    if [ ! -f "$THEME_DIR/$css_name" ]; then
      warn "跳过 $theme（未安装：$css_name）"
      continue
    fi
    echo "▸ $theme"
    set_theme "$theme" true
    restart_typora
    place_window
    shoot "$OUT_DIR/_$slug-$variant.png"
  done
done

echo "────────────────────────────────────────"
echo "  完成。产物在 $OUT_DIR 下 _<slug>-<variant>.png / .webp"
echo "  确认无误后再改名覆盖 docs/previews/<slug>-<variant>.webp"
