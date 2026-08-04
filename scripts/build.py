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
  src: local("Anthropic Sans"),
       local("Anthropic Sans Text"),
       url("./hekouwang/fonts-local/AnthropicSans-Romans-Variable-25x258.woff2") format("woff2"),
       url("./hekouwang/fonts-local/AnthropicSans-Romans-Variable-25x258.ttf") format("truetype");
  font-weight: 300 800;
  font-style: normal;
  font-display: swap;
  font-feature-settings: "dlig" 0;
}
@font-face {
  font-family: "Hekouwang Sans";
  src: local("Anthropic Sans"),
       local("Anthropic Sans Text Italic"),
       url("./hekouwang/fonts-local/AnthropicSans-Italics-Variable-25x258.woff2") format("woff2"),
       url("./hekouwang/fonts-local/AnthropicSans-Italics-Variable-25x258.ttf") format("truetype");
  font-weight: 300 800;
  font-style: italic;
  font-display: swap;
  font-feature-settings: "dlig" 0;
}
@font-face {
  font-family: "Hekouwang Serif";
  src: local("Anthropic Serif"),
       local("Anthropic Serif Text"),
       url("./hekouwang/fonts-local/AnthropicSerif-Romans-Variable-25x258.woff2") format("woff2"),
       url("./hekouwang/fonts-local/AnthropicSerif-Romans-Variable-25x258.ttf") format("truetype");
  font-weight: 300 800;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Hekouwang Mono";
  src: local("Anthropic Mono"),
       local("Anthropic Mono Variable"),
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
  color-scheme: ${color_scheme};   /* 原生控件/滚动条跟浅色或深色变体一致 */
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
  font-optical-sizing: auto;
  text-rendering: optimizeLegibility;
  font-feature-settings: "dlig" 0;
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
  overflow-wrap: break-word;
  text-autospace: normal;
  text-spacing-trim: space-first;
  hanging-punctuation: first last allow-end;
  text-align: ${type_body_align};
  -webkit-font-smoothing: antialiased;
  font-optical-sizing: auto;
  font-feature-settings: "dlig" 0;
  /* Anthropic Sans opsz：正文用 Text 光学尺寸（轴默认 16） */
  font-variation-settings: "opsz" 16;
}

/* C：首行缩进只打在段落上，绝不能写在 #write 上 —— 否则会继承到
   列表 / 标题 / 图片，序号会顶到最左、图片左侧空出一截灰底。
   对齐 Typora base 的 #write.first-line-indent p 机制。
   默认 tech 为 "0"；散文可读改为 "2em"。 */
#write p {
  text-indent: ${type_para_indent};
}
#write li,
#write li p,
#write blockquote p,
#write table p,
#write h1, #write h2, #write h3, #write h4, #write h5, #write h6,
#write .md-alert,
#write .md-toc,
#write pre,
#write p * {
  text-indent: 0;
}
/* 有首行缩进时，顶层列表整体右移，与正文首行对齐；
   嵌套序号就会落在「核心配置要素」这一级后面，而不是文档最左 */
#write > ul,
#write > ol {
  margin-left: ${type_para_indent};
}

#write > p {
  margin-top: 0;
  margin-bottom: ${type_para_gap};
}

#write > p:last-child { margin-bottom: 0; }

/* --------------------------------------------------------------------------
   标题
   字距克制：满幅汉字标题不宜强负 tracking（会挤）；西文标题仍略收一点。
   层级主要靠字号、字重、上下距，不靠装饰色块。
   -------------------------------------------------------------------------- */
#write h1, #write h2, #write h3,
#write h4, #write h5, #write h6 {
  font-family: var(--hk-sans);
  color: var(--text-color);
  break-after: avoid;
  text-wrap: balance;
  overflow-wrap: break-word;
}
#write p, #write li { text-wrap: pretty; }

