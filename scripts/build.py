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

if __package__:
    from .contrast_check import audit_css
else:
    from contrast_check import audit_css

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


def _rgb(hex_color):
    value = hex_color.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        raise ValueError(f"expected #rrggbb color, got {hex_color!r}")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#" + "".join(f"{round(channel):02x}" for channel in rgb)


def _luminance(hex_color):
    channels = [x / 255 for x in _rgb(hex_color)]
    linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
              for x in channels]
    return sum(x * weight for x, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast_ratio(foreground, background):
    a, b = sorted((_luminance(foreground), _luminance(background)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def _mix_color(base, target, fraction):
    return _hex(a + (b - a) * fraction for a, b in zip(_rgb(base), _rgb(target)))


def readable_color(base, backgrounds, minimum, dark):
    """保留原色相，向白/黑做最小混合，直到所有实际底色达到目标对比度。"""
    backgrounds = [backgrounds] if isinstance(backgrounds, str) else backgrounds
    if min(contrast_ratio(base, bg) for bg in backgrounds) >= minimum:
        return base
    target = "#ffffff" if dark else "#000000"
    lo, hi = 0.0, 1.0
    for _ in range(24):
        mid = (lo + hi) / 2
        candidate = _mix_color(base, target, mid)
        if min(contrast_ratio(candidate, bg) for bg in backgrounds) >= minimum:
            hi = mid
        else:
            lo = mid
    candidate = _mix_color(base, target, hi)
    # 8-bit rounding can land just below a threshold; move one step if needed.
    while min(contrast_ratio(candidate, bg) for bg in backgrounds) < minimum:
        hi = min(1.0, hi + 1 / 255)
        candidate = _mix_color(base, target, hi)
        if hi == 1.0:
            break
    return candidate


def composite_color(foreground, background, alpha):
    return _mix_color(background, foreground, float(alpha))


def paper_colors(tokens, dark):
    paper = tokens.get("paper") or {}
    variant = (paper.get("dark") or {}) if dark else paper
    bg = tokens["color"]["bg"]
    if not paper.get("enabled", True) or (dark and not variant.get("enabled", True)):
        return [bg]
    return [variant.get(name, bg) for name in ("highlight", "mid", "shade")]


def on_accent_color(accent):
    dark_ink, light_ink = "#141413", "#ffffff"
    if contrast_ratio(dark_ink, accent) >= 4.55:
        return dark_ink
    if contrast_ratio(light_ink, accent) >= 4.55:
        return light_ink
    return "#000000"


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
   默认：中文长文阅读档（work）· 素白纸面 + 墨绿强调 + Anthropic Sans/Inter 西文与系统中文混排。
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
  --active-file-text-color:   ${color_ink};
  --active-file-border-color: ${color_accent_text};
  --primary-color:            ${color_accent_text};
  --primary-btn-border-color: ${color_accent_text};
  --primary-btn-text-color:   ${color_on_accent};
  --window-border:            ${line};
  --md-char-color:            ${color_faint_readable};
  --meta-content-color:       ${color_muted_readable};
  --control-text-color:       ${color_text_soft};
  --control-text-hover-color: ${color_text};
  --select-text-bg-color:     ${accent_wash};
  --search-select-bg-color:   ${accent_soft};
  --blur-text-color:          ${color_muted_readable};
  --monospace:                ${font_mono_stack};
  --rawblock-edit-panel-bd:   ${line};
  --mermaid-theme:            ${mermaid_theme};

  /* —— Bone 私有 —— */
  --hk-raised:    ${color_bg_raised};
  --hk-sunken:    ${color_sunken};
  --hk-ink:       ${color_ink};
  --hk-soft:      ${color_text_soft};
  --hk-muted:     ${color_muted_readable};
  --hk-faint:     ${color_faint_readable};
  --hk-accent:    ${color_accent_text};
  --hk-accent-decor: ${color_accent};
  --hk-accent-text: ${color_accent_text};
  --hk-on-accent: ${color_on_accent};
  --hk-control-border: ${color_control_border};
  --hk-accent2:   ${color_accent2};
  --hk-accent3:   ${color_accent3};
  --hk-link:      ${color_link_readable};
  --hk-link-hover: ${color_link_hover};
  --hk-code:      ${color_code_text_readable};
  --hk-hairline:  ${hairline};
  --hk-line:      ${line};
  --hk-divider:   ${divider};
  --hk-r-sm:      ${shape_radius_sm};
  --hk-r:         ${shape_radius};
  --hk-r-lg:      ${shape_radius_lg};
  --hk-pill:      ${shape_radius_pill};
  --hk-sans:      ${font_sans_stack};
  --hk-serif:     ${font_serif_stack};
  /* 用户可在 hekouwang.user.css 中覆盖，不必重建整套配色。 */
  --hk-reading-measure: ${type_reading_measure};
}

/* --------------------------------------------------------------------------
   骨架
   -------------------------------------------------------------------------- */
html {
  font-size: ${type_root_px};          /* 规范：唯一允许用 px 的地方 */
  /* 画布 = 纸面色。导出无 <content>，html 即整页底；
     若 html 与 #write 一深一浅，就会「外面有底色、中间白柱」。 */
  background-color: ${paper_canvas_bg};
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

/* Windows：Typora 会在 body 挂 .os-windows。不能只把「微软雅黑」塞进通用
   fallback：system-ui 在 Windows 版本间的 CJK 回退并不稳定，且 macOS 的
   antialiased 会绕开 ClearType，长文会发灰。这里让阅读面、代码和 UI 控件
   共享可预期的栈；不打包 CJK 字体，保留系统更新与许可边界。 */
body.os-windows {
  --hk-sans: ${font_windows_sans_stack};
  --hk-serif: ${font_windows_serif_stack};
  --monospace: ${font_windows_mono_stack};
  -webkit-font-smoothing: auto;
  font-smoothing: auto;
  text-rendering: auto;
  font-synthesis: none;
  letter-spacing: 0.005em;
}
body.os-windows #write {
  -webkit-font-smoothing: auto;
  text-rendering: auto;
  letter-spacing: 0;
}
body.os-windows input,
body.os-windows textarea,
body.os-windows select,
body.os-windows button { font: inherit; }

/* 编辑区：两侧 gutter 铺浅底；纸感跟 #write 走，宽度随窗口伸缩 */
content {
  background: ${paper_gutter_bg};
}

#write {
  width: 100%;
  max-width: min(${type_measure}, calc(var(--hk-reading-measure) + 2 * ${layout_write_pad_x} + ${layout_wide_canvas_extra}), calc(100% - ${layout_measure_gutter}));
  box-sizing: border-box;
  margin: 0 auto;
  margin-top: ${layout_write_margin_top};
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

/* 宽窗口保留技术画布；正文阅读列在下方单独限宽。
   纸面只比阅读列多出 wide_canvas_extra，避免正文两侧留出大片空纸。 */
@media (min-width: ${layout_wide_breakpoint}) {
  #write {
    max-width: min(${layout_wide_measure}, calc(var(--hk-reading-measure) + 2 * ${layout_write_pad_x} + ${layout_wide_canvas_extra}), calc(100% - ${layout_measure_gutter}));
  }
}

/* 含 Windows 分屏在内的窄窗口：避免双重 padding 把正文挤成竖条。 */
@media (max-width: 760px) {
  #write {
    max-width: calc(100% - 1.5rem);
    margin-top: 0.75rem;
    padding: 1.5rem 1.25rem 3.5rem;
    border-radius: var(--hk-r);
  }
}
/* 侧栏收起时：纸面直接铺满内容区，不再出现纸边 / gutter / 投影；
   正文仍由 --hk-reading-measure 限宽居中。检测 Typora 的 body.pin-outline：
   侧栏打开时 Typora 会加这个类，收起时移除。 */
