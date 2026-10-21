# Changelog

## 1.6.1 — 2026-10-21

主题 2.0.2：修「折叠侧栏后整页发白」。这是主题自己的第 6 个静默坑被自己违反。

- **症状。** 深色主题 + 折叠左侧导航栏 → 整页几乎看不见（浅色纸面配浅色正文，
  对比度约 1.05:1）。侧栏展开时正常，所以只在折叠后出现。
- **根因。** `build.py` 里 `body:not(.pin-outline)` 的两条背景规则用了
  `var(--bg-color)` —— 而 Typora 会把上一个主题的窗口底色缓存进偏好
  `backgroundColor`，再写进 **body 的 inline style**（压过主题 `:root`）。
  于是深色主题拿到浅色纸面。**这正是 `references/typora-spec.md` 第 6 个坑
  写明要避免的写法，主题自己却犯了。**
- **修复。** 两条规则改用实色（`paper_canvas_bg` / `paper_gutter_bg`）；
  「纸感关闭」分支里的 `var(--bg-color)` 一并改掉。14 套产物现在
  **0 处**实际声明用到 `var(--bg-color)`。
- **防复发。** 构建期新增断言：实际声明里出现 `var(--bg-color)` 直接报错并指明
  选择器与后果。
- **文档。** `typora-spec.md` 第 6 个坑补上定位信息 —— 这个坑**症状只在特定
  条件下出现**，只盯着「深色主题」会误以为是深色配色本身有问题。

## 1.6.0 — 2026-10-21

skill 体检修复：真源边界、文档追平、构建门禁。

**P0 · 真源边界（最要紧的一条）**

- `tokens.json` 顶层曾同时存着 `color` / `paper` / `dark` / `type` / `layout`，
  而 palette 会整体覆盖它们 —— 这些段是**改了不生效的死代码**，而构建全绿、
  断言全过，没人发现。现已删除，职责拆成两处：
  - `scripts/tokens.json` → `_presets.work`（阅读指标）+ `font` + `alpha`
  - `scripts/palettes.json` → `color` / `dark` / `paper` / `shape` / `syntax`
- 新增 `build.py:resolve_theme()` —— **全仓库唯一的合并实现**。此前
  `build.main` / `contrast_check._variants` / 单测各写了一份，三份副本各自漂移。
- 新增 `build.py:check_source_layout()`：顶层放回会被覆盖的段 → 构建直接报错，
  把静默失败变成响亮失败。
- 修 `build.py` 的 gutter 断言：此前读 `tokens["paper"]["gutter"]`（死值），
  于是**改对 `palettes.json` 反而构建失败**。现在读实际生效的那一套 theme。
- 文档全面改口径：`tokens.md` 新增「改哪个文件」对照表，
  `SKILL.md` / `workflow.md` 同步修正。

**P1 · 可用性**

- `test_contrast_check.py` 修可独立运行（此前直接跑必崩
  `ModuleNotFoundError: No module named 'scripts'`，等于从没跑过）；
  同时让它构建**真正出货的那份 CSS** —— 以前用裸 tokens 重建，
  测的是一份不存在的 CSS（圆角 6px vs 出货 0，语法色也全不同）。
- `sample_colors.py` 改惰性导入 Pillow：`--solve-alpha` 是纯数学，
  不该被 Pillow 卡住（此前没装 Pillow 就直接退出）。

**P2 · 工程与文档**

- 新增 CI（`.github/workflows/ci.yml`）：构建 + 单测 + 对比度 +
  **产物字节级回归**（把 `workflow.md` 里写了但没人执行的规则变成门禁）。
- `verify_layout.py` 提速 12 倍：`--all` 从 6 分钟降到 31 秒
  （一次 Chrome 启动用多 iframe 测完全部档位）；临时文件从 `theme/` 移到
  系统临时目录，不再往产物目录里留垃圾。
- 文档追平主题 2.0.x：borderless paper（去掉 1px 边框）、墨玉深色、
  宽屏 1.78 行高补偿、10 列表格阈值。
- 新增第 7 个静默坑：**`:has()` 不能嵌套** —— 嵌套写法会被浏览器整条丢弃
  （实测 parsed=false），2.0.1 修过一处这种写法。
- `SKILL.md` 补依赖声明：python3 / google-chrome / pillow（仅读图需要）。
- 新增 `scripts/shoot_previews.sh`：在 Typora 里实拍 `docs/previews/` 的 14 张预览图
  （免费 V2 + 付费六套，各浅/深）。**不是** headless 渲染 —— 预览图是 Typora
  应用窗口截图，含侧边栏与工具栏。脚本用临时副本打开样张，
  避免 Typora 改坏仓库里的 frontmatter（它会把 `theme:` 改名成 `ctheme:`）。
- 预览图全部重拍为 2.0.1 真机效果，README 的版本标注同步。

## 1.5.2 — 2026-10-15

发布维护，内容同 1.5.1。

- ClawHub 的 css / design-tokens / fonts / markdown / theme / typora 标签随版本更新到最新

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
