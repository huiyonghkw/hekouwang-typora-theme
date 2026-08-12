# Changelog

## 1.3.1 — 2026-08-12

本地与 ClawHub 1.3.0 对齐，并统一 standalone / monorepo 双布局说明。

- `version` 升至 1.3.1；`homepage` 指向主题开源仓 `hekouwang-typora-theme`
- `summary` / 正文定位改为 **中文长文浅色 + 深色**（不再写「复刻 Claude 桌面」）
- SKILL.md 补 **安装布局** 说明：skill 目录即工作区，或 monorepo 内 `skills/` 软链
- 目录树补 `references/`；与 ClawHub 1.3.0 文案合并

## 1.3.0 — 2026-08-06（ClawHub）

- 产品收窄为 **CJK 长文专用**（Hekouwang + Dark）；移除 Claude 聊天变体叙事
- skill 真源迁入 `skills/hekouwang-typora-theme/` 布局；纸感 chrome 与 README 样张更新

## 1.0.1 — 2026-07-20

发布渠道适配，无功能变更。

- `LICENSE` → `LICENSE.txt`（SkillHub 的上传白名单不收无扩展名文件）
- 补齐 frontmatter：`slug` / `displayName` / `summary` / `license` / `homepage` / `version`
- 说明：SkillHub 渠道包不含 `.png` / `.woff2`（平台白名单限制），
  因此该渠道的西文会降级到系统字体而非 Inter；完整版见 GitHub

## 1.0.0 — 2026-07-20

首个版本。

- **主题**：`hekouwang`（浅色）+ `hekouwang-dark`（深色），复刻 Claude 桌面端阅读体验
- **生成式架构**：CSS 由 `tokens.json` 生成，两个变体同源（`dark` 段只覆盖 `color` / `alpha`，
  派生值从 `border_base` / `shadow_base` 算出）
- **构建断言**：0 个 `!important`、除根字号外 0 处 px 字号，违规当场失败
- **字体三级降级**：Anthropic（仅本机已装）→ Inter（随包，OFL，100 KB）→ 系统字体；
  不打包任何 CJK 字体（参照 App 本身就是 fallback 到系统中文字体）
- **`scripts/sample_colors.py`**：从参照截图采样真实色值，含 `--solve-alpha` 反解叠加色
- **`scripts/verify_render.py`**：渲染验证探针，带 fallback 基准，能分辨"字体真生效"与
  "悄悄用了系统字体"
- **`scripts/install.sh`**：幂等安装，备份进子目录（避免被 Typora 当成伪主题），
  `--use-local-anthropic` 默认关闭

配套开源仓库：https://github.com/huiyonghkw/hekouwang-typora-theme
已提交 theme.typora.io 主题库：PR #523