body:not(.pin-outline) content {
  background: var(--bg-color);
}
body:not(.pin-outline) #write {
  max-width: none;
  width: 100%;
  margin-left: 0;
  margin-right: 0;
  background: var(--bg-color);
  box-shadow: none;
}

/* 裸 pre > code 用于预览/HTML 片段；Typora 编辑器的 CodeMirror 仍自行滚动。
   pre 保留 overflow:visible 以让语言工具浮层可见，因此在 code 子节点折行。 */
@media screen {
  body:not(.typora-export) #write pre.md-fences > code {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
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

/* 宽屏补偿：1792px 起阅读列触顶 96rem（约 96 字/行）。
   1.65 的行距撑不住这个行宽，正文与引用放宽到 1.78、段距到 1rem；
   表格与代码保持原密度，避免整页被拉松。 */
@media screen and (min-width: 1800px) {
  #write { line-height: 1.78; }
  #write > p { margin-bottom: 1rem; }
  #write table { line-height: 1.6; }
}

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
  /* 大纲 / 目录跳转后给标题留出顶部呼吸，避免贴住工具栏 */
  scroll-margin-top: 3rem;
}
#write p, #write li { text-wrap: pretty; }

#write h1 { font-size: ${type_h1_size}; line-height: ${type_h1_lh}; font-weight: ${type_h1_weight}; letter-spacing: ${type_h1_ls}; margin: ${type_h1_mt} 0 ${type_h1_mb}; font-variation-settings: "opsz" 32; }
#write h2 { font-size: ${type_h2_size}; line-height: ${type_h2_lh}; font-weight: ${type_h2_weight}; letter-spacing: ${type_h2_ls}; margin: ${type_h2_mt} 0 ${type_h2_mb}; font-variation-settings: "opsz" 24; }
#write h3 { font-size: ${type_h3_size}; line-height: ${type_h3_lh}; font-weight: ${type_h3_weight}; letter-spacing: ${type_h3_ls}; margin: ${type_h3_mt} 0 ${type_h3_mb}; font-variation-settings: "opsz" 20; }
#write h4 { font-size: ${type_h4_size}; line-height: ${type_h4_lh}; font-weight: ${type_h4_weight}; letter-spacing: ${type_h4_ls}; margin: ${type_h4_mt} 0 ${type_h4_mb}; }
#write h5 { font-size: ${type_h5_size}; line-height: ${type_h5_lh}; font-weight: ${type_h5_weight}; margin: ${type_h5_mt} 0 ${type_h5_mb}; }
#write h6 { font-size: ${type_h6_size}; line-height: ${type_h6_lh}; font-weight: ${type_h6_weight}; margin: ${type_h6_mt} 0 ${type_h6_mb}; color: var(--hk-muted); }

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
/* 强调保持正文墨色，靠字重建立层级；不把语义强调降成灰字。 */
#write strong { font-weight: 650; color: inherit; }
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
  color: var(--hk-link-hover);
  text-decoration-color: var(--hk-accent);
}

#write mark {
  background: ${accent_wash};
  color: inherit;
  border-radius: var(--hk-r-sm);
  padding: 0.05em 0.2em;
}

/* 行内代码：极轻的中性浅底 + 深灰字，不抢正文 */
#write code,
#write tt {
  font-family: var(--monospace);
  font-size: ${type_code_size};
  color: var(--hk-code);
  background: ${inline_code_bg};
  border: none;
  border-radius: var(--hk-r-sm);
  padding: 0.12em 0.34em;
  word-break: break-word;
}

#write h1 code, #write h2 code, #write h3 code,
#write h4 code, #write h5 code, #write h6 code {
  font-size: 0.88em;
}

/* --------------------------------------------------------------------------
   引用
   V2 的粗浅灰竖线 + 弱化字色，不加沉底——沉底会让 `> ![](...)` 截图变成灰画框，
   也会让长文引用变成色块墙。
   -------------------------------------------------------------------------- */
#write blockquote {
  margin: ${type_block_gap} 0;
  padding: 0.1rem 0 0.1rem 1.1rem;
  border-left: 0.5rem solid var(--hk-line);
  background: transparent;
  color: var(--hk-muted);
}
#write blockquote blockquote {
  margin: 0.5rem 0;
  border-left-color: var(--hk-line);
}
/* 题头署名 / byline：紧跟 H1 的第一条引用（如「——来自…」），去左边线、缩小灰阶；正文里的 > 仍保留竖线 */
#write h1 + blockquote {
  border-left: none;
  padding: 0;
  margin: 1.35rem 0 1.2rem;
  color: var(--hk-muted);
  font-size: ${type_small};
  line-height: 1.55;
}
#write h1 + blockquote > p {
  margin: 0;
  color: inherit;
}
/* 题头元数据里的 code 不再铺灰底：一行八个小按钮会把 H1 压下去 */
#write h1 + blockquote code {
  background: transparent;
  padding: 0;
  color: var(--hk-soft);
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
   列表 —— disc/decimal + outside + padding-left≈18px，
   项间距由 type.list_gap 控制。圆点用正文软色，不抢 【标签】/加粗。
   -------------------------------------------------------------------------- */