#write h1 { font-size: ${type_h1_size}; line-height: ${type_h1_lh}; font-weight: ${type_h1_weight}; letter-spacing: ${type_h1_ls}; margin: ${type_h1_mt} 0 ${type_h1_mb}; font-variation-settings: "opsz" 32; }
#write h2 { font-size: ${type_h2_size}; line-height: ${type_h2_lh}; font-weight: ${type_h2_weight}; letter-spacing: ${type_h2_ls}; margin: ${type_h2_mt} 0 ${type_h2_mb}; font-variation-settings: "opsz" 24; }
#write h3 { font-size: ${type_h3_size}; line-height: ${type_h3_lh}; font-weight: ${type_h3_weight}; letter-spacing: ${type_h3_ls}; margin: ${type_h3_mt} 0 ${type_h3_mb}; font-variation-settings: "opsz" 20; }
#write h4 { font-size: ${type_h4_size}; line-height: ${type_h4_lh}; font-weight: ${type_h4_weight}; letter-spacing: ${type_h4_ls}; margin: ${type_h4_mt} 0 ${type_h4_mb}; }
#write h5 { font-size: ${type_h5_size}; line-height: ${type_h5_lh}; font-weight: ${type_h5_weight}; margin: ${type_h5_mt} 0 ${type_h5_mb}; }
#write h6 { font-size: ${type_h6_size}; line-height: ${type_h6_lh}; font-weight: ${type_h6_weight}; margin: ${type_h6_mt} 0 ${type_h6_mb}; color: var(--hk-soft); }

#write h1:first-child, #write h2:first-child,
#write h3:first-child, #write h4:first-child { margin-top: 0; }

/* 标题不加装饰线 —— Claude 桌面端靠字号/字重分层，没有签名下划线 */

/* --------------------------------------------------------------------------
   行内
   -------------------------------------------------------------------------- */
#write strong { font-weight: 600; color: var(--text-color); }
/* 强调：不用着重号。长句（尤其是「*(图：…)＊」图注）整段打点会像疹子；
   斜体对拉丁有效，CJK 无真斜体时保持正常字形、略用字色区分即可。 */
#write em {
  font-style: italic;
  color: var(--hk-soft);
}
#write figcaption em,
#write p > em:only-child {
  /* 图注 / 独占一段的说明：不斜、不抢，只做小字灰提示 */
  font-style: normal;
  color: var(--hk-muted);
  font-size: ${type_small};
}
#write del    { color: var(--hk-muted); }

#write a {
  color: var(--hk-link);
  text-decoration: underline;
  text-decoration-color: ${link_underline};
  text-underline-offset: 0.22em;
  text-decoration-thickness: from-font;
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
   只用墨色细竖线，不加沉底——沉底会让 `> ![](...)` 截图变成灰画框，
   也会让长文引用变成色块墙。层级靠左边线 + 字色即可。
   -------------------------------------------------------------------------- */
#write blockquote {
  margin: ${type_block_gap} 0;
  padding: 0.15rem 0 0.15rem 1rem;
  border-left: 2px solid var(--hk-divider);
  background: transparent;
  color: var(--hk-soft);
}
#write blockquote blockquote {
  margin: 0.5rem 0;
  border-left-color: var(--hk-line);
}
/* 纯图片引用：去掉左边线与内边距，截图贴正文栏宽 */
#write blockquote:has(.md-image, img):not(:has(> p:not(:has(.md-image, img)))) {
  border-left: none;
  padding: 0;
  color: inherit;
}
#write blockquote:has(.md-image, img):not(:has(> p:not(:has(.md-image, img)))) > p {
  margin: 0;
  text-indent: 0;
}

/* --------------------------------------------------------------------------
   列表 —— 对齐 Claude：disc/decimal + outside + padding-left≈20px，
   项间距≈6px（--p5）。圆点用正文软色，不抢 【标签】/加粗。
   -------------------------------------------------------------------------- */
#write ul, #write ol {
  margin: 0 0 ${type_para_gap};
  padding-left: 1.25rem;
}
#write li { margin: ${type_list_gap} 0; }
#write li > p { margin: ${type_list_gap} 0; }

