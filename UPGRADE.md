# 升级说明 · 1.3.1

发布日期：2026-10-15 · [返回主题首页](README.md) · [查看全部浅色与深色预览](https://huiyonghkw.github.io/hekouwang-typora-theme/#compare-shots)

## 1.3.1 修复

- **代码块与正文对齐。** 收起侧边栏、窗口变宽后，代码块不再比正文两侧各宽出一截，宽度和左右边缘与正文一致；宽表格和图表仍可比正文宽。
- **PDF 底色与纸面一致。** 浅色主题导出时整页改用纸面色，不再用窗口外圈的底色（如 V1 浅蓝、V6 浅粉）；纸面为纯白的主题，代码块与表格用略深的纸面阴影色区分。

## 1.3.0 更新了什么

- **宽屏铺满窗口。** 纸面随窗口伸缩，两侧只留约 3rem 窗口底色；正文阅读列为「窗口宽度 − 16rem」，介于 48rem 与 96rem 之间，正文两侧不再出现大片空纸。
- **表格更稳。** 七列及以上的表格先与正文对齐，内容放不下才向两侧展开，再宽才在表格内部横向滚动；多列数值表的单元格留白收窄，常见的十几列对照表在宽屏下可以完整显示。
- **更精致的背景层。** 免费版与六套付费主题的纸面、外框和侧栏改用 Tailwind 色阶：纸面保持白色或极浅中性色，主题色只染在外框与侧栏；纸面改为细边加轻阴影；深色版正文用浅灰而非纯白，减少刺眼。
- **标题装饰线随标题伸缩。** V1、V5、V6 的标题下划线，以及 PDF 导出时二级标题的签名线，长度与标题文字一致。
- **V3 纸面修正。** 从其他主题切换到 V3 时，纸面不再沿用上一个主题的窗口底色（深色版曾出现浅色纸面配浅色文字）。

## 从旧版升级

升级前在 Typora 中打开「偏好设置 → 外观 → 打开主题文件夹」，确认主题目录。下面的安装脚本会将同名旧 CSS 备份到主题目录内的 `.hekouwang-backups/`。

### 免费 V2 · macOS

在已克隆的仓库中更新文件，然后运行：

```bash
git pull
./scripts/install.sh
```

首次安装可参照 [README 的完整步骤](README.md#安装两分钟开始)。免费主题菜单仍为 **Hekouwang** 与 **Hekouwang Dark**。

### 免费 V2 · Windows

在已克隆的仓库中更新文件，然后在 PowerShell 运行：

```powershell
git pull
.\scripts\install-windows.ps1
```

默认安装到 `%APPDATA%\Typora\themes`。自定义路径可传 `-ThemeDir`，详见 [中文技术说明](README.zh.md#windows-安装与阅读兼容)。

### 付费包 · macOS

取得 **1.3.1** 新包后，先更新免费 V2 与随包字体，再安装付费 CSS：

```bash
./scripts/install.sh
./scripts/unlock.sh ~/Downloads/hekouwang-typora-theme-pack-v1.3.1-YYYYMMDD.zip
```

也可以解压付费包，在包内执行 `./unlock.sh`。安装器会检查 zip 完整性和 12 份付费 CSS，并备份同名旧文件。菜单名与 1.2.0 相同。购买、交付与图文安装说明见 [体验站](https://huiyonghkw.github.io/hekouwang-typora-theme/#unlock)。

### 付费包 · Windows

先运行免费版 Windows 安装器，随后解压 1.3.1 付费包，将包内 `theme/` 的 12 个 `hekouwang-v*.css` 复制到 Typora 的主题目录。替换旧文件前先备份；`unlock.sh` 是 macOS 安装脚本，不用于 PowerShell。

**安装后要完全退出 Typora，再重新打开。** 只在菜单里切换主题不会重新加载已修改的 CSS。macOS 使用 `Cmd+Q`；Windows 从菜单退出应用。

## 升级后核对

1. 主题菜单中有免费 2 项；安装付费包后另有 V1、V2 Pro、V3–V6 的浅色与深色共 12 项。
2. 在宽窗口中打开一篇含长段落、表格和代码块的文档：纸面应接近铺满窗口，正文两侧没有大片空白，表格、代码块与正文左右对齐。
3. 如需 PDF，在 Typora 导出设置中选择纸张和页边距后重新导出；旧 PDF 不会随主题自动更新。

## 个人阅读宽度

1.3.0 默认正文更宽。如果更喜欢窄一些的阅读列，在 Typora 主题目录新建 `hekouwang.user.css`（付费主题用同名 `.user.css`，或 `base.user.css` 统一覆盖），写入：

```css
:root { --hk-reading-measure: 60rem; }
```

纸面会跟着正文一起收窄。已有的 `*.user.css` 或 `base.user.css` 设置升级后仍会生效。