#write ul, #write ol {
  margin: 0 0 ${type_para_gap};
  padding-left: 1.1rem;
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
  padding-left: 1.1rem;
}

#write ul.task-list { padding-left: 1.25rem; }
#write ul.task-list li.task-list-item { list-style: none; }
#write .md-task-list-item > input {
  -webkit-appearance: none;
  appearance: none;
  width: 1.05em;
  height: 1.05em;
  margin-left: -1.45em;
  margin-top: 0.28em;
  border: 1.5px solid var(--hk-control-border);
  border-radius: var(--hk-r-sm);
  background: var(--hk-raised);
  transition: background .15s ease, border-color .15s ease;
}
#write .md-task-list-item > input:hover { border-color: var(--hk-accent-text); }
#write .md-task-list-item > input:checked {
  background: var(--hk-ink);
  border-color: var(--hk-ink);
}
#write .md-task-list-item > input:checked::after {
  content: "";
  display: block;
  width: 0.28em;
  height: 0.55em;
  margin: 0.08em 0 0 0.32em;
  border: solid var(--hk-on-accent);
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
  /* 默认 8 列会让 YAML / Makefile 的缩进宽一倍 */
  tab-size: 4;
  -moz-tab-size: 4;
}
#write pre.md-fences .CodeMirror-lines {
  padding: 0.15rem 0;
}
#write pre.md-fences .CodeMirror pre {
  padding: 0 0.5rem; /* 左右留空，避免 [ ] 贴边被裁 */
}
#write pre.md-fences.md-focus { border-color: var(--hk-accent-text); }

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

/* 语法高亮：低饱和语义色，跟白纸同一个色温 */
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

/* 源码模式保持与正文接近的阅读宽度，并保留 Typora 的行号内边距。 */
#typora-source .CodeMirror-lines {
  box-sizing: border-box;
  max-width: min(calc(var(--hk-reading-measure) + 4rem), calc(100% - ${layout_measure_gutter}));
  margin: 0 auto;
}
@media (max-width: 760px) {
  #typora-source .CodeMirror-lines { max-width: calc(100% - 1.5rem); }
}
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
   常规表填满阅读列，宽数据表使用技术画布和局部滚动。
   -------------------------------------------------------------------------- */
#write table {
  margin: ${type_block_gap} 0;
  width: 100%;
  min-width: min(100%, 32rem);
  max-width: 100%;
  font-size: ${type_table_size};
  border-collapse: collapse;
  border: 1px solid var(--hk-hairline);
}
/* 十列起的宽数据表：内容放得下时与阅读列对齐，放不下才向技术画布展开，
   再宽则在自身滚动容器中滚动。 */
@media screen {
  #write figure > table:has(tr > :nth-child(10)) {
    min-width: max-content;
    max-width: none;
  }
  #write > figure:has(> table tr > :nth-child(10)) {
    box-sizing: border-box;
    width: fit-content;
    min-width: min(100%, var(--hk-reading-measure));
    max-width: 100%;
    margin-left: auto;
    margin-right: auto;
  }
  /* 多列表多为短数值，收窄单元格左右留白，免得只因留白就横向滚动。 */
  #write table:has(tr > :nth-child(10)) :is(th, td) {
    padding-left: 0.55rem;
    padding-right: 0.55rem;
  }
}
/* 常规六列及以下表格填满响应式阅读列。 */
#write > figure:has(> table):not(:has(> table tr > :nth-child(10))) {
  box-sizing: border-box;
  max-width: min(100%, var(--hk-reading-measure));
  margin-left: auto;
  margin-right: auto;
}
/* 一至三列的小表不拉满宽栏：48rem 左对齐正文，避免三列各占 500px。 */
#write > figure:has(> table):not(:has(> table tr > :nth-child(4))) {
  max-width: min(100%, var(--hk-reading-measure), 48rem);
  margin-left: max(0px, calc((100% - var(--hk-reading-measure)) / 2));
  margin-right: auto;
}
/* 单元格至少留出可读宽度。窄窗中由 Typora 的 figure 自身滚动，
   避免长中文、代码和 URL 被挤成一两个字一行。 */
/* 只有窄窗才给表格 figure 加滚动；桌面上的 overflow 会裁掉 Typora
   的列拖拽 overlay，列边界就不出现 ew-resize 把手。 */
@media screen and (max-width: 1100px) {
  body:not(.typora-export) #write > figure:has(> table):not(:has(> table tr > :nth-child(10))) {
    overflow-x: auto;
  }
  body:not(.typora-export) #write > figure:has(> table):not(:has(> table tr > :nth-child(10))) > table {
    max-width: none;
  }
  body:not(.typora-export) #write > figure:has(> table):not(:has(> table tr > :nth-child(10))) > table th,
  body:not(.typora-export) #write > figure:has(> table):not(:has(> table tr > :nth-child(10))) > table td {
    min-width: 7rem;
  }
  body:not(.typora-export) #write > figure:has(> table):not(:has(> table tr > :nth-child(10))) > table td:has(code) {
    min-width: 12rem;
  }
}
#write > table:not(:has(tr > :nth-child(10))) {
  width: min(100%, var(--hk-reading-measure));
  max-width: min(100%, var(--hk-reading-measure));
  margin-left: auto;
  margin-right: auto;
}
#write > table:not(:has(tr > :nth-child(4))) {
  width: min(100%, var(--hk-reading-measure), 48rem);
  max-width: min(100%, var(--hk-reading-measure), 48rem);
  margin-left: max(0px, calc((100% - var(--hk-reading-measure)) / 2));
  margin-right: auto;
}
#write table th,
#write table td {
  overflow-wrap: anywhere;
}
/* 首列多是编号 / 字段名：允许折行，但别把 P01 拆成 P0 / 1 */
#write table th:first-child,
#write table td:first-child {
  overflow-wrap: break-word;
}
/* 多列表格的首列给一个下限，避免「编号」被挤成两行 */
#write table:has(tr > :nth-child(4)) :is(th, td):first-child {
  min-width: 4.5rem;
}
#write table th {
  font-weight: 700;
  text-align: left;
  color: var(--hk-ink);
  background: ${table_th_bg};
  border: 1px solid var(--hk-hairline);
  padding: ${type_cell_pad};
  font-variant-numeric: tabular-nums;
}
#write table td {
  border: 1px solid var(--hk-hairline);
  padding: ${type_cell_pad};
  vertical-align: top;
  font-variant-numeric: tabular-nums;
}
/* 十列起只留横向分隔，避免宽表变成 Excel 网格。 */
#write figure:has(> table tr > :nth-child(10)) th,
#write figure:has(> table tr > :nth-child(10)) td,
#write > table:has(tr > :nth-child(10)) th,
#write > table:has(tr > :nth-child(10)) td {
  border-left: 0;
  border-right: 0;
}
#write table tbody tr:hover { background: ${code_bg}; }
#write table code { font-size: 1em; }