#write ul:not(.task-list) {
  list-style-type: disc;
  list-style-position: outside;
}
#write ul:not(.task-list) > li::marker {
  color: var(--hk-soft);
}
#write ol {
  list-style-type: decimal;
  list-style-position: outside;
}
#write ol li::marker {
  color: var(--hk-muted);
  font-variant-numeric: tabular-nums;
}
#write li > ul,
#write li > ol {
  margin-top: 0.15rem;
  margin-bottom: 0.15rem;
  padding-left: 1.25rem;
}

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
#write .md-task-list-item > input:hover { border-color: var(--hk-accent); }
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
/* 任务列表：不加卡片底——清单文档一屏十几条灰块会毁阅读流。
   完成态只淡字色，不删线（删线在密集 checklist 里噪声太大）。 */
#write li.md-task-list-item > p { margin: ${type_list_gap} 0; }
#write li.md-task-list-item > input:checked ~ p,
#write li.md-task-list-item > input:checked ~ span {
  color: var(--hk-muted);
}

/* --------------------------------------------------------------------------
   代码块
   -------------------------------------------------------------------------- */
#write pre.md-fences {
  font-family: var(--monospace);
  font-size: ${type_fences_size};
  line-height: ${type_fences_lh};
  background: var(--hk-sunken);
  border: 1px solid var(--hk-hairline);
  border-radius: var(--hk-r);
  padding: 0.75rem 0.95rem;
  margin: ${type_block_gap} 0;
  color: var(--text-color);
  box-shadow: none;
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
   表头不加沉底——靠字重 + 底部分隔线建立层级，大表才不会变成灰条带。
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
  font-variant-numeric: tabular-nums;
}
#write table td {
  border-bottom: 1px solid var(--hk-hairline);
  padding: ${type_cell_pad};
  vertical-align: top;
  font-variant-numeric: tabular-nums;
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

/* 图片：只圆角，绝对不加任何背景/边框/阴影
   Typora 结构：<p><span class="md-image"><img></span></p> 或 <figure>
   每一层都必须显式透明；并补偿段落首行缩进（否则左侧空出一截，像灰底）。 */
#write img,
#write .md-image img,
#write a img {
  border-radius: var(--hk-r);
  max-width: 100%;
  height: auto;
  display: block;
  background: transparent;
  background-color: transparent;
  box-shadow: none;
}
#write figure,
#write .md-image,
#write p > .md-image,
#write li .md-image,
#write p:has(> .md-image),
#write p:has(> img) {
  background: transparent;
  background-color: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}
/* 对齐 Typora base：#write.first-line-indent p>.md-image… img { left:-2em }
   para_indent 为 "0" 时 calc 仍为 0，无副作用 */
#write p > .md-image:only-child:not(.md-img-error) img,
#write p > img:only-child {
  position: relative;
  left: calc(0px - ${type_para_indent});
}

/* 图注：居中 + 灰字 + 小字号，跟正文拉开层级 */
#write figcaption {
  text-align: center;
  color: var(--hk-muted);
  font-size: ${type_small};
  margin-top: 0.4rem;
}

/* 数学公式：强制正文色；块级只加细边框，不铺沉底 */
#write .md-math, #write .md-mathblock,
#write .md-inline-math, mjx-container, .katex { color: var(--text-color); }
#write .md-mathblock {
  background: transparent;
  border: 1px solid var(--hk-hairline);
  border-radius: var(--hk-r);
  padding: 0.6rem 0.9rem;
  margin: ${type_block_gap} 0;
  overflow-x: auto;
}

/* 图表 / mermaid 容器 —— 不加背景（之前加了背景泄漏到图片上）
   图表本身有自带样式，不需要主题包一层 */
.md-diagram-panel { padding: 0.3rem 0; }
.md-diagram-panel-preview { background: transparent; }

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

