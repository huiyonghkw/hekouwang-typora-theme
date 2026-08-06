#!/usr/bin/env bash
#
# hekouwang · 安装付费主题包到 Typora
#
# 两种用法：
#   1) 公开仓里（推荐）：
#        ./scripts/unlock.sh ~/Downloads/hekouwang-typora-theme-pack-YYYYMMDD.zip
#   2) 付费 zip 解压后自带同款脚本：
#        ./unlock.sh
#
# 不回连服务器、不搞解锁码。校验 zip 完整性后，把 V1/V3–V6 浅深 CSS
# 拷进 Typora 主题目录。免费 V2 请先用 ./scripts/install.sh。
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 在 zip 根目录时 SCRIPT_DIR 就是包根；在公开仓 scripts/ 时上一级是仓根
if [ -f "$SCRIPT_DIR/theme/hekouwang-v1.css" ]; then
  PACK_ROOT="$SCRIPT_DIR"
elif [ -f "$SCRIPT_DIR/../theme/hekouwang-v1.css" ] && [ ! -f "$SCRIPT_DIR/links.sh" ]; then
  PACK_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
else
  PACK_ROOT=""
fi

# shellcheck disable=SC1091
if [ -f "$SCRIPT_DIR/links.sh" ]; then
  . "$SCRIPT_DIR/links.sh"
elif [ -f "$SCRIPT_DIR/scripts/links.sh" ]; then
  . "$SCRIPT_DIR/scripts/links.sh"
else
  HKW_URL_BUY="https://huiyonghkw.github.io/hekouwang-typora-theme/#buy"
fi

THEME_DIR="$HOME/Library/Application Support/abnerworks.Typora/themes"
BACKUP_DIR="$THEME_DIR/.hekouwang-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
MARKER="theme/hekouwang-v1.css"
PAID_VARIANTS=(
  hekouwang-v1 hekouwang-v1-dark
  hekouwang-v3 hekouwang-v3-dark
  hekouwang-v4 hekouwang-v4-dark
  hekouwang-v5 hekouwang-v5-dark
  hekouwang-v6 hekouwang-v6-dark
)

ZIP=""
DRY=0
for a in "$@"; do
  case "$a" in
    --dry-run|-n) DRY=1 ;;
    -h|--help)
      sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    -*) echo "unknown option: $a" >&2; exit 1 ;;
    *) ZIP="$a" ;;
  esac
done

ok()   { printf '  ✅ %s\n' "$*"; }
bad()  { printf '  ❌ %s\n' "$*"; }
warn() { printf '  ⚠️  %s\n' "$*"; }
dim()  { printf '  · %s\n' "$*"; }

echo "hekouwang · unlock paid pack"
echo "────────────────────────────────────────"

# ---- resolve source tree (zip extract or already unpacked) ----
WORK=""
CLEANUP=""
if [ -n "$ZIP" ]; then
  [ -f "$ZIP" ] || { bad "找不到文件：$ZIP"; exit 1; }
  ok "zip $(du -h "$ZIP" | cut -f1 | tr -d ' ')"
  if ! unzip -tqq "$ZIP" >/dev/null 2>&1; then
    bad "zip 损坏或被截断（微信/网盘传输常见）。请重新下载后再试。"
    exit 1
  fi
  ok "zip 完整性通过"
  # 用 python 列名（macOS unzip -Z1 会弄坏中文名）
  if ! python3 - "$ZIP" "${MARKER}" <<'PY'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
names = z.namelist()
marker = sys.argv[2]
# 允许顶层目录包一层
ok = any(n == marker or n.endswith("/" + marker) for n in names)
sys.exit(0 if ok else 1)
PY
  then
    bad "这不是付费主题包（缺少 ${MARKER}）"
    dim "购买与交付：${HKW_URL_BUY}"
    exit 1
  fi
  ok "确认是付费包（含 ${MARKER}）"
  WORK="$(mktemp -d "${TMPDIR:-/tmp}/hkw-typora-pack.XXXXXX")"
  CLEANUP="$WORK"
  if ! unzip -o -q "$ZIP" -d "$WORK"; then
    bad "解压失败"
    rm -rf "$CLEANUP"
    exit 1
  fi
  # 若 zip 包了一层目录，找含 marker 的那一层
  if [ -f "$WORK/${MARKER}" ]; then
    PACK_ROOT="$WORK"
  else
    found="$(find "$WORK" -type f -path "*/${MARKER}" 2>/dev/null | head -1)"
    if [ -n "$found" ]; then
      PACK_ROOT="$(cd "$(dirname "$found")/.." && pwd)"
    else
      bad "解压后找不到 ${MARKER}"
      rm -rf "$CLEANUP"
      exit 1
    fi
  fi
