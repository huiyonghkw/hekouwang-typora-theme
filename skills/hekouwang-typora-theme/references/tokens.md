# 调参口径 — 改哪个文件

CSS 是生成物，**不要手改 `theme/*.css`**。但"改 tokens.json"这句话只对一半：

## 先看这张表（改错地方 = 静默失败）

| 你想改什么 | 改哪个文件 | 哪一段 |
|---|---|---|
| 行高、字号、段距、栏宽、断点 | `scripts/tokens.json` | `_presets.work.type` / `_presets.work.layout` |
| 配色（背景、文字、强调色、链接） | `scripts/palettes.json` | `themes[].color` |
| 深色配色 | `scripts/palettes.json` | `themes[].dark.color` |
| 纸感（纸面色、纸边、gutter、颗粒） | `scripts/palettes.json` | `themes[].paper` |
| 代码语法色 | `scripts/palettes.json` | `themes[].syntax` |
| 圆角 | `scripts/palettes.json` | `themes[].shape` |
| 透明度阶（边框/分隔线浓度） | `scripts/tokens.json` | `alpha` |
| 字体栈 | `scripts/tokens.json` | `font` |
| 付费六套（V1/V2 Pro/V3–V6）的配色 | `scripts/palettes.paid.json` | 同 `palettes.json` 结构 |

⚠️ **`tokens.json` 顶层没有 `color` / `paper` / `dark` / `type` / `layout` 段。**
这些段曾经存在过，但会被 palette 整体覆盖 —— 改了不生效，而构建却全绿、断言全过。
现在构建会**主动拒绝**这种结构（`check_source_layout`），一放回去就报错：

```
⚠️  真源边界未通过：tokens.json 顶层不该有 "color" 段 —— 它会被 palette 整体覆盖，
   改了不生效（静默失败）。配色真源在 scripts/palettes.json。
```

**两个文件各管一段，不要互相备份。** 曾经两处各存一份 color，纸面深色值已经漂成
两套（`#161b22` vs `#151816`），谁生效要看合并顺序——现在没有这个不确定性了。

## tokens.json 结构

```
_meta           主题名、slug、preset、presets_built（目前仅 work）
_presets.work   阅读指标唯一真源：type（字号/行高/间距）+ layout（栏宽/断点/内边距）
alpha           透明度阶（边框 / 分隔线 / 底纹取用）
font            字体栈
shape           圆角兜底值（免费档在 palettes.json 覆盖为直角，付费档由 craft_paid.py 覆盖）
```

合并顺序（`build.py` 的 `resolve_theme()`，全仓库唯一实现）：
基座 → palette 覆盖 → 阅读预设覆盖。**预设必须最后**，因为 `_presets.work` 的
type / layout 是"读文件时的默认真相"。

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

改 `scripts/tokens.json` 的 `_presets.work` —— **只有这一处**，顶层不再放副本：

| token | work 当前 | 管什么 |
|---|---|---|
| `type.body_lh` | `1.65` | 正文行高 |
| `type.para_gap` | `0.85rem` | 段间距 |
| `type.block_gap` | `1.1rem` | 引用/代码块/表格/图的上下间距 |
| `type.rule_gap` | `1.75rem` | 分隔线上下 |
| `type.list_gap` | `0.26rem` | 列表项间距 |
| `type.reading_measure` | `clamp(48rem, calc(100vw - 16rem), 96rem)` | 居中的正文阅读列，窄窗仍受可用宽度限制 |
| `type.measure` | `120em` | 普通窗口纸面绝对上限 |
| `layout.wide_breakpoint` | `1440px` | 技术画布开始增长的视口宽度 |
| `layout.wide_measure` | `120em` | 宽屏纸面绝对上限；`layout.wide_canvas_extra`（`6rem`）控制纸面比阅读列多出的宽度 |
| `type.small` / `type.table_size` | `0.875rem` | 小字 / 表格 14px |
| `type.fences_size` | `0.9375rem` | 代码块 15px；行内代码另用 `type.code_size` |
| `layout.write_margin_top` | `1rem` | 常规窗口纸面顶部间距，窄窗口为 `0.75rem` |
| `layout.write_pad_*` | 见文件 | 写作区内边距 |
| `layout.measure_gutter` | `4rem` | 栏宽流体时两侧预留的窗口底色 |

**纸感不在这里** —— `paper.*` 归 `palettes.json`（见上表）。想关掉纸感改
`palettes.json` 的 `themes[].paper.enabled`，不是 tokens.json。

### 宽屏补偿（2.0.1 起）

视口 ≥ `1800px` 时阅读列触顶 96rem（约 96 字/行），1.65 的行距撑不住，
构建器自动放宽：正文与引用 `line-height: 1.78`、段距 `1rem`；
表格与代码保持原密度，避免整页被拉松。这组值目前是**构建器内的硬编码**
（`build.py` 的宽屏补偿段），不在 token 里 —— 改它要动 `build.py`。

