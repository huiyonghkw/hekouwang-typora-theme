# hekouwang · Typora 长文阅读主题

把 Markdown 从“编辑器里的纯文本”，变成一张适合连续阅读与写作的纸。

这是为中文长文设计的 Typora 主题：一篇文章从开头读到结尾，标题、段落、代码、表格和图片应该保持同一种安静而清晰的节奏，而不是每个组件都在抢注意力。

**体验站：** [huiyonghkw.github.io/hekouwang-typora-theme](https://huiyonghkw.github.io/hekouwang-typora-theme/)　·　[English](README.en.md)　·　[详细中文技术说明](README.zh.md)

![Hekouwang 免费版 · 中文长文](docs/screenshot-zh.png)

## 这套主题解决什么

它不追求“像一张海报”，而是把精力放在长期使用时真正影响体验的地方：

- **中文长文读起来松而不散。** 正文 `1rem`、行高 `1.65`、流体行宽 `52em`，避免行太长造成扫读困难，也不会像聊天窗口一样局促。
- **层级清楚，但不用彩色竖条和重装饰。** 标题靠字号、字重与留白建立秩序；代码、引用和表格各有边界，却不会把文章切成一堆卡片。
- **编辑、专注与导出是一套体验。** 编辑区有克制纸感；导出 PDF 会压平浮层，同时保留可打印的标题签名线、代码块与表格节奏。
- **中英混排不将就。** 西文使用随包 Inter，中文使用系统字体；不打包庞大的中文字体，也不碰授权边界。
- **Windows 有独立适配。** Windows 上通过 Typora 的 `body.os-windows` 切换到“微软雅黑 UI / 微软雅黑”与 Cascadia Mono 优先的字栈，并保留 ClearType 渲染。

![Hekouwang 免费版 · 代码](docs/screenshot-fences-zh.png)

## 选择你的版本

| 版本 | Typora 菜单 | 适合谁 |
|---|---|---|
| 免费 · MIT | **Hekouwang** / **Hekouwang Dark** | 想先把 Markdown 阅读体验做好的所有人；暖米白 V2 编辑风格，公开仓与 Gallery 均是此版本。 |
| 付费包 · ¥9.9 | **Hekouwang V1–V6**（各含深色） | 希望和内容生产视觉统一，或对科技、财经、玻璃、紫色 HUD、焰彩有明确偏好的人。 |

免费版已经是完整的长文阅读主题，并不以功能阉割换购买。付费包提供的是六套不同的品牌视觉工艺；它们共享同一套阅读指标。

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

## 视觉版本

| 视觉 | 气质 | 浅色 | 深色 |
|---|---|---|---|
| V1 科技 | 冷调绿紫、文档站感 | [查看](docs/V1.png) | [查看](docs/V1-Dark.png) |
| V2 编辑（免费） | 暖米白纸感、长期阅读 | [查看](docs/screenshot-zh.png) | [查看](docs/screenshot-window.png) |
| V3 财经 | 数据感与克制蓝色 | [查看](docs/V3.png) | [查看](docs/V3-Dark.jpeg) |
| V4 玻璃 | 雾白、轻量、近黑 | [查看](docs/V4.png) | [查看](docs/V4-Dark.png) |
| V5 紫 HUD | 紫 × 青的发布会秩序 | [查看](docs/V5.png) | [查看](docs/V5-Dark.jpeg) |
| V6 焰彩 | 紫 × 橙 × 粉的强调表达 | [查看](docs/V6.png) | [查看](docs/V6-Dark.jpeg) |

## 给想定制的人

主题 CSS 是构建产物，请修改 [`scripts/tokens.json`](scripts/tokens.json) 后重建，而不是手改 `theme/*.css`：

```bash
python3 scripts/build.py
```

构建会拦截常见退化：非根字号使用 `px`、非导出区滥用 `!important`，以及纸感、行宽、PDF 导出结构被破坏。更多维护说明请看 [详细中文技术说明](README.zh.md)。

## 授权与说明

- 免费 V2（`hekouwang.css` / `hekouwang-dark.css`）及脚本使用 [MIT License](LICENSE)；Inter 使用 SIL OFL 1.1。
- 付费主题包仅供个人使用，以包内 `LICENSE-PRO.txt` 为准，请勿二次分发。
- 本仓库不包含、不分发 Anthropic 字体；可选本机字体流程仅供个人使用。

这是独立作品，与 Anthropic PBC 无从属关系；“Claude”与“Anthropic”为 Anthropic PBC 商标。
