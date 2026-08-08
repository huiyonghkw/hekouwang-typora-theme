# Typora 主题规范与选择器地图

官方文档在本地：`/Applications/Typora.app/Contents/Resources/TypeMark/Docs/Custom Themes.md`
基础样式：同级 `style/base.css`（压缩成一行，`wc -l` 显示 0，别以为是空文件）
线上：https://theme.typora.io/doc/Write-Custom-Theme/

## 硬规范

1. **文件名不许大写、不许空格**，用 `-` 连接。`my-theme.css` → 菜单显示 "My Theme"
   （连字符转空格 + 每词首字母大写，Typora 自动做）。
2. **除 `html` 的根字号外，一律用 `rem`**。用 px 会让 Typora 偏好面板的字号调节失效。
3. **优先覆盖官方 CSS 变量**，而不是硬写规则。
4. **少覆盖 `#write` 默认样式**。例如给它加 `white-space: pre-wrap` 会导致 Tab 键插不进 `\t`。
5. 只用 Webkit/Chromium 支持的属性。
6. 深色没有任何强制约定：要么出两个 css 文件（主流做法），要么单文件内用
   `@media (prefers-color-scheme: dark)`。

## 官方 CSS 变量（就这些）

```
--bg-color --text-color --md-char-color --meta-content-color
--primary-color --primary-btn-border-color --primary-btn-text-color
--window-border --active-file-bg-color --active-file-text-color --active-file-border-color
--side-bar-bg-color --item-hover-bg-color --item-hover-text-color --monospace
--select-text-bg-color --search-select-bg-color --control-text-color --blur-text-color
```

数量很少，所以大部分样式还是要写选择器 —— 但**靠 `#write` 的特异性就够，不需要
`!important`**（base.css 自己都不用）。对照：gallery 上某同类主题用了 397 个。

## 选择器地图

**块级**：`p` / `.md-line` / `h1`~`h6` / `blockquote` / `ul li`、`ol li` /
`ul.task-list li.task-list-item` / `.md-toc` / `pre.md-fences`（CodeMirror 初始化前是
`pre.md-fences.mock-cm`）/ `pre.md-meta-block`（YAML front matter）/ `.md-def-footnote` /
`table thead tbody th tr td` / `hr` / `.md-alert`（GitHub callout）

**行内**：`strong em code a img mark del sub sup u`。语法符号在 `.md-meta`（默认隐藏），
内容在 `.md-content`，光标进入时外层加 `.md-expand`。

**代码高亮**：CodeMirror 主题类是 **`.cm-s-inner`**（移植其他 CodeMirror 主题时把
`.cm-s-xxx` 全局替换成它）。常用 token：`.cm-keyword .cm-string .cm-comment .cm-number
.cm-def .cm-variable .cm-property .cm-operator .cm-tag .cm-atom .cm-builtin`。
同时要给 `pre.md-fences` 本身设 font/color/background（CodeMirror 渲染前的裸态）。

⚠️ 自建预览页测语法色时，`<pre>` 必须同时有 `md-fences` 和 **`cm-s-inner`** 两个类，
否则色值不生效 —— 那是预览的问题，不是主题的问题（我为此差点去改一个不存在的 bug）。

**源码模式**：另一套类 `.cm-s-typora-default`（容器 `#typora-source`），`cm-s-inner` 管不到。

**Focus mode**：变量 `--blur-text-color` 最省事；细粒度用 `body.on-focus-mode`、`.md-focus`、
`.md-focus-container`、`.md-end-block`。
⚠️ **typewriter mode 没有专属 class**，它只是滚动行为，别编一个。

**界面**：`#typora-sidebar` `#file-library` `.file-node-content` `.file-list-item`
`#outline-content .outline-item` `#md-searchpanel` `.md-search-hit` `.modal-content`
`.context-menu` `.btn` `::-webkit-scrollbar`

**导出 / PDF**：整页与画布（gutter `#ebe8df`）同色；`#write` 禁纯白底。导出精装：H2 签名线、
抬升 fence（`#fffef8`）、圆角表、渐变 HR；`!important` 仅导出段。整表勿整块 `break-inside`
（改 `tr`）。

## 五个静默失败的坑

全部踩过，共同点是**不报错、页面照常渲染**：

1. **备份文件变成伪主题**。Typora 把根目录下任何文件名含 `.css` 的都列进主题菜单，
   **连 `.` 开头的隐藏文件也算**。`.theme.css.bak-20260720` 会出现在菜单里，
   用户误选后看到旧版且毫无提示 —— 而且这种错误**会自我掩护**：你以为主题做得差，
   而不是"我选错主题了"。→ 备份进子目录。
2. **切换主题不重载被修改的 CSS**。必须 `Cmd+Q` 完全退出重开。
3. **`format("truetype-variations")` 被老 Chromium 丢弃**，整条 `src` 作废 → 静默 fallback。
4. **改名要全链路**：`@font-face` 族名、字体栈族名、字体源目录名、install 的 SLUG。
   任一处没跟上就静默失败，而 ttf 兜底还会掩盖问题（只装上 3/8 个文件也照常显示）。
5. **px 字号**让偏好面板的字号调节失效，但页面看起来完全正常。

## 提交到 theme.typora.io

仓库是 `typora/theme.typora.io`，默认分支 **`gh-pages`**（Jekyll 站）。流程：

1. Fork
2. `_posts/YYYY-MM-DD-slug.md`，YAML 字段：
   `layout: post` / `title` / `author` / `preview`（thumbnails 下的文件名）/ `homepage` /
   `download`（GitHub zip 链接）/ `description` / `tags`
3. `thumbnails/slug.png`，**250×200 或 500×400**
4. 开 PR

主题本体**不放进 gallery 仓**，托管在自己的仓库，`homepage` / `download` 指过去。

官方只有两条 Notes：
- 未覆盖某平台样式的必须声明（原句范例：`Designed and tested on macOS. Not fully tested,
  but should work for Windows/Linux. But this theme does not include styles for the Windows
  "unibody" style.`）
- **基于已有主题只改字体/padding 的，必须放 `_posts/fork/` 并标 `category: fork`、链接原主题**
