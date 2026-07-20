#!/usr/bin/env python3
"""
hekouwang · Typora 主题构建器
tokens.json（单一真相源） → theme/hekouwang.css

设计约束（来自 Typora 官方 Write-Custom-Theme 规范）：
  1. 只有 html 用 px，其余一律 rem —— 否则偏好面板的字号调节失效
  2. 优先覆盖官方 CSS 变量，而不是硬写规则
  3. 尽量不用 !important（base.css 自己都不用，特异性够就行）
  4. 少覆盖 #write 默认样式（例如 white-space 会破坏 Tab 键）
  5. 代码块 CodeMirror 主题类是 .cm-s-inner；源码模式是 .cm-s-typora-default
"""
import json
import os
from string import Template

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def flatten(tokens):
    """tokens.json → 扁平变量表，供模板取用。跳过 _ 开头的注释键。"""
    out = {}
    for group, val in tokens.items():
        if group.startswith("_"):
            continue
        for k, v in val.items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict):          # 标题这类嵌套一层
                for kk, vv in v.items():
                    out[f"{group}_{k}_{kk}"] = vv
            else:
                out[f"{group}_{k}"] = v
    return out


def hexa(hex_color, alpha):
    """#1f1e1d + 0.14 → rgba(31,30,29,0.14)。边框统一走墨色透明叠加，避免灰死色。"""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


