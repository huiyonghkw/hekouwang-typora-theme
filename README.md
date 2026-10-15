# hekouwang · Typora 长文阅读主题

把 Markdown 从“编辑器里的纯文本”，变成一张适合连续阅读与写作的纸。

这是为中文长文设计的 Typora 主题：一篇文章从开头读到结尾，标题、段落、代码、表格和图片应该保持同一种安静而清晰的节奏，而不是每个组件都在抢注意力。

**体验站：** [huiyonghkw.github.io/hekouwang-typora-theme](https://huiyonghkw.github.io/hekouwang-typora-theme/)　·　[1.3.0 升级说明](UPGRADE.md)　·　[English](README.en.md)　·　[详细中文技术说明](README.zh.md)

![Hekouwang 免费 V2 · 1.3.0 浅色](docs/previews/v2-light.webp)

*免费 V2 · 1.3.0 浅色，macOS Typora 真机截图。*

## 这套主题解决什么

它不追求“像一张海报”，而是把精力放在长期使用时真正影响体验的地方：

- **中文长文读起来松而不散。** 正文 `1rem`、行高 `1.65`，纸面随窗口伸缩、两侧各留约 `3rem`；段落、标题和列表居中排在「窗口宽度 − 16rem」的阅读列内（介于 `48–96rem`），纸面比阅读列多出 `6rem`，供代码和宽表格使用。
- **层级清楚，但不用彩色竖条和重装饰。** 标题靠字号、字重与留白建立秩序；代码、引用和表格各有边界，却不会把文章切成一堆卡片。
- **编辑、专注与导出是一套体验。** 常规窗口纸面顶部留 `1rem` 壳层；源码模式独立限宽，专注模式照顾图片、任务框与代码。导出 PDF 会压平浮层，纸张、页边距和页眉页脚遵循 Typora 的导出设置。
- **技术内容清楚且不挤正文。** 表格与小字以 `14px` 为基准、代码块 `15px`；句中图片保持行内流动。构建时逐套检查文字与控件的颜色对比度。
- **中英混排不将就。** 西文使用随包 Inter，中文使用系统字体；不打包庞大的中文字体，也不碰授权边界。
- **Windows 有独立适配。** Windows 上通过 Typora 的 `body.os-windows` 切换到“微软雅黑 UI / 微软雅黑”与 Cascadia Mono 优先的字栈，并保留 ClearType 渲染。

![Hekouwang 免费 V2 · 1.3.0 深色](docs/previews/v2-dark.webp)

*免费 V2 · 1.3.0 深色，macOS Typora 真机截图。*

## 选择你的版本

| 版本 | Typora 菜单 | 适合谁 |
|---|---|---|
| 免费 · MIT | **Hekouwang** / **Hekouwang Dark** | 想先把 Markdown 阅读体验做好的所有人；暖米白 V2 编辑风格，公开仓与 Gallery 均是此版本。 |
| 付费包 · ¥9.9 | **Hekouwang V1 / V2 Pro / V3–V6**（各含深色） | 六套独立视觉系统，共 12 个付费 CSS；免费 V2 仍是单独的完整主题。 |

免费版已经是完整的长文阅读主题，并不以功能阉割换购买。付费包提供六套独立的色彩、材质与标题工艺，和免费版共享同一套阅读指标。付费 V2 Pro 是新增的典藏编辑风格，与免费 V2 的 CSS 和菜单项均分开。

购买与付费包安装说明在体验站的 [购买页](https://huiyonghkw.github.io/hekouwang-typora-theme/#buy)。

## 安装：两分钟开始

先在 Typora 中打开「偏好设置 → 外观 → 打开主题文件夹」。也可以用下面的安装器。

### macOS

```bash
git clone https://github.com/huiyonghkw/hekouwang-typora-theme.git
cd hekouwang-typora-theme
./scripts/install.sh
```

### Windows

在 PowerShell 中运行：

```powershell
git clone https://github.com/huiyonghkw/hekouwang-typora-theme.git
cd hekouwang-typora-theme
.\scripts\install-windows.ps1
```

若你的公司策略阻止执行本地 PowerShell 脚本，可只对本次安装运行：`powershell -ExecutionPolicy Bypass -File .\scripts\install-windows.ps1`；它不修改系统执行策略。

Windows 安装器默认写入 `%APPDATA%\Typora\themes`，更新前会把同名 CSS 备份到 `.hekouwang-backups` 子目录；如果你的主题目录不同，可传入：

```powershell
.\scripts\install-windows.ps1 -ThemeDir 'D:\your\Typora\themes'
```

随后**完全退出并重开 Typora**，在「主题」菜单选择 **Hekouwang** 或 **Hekouwang Dark**。切换主题不会重新加载已被修改的 CSS，更新主题后也需要重启。

不使用脚本也可以：复制 `theme/hekouwang.css`、`theme/hekouwang-dark.css` 与 `theme/hekouwang/` 文件夹到 Typora 的主题目录。

### 可选：紧凑阅读宽度

正文默认随窗口伸缩，最宽 `96rem`。如果更喜欢约 40 字宽的中文长文阅读列，在 Typora 主题目录新建 `hekouwang.user.css`，写入：

```css
:root { --hk-reading-measure: 40rem; }
```

深色版对应 `hekouwang-dark.user.css`；要让全部 Hekouwang 配色共用这项设置，可写在 `base.user.css` 中。修改后完全退出并重开 Typora。标题、正文、常规表格和源码模式会一起调整，代码块与宽数据表仍使用较宽的技术画布。

## Windows 兼容承诺

Windows 不是“能打开 CSS 就算支持”。主题在 Windows 10/11 上的验收目标包括：

- 中英混排、粗体、链接、列表和长段落不跳字、不发灰；
- 编辑、源码、专注模式中的正文与界面字体一致；
- 代码块优先使用 Cascadia Mono / Cascadia Code，缺失时安全回退 Consolas；
- 表格、数学公式和 Mermaid 不因字体或窄窗口挤压而失真；
- PDF、HTML、图片导出不出现“外圈底色、中间白柱”或无意义的大留白。

仓库提供浏览器预检，但它只用于早期筛错，不能代替 Typora 真机验收：

```bash
python3 scripts/verify_render.py \
  --css theme/hekouwang.css \
  --windows \
  --fonts 'Hekouwang Sans Fb' \
  --vars bg-color,text-color
```

## 六套付费视觉

1.3.0 付费包包含六套真正独立的视觉系统，每套各有浅色与深色。它们共享免费版的长文排版指标，但纸面、外壳、标题、引用、代码块和表格都有自己的处理。

| 主题 | 视觉方向 | 适用场景 |
|---|---|---|
| **V1 · 石墨青绿** | 冷蓝灰、薄荷青、紫色链接，锐利的技术感 | 技术笔记、产品文档 |
| **V2 Pro · 典藏编辑** | 胡桃墨、古铜、暖纸色与双线装饰；中英文无衬线标题 | 随笔、长篇评论、知识库 |
| **V3 · 财经** | 海军蓝与黄铜，强调表格秩序 | 研究、复盘、数据阅读 |
| **V4 · 玻璃** | 冰蓝、雾面叠片与圆角 | 产品规划、轻量文档 |
| **V5 · HUD** | 紫晶与冷靛紫外壳，青色信号 | 技术方案、演示笔记 |
| **V6 · 焰彩** | 李紫、珊瑚橙与粉色 | 创作手稿、发布稿 |

下面展示 **1.3.0 最新 CSS 在 macOS Typora 中的真机截图**，点击图片可查看原图。免费 V2 仍以 **Hekouwang / Hekouwang Dark** 单独提供。也可以在[体验站对比全部主题](https://huiyonghkw.github.io/hekouwang-typora-theme/#compare-shots)。

### V1 · 石墨青绿

| 浅色 | 深色 |
|---|---|
| ![V1 石墨青绿浅色预览](docs/previews/v1-light.webp) | ![V1 石墨青绿深色预览](docs/previews/v1-dark.webp) |

### V2 Pro · 典藏编辑

| 浅色 | 深色 |
|---|---|
| ![V2 Pro 典藏编辑浅色预览](docs/previews/v2-pro-light.webp) | ![V2 Pro 典藏编辑深色预览](docs/previews/v2-pro-dark.webp) |

### V3 · 财经

| 浅色 | 深色 |
|---|---|
| ![V3 财经浅色预览](docs/previews/v3-light.webp) | ![V3 财经深色预览](docs/previews/v3-dark.webp) |

### V4 · 玻璃

| 浅色 | 深色 |
|---|---|
| ![V4 玻璃浅色预览](docs/previews/v4-light.webp) | ![V4 玻璃深色预览](docs/previews/v4-dark.webp) |

### V5 · HUD

| 浅色 | 深色 |
|---|---|
| ![V5 HUD 浅色预览](docs/previews/v5-light.webp) | ![V5 HUD 深色预览](docs/previews/v5-dark.webp) |

### V6 · 焰彩

| 浅色 | 深色 |
|---|---|
| ![V6 焰彩浅色预览](docs/previews/v6-light.webp) | ![V6 焰彩深色预览](docs/previews/v6-dark.webp) |

## 给想定制的人

主题 CSS 是构建产物，请修改 [`scripts/tokens.json`](scripts/tokens.json) 后重建，而不是手改 `theme/*.css`：

```bash
python3 scripts/build.py
python3 scripts/verify_layout.py --all
python3 scripts/verify_export_pdf.py
```

构建会拦截常见退化：非根字号使用 `px`、非导出区滥用 `!important`，以及纸感、行宽、PDF 导出结构被破坏。它还会自动审计每份生成 CSS 的文字和控件对比度：公开仓的免费浅 / 深两套；本机有付费色板时覆盖 12 套付费 CSS，共 14 套。静态构建检查仍需配合 Typora 中的窄窗、源码、专注和多页 PDF 验收。更多维护说明请看 [详细中文技术说明](README.zh.md)。

## 授权与说明

- 免费 V2（`hekouwang.css` / `hekouwang-dark.css`）及脚本使用 [MIT License](LICENSE)；Inter 使用 SIL OFL 1.1。
- 付费主题包仅供个人使用，以包内 `LICENSE-PRO.txt` 为准，请勿二次分发。
- 本仓库不包含、不分发 Anthropic 字体；可选本机字体流程仅供个人使用。

这是独立作品，与 Anthropic PBC 无从属关系；“Claude”与“Anthropic”为 Anthropic PBC 商标。