/* --------------------------------------------------------------------------
   其他块
   -------------------------------------------------------------------------- */
#write hr {
  width: 100%;
  height: 1px;
  border: none;
  margin: 2.4rem auto;
  background: var(--hk-line);
}
/* Typora 给可聚焦的 .md-hr 加 5px 自动外框；点中 HR 时会像多出一条线 */
#write .md-hr:focus {
  outline: none;
}
#write .md-hr {
  padding: 0;
  border: 0;
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
  background: transparent;
  background-color: transparent;
  box-shadow: none;
}
/* :only-child 不计文本节点，句内图片也可能被 Typora 误排成整行。 */
#write p > .md-image,
#write p > .md-image:only-child {
  display: inline;
  width: auto;
}
#write p > .md-image img,
#write p > .md-image:only-child img,
#write p > img:only-child {
  display: inline-block;
  vertical-align: middle;
}
#write figure img { display: block; }
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

/* Typora 1.14 的可见块级公式使用 .md-math-block；.md-mathblock-panel 是编辑控件。 */
#write .md-math-block, #write .md-inline-math,
#write mjx-container, #write .katex { color: var(--text-color); }
#write .md-math-block {
  background: transparent;
  border: 1px solid var(--hk-hairline);
  border-radius: var(--hk-r);
  padding: 0.6rem 0.9rem;
  margin: ${type_block_gap} 0;
  overflow-x: auto;
}
/* Typora 编辑时会加 .md-rawblock-on-edit，让内部公式工具条完整露出。 */
#write .md-math-block.md-rawblock-on-edit {
  overflow: visible;
  border-color: var(--hk-control-border);
}

/* Mermaid：浅色用 neutral 灰阶，避免默认主题的淡紫节点；
   图表块不铺代码块灰底，让图直接落在纸面上。 */
.md-diagram-panel { padding: 0.3rem 0; background: transparent; }
.md-diagram-panel-preview { background: transparent; }
#write pre.md-fences[lang="mermaid"],
#write pre.md-fences[lang="sequence"] {
  background: transparent;
  border-color: transparent;
}
#write .md-diagram-panel svg { background: transparent; }

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
  color: var(--hk-accent-text);
  border-radius: var(--hk-pill);
  padding: 1px 5px;
  font-size: 0.72em;
  /* 行内上标会把行盒撑高 1.3px，长文里出现忽松忽紧的行 */
  line-height: 0;
}
#write .footnotes {
  color: var(--hk-muted);
  font-size: ${type_small};
  /* Typora base 默认 .footnotes{opacity:.8}，叠加后掉到 AA 以下 */
  opacity: 1;
}
#write .footnote-line { font-size: ${type_small}; }

/* 目录 */
#write .md-toc { font-size: ${type_small}; }
/* 目录是导航不是正文链接：默认用弱化墨色，悬停 / 焦点才点亮 */
#write .md-toc-item,
#write .md-toc-item a { color: var(--hk-soft); }
#write .md-toc-item:hover,
#write .md-toc-item:hover a,
#write .md-toc-item:focus-within,
#write .md-toc-item:focus-within a { color: var(--hk-link); }

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

/* 宽纸面中的阅读列：连续文字和代码块居中对齐；宽表格、图表保留整幅空间。
   代码块不跟纸面同宽：收起侧边栏后会比正文两侧各宽出一截。 */
#write > :is(p, h1, h2, h3, h4, h5, h6, pre.md-fences,
             ul, ol, blockquote, hr, .md-hr, .md-alert, .md-toc,
             .md-htmlblock, .md-def-footnote, .footnotes) {
  box-sizing: border-box;
  max-width: min(100%, var(--hk-reading-measure));
  margin-left: auto;
  margin-right: auto;
}

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
.on-focus-mode .md-end-block:not(.md-focus):not(.md-focus-container) :is(img, input[type="checkbox"], .md-diagram-panel),
.on-focus-mode .md-math-block:not(.md-focus):not(.md-focus-container):not(.md-rawblock-on-edit) {
  opacity: 0.42;
  transition: opacity .2s ease;
}
.on-focus-mode pre.md-fences:not(.md-focus):not(.md-focus-container) .cm-s-inner span {
  color: var(--blur-text-color);
}

/* 键盘焦点要与装饰强调色分开：焦点环至少有 3:1 的边界对比。 */
#write a:focus-visible,
#write .md-task-list-item > input:focus-visible,
.btn:focus-visible,
.file-node-content:focus-visible,
.file-list-item:focus-visible,
#outline-content .outline-item:focus-visible,
#file-library-search-input:focus-visible,
#md-searchpanel input:focus-visible,
.ty-editor-toolbar-btn:focus-visible,
.ty-editor-toolbar-hint-close:focus-visible,
.ty-editor-toolbar-menu-item:focus-visible {
  outline: 2px solid var(--hk-accent-text);
  outline-offset: 2px;
}

/* --------------------------------------------------------------------------
   无障碍：尊重系统"减少动效"偏好
   -------------------------------------------------------------------------- */
@media (prefers-reduced-motion: reduce) {
  #write a, #write .md-task-list-item > input,
  .btn, .file-node-content:hover,
  .file-list-item:hover,
  .on-focus-mode .md-end-block:not(.md-focus):not(.md-focus-container),
  .on-focus-mode .md-end-block:not(.md-focus):not(.md-focus-container) *,
  .on-focus-mode .md-end-block:not(.md-focus):not(.md-focus-container) :is(img, input[type="checkbox"], .md-diagram-panel),
  .on-focus-mode .md-math-block:not(.md-focus):not(.md-focus-container):not(.md-rawblock-on-edit) {
    transition: none;
  }
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
/* 树：加大左边距 + 每层缩进，深层级不再贴纸边；给 4px 强调色条留空 */
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
  background: var(--active-file-bg-color);
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
.md-search-hit    { background: ${accent_wash}; border-radius: var(--hk-r-sm); }
.md-search-select { background: ${accent_soft}; }

#outline-content .outline-item { color: var(--hk-soft); font-size: ${type_small}; border-radius: var(--hk-r-sm); }
#outline-content .outline-item:hover { background: var(--item-hover-bg-color); }
#outline-content .outline-active > .outline-item { color: var(--hk-accent-text); font-weight: 650; }

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
  color: var(--hk-on-accent);
}

