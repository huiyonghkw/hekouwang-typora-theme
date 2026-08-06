# tokens.json — 调参口径

CSS 是生成物，**所有视觉调整都在这个文件里**。改完跑 `python3 scripts/build.py`。

## 结构

```
_meta           主题名、slug、默认 preset、presets_built
_presets.work   中文长文默认档（完整 type/layout/paper）
_presets.claude_read  Claude 对话档（另出 hekouwang-claude*.css）
color / alpha   浅色配色与透明度阶
type / layout   与 work 同步的「读文件时的默认真相」
paper           浅色纸感参数
font / shape    字体栈与圆角
dark            深色覆盖（只覆盖 color 和 alpha）
```

## 两套阅读档（必读）

| | work（默认 · Hekouwang） | claude_read（可选 · Hekouwang Claude） |
|---|---|---|
| 正文 | `1rem` | `0.875rem` |
| 行高 | `1.65`（**别低于 1.6**，中文会闷） | `1.42857`（对话栏） |
| 行宽 | `42em`（约 40–42 汉字） | `65ch` |
| 段距 | `0.78rem` | `0.625rem` |
| 纸感 | 浅色开 | 关 |

构建结束会断言：work CSS 含 `1.65` + `42em` + 径向纸感；claude CSS 含 `1.42857` + `65ch` 且 content 无径向。**断言过不了 = preset 没接上，别假装交付。**

## 紧凑度：调这几个就够

改 `_presets.work`（以及同步顶层 `type` / `layout`），不要只改一半：

| token | work 当前 | 管什么 |
|---|---|---|
| `type.body_lh` | `1.65` | 正文行高 |
| `type.para_gap` | `0.78rem` | 段间距 |
| `type.block_gap` | `1.1rem` | 引用/代码块/表格/图的上下间距 |
| `type.rule_gap` | `1.75rem` | 分隔线上下 |
| `type.list_gap` | `0.28rem` | 列表项间距 |
| `type.measure` | `42em` | 行宽 |
| `layout.write_pad_*` | 见文件 | 写作区内边距 |
| `paper.*` | 见文件 | 纸感；`enabled: false` 关闭 |

想量化对比，用 `verify_render.py --screenshot` 前后各出一张图，比较 `#write` 的 computed `line-height` / `max-width`。

## 纸感

浅色 / 深色 **work** 都开：纸面画在 `#write` 上（大圆角 + 外阴影），`content` 做 gutter。  
深色 gutter = 侧栏 `#262626`（比正文底更亮，与浅色关系相反）。  
`claude_read` 两套都不开纸感。  
`paper.grain_opacity` 默认 `0`。

## 字阶与字距

work 档标题比对话档更大（中文长标题要开篇重量）。字号越大字距略收；满幅汉字标题不要用过猛的负 tracking。

## 配色：派生关系

不要到处写死颜色，派生值由基色算出，这样换肤只改基色：

| 基色 token | 浅色 | 深色 | 派生出 |
|---|---|---|---|
| `border_base` | `#1f1e1d` 墨 | `#ffffff` 白 | 边框、分隔线、滚动条、代码块底 |
| `shadow_base` | `#1f1e1d` | `#000000` | 阴影（深色下 alpha 从 5% 提到 30%） |
| `code_bg_base` + `code_bg_alpha` | 品牌橙 11% | 白 5.5% | 行内代码底 |
| `accent` | `#d97757` | 同 | 链接、光标、勾选框、选中背景 |

**边框一律用基色叠透明度，不要用平铺灰。**

## 深色不是把浅色取反

`dark` 段的值全部采样自参照 App 的深色模式。两条不能靠推演的事实：

1. **深色下侧边栏 `#262626` 比正文区 `#1f1f1e` 更亮**，与浅色模式（侧边栏更暗）正好相反。
2. **行内代码底在深色下是中性白叠加，不是品牌橙**。用 `sample_colors.py --solve-alpha`
   验证过：白色三通道 alpha 解出 0.036/0.036/0.031（一致），橙色 0.043/0.091/0.123（不一致）。

深色字色阶（长文可读）：`text` 暖灰正文、`ink` 纯白给标题；`text_muted` / `text_soft` 略抬，避免灰阶塌成一团。

浅色壳层（侧栏 / gutter / html 顶栏）`#ebe8df`，纸面 `#fdfdfc`——两层故意分开，别把侧栏刷成纸白。深色 `sunken` `#141413`，fence 比纸面再沉一档。

## 题头署名 vs 正文引用

`#write h1 + blockquote` = lede / byline（去左边线、`type.small` + muted）。正文里的 `>` 仍走左边线。

## 表格

work：`th` 用 `--hk-ink` + 极淡 `table_th_bg`（浅 4% / 深 5%）；表宽跟正文栏（不破栏——负 margin 会让首列贴纸边像被裁）。`cell_pad` 约 `0.68rem 0.85rem`。H2 `mb` 约 `0.92rem`；开篇 `#write h1 ~ h2:first-of-type` 额外 `+0.55rem` 顶距。

## 改完必做

1. `python3 scripts/build.py` —— 自检 + work/claude 分辨力断言
2. `./scripts/install.sh`
3. **`Cmd+Q` 完全退出 Typora 再重开**
4. 若改了配色，用 `verify_render.py --vars ...` 确认 computed 值
5. 改了排版后更新 `docs/screenshot*.png`（必须在真 Typora 窗口截，headless 不算签收）
