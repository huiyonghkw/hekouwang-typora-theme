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
| 正文阅读列 | `clamp(48rem, calc(50vw + 3rem), 60rem)`；段落、标题、列表与引用随宽屏从 `48rem` 渐进至最多 `60rem`，在纸面内居中 |
| 纸面 / 技术画布 | 普通窗口 `52em`；视口从 `1440px` 起平滑增长，最高 `80em`；两侧至少共留 `4rem` |
| 段距 | `0.78rem` |
| 小字 / 表格 / 代码块 | `14px` / `14px` / `15px`（配置使用 rem） |
| 纸感 | 浅 / 深都开，画在 `#write` |

构建结束会断言：CSS 含 `1.65`、正文阅读列、普通纸面与宽屏技术画布规则，以及 `#write` 上的径向纸感。构建也对每份生成 CSS 自动审计文字、链接、代码、按钮和任务框对比度：公开仓的免费浅 / 深两套，本机有付费色板时再覆盖 12 套付费 CSS，共 14 套。**断言过不了别假装交付。**

## 紧凑度：调这几个就够

改 `_presets.work`（以及同步顶层 `type` / `layout`），不要只改一半：

| token | work 当前 | 管什么 |
|---|---|---|
| `type.body_lh` | `1.65` | 正文行高 |
| `type.para_gap` | `0.78rem` | 段间距 |
| `type.block_gap` | `1.1rem` | 引用/代码块/表格/图的上下间距 |
| `type.rule_gap` | `1.75rem` | 分隔线上下 |
| `type.list_gap` | `0.2rem` | 列表项间距 |
| `type.reading_measure` | `clamp(48rem, calc(50vw + 3rem), 60rem)` | 居中的正文阅读列，窄窗仍受可用宽度限制 |
| `type.measure` | `52em` | 普通窗口纸面上限 |
| `layout.wide_breakpoint` | `1440px` | 技术画布开始增长的视口宽度 |
| `layout.wide_measure` | `80em` | 宽屏技术画布上限 |
| `type.small` / `type.table_size` | `0.875rem` | 小字 / 表格 14px |
| `type.fences_size` | `0.9375rem` | 代码块 15px；行内代码另用 `type.code_size` |
| `layout.write_margin_top` | `1rem` | 常规窗口纸面顶部间距，窄窗口为 `0.75rem` |
| `layout.write_pad_*` | 见文件 | 写作区内边距 |
| `paper.*` | 见文件 | 纸感；`enabled: false` 关闭 |

生成的主题将 `type.reading_measure` 写为 `--hk-reading-measure`。用户可在 Typora 主题目录的 `hekouwang.user.css` 中设置 `:root { --hk-reading-measure: 40rem; }`，无需重建主题；其他配色使用同名主题的 `.user.css`，或在 `base.user.css` 中统一覆盖。

## 纸感

浅色 / 深色都开：纸面画在 `#write` 上（大圆角 + 外阴影），`content` / 侧栏 / 顶栏做壳层。  
深色 gutter = 侧栏 `#262626`（比正文底更亮，与浅色关系相反）。  
`paper.grain_opacity` 默认 `0`。

## 字阶与字距

字号越大字距略收；满幅汉字标题不要用过猛的负 tracking。

## 配色：派生关系

| 基色 token | 浅色 | 深色 | 派生出 |
|---|---|---|---|
| `border_base` | `#1f1e1d` 墨 | `#ffffff` 白 | 边框、分隔线、滚动条、代码块底 |
| `shadow_base` | `#1f1e1d` | `#000000` | 阴影（深色下 alpha 从 5% 提到 30%） |
| `code_bg_base` + `code_bg_alpha` | 品牌橙 11% | 白 5.5% | 行内代码底 |
| `accent` | `#d97757` | 同 | 装饰强调、光标与选中背景；链接文字色、按钮前景色由构建器按背景对比度派生 |

**边框一律用基色叠透明度，不要用平铺灰。**

浅色壳层（侧栏 / gutter / html 顶栏）`#ebe8df`，纸面 `#fdfdfc`——两层故意分开。深色 `sunken` `#141413`，fence 比纸面再沉一档。

## 深色不是把浅色取反

1. **深色下侧边栏 `#262626` 比正文区 `#1f1f1e` 更亮**。
2. **行内代码底在深色下是中性白叠加，不是品牌橙**。

深色字色阶：`text` 暖灰正文、`ink` 纯白给标题；`text_muted` / `text_soft` 略抬。

## 题头署名 vs 正文引用

`#write h1 + blockquote` = lede / byline（去左边线、`type.small` + muted）。正文里的 `>` 仍走左边线。

## 表格

`th` 用 `--hk-ink` + 极淡 `table_th_bg`（浅 4% / 深 5%）；六列及以下的表格填满响应式正文阅读列，超过 6 列的表使用技术画布，只在自身容器中横向展开，不推宽页面。单元格字体 `0.875rem`、`cell_pad` 约 `0.68rem 0.85rem`。开篇 `#write h1 ~ h2:first-of-type` 额外 `+0.55rem` 顶距。

源码模式单独限制 CodeMirror 行宽；专注模式会弱化非当前块的图片、任务框、图表和代码，并在系统要求减少动效时关闭相关过渡。句中 Markdown 图片保留行内流动，`figure` 图片仍为块级。导出/打印按 Typora 的设置使用纸张、页边距与页眉页脚；长代码行折行，长表按行跨页。以上仍需用 `demo/验收样张.md` 在 Typora 中实测，构建检查不能代替真实编辑和多页 PDF 验收。

## 改完必做

1. `python3 scripts/build.py`
2. `./scripts/install.sh`
3. **`Cmd+Q` 完全退出 Typora 再重开**
4. 若改了配色，用 `verify_render.py --vars ...` 确认 computed 值
5. 改了排版后用 `demo/主题展示样张.md` 在 Typora 中重拍 `docs/previews/` 对应的浅色、深色截图，并核对侧栏与纸面均属于当前主题