/* Typora 1.14 的浮动工具栏：保留原生位置和收起逻辑，只修正灰化文字与焦点。 */
.ty-editor-toolbar,
.ty-editor-toolbar-menu {
  background-color: var(--hk-raised);
  color: var(--text-color);
  border-color: var(--hk-control-border);
  font-family: var(--hk-sans);
}
.ty-editor-toolbar-btn,
.ty-editor-toolbar-hint-close,
.ty-editor-toolbar-hint-text,
.ty-editor-toolbar-menu-item .tmi-extra,
.ty-editor-toolbar-menu-item .tmi-icon,
.ty-editor-toolbar-select .fa {
  color: var(--hk-muted);
  opacity: 1;
}
.ty-editor-toolbar-btn,
.ty-editor-toolbar-hint-close { background-color: transparent; }
.ty-editor-toolbar-btn:is(:hover, .hover, .active, :focus-visible),
.ty-editor-toolbar-hint-close:is(:hover, :focus-visible),
.ty-editor-toolbar-menu-item:is(:hover, .active, :focus-visible) {
  color: var(--text-color);
}
.ty-editor-toolbar-btn:is(:hover, .hover, .active),
.ty-editor-toolbar-menu-item:is(:hover, .active) {
  background-color: var(--item-hover-bg-color);
}
.ty-editor-toolbar-divider,
.ty-editor-toolbar-menu-divider { background-color: var(--hk-control-border); }

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
   壳层 = 侧栏 / content gutter；顶栏显式铺 gutter（html 已改为画布色）。
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
   1) 整页画布同色（纸面），拆掉 #write 浮卡片 —— 不许画布与纸面一深一浅
   2) 精装层：呼吸边距、H2 签名线、抬升 fence、表格圆角、渐变 HR
   导出 DOM：body.typora-export > .typora-export-content > #write
   !important 仅本段；check() 豁免。⛔ 不用左边彩色竖条。
   -------------------------------------------------------------------------- */

html {
  background: ${paper_canvas_bg} !important;
  background-color: ${paper_canvas_bg} !important;
}

body.typora-export,
body.typora-export .typora-export-content,
body.typora-export #write {
  background: ${paper_canvas_bg} !important;
  background-color: ${paper_canvas_bg} !important;
  background-image: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}
body.typora-export #write {
  max-width: none !important;
  width: 100% !important;
  margin: 0 !important;
  /* 页内呼吸：保留 Typora 导出设置的左右留白，这里只补内边距。 */
  padding: 2rem 0.15rem 2.4rem !important;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

/* —— 标题：字距 + H2 底部签名线（非左边竖条）—— */
body.typora-export #write h1 {
  letter-spacing: -0.02em;
  margin-top: 0 !important;
  margin-bottom: 0.85rem !important;
}
body.typora-export #write h2 {
  width: fit-content;
  max-width: min(100%, var(--hk-reading-measure));
  margin-left: max(0px, calc((100% - var(--hk-reading-measure)) / 2));
  margin-right: auto;
  letter-spacing: -0.014em;
  padding-bottom: 0.55rem;
  margin-top: 2rem !important;
  background-image: linear-gradient(90deg, ${color_accent} 0%, transparent 100%);
  background-repeat: no-repeat;
  background-position: left bottom;
  background-size: 100% 2px;
}
body.typora-export #write h3 {
  letter-spacing: -0.006em;
  margin-top: 1.35rem !important;
}

/* 开篇元信息引用：h1 后连续引用更轻，不抢标题 */
body.typora-export #write h1 + blockquote,
body.typora-export #write h1 + blockquote + blockquote,
body.typora-export #write h1 + blockquote + blockquote + blockquote,
body.typora-export #write h1 + blockquote + blockquote + blockquote + blockquote {
  background: transparent !important;
  border-left: none !important;
  padding-left: 0 !important;
  color: var(--hk-muted);
  font-size: 0.92em;
  line-height: 1.55;
  margin: 0.2rem 0 !important;
}
body.typora-export #write h1 + blockquote {
  margin-top: 0.35rem !important;
}
body.typora-export #write h1 + blockquote + blockquote + blockquote + blockquote {
  margin-bottom: 1.25rem !important;
}

/* 普通引用：V2 的粗浅灰竖线 + 弱化字色，不加底 */
body.typora-export #write blockquote {
  background: transparent !important;
  border-left: 0.5rem solid ${line} !important;
  border-radius: 0 !important;
  padding: 0.1rem 0 0.1rem 1.1rem !important;
}

/* 标题 fence（发布文案灰盒）→ 纸面抬升，略亮于画布、绝不用纯白 */
body.typora-export #write pre.md-fences {
  background: ${export_surface} !important;
  border: 1px solid ${hairline} !important;
  border-radius: var(--hk-r-lg) !important;
  box-shadow:
    0 1px 0 ${export_shine},
    0 8px 22px ${shadow_soft} !important;
  padding: 1rem 1.2rem !important;
  margin: 0.85rem auto 1.15rem !important;
  /* 编辑区仍保留语言选择器；导出的静态代码允许长行在页内折行。 */
  white-space: pre-wrap !important;
  overflow-wrap: break-word !important;
  overflow-wrap: anywhere !important;
  word-break: break-word !important;
  overflow: visible !important;
}
body.typora-export #write pre.md-fences code,
body.typora-export #write pre.md-fences .CodeMirror-line {
  white-space: pre-wrap !important;
  overflow-wrap: break-word !important;
  overflow-wrap: anywhere !important;
  word-break: break-word !important;
}
body.typora-export #write pre.md-fences + pre.md-fences {
  margin-top: 1.35rem !important;
}

