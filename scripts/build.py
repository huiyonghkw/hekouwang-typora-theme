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


# 纸感默认只用径向 + inset（无噪点图）。噪点 SVG 在部分 Chromium 上又重又脏，留作可选实验。
_PAPER_NOISE_TMPL = (
    "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E"
    "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' "
    "numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E"
    "%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='{op}'/%3E%3C/svg%3E\")"
)


CSS = Template(r"""
/* ==========================================================================
   hekouwang — a Typora theme
   默认：中文长文阅读档（work）· 骨白底 + 克制纸感 + Anthropic Sans/Inter 西文与系统中文混排。
   浅色 / 深色各一份：hekouwang.css · hekouwang-dark.css。

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
  --hk-ink:       ${color_ink};
  --hk-soft:      ${color_text_soft};
  --hk-muted:     ${color_text_muted};
  --hk-faint:     ${color_text_faint};
  --hk-accent:    ${color_accent};
  --hk-accent2:   ${color_accent2};
  --hk-accent3:   ${color_accent3};
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
  /* 壳层跟侧栏/gutter；纸面只在 #write。mac seamless 顶栏 inherit 自此 */
  background-color: ${paper_gutter_bg};
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

/* 编辑区：两侧 gutter 铺浅底；纸感跟 #write 走，宽度随窗口伸缩 */
content {
  background: ${paper_gutter_bg};
}

#write {
  width: 100%;
  max-width: min(${type_measure}, calc(100% - ${layout_measure_gutter}));
  box-sizing: border-box;
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
  ${paper_write_extra}
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
  color: var(--hk-ink);
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

/* 开篇第一枚 H2：题头区之后多一口气，后文章节仍用常规 h2.mt */
#write h1 ~ h2:first-of-type {
  margin-top: calc(${type_h2_mt} + 0.55rem);
}

/* 标题不加装饰线 —— Claude 桌面端靠字号/字重分层，没有签名下划线 */

/* --------------------------------------------------------------------------
   行内
   -------------------------------------------------------------------------- */
/* strong 让一档给标题：列表里「精准筛选：」不再和 h2 同级抢黑 */
#write strong { font-weight: 600; color: var(--hk-soft); }
#write h1 strong, #write h2 strong, #write h3 strong,
#write h4 strong, #write h5 strong, #write h6 strong {
  color: inherit;
}
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
/* 题头署名 / byline：紧跟 H1 的第一条引用（如「——来自…」），去左边线、缩小灰阶；正文里的 > 仍保留竖线 */
#write h1 + blockquote {
  border-left: none;
  padding: 0;
  margin: -0.25rem 0 ${type_block_gap};
  color: var(--hk-muted);
  font-size: ${type_small};
  line-height: 1.5;
}
#write h1 + blockquote > p {
  margin: 0;
  color: inherit;
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
  padding: 0.88rem 1.05rem;
  margin: 1.25rem 0;
  color: var(--text-color);
  box-shadow: none;
  /* 继承自 #write 的 hanging-punctuation 会把行首 [ 挂到盒外再被裁 */
  hanging-punctuation: none;
  text-spacing-trim: space-all;
  /* ⛔ 勿设 overflow-x:auto —— 规范会把 overflow-y 也变成 auto，
     裁掉 Typora 语言输入框（.code-tooltip 在 bottom:-2.5em） */
  overflow: visible;
}
/* 连续短 fence：多留一点，避免实操贴连成灰条墙 */
#write pre.md-fences + pre.md-fences {
  margin-top: 1.55rem;
}
#write pre.md-fences,
#write pre.md-fences .CodeMirror,
#write pre.md-fences .CodeMirror-code,
#write pre.md-fences .CodeMirror-line {
  hanging-punctuation: none;
}
#write pre.md-fences .CodeMirror-lines {
  padding: 0.15rem 0;
}
#write pre.md-fences .CodeMirror pre {
  padding: 0 0.5rem; /* 左右留空，避免 [ ] 贴边被裁 */
}
${craft_extra}
#write pre.md-fences.md-focus { border-color: ${accent_border}; }

/* 语言选择器：必须露在代码块下方，可点可输入 */
.md-fences .code-tooltip {
  background: var(--hk-raised);
  border: 1px solid var(--hk-line);
  border-radius: var(--hk-r-sm);
  box-shadow: 0 6px 18px ${shadow_soft};
  color: var(--text-color);
  z-index: 30;
  pointer-events: auto;
}
.md-fences .code-tooltip .ty-input,
.md-fences .code-tooltip .ty-cm-lang-input,
.md-fences .code-tooltip input {
  color: var(--text-color);
  caret-color: var(--hk-accent);
  min-width: 8em;
}

/* 语法高亮：低饱和语义色，跟骨白底同一个色温 */
.cm-s-inner .CodeMirror-gutters   { background: transparent; border: none; }
.cm-s-inner .CodeMirror-linenumber{ color: var(--hk-faint); }
.cm-s-inner .CodeMirror-cursor    { border-left: 1.5px solid var(--hk-accent); }
.cm-s-inner div.CodeMirror-selected,
.cm-s-inner .CodeMirror-selectedtext { background: ${accent_wash}; }
.cm-s-inner .CodeMirror-activeline-background { background: transparent; }

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
.cm-s-typora-default .cm-header      { color: var(--hk-ink); font-weight: 650; }
.cm-s-typora-default .cm-comment     { color: ${syn_comment}; }
.cm-s-typora-default .cm-string      { color: ${syn_string}; }
.cm-s-typora-default .cm-link        { color: var(--hk-link); }
.cm-s-typora-default .cm-variable-2  { color: var(--hk-soft); }
#typora-source .CodeMirror-cursor    { border-left: 1.5px solid var(--hk-accent); }

/* --------------------------------------------------------------------------
   表格
   表头：极淡沉底 + ink 字色（认出行，不成灰条带）。
   表宽跟正文栏走——曾用负 margin 破栏，首列会贴纸边像被裁切，已撤回。
   -------------------------------------------------------------------------- */
#write table {
  margin: ${type_block_gap} 0;
  width: 100%;
  max-width: 100%;
  font-size: ${type_small};
  border-collapse: collapse;
}
#write table th {
  font-weight: 650;
  text-align: left;
  color: var(--hk-ink);
  background: ${table_th_bg};
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
/* 树：加大左边距 + 每层缩进，深层级不再贴纸边；给 4px 橙条留空 */
#file-library-tree {
  padding-left: 14px;
  padding-right: 8px;
}
.file-tree-node {
  padding-left: 12px;
}
.file-node-content {
  padding-left: 2px;
}
.file-tree-node.active > .file-node-background {
  border-left-width: 3px;
  border-left-style: solid;
  border-left-color: var(--active-file-border-color);
}
#file-library-list {
  padding-left: 10px;
  padding-right: 8px;
}
.file-list-item {
  padding-left: 12px;
  padding-right: 10px;
}
#outline-content {
  padding-left: 12px;
  padding-right: 8px;
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
   壳层 = 侧栏 / gutter；html 已铺 gutter，titlebar inherit；此处再钉死一遍。
   -------------------------------------------------------------------------- */
#top-titlebar,
titlebar {
  background-color: ${paper_gutter_bg};
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


def apply_reading_preset(tokens, preset_name):
    """把 _presets[preset_name] 的 type / layout / paper 盖到 tokens 上。"""
    import copy
    t = copy.deepcopy(tokens)
    presets = t.get("_presets") or {}
    if preset_name not in presets or preset_name.startswith("_"):
        raise KeyError(f"unknown reading preset: {preset_name}")
    p = presets[preset_name]
    for group in ("type", "layout", "paper"):
        if group not in p:
            continue
        t.setdefault(group, {})
        for k, v in p[group].items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict):
                t[group].setdefault(k, {})
                t[group][k].update({kk: vv for kk, vv in v.items()
                                    if not str(kk).startswith("_")})
            else:
                t[group][k] = v
    return t, p


def paper_surfaces(t, dark):
    """纸感画在 #write 上（随栏宽伸缩）；content 做 gutter。浅/深均可开。"""
    paper = t.get("paper") or {}
    # 深色用 paper.dark 覆盖色值；总开关仍看 enabled（preset 可关）
    base_enabled = bool(paper.get("enabled"))
    if dark:
        dp = {k: v for k, v in (paper.get("dark") or {}).items()
              if not str(k).startswith("_")}
        enabled = base_enabled and bool(dp.get("enabled", True))
        # 深色默认色：正文底卡片 + 更亮侧栏作 gutter
        mid = dp.get("mid", t["color"]["bg"])
        highlight = dp.get("highlight", t["color"].get("hover", "#2c2c2a"))
        shade = dp.get("shade", t["color"].get("sunken", "#1a1a19"))
        gutter = dp.get("gutter", t["color"].get("sidebar_bg", "#262626"))
        inset_a = dp.get("inset_alpha", "0.14")
        grain = dp.get("grain_opacity", paper.get("grain_opacity", "0"))
        ink = t["color"]["border_base"]          # 深色是白
        shadow = t["color"]["shadow_base"]       # 深色是黑
        outer_soft, outer_mid = "0.35", "0.55"
    else:
        enabled = base_enabled
        mid = paper.get("mid", t["color"]["bg"])
        highlight = paper.get("highlight", "#fffef8")
        shade = paper.get("shade", "#f0ede4")
        gutter = paper.get("gutter", paper.get("shade", "#f0ede4"))
        inset_a = paper.get("inset_alpha", "0.05")
        grain = paper.get("grain_opacity", "0")
        ink = t["color"]["border_base"]
        shadow = t["color"]["shadow_base"]
        outer_soft, outer_mid = "0.04", "0.06"

    if not enabled:
        return {
            "paper_gutter_bg": "var(--bg-color)",
            "paper_write_extra": "/* paper off */",
        }

    use_grain = str(grain).strip() not in ("0", "0.0", "false", "")
    craft = bool((t.get("_craft") or {}).get("premium"))
    if craft:
        radial = (
            f"radial-gradient(150% 110% at 50% -12%, {highlight} 0%, "
            f"{mid} 42%, {shade} 100%)"
        )
        if dark:
            outer_soft, outer_mid, outer_far = "0.40", "0.62", "0.45"
            inset_top, inset_wash = "0.08", inset_a
        else:
            outer_soft, outer_mid, outer_far = "0.055", "0.11", "0.07"
            inset_top, inset_wash = "0.055", inset_a
        far = f", 0 28px 64px {hexa(shadow, outer_far)}"
        inset = (
            f"inset 0 1px 0 {hexa(ink, inset_top)}, "
            f"inset 0 0 5.5rem {hexa(ink, inset_wash)}"
        )
    else:
        radial = (
            f"radial-gradient(140% 95% at 50% -8%, {highlight} 0%, "
            f"{mid} 48%, {shade} 100%)"
        )
        far = ""
        inset = (
            f"inset 0 1px 0 {hexa(ink, '0.06' if dark else '0.04')}, "
            f"inset 0 0 4.5rem {hexa(ink, inset_a)}"
        )

    if use_grain and float(grain) > 0:
        noise = _PAPER_NOISE_TMPL.format(op=grain)
        bg = f"{noise}, {radial}"
    else:
        bg = radial
    return {
        "paper_gutter_bg": gutter,
        "paper_write_extra": (
            f"background: {bg}; "
            f"border-radius: var(--hk-r-lg); "
            f"box-shadow: {inset}, "
            f"0 1px 2px {hexa(shadow, outer_soft)}, "
            f"0 {'12px 32px' if craft else '10px 28px'} {hexa(shadow, outer_mid)}{far};"
        ),
    }


def apply_paid_craft_layout(t):
    """付费档：钉死同一套 1rem / 1.65 / 52em，只加呼吸与圆角。"""
    t.setdefault("layout", {})
    t["layout"]["write_pad_top"] = "2.55rem"
    t["layout"]["write_pad_x"] = "2.4rem"
    t["layout"]["write_pad_bottom"] = "5.5rem"
    t.setdefault("type", {})
    t["type"]["para_gap"] = "0.88rem"
    t["type"]["block_gap"] = "1.25rem"
    t.setdefault("shape", {})
    t["shape"]["radius"] = "12px"
    t["shape"]["radius_lg"] = "18px"
    t["_craft"] = {"premium": True}
    return t


def craft_extra_css(accent, accent2, accent3, shadow_soft, dark):
    """付费阅读工艺。⛔ 不用卡片左边彩色竖条。不用 color-mix（Typora Chromium 偏旧）。

    skill 分色靠副强调色：
      V5 紫×青 → accent2 青绿进 H2 / 引用边 / 链接气质
      V6 焰彩   → accent2 橙 + accent3 粉，三停靠渐变（对齐 flare）
    """
    a2 = accent2 or accent
    a3 = accent3 or a2
    dual = (a2.lower() != accent.lower())
    triple = dual and (a3.lower() != a2.lower())

    if triple:
        # V6 焰彩：紫 → 橙 → 粉
        h2_grad = f"linear-gradient(90deg, {accent} 0%, {a2} 55%, {a3} 100%)"
        h2_size = "min(16rem, 58%) 3px"
        hr_bg = (
            f"linear-gradient(90deg, transparent 0%, {accent} 22%, "
            f"{a2} 50%, {a3} 78%, transparent 100%)"
        )
        bq_bg = hexa(a2, "0.08" if not dark else "0.14")
        bq_edge = hexa(a2, "0.55" if not dark else "0.65")
        fence_border = hexa(a2, "0.22" if not dark else "0.32")
        fence_top = hexa(a3, "0.12" if not dark else "0.18")
        th_bg = hexa(accent, "0.07" if not dark else "0.12")
        # 代码块右侧一点焰彩内光（不用左边竖条）
        fence_extra = (
            f", inset -2.5rem 0 3rem {hexa(a2, '0.06' if not dark else '0.10')}"
        )
        # 长文里别给全部 strong 套焰彩渐变（skill 只给 .hl / pull em）
        strong_mark = f"""
#write h1 {{
  background-image: linear-gradient(100deg, {accent}, {a2} 55%, {a3});
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}}
"""
    elif dual:
        # V5 HUD：紫 → 青
        h2_grad = f"linear-gradient(90deg, {accent} 0%, {a2} 100%)"
        h2_size = "min(14rem, 50%) 2.5px"
        hr_bg = (
            f"linear-gradient(90deg, transparent 0%, {accent} 35%, "
            f"{a2} 65%, transparent 100%)"
        )
        bq_bg = hexa(a2, "0.07" if not dark else "0.12")
        bq_edge = hexa(a2, "0.50" if not dark else "0.60")
        fence_border = hexa(accent, "0.16" if not dark else "0.26")
        fence_top = hexa(a2, "0.14" if not dark else "0.20")
        th_bg = hexa(accent, "0.07" if not dark else "0.12")
        fence_extra = f", inset -2rem 0 2.5rem {hexa(a2, '0.05' if not dark else '0.09')}"
        strong_mark = ""
    else:
        h2_grad = f"linear-gradient(90deg, {accent} 0%, transparent 100%)"
        h2_size = "min(11rem, 40%) 2px"
        hr_bg = (
            f"linear-gradient(90deg, transparent 0%, "
            f"{hexa(accent, '0.35' if not dark else '0.45')} 50%, transparent 100%)"
        )
        bq_bg = hexa(accent, "0.07" if not dark else "0.12")
        bq_edge = hexa(accent, "0.45" if not dark else "0.55")
        fence_border = hexa(accent, "0.18" if not dark else "0.28")
        fence_top = hexa(accent, "0.08" if not dark else "0.14")
        th_bg = hexa(accent, "0.08" if not dark else "0.14")
        fence_extra = ""
        strong_mark = ""

    return f"""
/* --------------------------------------------------------------------------
   Paid craft · premium reading（仅 V1 / V3–V6）
   免费 V2 不含本段。指标仍是 1rem · 1.65 · 52em。
   accent2/accent3 来自 skill（V5 青 / V6 橙粉），用来拉开同紫系皮肤。
   -------------------------------------------------------------------------- */
#write h1 {{
  letter-spacing: -0.018em;
}}
#write h2 {{
  padding-bottom: 0.55rem;
  background-image: {h2_grad};
  background-repeat: no-repeat;
  background-position: left bottom;
  background-size: {h2_size};
}}
#write blockquote {{
  background: {bq_bg};
  border-left: 2.5px solid {bq_edge};
  border-radius: 0 var(--hk-r) var(--hk-r) 0;
  padding: 0.55rem 1.05rem 0.55rem 1.05rem;
}}
#write h1 + blockquote {{
  background: transparent;
  border-left: none;
  border-radius: 0;
  padding: 0;
}}
#write pre.md-fences {{
  border: 1px solid {fence_border};
  box-shadow: 0 1px 0 {fence_top}, 0 8px 24px {shadow_soft}{fence_extra};
  padding: 1rem 1.15rem;
}}
#write table th {{
  background: {th_bg};
}}
#write hr {{
  height: 1px;
  border: 0;
  margin: 2rem 0;
  background: {hr_bg};
}}
#write a {{
  text-underline-offset: 0.2em;
  text-decoration-thickness: from-font;
}}
{strong_mark}""".lstrip("\n")


def build(tokens, dark=False, banner_name=None, premium=False):
    """按变体生成 CSS。dark 变体用 tokens['dark'] 覆盖 color / alpha 两组。"""
    import copy
    t = copy.deepcopy(tokens)
    if premium:
        t = apply_paid_craft_layout(t)
    if dark:
        for group in ("color", "alpha"):
            t[group].update({k: v for k, v in t["dark"][group].items()
                             if not k.startswith("_")})

    # accent2/3：skill 副色；缺省回落到主色，保证模板变量齐全
    c = t["color"]
    c.setdefault("accent2", c["accent"])
    c.setdefault("accent3", c.get("accent2", c["accent"]))

    v = flatten({k: val for k, val in t.items() if k not in ("dark", "_craft")})
    a = t["alpha"]
    accent = c["accent"]
    accent2 = c["accent2"]
    accent3 = c["accent3"]
    border = c["border_base"]
    shadow = c["shadow_base"]
    shadow_soft = hexa(shadow, "0.05" if not dark else "0.30")

    v.update({
        "color_scheme":   "dark" if dark else "light",
        "hairline":       hexa(border, a["hairline"]),
        "line":           hexa(border, a["line"]),
        "divider":        hexa(border, a["divider"]),
        "code_bg":        hexa(border, "0.045"),
        "table_th_bg":    hexa(border, "0.04" if not dark else "0.05"),
        "shadow_soft":    shadow_soft,
        "shadow_mid":     hexa(shadow, "0.14" if not dark else "0.50"),
        "scrollbar":      hexa(border, "0.22"),
        "scrollbar_hover": hexa(border, "0.36"),
        "accent_wash":    hexa(accent, "0.16" if not dark else "0.24"),
        "accent_soft":    hexa(accent, "0.26" if not dark else "0.34"),
        "accent_border":  hexa(accent, "0.45"),
        "link_underline": hexa(c.get("link", accent), "0.42"),
        "inline_code_bg": hexa(c["code_bg_base"], c["code_bg_alpha"]),
        "syn_comment": "#8f8e86" if not dark else "#7f7e74",
        "syn_keyword": "#8b5cb8" if not dark else "#c9a0e8",
        "syn_string":  "#3f7d54" if not dark else "#8fc9a0",
        "syn_number":  "#b06c2c" if not dark else "#e0a76a",
        "syn_def":     "#2f6f9f" if not dark else "#8ab8dd",
        "syn_error":   "#b80a18" if not dark else "#ff8b8b",
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
        "craft_extra": (
            craft_extra_css(accent, accent2, accent3, shadow_soft, dark)
            if premium else "/* free tier: no paid craft overlay */\n"
        ),
    })
    v.update(paper_surfaces(t, dark))

    css = CSS.substitute(v).lstrip("\n")
    label = banner_name or ("hekouwang-dark — a Typora theme (dark variant)"
                            if dark else "hekouwang — a Typora theme")
    css = css.replace("hekouwang — a Typora theme", label, 1)
    return css


def load_themes(tier: str):
    """公开仓只有 palettes.json（免费 V2）。本机/付费包另有 palettes.paid.json。"""
    with open(os.path.join(HERE, "palettes.json"), encoding="utf-8") as f:
        free = json.load(f)
    themes = list(free.get("themes") or [])
    paid_path = os.path.join(HERE, "palettes.paid.json")
    paid_themes = []
    if os.path.isfile(paid_path):
        with open(paid_path, encoding="utf-8") as f:
            paid = json.load(f)
        paid_themes = list(paid.get("themes") or [])

    if tier == "free":
        return [t for t in themes if t.get("tier", "free") == "free"]
    if tier == "paid":
        if not paid_themes:
            raise SystemExit(
                "缺少 scripts/palettes.paid.json —— 付费色板不进公开仓。"
                "开发机保留该文件，或从付费 zip 解压后再 --tier paid。"
            )
        return paid_themes
    # all
    by_id = {t["id"]: t for t in themes}
    for t in paid_themes:
        by_id[t["id"]] = t
    # 稳定顺序：v2 免费默认先，再 v1/v3–v6
    order = ["v2", "v1", "v3", "v4", "v5", "v6"]
    out = [by_id[i] for i in order if i in by_id]
    for tid, t in by_id.items():
        if tid not in order:
            out.append(t)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Build hekouwang Typora CSS from tokens + palettes")
    ap.add_argument(
        "--tier",
        choices=("free", "paid", "all"),
        default="all",
        help="free=公开默认 V2；paid=仅付费肤；all=有 paid 文件则六套，否则只出免费",
    )
    args = ap.parse_args()
    tier = args.tier
    paid_path = os.path.join(HERE, "palettes.paid.json")
    if tier == "all" and not os.path.isfile(paid_path):
        tier = "free"
        print("ℹ️  无 palettes.paid.json → 只构建免费档（与公开仓一致）")

    with open(os.path.join(HERE, "tokens.json"), encoding="utf-8") as f:
        tokens = json.load(f)
    themes = load_themes(tier)

    out_dir = os.path.join(ROOT, "theme")
    os.makedirs(out_dir, exist_ok=True)
    slug = tokens["_meta"]["slug"]
    built = tokens["_meta"].get("presets_built") or [tokens["_meta"].get("preset", "work")]

    any_fail = False
    written = []

    for theme in themes:
        # 以 tokens.json 为骨架（阅读指标 / 字体 / 布局），只换配色与纸感
        base = json.loads(json.dumps(tokens))  # deep copy
        base["color"].update(theme["color"])
        if theme.get("paper"):
            # 保留 _note，覆盖色值
            paper = dict(base.get("paper") or {})
            for k, v in theme["paper"].items():
                if k == "dark" and isinstance(v, dict):
                    paper["dark"] = {**(paper.get("dark") or {}), **v}
                elif k != "_note":
                    paper[k] = v
            base["paper"] = paper
        if theme.get("dark"):
            dark_blk = dict(base.get("dark") or {})
            if "color" in theme["dark"]:
                dark_blk["color"] = {**(dark_blk.get("color") or {}), **theme["dark"]["color"]}
            if "alpha" in theme["dark"]:
                dark_blk["alpha"] = {**(dark_blk.get("alpha") or {}), **theme["dark"]["alpha"]}
            base["dark"] = dark_blk

        suffix = theme.get("slug_suffix", "")
        menu = theme.get("menu", f"hekouwang{suffix}")
        label = theme.get("label", theme.get("id", ""))
        tier = theme.get("tier", "paid")

        for preset_name in built:
            t, preset = apply_reading_preset(base, preset_name)
            # 预设可能覆盖 paper；主题纸感色在 preset 之后再贴一次色值
            if theme.get("paper"):
                paper = dict(t.get("paper") or {})
                for k, v in theme["paper"].items():
                    if k == "dark" and isinstance(v, dict):
                        paper["dark"] = {**(paper.get("dark") or {}), **v}
                    elif k not in ("_note",) and k != "enabled":
                        paper[k] = v
                    elif k == "enabled":
                        paper[k] = v
                t["paper"] = paper
            for dark in (False, True):
                name = f"{slug}{suffix}{'-dark' if dark else ''}.css"
                banner = (
                    f"{menu}{'-dark' if dark else ''} — Typora theme"
                    f" ({label}{', dark' if dark else ''} · {tier}"
                    f" · skill {theme.get('id', '').upper()})"
                )
                css = build(t, dark=dark, banner_name=banner, premium=(tier == "paid"))
                # 模板首行仍是 hekouwang — …，build() 只 replace 一次；再标套名
                out = os.path.join(out_dir, name)
                with open(out, "w", encoding="utf-8") as f:
                    f.write(css)
                written.append(name)

                problems = check(css)
                tag = f"{theme['id']}/{preset_name}/{'dark' if dark else 'light'}"
                print(f"✅ [{tag}] {name}  ({len(css):,} 字节)")
                if tier == "paid" and "Paid craft" not in css:
                    any_fail = True
                    print("   ⚠️  付费档应含 Paid craft 工艺段")
                if tier == "free" and "Paid craft" in css:
                    any_fail = True
                    print("   ⚠️  免费档不应含 Paid craft")
                if problems:
                    any_fail = True
                    print("   ⚠️  自检未通过：")
                    for p in problems:
                        print("     -", p)

    # 快速分辨力：本趟若含免费默认，必须在
    work_css_path = os.path.join(out_dir, f"{slug}.css")
    work_dark_path = os.path.join(out_dir, f"{slug}-dark.css")
    built_free = f"{slug}.css" in written
    if built_free and (not os.path.isfile(work_css_path) or not os.path.isfile(work_dark_path)):
        print("⚠️  分辨力失败：缺少免费默认 hekouwang.css / hekouwang-dark.css")
        any_fail = True
        raise SystemExit(1)

    if built_free:
        work_css = open(work_css_path, encoding="utf-8").read()
        work_dark_css = open(work_dark_path, encoding="utf-8").read()
        if "line-height: 1.65" not in work_css:
            print("⚠️  分辨力失败：默认 CSS 未含 work 行高 1.65")
            any_fail = True
        if "max-width: min(52em," not in work_css:
            print("⚠️  分辨力失败：默认 CSS 未含流体行宽 min(52em, …)")
            any_fail = True
        if "radial-gradient" not in work_css:
            print("⚠️  分辨力失败：浅色应含纸感径向渐变")
            any_fail = True
        if "radial-gradient" not in work_dark_css or "10px 28px" not in work_dark_css:
            # 免费档仍是 10px 28px；付费 craft 会变成 12px 32px
            print("⚠️  分辨力失败：深色应同步纸面卡片（径向 + 外阴影）")
            any_fail = True
        import re
        content_block = re.search(r"content \{([^}]*)\}", work_css)
        write_chunk = work_css.split("#write {")[1].split("}")[0] if "#write {" in work_css else ""
        if content_block and "radial-gradient" in content_block.group(1):
            print("⚠️  分辨力失败：纸感不应铺在 content 全宽（会变成两侧假空白）")
            any_fail = True
        if "radial-gradient" not in write_chunk:
            print("⚠️  分辨力失败：纸感应画在 #write 上随栏宽伸缩")
            any_fail = True
        if "Paid craft" in work_css:
            print("⚠️  分辨力失败：免费默认不该含 Paid craft")
            any_fail = True

    # 按本趟 expect 验齐
    expect = []
    for theme in themes:
        suf = theme.get("slug_suffix", "")
        expect.append(f"{slug}{suf}.css")
        expect.append(f"{slug}{suf}-dark.css")
    for name in expect:
        if name not in written:
            print(f"⚠️  分辨力失败：缺 {name}")
            any_fail = True

    print(f"\n共写出 {len(written)} 个 CSS（tier={tier}）：{', '.join(written)}")
    if any_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
