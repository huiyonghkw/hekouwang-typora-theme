#!/usr/bin/env bash
#
# hekouwang · install to Typora themes folder
#
# Usage:
#   ./scripts/install.sh                          # install theme (recommended)
#   ./scripts/install.sh --use-local-anthropic    # additionally link Anthropic fonts (see below)
#
# ---------------------------------------------------------------------------
# ABOUT --use-local-anthropic
#
# The theme ships with Inter (SIL OFL) and looks complete without this flag.
#
# Anthropic Sans / Serif are PROPRIETARY fonts owned by Anthropic PBC. They
# carry no open license and are NOT included in this repository. This flag only
# copies files that already exist on YOUR machine (from an app you installed)
# into the theme folder, for YOUR personal use.
#
# It is OFF by default and you should leave it off unless you understand this.
# Do not redistribute the copied files. If in doubt, don't use the flag —
# the Inter fallback is what everyone else sees and it looks good.
# ---------------------------------------------------------------------------
#
# Design notes (learned the hard way):
#   - Back up into a SUBDIRECTORY, never the themes root: Typora lists any file
#     containing ".css" in the themes root as a theme — including dotfiles.
#     A backup left there shows up in the Themes menu and users can select it
#     by accident, silently getting an old version.
#   - After the first destructive action, warn instead of aborting. Never leave
#     someone in a half-installed state.
#   - Idempotent: running it twice produces the same result.
#
set -uo pipefail

SLUG="hekouwang"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THEME_DIR="$HOME/Library/Application Support/abnerworks.Typora/themes"
BACKUP_DIR="$THEME_DIR/.$SLUG-backups"
STAMP="$(date +%Y%m%d-%H%M%S)"
USE_LOCAL_ANTHROPIC=0

for arg in "$@"; do
  case "$arg" in
    --use-local-anthropic) USE_LOCAL_ANTHROPIC=1 ;;
    -h|--help) sed -n '2,25p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 1 ;;
  esac
done

ok()   { printf '  ✅ %s\n' "$*"; }
warn() { printf '  ⚠️  %s\n' "$*"; }

echo "hekouwang · install"
echo "────────────────────────────────────────"

# ---- preflight (safe to abort: nothing touched yet) ----
if [ ! -d "$THEME_DIR" ]; then
  echo "Typora themes folder not found: $THEME_DIR" >&2
  echo "Install Typora first, or check the path via Preferences → Open Theme Folder." >&2
  exit 1
fi
if [ ! -f "$SRC_DIR/theme/$SLUG.css" ]; then
  echo "Missing $SRC_DIR/theme/$SLUG.css — run: python3 scripts/build.py" >&2
  exit 1
fi

# ---- backup (from here on: warn, never abort) ----
# 免费默认 V2 + 付费六套（V1–V6）浅/深 = 12 个 CSS
VARIANTS=(
  "$SLUG" "$SLUG-dark"
  "$SLUG-v1" "$SLUG-v1-dark"
  "$SLUG-v3" "$SLUG-v3-dark"
  "$SLUG-v4" "$SLUG-v4-dark"
  "$SLUG-v5" "$SLUG-v5-dark"
  "$SLUG-v6" "$SLUG-v6-dark"
)
# 旧版曾安装 claude 变体，安装时清掉，避免主题菜单残留
LEGACY_REMOVE=(
  "$SLUG-claude"
  "$SLUG-claude-dark"
)
for variant in "${VARIANTS[@]}" "${LEGACY_REMOVE[@]}"; do
  [ -f "$THEME_DIR/$variant.css" ] || continue
  mkdir -p "$BACKUP_DIR" 2>/dev/null
  cp "$THEME_DIR/$variant.css" "$BACKUP_DIR/$variant-$STAMP.css" 2>/dev/null \
    && ok "backed up → .$SLUG-backups/$variant-$STAMP.css" \
    || warn "backup of $variant failed, continuing anyway"
done

# ---- theme css（免费 V2 + 付费 V1/V3–V6 浅深） ----
for variant in "${VARIANTS[@]}"; do
  src="$SRC_DIR/theme/$variant.css"
  [ -f "$src" ] || continue
  if cp "$src" "$THEME_DIR/$variant.css" 2>/dev/null; then
    ok "installed $variant.css"
  else
    warn "failed to copy $variant.css — check folder permissions"
  fi
done

for variant in "${LEGACY_REMOVE[@]}"; do
  if [ -f "$THEME_DIR/$variant.css" ]; then
    rm -f "$THEME_DIR/$variant.css" 2>/dev/null \
      && ok "removed legacy $variant.css from Themes menu" \
      || warn "could not remove legacy $variant.css"
  fi
done

# ---- bundled fonts (Inter, OFL — everyone gets these) ----
mkdir -p "$THEME_DIR/$SLUG/fonts" 2>/dev/null || warn "could not create resource folder"
n=0
for f in "$SRC_DIR/theme/$SLUG/fonts"/*; do
  [ -f "$f" ] || continue
  cp "$f" "$THEME_DIR/$SLUG/fonts/" 2>/dev/null && n=$((n+1))
done
[ "$n" -gt 0 ] && ok "installed $n bundled font files (Inter, SIL OFL)" \
               || warn "no bundled fonts copied — Latin text falls back to system fonts"

# ---- optional: local Anthropic fonts (opt-in, see header) ----
if [ "$USE_LOCAL_ANTHROPIC" -eq 1 ]; then
  FONT_SRC="/Applications/Claude.app/Contents/Resources/fonts"
  mkdir -p "$THEME_DIR/$SLUG/fonts-local" 2>/dev/null
  m=0
  if [ -d "$FONT_SRC" ]; then
    for f in "$FONT_SRC"/AnthropicSans-*.ttf \
             "$FONT_SRC"/AnthropicSerif-*.ttf; do
      [ -f "$f" ] || continue
      cp "$f" "$THEME_DIR/$SLUG/fonts-local/" 2>/dev/null && m=$((m+1))
    done
  fi
  if [ "$m" -gt 0 ]; then
    ok "linked $m local Anthropic font files (personal use only — do not redistribute)"
  else
    warn "Claude desktop app not found — skipping; the Inter fallback is used instead"
  fi
fi

echo "────────────────────────────────────────"
echo "  Done. Quit Typora completely (Cmd+Q) and reopen."
echo "  Themes menu (same reading metrics · different skins):"
echo "    Free · V2 编辑"
echo "      • Hekouwang / Hekouwang Dark"
echo "    Pack · V1–V6（skill 六套视觉 · ¥9.9）"
echo "      • Hekouwang V1 … V6  (+ Dark)"
echo
echo "  Note: switching themes does NOT reload a modified CSS file."
echo "  You must fully quit and relaunch Typora."
