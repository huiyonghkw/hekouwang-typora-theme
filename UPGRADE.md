# 升级说明 · 1.2.0

发布日期：2026-10-08 · [返回主题首页](README.md) · [查看全部浅色与深色预览](https://huiyonghkw.github.io/hekouwang-typora-theme/#compare-shots)

## 这次更新了什么

- **六套独立付费视觉。** V1 石墨青绿、V2 Pro 典藏编辑、V3 海军蓝财经、V4 冰蓝玻璃、V5 紫晶电青 HUD、V6 李紫焰彩各有自己的浅色与深色配色、标题、引用、代码块和表格细节，共 12 个付费 CSS。免费 V2 仍以 **Hekouwang / Hekouwang Dark** 单独提供。
- **V2 Pro 标题修正。** 中英文标题改用统一的无衬线字体，保留暖纸色、古铜和双线装饰。
- **宽屏阅读与表格。** 正文列随窗口渐进扩展，技术画布为宽代码和表格留空间；普通表格与正文对齐，长内容在窄窗口内滚动，避免截断页面。
- **编辑与导出。** 调整纸面顶部间距、源码与专注模式、图片排版和 PDF 分页；打印时压平屏幕上的浮层，让纸张与页边距遵循 Typora 导出设置。
- **可检查的构建。** 主题构建会检查颜色对比度；仓库还提供宽屏、窄屏、文字间距及 A4/A5 导出预检脚本。主题展示图使用 macOS Typora 真机拍摄，实际外观以各自设备上的 Typora 为准。

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

取得 **1.2.0** 新包后，先更新免费 V2 与随包字体，再安装付费 CSS：

```bash
./scripts/install.sh
./scripts/unlock.sh ~/Downloads/hekouwang-typora-theme-pack-v1.2.0-YYYYMMDD.zip
```

也可以解压付费包，在包内执行 `./unlock.sh`。安装器会检查 zip 完整性和 12 份付费 CSS，并备份同名旧文件。原有 V1、V3–V6 菜单名不变；**Hekouwang V2 Pro / Hekouwang V2 Pro Dark** 是新增的两项，不会覆盖免费 V2。购买、交付与图文安装说明见 [体验站](https://huiyonghkw.github.io/hekouwang-typora-theme/#unlock)。

### 付费包 · Windows

先运行免费版 Windows 安装器，随后解压 1.2.0 付费包，将包内 `theme/` 的 12 个 `hekouwang-v*.css` 复制到 Typora 的主题目录。替换旧文件前先备份；`unlock.sh` 是 macOS 安装脚本，不用于 PowerShell。

**安装后要完全退出 Typora，再重新打开。** 只在菜单里切换主题不会重新加载已修改的 CSS。macOS 使用 `Cmd+Q`；Windows 从菜单退出应用。

## 升级后核对

1. 主题菜单中有免费 2 项；安装付费包后另有 V1、V2 Pro、V3–V6 的浅色与深色共 12 项。
2. 用一篇同时包含长段落、表格、代码块和图片的文档，在普通窗口与宽窗口中检查阅读列和表格。
3. 如需 PDF，在 Typora 导出设置中选择纸张和页边距后重新导出；旧 PDF 不会随主题自动更新。

如仍看到旧颜色，或切换主题后侧栏、窗口底色残留上一套配色，先确认已经完全退出并重开 Typora，再检查主题文件夹内同名 CSS 是否已替换。个人阅读宽度设置若写在 `*.user.css` 或 `base.user.css`，升级后仍会生效。