生成的主题将 `type.reading_measure` 写为 `--hk-reading-measure`。用户可在 Typora 主题目录的 `hekouwang.user.css` 中设置 `:root { --hk-reading-measure: 40rem; }`，无需重建主题；其他配色使用同名主题的 `.user.css`，或在 `base.user.css` 中统一覆盖。

## 纸感

浅色 / 深色都开：纸面画在 `#write` 上（**直角 + 轻阴影**，即 Tailwind `shadow-sm` 做法）。
**2.0.1 起去掉了 `ring-1` 的 1px 边框**——纸面不再被一圈细线圈住，只靠阴影浮起。
`content` / 侧栏 / 顶栏做壳层。

背景层取 Tailwind v3 色阶：浅色纸面 white / 50，纸边渐变只深一档，
外框与侧栏 100–200（主题色只染外框）；深色纸面 900、外框与侧栏 950（比纸面更暗）。
浅色 `paper.grain_opacity` 为 `0`；深色为 `0.015`（墨玉带极轻颗粒）。

## 字阶与字距

字号越大字距略收；满幅汉字标题不要用过猛的负 tracking。

## 配色：派生关系

改这些在 **`scripts/palettes.json`** 的 `themes[0]`（免费 V2）与
`themes[].dark`（深色）里。

| 基色 token | 浅色 | 深色 | 派生出 |
|---|---|---|---|
| `border_base` | `#141a17` 墨 | `#ffffff` 白 | 边框、分隔线、滚动条、代码块底 |
| `shadow_base` | `#141a17` | `#000000` | 阴影 |
| `code_bg_base` + `code_bg_alpha` | 墨 4% | 白 6% | 行内代码底 |
| `control_border` | `#858d87` | `#7f8781` | 复选框/输入框描边；可选，缺省回落 `text_faint`，按 3:1 校正 |
| `accent` | `#2e6f5e` | `#74b7a2` | 装饰强调、光标与选中背景；链接文字色、按钮前景色由构建器按背景对比度派生 |

**边框一律用基色叠透明度，不要用平铺灰。**

### 免费 V2 实测色值

浅色：纸面 `#ffffff`、纸边 `#fbfbf8`、gutter `#f8f8f5`、侧栏 `#fafaf7`；
正文 `#37413c`、标题 `#141a17`、强调绿 `#2e6f5e`。

深色（墨玉）：纸面 `#151816`、纸边 `#111411`、高光 `#1a1e1a`、
侧栏/gutter `#0c0e0d`（**比纸面更暗**，让纸面浮起来）、`sunken` `#101311`；
正文 `#c2c8c2`、标题 `#eef2ee`、强调绿 `#74b7a2`。
深色纸面带 1.5% 颗粒（`paper.dark.grain_opacity`）。

⚠️ 以前 `tokens.json` 里还存着另一套深色值（`#161b22` / `#1f242b` / `#0d1117`，
GitHub 冷灰系），但它会被 palette 整体覆盖 —— 从没生效过，却让人以为"深色底是那个"。
那段已删除，别再加回来。

免费 V2 的语法色不贴 WCAG 下限：浅色最低 5.27:1、深色注释 6.50:1（构建只保证 4.55）。改完配色跑 `python3 scripts/contrast_check.py --tier free --all`，它会读每套主题的 `syntax` 覆盖，与 build 写出的 CSS 一致（两边共用同一个 `resolve_theme()`）。

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

1. `python3 scripts/build.py`（断言不过别假装交付）
2. `python3 scripts/test_contrast_check.py`（7 个单测，含出货 CSS 的对比度）
3. `./scripts/install.sh`
4. **`Cmd+Q` 完全退出 Typora 再重开**
5. 若改了配色，用 `verify_render.py --vars ...` 确认 computed 值
6. 改了排版或配色后重拍 `docs/previews/` 的预览图（Typora 真机截图，
   不能用 headless 渲染替代）：

   ```bash
   ./scripts/shoot_previews.sh /tmp/shots   # 拍全套浅色 + 深色
   ```

   脚本会切主题、重启 Typora、逐套截图到 `/tmp/shots`，
   确认无误后再覆盖 `docs/previews/<slug>-<variant>.webp`。
   注意：预览图是 Typora **应用窗口**截图，含侧边栏与工具栏。

**改完先确认"改的地方真的生效了"**：构建全绿不代表你改的字段被用上了。
最直接的办法是看产物里有没有你的新值：

```bash
python3 scripts/build.py >/dev/null && grep -o '你的新值' theme/hekouwang.css | head -1
```

grep 不到 = 改错地方了（多半是改了 `tokens.json` 里已被 palette 覆盖的段）。
这个坑以前是**静默**的：改了不生效、构建却全绿、断言也全过。
现在顶层放错段会被 `check_source_layout` 直接拦下，但"改了个存在却没被用的字段"
仍需你用上面这行自查。