CSS = Template(r"""
/* ==========================================================================
   hekouwang — a Typora theme
   复刻 Claude 桌面端的阅读体验：骨白底、Anthropic Sans 西文 + 系统中文混排。

   本文件由 scripts/build.py 从 scripts/tokens.json 生成，请勿手改。
   改视觉 → 改 tokens.json → 重跑 build.py。
   ========================================================================== */

/* --------------------------------------------------------------------------
   字体
   实测：Anthropic Sans 共 581 字符、CJK 汉字 0 个，连「，」「。」都没有。
   所以中文必然 fallback 到系统字体 —— 桌面端本身就是这个机制，不是妥协。
   栈序铁律：西文族必须排在中文族之前，否则中文字体会把西文一起吃掉。

   local() 优先命中系统已装字体；未装则读主题目录内的文件；
   两者都没有时，优雅降级到 -apple-system。
   -------------------------------------------------------------------------- */
/* ⚠️ 别用 format("truetype-variations")：那是早期实验语法，
   Typora 内嵌的 Chromium 不认识它，整条 src 会被丢弃 → 悄悄 fallback 到 SF Pro。
   在新版 Chrome 里测是通过的，所以这个坑只有在 Typora 里才暴露。
   正解：woff2 优先（体积小、可变字体支持面最广），ttf 作兜底，
   format 一律用标准值，让不认识的浏览器跳到下一个 src 而不是整条作废。 */
@font-face {
  font-family: "Hekouwang Sans";
  src: local("Anthropic Sans Text"),
       url("./hekouwang/fonts-local/AnthropicSans-Romans-Variable-25x258.woff2") format("woff2"),
       url("./hekouwang/fonts-local/AnthropicSans-Romans-Variable-25x258.ttf") format("truetype");
  font-weight: 300 800;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Hekouwang Sans";
  src: local("Anthropic Sans Text Italic"),
       url("./hekouwang/fonts-local/AnthropicSans-Italics-Variable-25x258.woff2") format("woff2"),
       url("./hekouwang/fonts-local/AnthropicSans-Italics-Variable-25x258.ttf") format("truetype");
  font-weight: 300 800;
  font-style: italic;
  font-display: swap;
}
@font-face {
  font-family: "Hekouwang Serif";
  src: local("Anthropic Serif Text"),
       url("./hekouwang/fonts-local/AnthropicSerif-Romans-Variable-25x258.woff2") format("woff2"),
       url("./hekouwang/fonts-local/AnthropicSerif-Romans-Variable-25x258.ttf") format("truetype");
  font-weight: 300 800;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Hekouwang Mono";
  src: local("Anthropic Mono"),
       url("./hekouwang/fonts-local/AnthropicMonoVariable.woff2") format("woff2"),
       url("./hekouwang/fonts-local/AnthropicMonoVariable.ttf") format("truetype");
  font-weight: 300 800;
  font-style: normal;
  font-display: swap;
}

/* —— 兜底字体：Inter（SIL OFL，随包分发）——
   没有 Anthropic 字体的人（也就是绝大多数下载者）会落到这一层。
   Inter 与 Anthropic Sans 同属几何人文 sans，x-height 接近，
   与苹方混排的基线关系也接近，是最省事的替身。
   只打包 latin 子集：中文由系统字体承担，不需要 CJK。 */
@font-face {
  font-family: "Hekouwang Sans Fb";
  src: url("./hekouwang/fonts/inter-latin-wght-normal.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Hekouwang Sans Fb";
  src: url("./hekouwang/fonts/inter-latin-wght-italic.woff2") format("woff2");
  font-weight: 100 900;
  font-style: italic;
  font-display: swap;
}

/* 字体诊断条：主题装好后，在 Typora 里新建一篇 md 粘贴
   <p class="bone-probe">Handgloves Fupanwang 2026</p>
   若它与正文西文长得一样 → 字体已生效；若明显不同 → 没加载上。 */
.hk-probe { font-family: "Hekouwang Sans", sans-serif; }
.hk-probe-fallback { font-family: -apple-system, sans-serif; }

/* --------------------------------------------------------------------------
   Tokens
   -------------------------------------------------------------------------- */
:root {
  /* —— Typora 官方变量（优先覆盖这些，而不是硬写规则）—— */
  --bg-color:                 ${color_bg};
  --text-color:               ${color_text};
  --side-bar-bg-color:        ${color_sidebar_bg};
  --item-hover-bg-color:      ${color_hover};
  --item-hover-text-color:    ${color_text};
  --active-file-bg-color:     ${color_hover};
  --active-file-text-color:   ${color_text};
  --active-file-border-color: ${color_accent};
  --primary-color:            ${color_accent};
  --primary-btn-border-color: ${color_accent};
  --primary-btn-text-color:   #ffffff;
  --window-border:            ${line};
  --md-char-color:            ${color_text_faint};
  --meta-content-color:       ${color_text_muted};
  --control-text-color:       ${color_text_soft};
  --control-text-hover-color: ${color_text};
  --select-text-bg-color:     ${accent_wash};
  --search-select-bg-color:   ${accent_soft};
  --blur-text-color:          ${color_text_faint};
  --monospace:                ${font_mono_stack};
  --rawblock-edit-panel-bd:   ${line};

  /* —— Bone 私有 —— */
  --hk-raised:    ${color_bg_raised};
  --hk-sunken:    ${color_sunken};
  --hk-soft:      ${color_text_soft};
  --hk-muted:     ${color_text_muted};
  --hk-faint:     ${color_text_faint};
  --hk-accent:    ${color_accent};
  --hk-link:      ${color_link};
  --hk-code:      ${color_code_text};
  --hk-hairline:  ${hairline};
  --hk-line:      ${line};
  --hk-divider:   ${divider};
  --hk-r-sm:      ${shape_radius_sm};
  --hk-r:         ${shape_radius};
  --hk-r-lg:      ${shape_radius_lg};
  --hk-pill:      ${shape_radius_pill};
  --hk-sans:      ${font_sans_stack};
  --hk-serif:     ${font_serif_stack};
}

/* --------------------------------------------------------------------------
   骨架
   -------------------------------------------------------------------------- */
html {
  font-size: ${type_root_px};          /* 规范：唯一允许用 px 的地方 */
  background-color: var(--bg-color);
}

html, body {
  font-family: var(--hk-sans);
  color: var(--text-color);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-optical-sizing: auto;           /* 吃上 Anthropic Sans 的 opsz 16→48 轴 */
  text-rendering: optimizeLegibility;
}

body {
  font-variant-numeric: proportional-nums;
  font-kerning: normal;
}

#write {
  max-width: ${type_measure};
  margin: 0 auto;
  padding: ${layout_write_pad_top} ${layout_write_pad_x} ${layout_write_pad_bottom};
  font-size: ${type_body_size};
  line-height: ${type_body_lh};
  color: var(--text-color);
  caret-color: var(--hk-accent);
}

#write > p {
  margin-top: 0;
  margin-bottom: ${type_para_gap};
}

#write > p:last-child { margin-bottom: 0; }

/* --------------------------------------------------------------------------
   标题
   大字号收紧字距（负 letter-spacing）是高级感的主要来源，
   字号越大收得越多，小字号回到 0。
   -------------------------------------------------------------------------- */
#write h1, #write h2, #write h3,
#write h4, #write h5, #write h6 {
  font-family: var(--hk-sans);
  color: var(--text-color);
  break-after: avoid;
}

#write h1 { font-size: ${type_h1_size}; line-height: ${type_h1_lh}; font-weight: ${type_h1_weight}; letter-spacing: ${type_h1_ls}; margin: ${type_h1_mt} 0 ${type_h1_mb}; }
#write h2 { font-size: ${type_h2_size}; line-height: ${type_h2_lh}; font-weight: ${type_h2_weight}; letter-spacing: ${type_h2_ls}; margin: ${type_h2_mt} 0 ${type_h2_mb}; }
#write h3 { font-size: ${type_h3_size}; line-height: ${type_h3_lh}; font-weight: ${type_h3_weight}; letter-spacing: ${type_h3_ls}; margin: ${type_h3_mt} 0 ${type_h3_mb}; }
#write h4 { font-size: ${type_h4_size}; line-height: ${type_h4_lh}; font-weight: ${type_h4_weight}; letter-spacing: ${type_h4_ls}; margin: ${type_h4_mt} 0 ${type_h4_mb}; }
#write h5 { font-size: ${type_h5_size}; line-height: ${type_h5_lh}; font-weight: ${type_h5_weight}; margin: ${type_h5_mt} 0 ${type_h5_mb}; }
#write h6 { font-size: ${type_h6_size}; line-height: ${type_h6_lh}; font-weight: ${type_h6_weight}; margin: ${type_h6_mt} 0 ${type_h6_mb}; color: var(--hk-soft); }

#write h1:first-child, #write h2:first-child,
#write h3:first-child, #write h4:first-child { margin-top: 0; }

/* h1 下方一条极细分隔，给全文定一个基准线 */
#write h1 {
  padding-bottom: 0.32rem;
  border-bottom: 1px solid var(--hk-hairline);
}

/* --------------------------------------------------------------------------
   行内
   -------------------------------------------------------------------------- */
#write strong { font-weight: 650; color: var(--text-color); }
#write em     { font-style: italic; }
#write del    { color: var(--hk-muted); }

#write a {
  color: var(--hk-link);
  text-decoration: underline;
  text-decoration-color: ${link_underline};
  text-underline-offset: 0.18em;
  text-decoration-thickness: 1px;
  transition: text-decoration-color .15s ease, color .15s ease;
}
#write a:hover {
  color: var(--hk-accent);
  text-decoration-color: var(--hk-accent);
}

#write mark {
  background: ${accent_wash};
  color: inherit;
  border-radius: 3px;
  padding: 0.05em 0.2em;
}

/* 行内代码：桌面端那种极轻的浅底 + 暖红字，不抢正文 */
#write code,
#write tt {
  font-family: var(--monospace);
  font-size: ${type_code_size};
  color: var(--hk-code);
  background: ${inline_code_bg};
  border: none;
  border-radius: var(--hk-r-sm);
  padding: 0.14em 0.4em;
  word-break: break-word;
}

#write h1 code, #write h2 code, #write h3 code,
#write h4 code, #write h5 code, #write h6 code {
  font-size: 0.88em;
}

/* --------------------------------------------------------------------------
   引用
   刻意不用品牌色竖条 —— 桌面端的克制感来自低对比的墨色细线 + 微沉底。
   -------------------------------------------------------------------------- */
#write blockquote {
  margin: ${type_block_gap} 0;
  padding: 0.1rem 0 0.1rem 1rem;
  border-left: 2px solid var(--hk-divider);
  color: var(--hk-soft);
}
#write blockquote blockquote { margin: 0.5rem 0; }

/* --------------------------------------------------------------------------
   列表
   -------------------------------------------------------------------------- */
#write ul, #write ol { margin: 0 0 ${type_para_gap}; padding-left: 1.45rem; }
#write li { margin: ${type_list_gap} 0; }
#write li > p { margin: ${type_list_gap} 0; }
#write ul li::marker { color: var(--hk-faint); }
#write ol li::marker { color: var(--hk-muted); font-variant-numeric: tabular-nums; }

#write ul.task-list { padding-left: 1.35rem; }
#write ul.task-list li.task-list-item { list-style: none; }
#write .md-task-list-item > input {
  -webkit-appearance: none;
  appearance: none;
  width: 1.05em;
  height: 1.05em;
  margin-left: -1.45em;
  margin-top: 0.28em;
  border: 1.5px solid var(--hk-divider);
  border-radius: 4px;
  background: var(--hk-raised);
  transition: background .15s ease, border-color .15s ease;
}
#write .md-task-list-item > input:checked {
  background: var(--hk-accent);
  border-color: var(--hk-accent);
}
#write .md-task-list-item > input:checked::after {
  content: "";
  display: block;
  width: 0.28em;
  height: 0.55em;
  margin: 0.08em 0 0 0.32em;
  border: solid #fff;
  border-width: 0 1.8px 1.8px 0;
  transform: rotate(45deg);
}
#write .task-list-item.md-task-list-item > p { color: inherit; }

/* --------------------------------------------------------------------------
   代码块
   -------------------------------------------------------------------------- */
#write pre.md-fences {
  font-family: var(--monospace);
  font-size: ${type_fences_size};
  line-height: ${type_fences_lh};
  background: var(--hk-raised);
  border: 1px solid var(--hk-line);
  border-radius: var(--hk-r);
  padding: 0.75rem 0.95rem;
  margin: ${type_block_gap} 0;
  color: var(--text-color);
  box-shadow: 0 1px 2px ${shadow_soft};
}
#write pre.md-fences.md-focus { border-color: ${accent_border}; }

.md-fences .code-tooltip {
  background: var(--hk-raised);
  border: 1px solid var(--hk-line);
  border-radius: var(--hk-r-sm);
  box-shadow: 0 6px 18px ${shadow_soft};
  color: var(--hk-muted);
}

/* 语法高亮：低饱和语义色，跟骨白底同一个色温 */
.cm-s-inner .CodeMirror-gutters   { background: transparent; border: none; }
.cm-s-inner .CodeMirror-linenumber{ color: var(--hk-faint); }
.cm-s-inner .CodeMirror-cursor    { border-left: 1.5px solid var(--hk-accent); }
.cm-s-inner div.CodeMirror-selected,
.cm-s-inner .CodeMirror-selectedtext { background: ${accent_wash}; }
.cm-s-inner .CodeMirror-activeline-background { background: ${code_bg}; }

.cm-s-inner .cm-comment  { color: ${syn_comment}; font-style: italic; }
.cm-s-inner .cm-keyword  { color: ${syn_keyword}; }
.cm-s-inner .cm-atom     { color: ${syn_keyword}; }
.cm-s-inner .cm-def      { color: ${syn_def}; }
.cm-s-inner .cm-variable { color: var(--text-color); }
.cm-s-inner .cm-variable-2,
.cm-s-inner .cm-variable-3 { color: ${syn_def}; }
.cm-s-inner .cm-property { color: ${syn_def}; }
.cm-s-inner .cm-operator { color: var(--hk-soft); }
.cm-s-inner .cm-string,
.cm-s-inner .cm-string-2 { color: ${syn_string}; }
.cm-s-inner .cm-number   { color: ${syn_number}; }
.cm-s-inner .cm-tag      { color: ${syn_keyword}; }
.cm-s-inner .cm-attribute{ color: ${syn_number}; }
.cm-s-inner .cm-builtin  { color: ${syn_def}; }
.cm-s-inner .cm-meta     { color: var(--hk-muted); }
.cm-s-inner .cm-link     { color: var(--hk-link); }
.cm-s-inner .cm-error    { color: ${syn_error}; }

/* 源码模式（另一套 CodeMirror 主题类，cm-s-inner 管不到） */
.cm-s-typora-default .cm-header      { color: var(--text-color); font-weight: 650; }
.cm-s-typora-default .cm-comment     { color: ${syn_comment}; }
.cm-s-typora-default .cm-string      { color: ${syn_string}; }
.cm-s-typora-default .cm-link        { color: var(--hk-link); }
.cm-s-typora-default .cm-variable-2  { color: var(--hk-soft); }
#typora-source .CodeMirror-cursor    { border-left: 1.5px solid var(--hk-accent); }

/* --------------------------------------------------------------------------
   表格
   -------------------------------------------------------------------------- */
#write table {
  margin: ${type_block_gap} 0;
  font-size: ${type_small};
  border-collapse: collapse;
}
#write table th {
  font-weight: 650;
  text-align: left;
  color: var(--hk-soft);
  background: transparent;
  border-bottom: 1.5px solid var(--hk-divider);
  padding: ${type_cell_pad};
}
#write table td {
  border-bottom: 1px solid var(--hk-hairline);
  padding: ${type_cell_pad};
  vertical-align: top;
}
#write table tbody tr:last-child td { border-bottom: none; }
#write table tbody tr:hover { background: ${code_bg}; }
#write table code { font-size: 0.9em; }

/* --------------------------------------------------------------------------
   其他块
   -------------------------------------------------------------------------- */
#write hr {
  height: 1px;
  border: none;
  background: var(--hk-line);
  margin: ${type_rule_gap} 0;
}

#write img { border-radius: var(--hk-r); }

#write figure { margin: ${type_block_gap} 0; }

/* YAML front matter */
#write pre.md-meta-block {
  background: var(--hk-sunken);
  border: 1px solid var(--hk-hairline);
  border-radius: var(--hk-r);
  padding: 0.7rem 0.95rem;
  color: var(--hk-muted);
  font-family: var(--monospace);
  font-size: ${type_small};
  line-height: 1.6;
}

/* 脚注 */
#write .md-def-footnote { color: var(--hk-muted); font-size: ${type_small}; }
#write sup.md-footnote {
  background: ${code_bg};
  color: var(--hk-accent);
  border-radius: var(--hk-pill);
  padding: 1px 5px;
  font-size: 0.72em;
}
#write .footnotes { color: var(--hk-muted); font-size: ${type_small}; }

/* 目录 */
#write .md-toc { font-size: ${type_small}; }
#write .md-toc-item { color: var(--hk-link); }

/* GitHub 风格 callout */
#write .md-alert { border-left-width: 3px; border-radius: 0 var(--hk-r-sm) var(--hk-r-sm) 0; padding: 0.6rem 1rem; background: ${code_bg}; }
#write .md-alert-text { font-weight: 650; }

/* Markdown 语法符号（未展开时的灰度） */
#write .md-meta { color: var(--md-char-color); font-family: var(--monospace); font-size: 0.9em; }

/* --------------------------------------------------------------------------
   Focus mode
   -------------------------------------------------------------------------- */
.on-focus-mode .md-end-block:not(.md-focus):not(.md-focus-container) *,
.on-focus-mode .md-end-block:not(.md-focus):not(.md-focus-container) {
  color: var(--blur-text-color);
  transition: color .2s ease;
}

/* --------------------------------------------------------------------------
   界面：侧边栏 / 文件树 / 大纲 / 搜索
   现成主题基本没管这块，这里逐项对齐桌面端。
   -------------------------------------------------------------------------- */
#typora-sidebar {
  background: var(--side-bar-bg-color);
  border-right: 1px solid var(--hk-hairline);
  font-family: var(--hk-sans);
}
#typora-sidebar .file-list-item,
#typora-sidebar .file-node-content {
  color: var(--hk-soft);
  font-size: ${type_small};
  border-radius: var(--hk-r-sm);
}
.file-node-content:hover,
.file-list-item:hover { background: var(--item-hover-bg-color); }
.file-list-item.active,
.file-node-content.active { background: var(--active-file-bg-color); color: var(--active-file-text-color); }
.file-list-item-summary,
.file-list-item-time { color: var(--hk-faint); }

#file-library-search-input,
#md-searchpanel input {
  background: var(--hk-raised);
  border: 1px solid var(--hk-line);
  border-radius: var(--hk-r-sm);
  color: var(--text-color);
}

#md-searchpanel {
  background: var(--hk-raised);
  border: 1px solid var(--hk-line);
  border-radius: var(--hk-r);
  box-shadow: 0 12px 32px ${shadow_mid};
}
.md-search-hit    { background: ${accent_wash}; border-radius: 3px; }
.md-search-select { background: ${accent_soft}; }

#outline-content .outline-item { color: var(--hk-soft); font-size: ${type_small}; border-radius: var(--hk-r-sm); }
#outline-content .outline-item:hover { background: var(--item-hover-bg-color); }
#outline-content .outline-active > .outline-item { color: var(--hk-accent); font-weight: 650; }

.sidebar-tabs, .sidebar-footer, #ty-sidebar-footer {
  border-color: var(--hk-hairline);
  color: var(--hk-muted);
}

/* 弹层 / 菜单 / 按钮 */
.modal-content, .popover .popover-content, .context-menu, .dropdown-menu {
  background: var(--hk-raised);
  border: 1px solid var(--hk-line);
  border-radius: var(--hk-r);
  box-shadow: 0 16px 44px ${shadow_mid};
  font-family: var(--hk-sans);
}
.btn {
  border-radius: var(--hk-r-sm);
  border: 1px solid var(--hk-line);
  background: var(--hk-raised);
  color: var(--hk-soft);
}
.btn-primary {
  background: var(--hk-accent);
  border-color: var(--hk-accent);
  color: #fff;
}

/* 滚动条 */
.typora-node ::-webkit-scrollbar,
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb {
  background: ${scrollbar};
  border-radius: var(--hk-pill);
  border: 3px solid transparent;
  background-clip: content-box;
}
::-webkit-scrollbar-thumb:hover { background: ${scrollbar_hover}; background-clip: content-box; }
::-webkit-scrollbar-track { background: transparent; }

/* --------------------------------------------------------------------------
   导出 / 打印
   -------------------------------------------------------------------------- */
@media print {
  .typora-export * { -webkit-print-color-adjust: exact; }
  #write { max-width: 100%; }
}
""")


