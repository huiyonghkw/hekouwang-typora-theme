# Changelog

## 1.5.1 — 2026-10-15

同步主题 1.3.1（代码块对齐、PDF 底色）。

- 代码块并入阅读列，与正文同宽同左右边缘；导出时代码块与分隔线改 `margin: … auto` 居中
- 导出 PDF 整页改用纸面 mid 色（原为 gutter）；highlight 与 mid 同为白时，导出代码块和表格底退到 shade
- `verify_layout.py`：代码块断言改为与正文对齐；构建自检改查 html 画布为纸面色

## 1.5.0 — 2026-10-15

同步主题 1.3.0（宽屏版面、Tailwind 背景层、标题装饰线）。

- 版面：纸面随窗口铺满、两侧各留约 `3rem`；阅读列 `clamp(48rem, calc(100vw - 16rem), 96rem)`；新增 `layout.wide_canvas_extra`（纸面比阅读列多出的技术画布，默认 `6rem`）
- 表格：七列起的宽表先与阅读列对齐，内容放不下才向画布展开再局部滚动；七列起单元格左右留白收窄到 `0.55rem`
- 配色：14 套背景层改用 Tailwind v3 色阶（纸面 white / 50，外框与侧栏 100–200，深色纸面 900、外框 950）；纸面改 1px 细边 + 轻阴影，去掉内阴影；深色正文用 200 档而非纯白
- 标题：V1 / V5 / V6 标题装饰线与导出 H2 签名线随标题文字长短伸缩
- `verify_layout.py` 新增七列表、17 列数值表、宽表对齐与 20 列滚动样例
- 踩坑：Typora 启动时把上一个主题缓存的窗口底色（偏好 `backgroundColor`）写进 `--bg-color`，纸面不能用 `var(--bg-color)`，必须写实色

## 1.4.1 — 2026-10-12

skill-doctor 体检修复。

- SKILL.md 补说明：从 ClawHub / SkillHub 安装需先 clone 开源仓库，命令在仓库根目录执行
- 目录说明补 `verify_export_pdf.py`
- skill-card 版本号与许可证说明对齐 frontmatter

## 1.4.0 — 2026-10-12

同步主题 1.2.0（主题画廊与升级指南）。

- 付费清单改为 V1 / V2 Pro / V3–V6（各含浅/深，共 12 个 CSS），V2 Pro 与免费 V2 分立
- 新增 `verify_layout.py`（多窗口宽度、窄屏、表格、源码模式几何预检）与 `verify_export_pdf.py`（A4/A5、长代码、长表）
- 构建内置 `contrast_check.py`，对文字、链接、代码、按钮、任务框做最小对比度校正与审计
- 排版：响应式正文阅读列 `--hk-reading-measure`、宽屏技术画布、小字/表格/代码块字号 token
- `!important` 规则收窄为「编辑区零」，导出段可用于覆盖 Typora 打印基础样式
- 截图验收改为 `demo/主题展示样张.md` → `docs/previews/`

## 1.3.3 — 2026-08-12

ClawHub 分类：`creative`；误建 slug `hekouwang-typora-theme` 已合并进本 skill。

## 1.3.2 — 2026-08-12

P2：商业化可发现性 + SEO。

- summary 补英文关键词（Typora theme / CJK long-form）
- README.zh 补 30 秒验收命令块

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