/* GitHub 风格 callout：左边线定语义，底色压到几乎看不见 */
#write .md-alert {
  margin: ${type_block_gap} 0;
  padding: 0.5rem 1rem;
  border-left: 3px solid var(--hk-divider);
  border-radius: 0;
  background: ${alert_note_bg};
}
#write .md-alert-note      { border-left-color: ${alert_note_fg};     background: ${alert_note_bg}; }
#write .md-alert-important { border-left-color: ${alert_important_fg}; background: ${alert_important_bg}; }
#write .md-alert-warning   { border-left-color: ${alert_warning_fg};   background: ${alert_warning_bg}; }
#write .md-alert-tip       { border-left-color: ${alert_tip_fg};       background: ${alert_tip_bg}; }
#write .md-alert-caution   { border-left-color: ${alert_caution_fg};   background: ${alert_caution_bg}; }
#write .md-alert-text      { font-weight: 650; font-size: 0.9rem; }
#write .md-alert-text-note      { color: ${alert_note_fg}; }
#write .md-alert-text-important { color: ${alert_important_fg}; }
#write .md-alert-text-warning   { color: ${alert_warning_fg}; }
#write .md-alert-text-tip       { color: ${alert_tip_fg}; }
#write .md-alert-text-caution   { color: ${alert_caution_fg}; }

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
   无障碍：尊重系统"减少动效"偏好
   -------------------------------------------------------------------------- */
@media (prefers-reduced-motion: reduce) {
  #write a, #write .md-task-list-item > input,
  .btn, .file-node-content:hover,
  .file-list-item:hover { transition: none; }
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
   顶栏 / 标题栏 / 菜单（整窗一致性最后一块）
   Typora 的 #top-titlebar 已用 var(--bg-color) / var(--text-color)，
   这里只覆盖 hover / 按钮等硬编码色值，让标题栏融入主题。
   -------------------------------------------------------------------------- */
#top-titlebar {
  background-color: var(--side-bar-bg-color);
  border-bottom: 1px solid var(--hk-hairline);
}
#top-titlebar .title-text {
  color: var(--hk-muted);
  font-size: ${type_small};
}
#top-titlebar .title-text:hover { color: var(--text-color); }
#top-titlebar header:hover .title-text { color: var(--text-color); }
/* 窗口控制按钮区域：hover 不用系统默认的刺眼红/黄/绿 */
#top-titlebar #w-close:hover { background-color: #e81123; }
#top-titlebar #w-minimize:hover,
#top-titlebar #w-maximize:hover { background-color: rgba(0,0,0,.12); }
/* 大菜单面板 */
.megamenu-content {
  background: var(--hk-raised);
  color: var(--text-color);
  box-shadow: 0 16px 44px ${shadow_mid};
}
.megamenu-menu-section { background: transparent; }
.megamenu-menu-list li a.active,
.megamenu-menu-list:not(.saved) li a:hover {
  background: var(--item-hover-bg-color);
  color: var(--item-hover-text-color);
}
/* 大菜单内的搜索框：默认白底输入框在深色大菜单里会露馅 */
.megamenu-content input {
  background: var(--hk-sunken);
  border: 1px solid var(--hk-line);
  border-radius: var(--hk-r-sm);
  color: var(--text-color);
}

/* --------------------------------------------------------------------------
   导出 / 打印
   -------------------------------------------------------------------------- */