elif [ -n "$PACK_ROOT" ] && [ -f "$PACK_ROOT/${MARKER}" ]; then
  ok "使用已解压目录：$PACK_ROOT"
else
  echo "用法："
  echo "  ./scripts/unlock.sh ~/Downloads/hekouwang-typora-theme-pack-YYYYMMDD.zip"
  echo "  # 或在付费包解压目录里：./unlock.sh"
  echo
  dim "购买：${HKW_URL_BUY}"
  exit 1
fi

if [ ! -d "$THEME_DIR" ]; then
  bad "找不到 Typora 主题目录：$THEME_DIR"
  dim "请先安装 Typora，或 Preferences → Open Theme Folder 核对路径"
  [ -n "$CLEANUP" ] && rm -rf "$CLEANUP"
  exit 1
fi
ok "Typora 主题目录就绪"

missing=0
for v in "${PAID_VARIANTS[@]}"; do
  [ -f "$PACK_ROOT/theme/$v.css" ] || { bad "缺 theme/$v.css"; missing=1; }
done
if [ "$missing" -eq 1 ]; then
  [ -n "$CLEANUP" ] && rm -rf "$CLEANUP"
  exit 1
fi
ok "付费 CSS 10 份齐全（V1/V3–V6 × 浅深）"

if [ "$DRY" -eq 1 ]; then
  echo
  echo "dry-run · 将拷贝到："
  for v in "${PAID_VARIANTS[@]}"; do
    dim "$THEME_DIR/$v.css"
  done
  [ -n "$CLEANUP" ] && rm -rf "$CLEANUP"
  exit 0
fi

mkdir -p "$BACKUP_DIR" 2>/dev/null || true
for v in "${PAID_VARIANTS[@]}"; do
  if [ -f "$THEME_DIR/$v.css" ]; then
    cp "$THEME_DIR/$v.css" "$BACKUP_DIR/$v-$STAMP.css" 2>/dev/null \
      && ok "backed up $v.css" \
      || warn "backup $v failed, continuing"
  fi
  if cp "$PACK_ROOT/theme/$v.css" "$THEME_DIR/$v.css" 2>/dev/null; then
    ok "installed $v.css"
  else
    bad "failed to copy $v.css"
  fi
done

# 若在公开仓开发树里跑，顺带把 CSS / paid palette 落回 theme/ 方便 rebuild
REPO_THEME=""
if [ -f "$SCRIPT_DIR/build.py" ]; then
  REPO_THEME="$(cd "$SCRIPT_DIR/.." && pwd)/theme"
elif [ -f "$SCRIPT_DIR/scripts/build.py" ]; then
  REPO_THEME="$SCRIPT_DIR/theme"
fi
if [ -n "$REPO_THEME" ] && [ -d "$REPO_THEME" ]; then
  for v in "${PAID_VARIANTS[@]}"; do
    cp "$PACK_ROOT/theme/$v.css" "$REPO_THEME/$v.css" 2>/dev/null || true
  done
  if [ -f "$PACK_ROOT/scripts/palettes.paid.json" ] && [ -d "$(dirname "$REPO_THEME")/scripts" ]; then
    cp "$PACK_ROOT/scripts/palettes.paid.json" "$(dirname "$REPO_THEME")/scripts/palettes.paid.json" 2>/dev/null \
      && ok "synced palettes.paid.json into repo (gitignored)"
  fi
fi

[ -n "$CLEANUP" ] && rm -rf "$CLEANUP"

echo "────────────────────────────────────────"
echo "  Done. Quit Typora completely (Cmd+Q) and reopen."
echo "  Themes menu · Pack："
echo "    • Hekouwang V1 … V6  (+ Dark)"
echo "  Free V2（若还没装）：clone 公开仓后 ./scripts/install.sh"
echo "  更新 / 答疑：微信 hekouwang · ${HKW_URL_BUY}"
