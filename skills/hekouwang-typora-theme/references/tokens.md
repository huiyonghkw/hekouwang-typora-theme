# tokens.json — 调参口径

CSS 是生成物，**所有视觉调整都在这个文件里**。改完跑 `python3 scripts/build.py`。

## 结构

```
_meta           主题名、slug、preset、presets_built（目前仅 work）
_presets.work   中文长文（完整 type/layout/paper）→ hekouwang.css / hekouwang-dark.css
color / alpha   浅色配色与透明度阶
type / layout   与 work 同步的「读文件时的默认真相」
paper           纸感参数（浅 / 深）
font / shape    字体栈与圆角
dark            深色覆盖（只覆盖 color 和 alpha）
```

## 阅读指标（Hekouwang / Hekouwang Dark）

| Token | 值 |
|---|---|
| 正文 | `1rem` |
| 行高 | `1.65`（**别低于 1.6**） |
| 正文阅读列 | `clamp(48rem, calc(100vw - 16rem), 96rem)`；段落、标题、列表与引用随窗口伸缩，最宽 `96rem`，在纸面内居中 |
| 纸面 / 技术画布 | 阅读列 + 两侧内边距 + `6rem`，两侧各留约 `3rem` 窗口底色；上限 `120em`，两侧至少共留 `4rem` |
| 段距 | `0.85rem` |
| 小字 / 表格 / 代码块 | `14px` / `14px` / `15px`（配置使用 rem） |
| 纸感 | 浅 / 深都开，画在 `#write` |

构建结束会断言：CSS 含 `1.65`、正文阅读列、普通纸面与宽屏技术画布规则，以及 `#write` 上的径向纸感。构建也对每份生成 CSS 自动审计文字、链接、代码、按钮和任务框对比度：公开仓的免费浅 / 深两套，本机有付费色板时再覆盖 12 套付费 CSS，共 14 套。**断言过不了别假装交付。**

## 紧凑度：调这几个就够

改 `_presets.work`（以及同步顶层 `type` / `layout`），不要只改一半：

| token | work 当前 | 管什么 |
|---|---|---|
| `type.body_lh` | `1.65` | 正文行高 |
| `type.para_gap` | `0.85rem` | 段间距 |
| `type.block_gap` | `1.1rem` | 引用/代码块/表格/图的上下间距 |
| `type.rule_gap` | `1.75rem` | 分隔线上下 |
| `type.list_gap` | `0.2rem` | 列表项间距 |
| `type.reading_measure` | `clamp(48rem, calc(100vw - 16rem), 96rem)` | 居中的正文阅读列，窄窗仍受可用宽度限制 |
| `type.measure` | `120em` | 普通窗口纸面绝对上限 |
| `layout.wide_breakpoint` | `1440px` | 技术画布开始增长的视口宽度 |
| `layout.wide_measure` | `120em` | 宽屏纸面绝对上限；`layout.wide_canvas_extra`（`6rem`）控制纸面比阅读列多出的宽度 |
| `type.small` / `type.table_size` | `0.875rem` | 小字 / 表格 14px |
| `type.fences_size` | `0.9375rem` | 代码块 15px；行内代码另用 `type.code_size` |
| `layout.write_margin_top` | `1rem` | 常规窗口纸面顶部间距，窄窗口为 `0.75rem` |
| `layout.write_pad_*` | 见文件 | 写作区内边距 |
| `paper.*` | 见文件 | 纸感；`enabled: false` 关闭 |

生成的主题将 `type.reading_measure` 写为 `--hk-reading-measure`。用户可在 Typora 主题目录的 `hekouwang.user.css` 中设置 `:root { --hk-reading-measure: 40rem; }`，无需重建主题；其他配色使用同名主题的 `.user.css`，或在 `base.user.css` 中统一覆盖。

## 纸感