/* 表格：圆角容器 + 表头轻强调 + 斑马纹 */
body.typora-export #write table {
  border-collapse: separate !important;
  border-spacing: 0;
  width: 100%;
  border: 1px solid ${hairline} !important;
  border-radius: var(--hk-r-lg);
  overflow: hidden;
  margin: 1rem 0 1.35rem !important;
  background: ${export_surface} !important;
}
body.typora-export #write table th {
  background: ${table_th_bg} !important;
  border-bottom: 1px solid ${hairline} !important;
  padding: 0.72rem 0.9rem !important;
  font-weight: 700;
}
body.typora-export #write table td {
  padding: 0.62rem 0.9rem !important;
  border-bottom: 1px solid ${hairline} !important;
  background: transparent !important;
}
body.typora-export #write table tbody tr:nth-child(even) td {
  background: ${code_bg} !important;
}
body.typora-export #write table tbody tr:last-child td {
  border-bottom: none !important;
}
body.typora-export #write table tbody tr:hover {
  background: transparent !important;
}

/* 分隔线：中间淡入的品牌色 */
body.typora-export #write hr {
  width: 100% !important;
  max-width: var(--hk-reading-measure);
  height: 1px !important;
  border: 0 !important;
  margin: 1.85rem auto !important;
  background: ${line} !important;
}

/* 行内代码：在白纸上更清晰一点 */
body.typora-export #write code,
body.typora-export #write tt {
  background: ${inline_code_bg} !important;
  border-radius: var(--hk-r-sm);
  padding: 0.12em 0.38em;
}

@media print {
  .typora-export * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  @page {
    /* 纸张尺寸、页边距和页眉页脚交给 Typora 的导出设置。 */
    background: ${paper_canvas_bg};
  }
  html, body, #write {
    background: ${paper_canvas_bg} !important;
    background-color: ${paper_canvas_bg} !important;
    background-image: none !important;
    box-shadow: none !important;
    border-radius: 0 !important;
  }
  #write {
    max-width: none !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 0.15rem !important;
  }
  #typora-sidebar { display: none; }
  #write pre.md-fences, #write blockquote,
  #write figure:not(:has(> table)), #write img, #write .md-alert,
  #write .md-math-block { break-inside: avoid; }
  /* Typora base.css 在 macOS 对整表设 page-break-inside:avoid。
     表格 figure 和 table 都要恢复按行分页，否则长表会留下大块空白。 */
  #write figure.table-figure, #write figure.md-table-fig,
  #write table {
    break-inside: auto !important;
    page-break-inside: auto !important;
  }
  #write figure.table-figure, #write figure.md-table-fig,
  #write table { overflow: visible !important; }
  #write table tr { break-inside: avoid; page-break-inside: avoid; }
  #write p, #write li { orphans: 3; widows: 3; }
}

/* 付费工艺必须压在共享编辑区与导出规则之后，避免同权重规则被覆盖。 */
${craft_extra}
${free_dark_extra}
""")


def check(css):
    """
    自检：把踩过的坑做成断言。

    ⚠️ 判据必须能分辨合法与违规 —— `html { font-size: 16px }` 是规范里
    唯一允许的 px 字号（根字号），而 `#write h1 { font-size: 30px }` 是违规。
    一刀切 grep "font-size.*px" 两者都报，等于没有区分力。所以按规则块解析，
    只豁免选择器为 html 的那一块。

    !important：全局禁止，但「导出压平」段豁免——Typora 注入规则要用它才能压住。
    """
    import re
    problems = []

    # 导出段：从注释标记到文件尾（或仅该段）允许 !important
    export_mark = "导出 / 打印"
    export_css = css.split(export_mark, 1)[1] if export_mark in css else ""
    head_css = css.split(export_mark, 1)[0] if export_mark in css else css

    n_imp = head_css.count("!important")
    if n_imp:
        problems.append(f"出现 !important × {n_imp}（目标 0：靠 #write 特异性覆盖即可；导出段除外）")

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
            "paper_canvas_bg": "var(--bg-color)" if not dark else t["color"]["bg"],
            "export_surface": "#f7f4ec" if not dark else t["color"].get("hover", "#2c2c2a"),
            "export_shine": (
                "rgba(255, 255, 255, 0.55)" if not dark else "rgba(255, 255, 255, 0.06)"
            ),
            "paper_write_extra": "/* paper off */",
        }

    use_grain = str(grain).strip() not in ("0", "0.0", "false", "")
    craft = bool((t.get("_craft") or {}).get("premium"))
    radial = (
        f"radial-gradient(140% 95% at 50% -8%, {highlight} 0%, "
        f"{mid} 48%, {shade} 100%)"
    )
    # 细边 + 轻阴影（Tailwind ring-1 / shadow-sm 的做法），不再用内阴影压暗纸边。
    if dark:
        shadow_css = (
            f"inset 0 1px 0 {hexa(ink, '0.04')}, "
            f"0 0 0 1px {hexa(ink, '0.06')}, "
            f"0 1px 2px {hexa(shadow, '0.30')}, "
            f"0 {'10px 30px -8px' if craft else '4px 14px -10px'} {hexa(shadow, '0.50' if craft else '0.40')}"
        )
    else:
        shadow_css = (
            f"0 0 0 1px {hexa(ink, '0.06')}, "
            f"0 1px 2px {hexa(shadow, '0.04')}"
        )
        if craft:
            shadow_css += f", 0 10px 30px -8px {hexa(shadow, '0.08')}"

    if use_grain and float(grain) > 0:
        noise = _PAPER_NOISE_TMPL.format(op=grain)
        bg = f"{noise}, {radial}"
    else:
        bg = radial
    return {
        "paper_gutter_bg": gutter,
        # 导出整页 = 纸面色（mid），PDF 与编辑区纸面一致，不用窗口外圈 gutter。
        # 纸面已是白色时，抬升面退到 sunken，否则代码块和表格会融进页面。
        "paper_canvas_bg": mid,
        "export_surface": (t["color"].get("sunken") or shade) if (not dark and highlight.lower() == mid.lower()) else highlight,
        "export_shine": (
            "rgba(255, 255, 255, 0.55)" if not dark else "rgba(255, 255, 255, 0.06)"
        ),
        "paper_write_extra": (
            f"background: {bg}; "
            f"border-radius: var(--hk-r-lg); "
            f"box-shadow: {shadow_css};"
        ),
    }


def _load_paid_craft():
    """付费工艺模块不进公开仓；缺席时 premium 构建优雅降级（无工艺段）。"""
    import sys
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    try:
        from craft_paid import apply_paid_craft_layout, craft_extra_css  # type: ignore
        return apply_paid_craft_layout, craft_extra_css
    except ImportError:
        def apply_paid_craft_layout(t):
            return t

        def craft_extra_css(*_a, **_k):
            return "/* paid craft module absent — public tree */\n"

        return apply_paid_craft_layout, craft_extra_css


apply_paid_craft_layout, craft_extra_css = _load_paid_craft()


FREE_DARK_EXTRA = """
/* 免费深色材质收口：标题降半档、表格只留横线、代码块做凹槽、图片细边。 */