@media print {
  .typora-export * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  #write { max-width: 100%; }
  #typora-sidebar { display: none; }                 /* 导出 PDF 不带侧边栏 */
  /* 防止表格 / 代码块 / 图片 / 引用 / 公式在分页处被拦腰切断 */
  #write table, #write pre.md-fences, #write blockquote,
  #write figure, #write img, #write .md-alert,
  #write .md-mathblock { break-inside: avoid; }
  #write p, #write li { orphans: 2; widows: 2; }      /* 段落首尾至少留 2 行 */
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


def build(tokens, dark=False):
    """按变体生成 CSS。dark 变体用 tokens['dark'] 覆盖 color / alpha 两组。"""
    import copy
    t = copy.deepcopy(tokens)
    if dark:
        for group in ("color", "alpha"):
            t[group].update({k: v for k, v in t["dark"][group].items()
                             if not k.startswith("_")})

    v = flatten({k: val for k, val in t.items() if k != "dark"})
    c = t["color"]
    a = t["alpha"]
    accent = c["accent"]
    border = c["border_base"]
    shadow = c["shadow_base"]

    v.update({
        "color_scheme":   "dark" if dark else "light",
        "hairline":       hexa(border, a["hairline"]),
        "line":           hexa(border, a["line"]),
        "divider":        hexa(border, a["divider"]),
        "code_bg":        hexa(border, "0.045"),
        "shadow_soft":    hexa(shadow, "0.05" if not dark else "0.30"),
        "shadow_mid":     hexa(shadow, "0.14" if not dark else "0.50"),
        "scrollbar":      hexa(border, "0.22"),
        "scrollbar_hover": hexa(border, "0.36"),
        "accent_wash":    hexa(accent, "0.16" if not dark else "0.24"),
        "accent_soft":    hexa(accent, "0.26" if not dark else "0.34"),
        "accent_border":  hexa(accent, "0.45"),
        "link_underline": hexa(accent, "0.42"),
        # 行内代码底：浅色是品牌橙浅铺，深色实测是中性白叠加（见 tokens 的 dark._note）
        "inline_code_bg": hexa(c["code_bg_base"], c["code_bg_alpha"]),
        # 语法高亮：浅色低饱和暖调；深色需提亮，否则在 #1f1f1e 上糊成一团
        "syn_comment": "#8f8e86" if not dark else "#7f7e74",
        "syn_keyword": "#8b5cb8" if not dark else "#c9a0e8",
        "syn_string":  "#3f7d54" if not dark else "#8fc9a0",
        "syn_number":  "#b06c2c" if not dark else "#e0a76a",
        "syn_def":     "#2f6f9f" if not dark else "#8ab8dd",
        "syn_error":   "#b80a18" if not dark else "#ff8b8b",
        # callout：底色再压一档，语义靠左边线 + 标签色
        "alert_note_fg":     "#0969da" if not dark else "#6cb6ff",
        "alert_important_fg":"#8250df" if not dark else "#c8a4ff",
        "alert_warning_fg":  "#9a6700" if not dark else "#e3b341",
        "alert_tip_fg":      "#1f883d" if not dark else "#56d364",
        "alert_caution_fg":  "#cf222e" if not dark else "#ff7b72",
        "alert_note_bg":     hexa("#0969da", "0.04" if not dark else "0.10"),
        "alert_important_bg":hexa("#8250df", "0.04" if not dark else "0.10"),
        "alert_warning_bg":  hexa("#9a6700", "0.05" if not dark else "0.12"),
        "alert_tip_bg":      hexa("#1f883d", "0.04" if not dark else "0.10"),
        "alert_caution_bg":  hexa("#cf222e", "0.04" if not dark else "0.10"),
    })

    css = CSS.substitute(v).lstrip("\n")
    if dark:
        css = css.replace("hekouwang — a Typora theme",
                          "hekouwang-dark — a Typora theme (dark variant)")
    return css


def main():
    with open(os.path.join(HERE, "tokens.json"), encoding="utf-8") as f:
        tokens = json.load(f)

    out_dir = os.path.join(ROOT, "theme")
    os.makedirs(out_dir, exist_ok=True)
    slug = tokens["_meta"]["slug"]

    for dark, name in ((False, f"{slug}.css"), (True, f"{slug}-dark.css")):
        css = build(tokens, dark=dark)
        out = os.path.join(out_dir, name)
        with open(out, "w", encoding="utf-8") as f:
            f.write(css)

        problems = check(css)
        tag = "dark " if dark else "light"
        print(f"✅ [{tag}] {name}  ({len(css):,} 字节 / {css.count(chr(10)):,} 行 / 约 {css.count('{'):,} 条规则)")
        if problems:
            print("   ⚠️  自检未通过：")
            for p in problems:
                print("     -", p)
        else:
            print(f"   自检通过：0 个 !important，0 处 px 字号")


if __name__ == "__main__":
    main()
