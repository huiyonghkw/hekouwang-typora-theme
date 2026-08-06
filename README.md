# hekouwang

**Live site:** [huiyonghkw.github.io/hekouwang-typora-theme](https://huiyonghkw.github.io/hekouwang-typora-theme/) — V1 tech-white shell + interactive paper reading stage (light / dark).

A Typora theme for people who write long-form Markdown in Chinese for hours.

Two themes in the menu:

| Menu | What you get |
|---|---|
| **Hekouwang** | Light · CJK long-form · paper card |
| **Hekouwang Dark** | Dark · same metrics · paper card |

Body `1rem`, leading `1.65`, measure `min(52em, 100% − gutter)`. Colors, type, and spacing live in [`scripts/tokens.json`](scripts/tokens.json); [`scripts/build.py`](scripts/build.py) generates both CSS files.

![English acceptance sample](docs/screenshot.png)

*English sample (`demo/acceptance-sample.md`) — body, metrics, mixed Latin + CJK.*

![Chinese acceptance sample](docs/screenshot-zh.png)

*Chinese sample (`demo/验收样张.md`) — same reading metrics, CJK-first copy.*

![Code fences](docs/screenshot-fences.png)

*Consecutive fences (Python / shell / CSS) — syntax colors stay quiet; blocks breathe.*

*[中文说明](README.zh.md)*

---

## Design principles

- **Built for CJK long-form, not chat bubbles.** Chinese paragraphs need leading `≥1.6` and a measure near ~40–50 characters — not conversation-pane density.
- **No high-saturation accents.** Inline code uses warm brown (`#8a5a3c`) on a soft wash, so a line with many `` `code` `` spans still reads as text.
- **Hierarchy from size, weight, and spacing — not color bars.** No left accent stripes, no heavy chrome borders.
- **Borders are ink at low alpha**, never flat gray on a warm page.
- **Paper card on `#write`** (light and dark): warm radial, large radius, outer shadow; chrome (sidebar / gutter / titlebar) sits one step behind the paper.
- **Larger type, slightly tighter tracking.** CJK titles stay milder than Latin display tracking.

### Reading metrics

| Token | Value | Why |
|---|---|---|
| `body_size` | `1rem` | Comfortable for multi-hour writing |
| `body_lh` | `1.65` | CJK density needs more leading than Latin UI copy |
| `measure` | `52em` | Fluid: `min(52em, calc(100% − gutter))` |
| `para_gap` | `0.78rem` | Compact without stacking into a wall |

---

## Typography: how CJK and Latin mix

Anthropic Sans has **581 glyphs and zero CJK characters** — not even ideographic punctuation. Chinese always falls back to the system face (PingFang SC on macOS). The theme pairs a Latin face with that system CJK face and **does not ship a CJK font**.

| Tier | Font | Shipped? |
|---|---|---|
| 1 | Anthropic Sans (if already on your machine) | No — proprietary |
| 2 | **Inter** variable, Latin subset, ~100 KB | Yes — SIL OFL |
| 3 | System UI font | n/a |

Most people see tier 2; screenshots are checked against that.

## Install

```bash
git clone https://github.com/huiyonghkw/hekouwang-typora-theme.git
cd hekouwang-typora-theme
./scripts/install.sh
```

Or copy `theme/hekouwang.css`, `theme/hekouwang-dark.css`, and the `theme/hekouwang/` folder into Typora’s themes directory (Preferences → Open Theme Folder).

Then **quit Typora completely (Cmd+Q) and relaunch** — switching themes does not reload a modified CSS file. Choose **Hekouwang** or **Hekouwang Dark**.

## Customizing

Do not edit the CSS; it is generated. Edit `scripts/tokens.json` and rebuild:

```bash
python3 scripts/build.py
# → theme/hekouwang.css
# → theme/hekouwang-dark.css
./scripts/install.sh
```

The `dark` block overrides only `color` / `alpha`. Derived borders and washes come from `border_base` / `shadow_base`.

Build checks:

- **zero `!important`**
- **zero `px` font sizes except the root**
- paper metrics present on both light and dark work CSS

## How this differs from the gallery “Claude Theme”

There is an [existing Claude Theme](https://theme.typora.io/theme/Claude-Theme/) with a similar inspiration. This is an independent implementation — no CSS was copied.

| | Gallery Claude Theme | hekouwang |
|---|---|---|
| Authoring | ~3,158 hand-written lines | generated from tokens |
| `!important` | 397 | **0** (build-enforced) |
| Font sizes | some `px` | all `rem` except root |
| Bundled fonts | ~24 MB (incl. full Noto Serif SC) | **~100 KB** (Inter Latin) |
| Anthropic fonts | redistributed | **not shipped**; `local()` + Inter |
| Body CJK | Noto Serif SC | system sans-serif |
| Latin weights | single 400 → synthetic bold | variable **300–800** + `opsz` |
| UI coverage | mainly the editor | sidebar, tree, outline, search, focus |

**CJK.** Matching a desktop app that has no CJK glyphs means *not* bundling a serif CJK face.

**Backgrounds.** Cream `#faf9f5` is often the *window* color; the editor pane samples closer to `#fdfdfc`, with a slightly deeper chrome behind the paper card.

## Fonts and licensing

This repository **does not contain or redistribute any Anthropic font.** Anthropic Sans / Serif are proprietary.

`scripts/install.sh --use-local-anthropic` can copy those fonts from an installed Claude desktop app into *your* theme folder for personal use. **Off by default.** Do not redistribute copies. Inter is the intended default.

## Status

- Light + dark: complete
- Dark colors: **sampled**, not inverted from light
- Designed and tested on **macOS** (Windows / Linux untested; no Windows unibody styles yet)

## Theme engineering skill

This repo ships the maintenance skill **in-tree** under [`skills/`](skills/) (not a separate skill repo). Clone or open the project and agents that load project skills can use it directly — token-driven CSS, screenshot color sampling, font-on-screen checks.

**Canonical entry:**

- [`skills/hekouwang-typora-theme/SKILL.md`](skills/hekouwang-typora-theme/SKILL.md)

`.claude/skills/` and `.cursor/skills/` are symlinks to that folder so Claude Code / Cursor discover it automatically. No extra skill install step after clone.

## License

MIT for CSS and scripts — [LICENSE](LICENSE). Inter is SIL OFL 1.1.

Independent work inspired by a calm desktop reading surface. Not affiliated with Anthropic PBC. “Claude” and “Anthropic” are trademarks of Anthropic PBC.