:root { --hk-link-hover: #9ad2bd; }

#write h1,
#write h2 { font-weight: 650; }

#write table { border-left: 0; border-right: 0; }
#write table th,
#write table td { border-left: 0; border-right: 0; }

#write pre.md-fences {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

#write img,
#write .md-image img,
#write a img {
  border: 1px solid rgba(255, 255, 255, 0.08);
}
"""


def build(tokens, dark=False, banner_name=None, premium=False, flavor=""):
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
    fl = flavor or t.get("_meta", {}).get("theme_id", "")

    # 品牌色继续用于装饰；承载文字或状态信息时，按各套色板的真实底色
    # 自动做最小明度校正。付费变体也走同一规则，无需另写一份猜测色值。
    paper_shades = paper_colors(t, dark)
    footnote_surfaces = [composite_color(border, bg, "0.045") for bg in paper_shades]
    surfaces = list(dict.fromkeys([
        *paper_shades, *footnote_surfaces, c["bg"], c["bg_raised"],
        c["sidebar_bg"], c["hover"], c["sunken"],
    ]))
    inline_surfaces = [
        composite_color(c["code_bg_base"], bg, c["code_bg_alpha"])
        for bg in surfaces
    ]
    accent_ui = readable_color(accent, surfaces, 4.55, dark)
    semantic = {
        "color_link_readable": readable_color(c.get("link", accent), surfaces, 4.55, dark),
        "color_link_hover": readable_color(c.get("accent_deep", accent), surfaces, 4.55, dark),
        "color_accent_text": accent_ui,
        "color_muted_readable": readable_color(c["text_muted"], surfaces, 5.5, dark),
        "color_faint_readable": readable_color(c["text_faint"], surfaces, 4.55, dark),
        "color_control_border": readable_color(c.get("control_border", c["text_faint"]),
                                                surfaces, 3.05, dark),
        "color_code_text_readable": readable_color(c["code_text"], inline_surfaces, 4.55, dark),
        "color_on_accent": on_accent_color(accent_ui),
    }
    syntax_base = {
        "syn_comment": "#8f8e86" if not dark else "#7f7e74",
        "syn_keyword": "#8b5cb8" if not dark else "#c9a0e8",
        "syn_string":  "#3f7d54" if not dark else "#8fc9a0",
        "syn_number":  "#b06c2c" if not dark else "#e0a76a",
        "syn_def":     "#2f6f9f" if not dark else "#8ab8dd",
        "syn_error":   "#b80a18" if not dark else "#ff8b8b",
    }
    # 付费色板可给语法色定义各自的冷暖语气；可读性仍走统一校正。
    syntax_base.update((t.get("syntax") or {}).get("dark" if dark else "light", {}))
    syntax = {name: readable_color(value, [c["sunken"], c["bg"], paper_shades[0]], 4.55, dark)
              for name, value in syntax_base.items()}
    alert_base = {
        "note": "#0969da", "important": "#8250df", "warning": "#9a6700",
        "tip": "#1f883d", "caution": "#cf222e",
    } if not dark else {
        "note": "#6cb6ff", "important": "#c8a4ff", "warning": "#e3b341",
        "tip": "#56d364", "caution": "#ff7b72",
    }
    alert_alpha = {"note": "0.04", "important": "0.04", "warning": "0.05",
                   "tip": "0.04", "caution": "0.04"} if not dark else {
                       "note": "0.10", "important": "0.10", "warning": "0.12",
                       "tip": "0.10", "caution": "0.10",
                   }
    alerts = {}
    for kind, base_color in alert_base.items():
        tint = alert_alpha[kind]
        alert_surfaces = [composite_color(base_color, bg, tint) for bg in paper_shades]
        alerts[f"alert_{kind}_fg"] = readable_color(base_color, alert_surfaces, 4.55, dark)
        alerts[f"alert_{kind}_bg"] = hexa(base_color, tint)

    v.update({
        **semantic,
        **syntax,
        **alerts,
        "color_scheme":   "dark" if dark else "light",
        "mermaid_theme":  "night" if dark else "neutral",
        "hairline":       hexa(border, a["hairline"]),
        "line":           hexa(border, a["line"]),
        "divider":        hexa(border, a["divider"]),
        "code_bg":        hexa(border, "0.045"),
        "table_th_bg":    hexa(border, "0.03" if not dark else "0.05"),
        "shadow_soft":    shadow_soft,
        "shadow_mid":     hexa(shadow, "0.14" if not dark else "0.50"),
        "scrollbar":      hexa(border, "0.22"),
        "scrollbar_hover": hexa(border, "0.36"),
        "accent_wash":    hexa(accent, "0.16" if not dark else "0.24"),
        "accent_soft":    hexa(accent, "0.26" if not dark else "0.34"),
        "accent_border":  hexa(accent, "0.45"),
        "link_underline": hexa(semantic["color_link_readable"], "0.50"),
        "inline_code_bg": hexa(c["code_bg_base"], c["code_bg_alpha"]),
        "craft_extra": (
            craft_extra_css(accent, accent2, accent3, shadow_soft, dark, flavor=fl, paper=c["bg"])
            if premium else "/* free tier: no paid craft overlay */\n"
        ),
        "free_dark_extra": FREE_DARK_EXTRA if (dark and not premium) else "",
    })
    v.update(paper_surfaces(t, dark))

    css = CSS.substitute(v).strip("\n") + "\n"
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
    # 免费 V2 先生成；V2 Pro 使用独立 id/文件名，不覆盖免费默认。
    order = ["v2", "v1", "v2pro", "v3", "v4", "v5", "v6"]
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
        help="free=公开默认 V2；paid=六套独立高级主题；all=免费与本机付费档一起构建",
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
        if theme.get("syntax"):
            base["syntax"] = theme["syntax"]
        # 单套主题可覆盖形状（免费 V2 直角，付费档仍用全局圆角）
        if theme.get("shape"):
            base["shape"] = {**(base.get("shape") or {}), **theme["shape"]}
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
        theme_tier = theme.get("tier", "paid")

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
                    f" ({label}{', dark' if dark else ''} · {theme_tier}"
                    f" · skill {theme.get('id', '').upper()})"
                )
                css = build(
                    t,
                    dark=dark,
                    banner_name=banner,
                    premium=(theme_tier == "paid"),
                    flavor=theme.get("id", ""),
                )
                # 模板首行仍是 hekouwang — …，build() 只 replace 一次；再标套名
                out = os.path.join(out_dir, name)
                with open(out, "w", encoding="utf-8") as f:
                    f.write(css)
                written.append(name)

                tag = f"{theme['id']}/{preset_name}/{'dark' if dark else 'light'}"
                problems = check(css) + audit_css(css, tag)
                print(f"✅ [{tag}] {name}  ({len(css):,} 字节)")
                if theme_tier == "paid" and "Paid craft" not in css:
                    any_fail = True
                    print("   ⚠️  付费档应含 Paid craft 工艺段")
                if theme_tier == "free" and "Paid craft" in css:
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
        work_preset = (tokens.get("_presets") or {}).get("work") or {}
        work_type = work_preset.get("type") or tokens["type"]
        work_layout = work_preset.get("layout") or tokens["layout"]
        gutter = work_layout["measure_gutter"]
        paper_term = (
            f"calc(var(--hk-reading-measure) + 2 * {work_layout['write_pad_x']} + "
            f"{work_layout['wide_canvas_extra']})"
        )
        normal_width = (f"max-width: min({work_type['measure']}, {paper_term}, "
                        f"calc(100% - {gutter}));")
        wide_width = (f"max-width: min({work_layout['wide_measure']}, {paper_term}, "
                      f"calc(100% - {gutter}));")
        wide_query = f"@media (min-width: {work_layout['wide_breakpoint']})"
        if normal_width not in work_css:
            print("⚠️  分辨力失败：默认 CSS 未含普通窗口流体栏宽")
            any_fail = True
        if wide_query not in work_css or wide_width not in work_css:
            print("⚠️  分辨力失败：默认 CSS 未含宽窗口扩展栏宽")
            any_fail = True
        reading_default = f"--hk-reading-measure: {work_type['reading_measure']};"
        reading_width = "max-width: min(100%, var(--hk-reading-measure));"
        if reading_default not in work_css or reading_width not in work_css:
            print("⚠️  分辨力失败：宽纸面内的正文阅读列未限宽")
            any_fail = True
        if f"margin-top: {work_layout['write_margin_top']};" not in work_css:
            print("⚠️  分辨力失败：纸面顶部缺少与工具栏的间距")
            any_fail = True
        if "radial-gradient" not in work_css:
            print("⚠️  分辨力失败：浅色应含纸感径向渐变")
            any_fail = True
        if "radial-gradient" not in work_dark_css or "4px 14px -10px" not in work_dark_css:
            # 免费档深色阴影是 4px 14px -10px；付费 craft 会变成 10px 30px -8px
            print("⚠️  分辨力失败：深色应同步纸面卡片（径向 + 外阴影）")
            any_fail = True
        import re
        content_block = re.search(r"content \{([^}]*)\}", work_css)
        # 只取基础 #write 规则。平台增强（如 body.os-windows #write）可以在它之前，
        # 不能因此把「纸感是否画在阅读面」误判为失败。
        write_match = re.search(r"^#write\s*\{([^}]*)\}", work_css, re.M)
        write_chunk = write_match.group(1) if write_match else ""
        if content_block and "radial-gradient" in content_block.group(1):
            print("⚠️  分辨力失败：纸感不应铺在 content 全宽（会变成两侧假空白）")
            any_fail = True
        if "radial-gradient" not in write_chunk:
            print("⚠️  分辨力失败：纸感应画在 #write 上随栏宽伸缩")
            any_fail = True
        if "Paid craft" in work_css:
            print("⚠️  分辨力失败：免费默认不该含 Paid craft")
            any_fail = True
        # html 画布（即 PDF 整页底）= 纸面 mid #ffffff，不能退回 gutter #f8f8f5
        html_rule = re.search(r"^html\s*\{([^}]*)\}", work_css, re.M)
        if not html_rule or "background-color: #ffffff" not in html_rule.group(1):
            print("⚠️  分辨力失败：浅色 html 画布须为纸面色 #ffffff（PDF 与纸面同色）")
            any_fail = True
        # gutter 仍应在 content 上（编辑器两侧）；取 tokens 的纸面 gutter，
        # 不再写死某个灰值，避免换配色时断言与主题脱节。
        gutter_color = ((tokens.get("paper") or {}).get("gutter") or "#f8f8f9")
        if not content_block or gutter_color not in content_block.group(1):
            print("⚠️  分辨力失败：content 仍应铺 gutter（编辑器两侧）")
            any_fail = True
        # 导出：#write 也压成同色，禁止导出段再写 #ffffff
        export_at = work_css.find("导出 / 打印")
        export_chunk = work_css[export_at:] if export_at >= 0 else ""
        if export_at < 0 or "box-shadow: none !important" not in export_chunk:
            print("⚠️  分辨力失败：导出段须用 !important 拆掉 #write 纸感阴影")
            any_fail = True
        canvas_is_white = bool(html_rule and "background-color: #ffffff" in html_rule.group(1))
        if re.search(r"background(?:-color)?:\s*#ffffff\b", export_chunk) and not canvas_is_white:
            print("⚠️  分辨力失败：导出段用纯白但画布不是纯白（会与外圈底色打架出白柱）")
            any_fail = True
        if "background-size: 100% 2px" not in export_chunk:
            print("⚠️  分辨力失败：导出精装须含 H2 签名线")
            any_fail = True
        if "export_surface" in work_css and "${export_surface}" in work_css:
            print("⚠️  分辨力失败：export_surface 未被替换")
            any_fail = True
        if "border-radius: var(--hk-r-lg) !important" not in export_chunk:
            print("⚠️  分辨力失败：导出 fence/表格应有抬升圆角")
            any_fail = True
        print_at = work_css.find("\n@media print")
        print_block = work_css[print_at:print_at + 4000] if print_at >= 0 else ""
        if "#write table," in print_block and "break-inside: avoid" in print_block.split("#write table")[1][:80]:
            print("⚠️  分辨力失败：整表 break-inside:avoid 会制造 PDF 末页空白，应改为 tr")
            any_fail = True
        if "table tr" not in print_block or "break-inside: avoid" not in print_block:
            print("⚠️  分辨力失败：打印应保留 table tr { break-inside: avoid }")
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