浅色 / 深色都开：纸面画在 `#write` 上（大圆角 + 1px 细边 + 轻阴影，即 Tailwind `ring-1` + `shadow-sm` 做法），`content` / 侧栏 / 顶栏做壳层。  
背景层取 Tailwind v3 色阶：纸面 white / 50，纸边渐变只深一档，外框与侧栏 100–200（主题色只染外框）；深色纸面 900、外框与侧栏 950（比纸面更暗）。  
`paper.grain_opacity` 默认 `0`。

## 字阶与字距

字号越大字距略收；满幅汉字标题不要用过猛的负 tracking。

## 配色：派生关系

| 基色 token | 浅色 | 深色 | 派生出 |
|---|---|---|---|
| `border_base` | `#141a17` 墨 | `#ffffff` 白 | 边框、分隔线、滚动条、代码块底 |
| `shadow_base` | `#141a17` | `#000000` | 阴影 |
| `code_bg_base` + `code_bg_alpha` | 墨 4% | 白 6% | 行内代码底 |
| `control_border` | `#858d87` | `#7f8781` | 复选框/输入框描边；可选，缺省回落 `text_faint`，按 3:1 校正 |
| `accent` | `#2e6f5e` | `#74b7a2` | 装饰强调、光标与选中背景；链接文字色、按钮前景色由构建器按背景对比度派生 |

**边框一律用基色叠透明度，不要用平铺灰。**

免费 V2 的语法色不贴 WCAG 下限：浅色最低 5.27:1、深色注释 6.50:1（构建只保证 4.55）。改完配色跑 `python3 scripts/contrast_check.py --tier free --all`，它现在会读每套主题的 `syntax` 覆盖，与 build 写出的 CSS 一致。

浅色壳层：侧栏 `#fafaf7`、gutter `#f8f8f5`、纸面 `#ffffff`——三层故意分开，纸边 `#fbfbf8`。深色侧栏 / gutter `#0c0e0d`、纸面 `#151816`，`sunken` `#101311`，fence 比纸面再沉一档。

## 深色不是把浅色取反

1. **深色明暗关系要单独定**：外框 / 侧栏 `#0c0e0d` 比纸面 `#151816` 更暗，让纸面浮起来。
2. **行内代码底在深色下是中性白叠加，不是品牌绿**。

深色字色阶收成四级：`ink` `#eef2ee`、`text` `#c2c8c2`、`soft` `#a9b1ab`、`muted` `#9aa39c`、`faint` `#878f88`；正文不用纯白。**soft 与 muted 不能同值**，否则斜体、图注、元数据会塌成一层。链接 hover 走 `accent_deep`，下划线 0.50。

## 题头署名 vs 正文引用

`#write h1 + blockquote` = lede / byline（去左边线、`type.small` + muted）。正文里的 `>` 仍走左边线。

## 表格

`th` 用 `--hk-ink` + 极淡 `table_th_bg`（浅 3% / 深 5%）；1–3 列小表最多 `48rem` 并左对齐正文，4–9 列填满阅读列，10+ 列使用技术画布、只留横向分隔线。单元格字体 `0.875rem`、`cell_pad` 约 `0.68rem 0.85rem`。开篇 `#write h1 ~ h2:first-of-type` 额外 `+0.55rem` 顶距。

源码模式单独限制 CodeMirror 行宽；专注模式会弱化非当前块的图片、任务框、图表和代码，并在系统要求减少动效时关闭相关过渡。句中 Markdown 图片保留行内流动，`figure` 图片仍为块级。导出/打印按 Typora 的设置使用纸张、页边距与页眉页脚；长代码行折行，长表按行跨页。以上仍需用 `demo/验收样张.md` 在 Typora 中实测，构建检查不能代替真实编辑和多页 PDF 验收。

## 改完必做

1. `python3 scripts/build.py`
2. `./scripts/install.sh`
3. **`Cmd+Q` 完全退出 Typora 再重开**
4. 若改了配色，用 `verify_render.py --vars ...` 确认 computed 值
5. 改了排版后用 `demo/主题展示样张.md` 在 Typora 中重拍 `docs/previews/` 对应的浅色、深色截图，并核对侧栏与纸面均属于当前主题