def check(css):
    """
    自检：把踩过的坑做成断言。

    ⚠️ 判据必须能分辨合法与违规 —— `html { font-size: 16px }` 是规范里
    唯一允许的 px 字号（根字号），而 `#write h1 { font-size: 30px }` 是违规。
    一刀切 grep "font-size.*px" 两者都报，等于没有区分力。所以按规则块解析，
    只豁免选择器为 html 的那一块。
    """
    import re
    problems = []

    n_imp = css.count("!important")
    if n_imp:
        problems.append(f"出现 !important × {n_imp}（目标 0：靠 #write 特异性覆盖即可）")

    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        selector = m.group(1).strip().split("\n")[-1].strip()
        body = m.group(2)
        is_root_rule = selector == "html"
        for fm in re.finditer(r"font-size:\s*[\d.]+px", body):
            if is_root_rule:
                continue                      # 合法：根字号
            problems.append(
                f"字号用了 px：`{selector}` 里 {fm.group(0)}"
                f"（规范要求 rem，否则 Typora 偏好里的字号调节失效）"
            )
    return problems


def main():
    with open(os.path.join(HERE, "tokens.json"), encoding="utf-8") as f:
        tokens = json.load(f)

    v = flatten(tokens)
    ink = tokens["color"]["ink"]
    accent = tokens["color"]["accent"]
    a = tokens["alpha"]

    # 派生色：全部由 ink / accent 叠透明度算出，保证整套色温一致
    v.update({
        "hairline":       hexa(ink, a["hairline"]),
        "line":           hexa(ink, a["line"]),
        "divider":        hexa(ink, a["divider"]),
        "code_bg":        hexa(ink, "0.045"),
        "shadow_soft":    hexa(ink, "0.05"),
        "shadow_mid":     hexa(ink, "0.14"),
        "scrollbar":      hexa(ink, "0.22"),
        "scrollbar_hover": hexa(ink, "0.36"),
        "accent_wash":    hexa(accent, "0.16"),
        # 行内代码专用底：品牌橙浅铺，与通用墨色 code_bg 区分开
        "inline_code_bg": hexa(accent, "0.11"),
        "accent_soft":    hexa(accent, "0.26"),
        "accent_border":  hexa(accent, "0.45"),
        "link_underline": hexa(accent, "0.42"),
        # 语法高亮：低饱和，跟骨白同色温
        "syn_comment": "#8f8e86",
        "syn_keyword": "#8b5cb8",
        "syn_string":  "#3f7d54",
        "syn_number":  "#b06c2c",
        "syn_def":     "#2f6f9f",
        "syn_error":   "#b80a18",
    })

    css = CSS.substitute(v).lstrip("\n")

    out_dir = os.path.join(ROOT, "theme")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{tokens['_meta']['slug']}.css")
    with open(out, "w", encoding="utf-8") as f:
        f.write(css)

    problems = check(css)

    print(f"✅ 生成 {os.path.relpath(out, ROOT)}  ({len(css):,} 字节 / {css.count(chr(10)):,} 行)")
    print(f"   规则数约 {css.count('{'):,}")
    if problems:
        print("⚠️  自检发现问题：")
        for p in problems:
            print("   -", p)
    else:
        print("   自检通过：0 个 !important，0 处 px 字号")


if __name__ == "__main__":
    main()
