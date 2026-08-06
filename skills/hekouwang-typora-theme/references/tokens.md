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
| 行宽 | `52em` → CSS：`min(52em, calc(100% − gutter))` |
| 段距 | `0.78rem` |
| 纸感 | 浅 / 深都开，画在 `#write` |

构建结束会断言：CSS 含 `1.65` + `min(52em,` + `#write` 上径向纸感。**断言过不了别假装交付。**

## 紧凑度：调这几个就够

改 `_presets.work`（以及同步顶层 `type` / `layout`），不要只改一半：

| token | work 当前 | 管什么 |
|---|---|---|
| `type.body_lh` | `1.65` | 正文行高 |
| `type.para_gap` | `0.78rem` | 段间距 |
| `type.block_gap` | `1.1rem` | 引用/代码块/表格/图的上下间距 |
| `type.rule_gap` | `1.75rem` | 分隔线上下 |
| `type.list_gap` | `0.2rem` | 列表项间距 |
| `type.measure` | `52em` | 行宽上限 |
| `layout.write_pad_*` | 见文件 | 写作区内边距 |
| `paper.*` | 见文件 | 纸感；`enabled: false` 关闭 |

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
| `accent` | `#d97757` | 同 | 链接、光标、勾选框、选中背景 |

**边框一律用基色叠透明度，不要用平铺灰。**

浅色壳层（侧栏 / gutter / html 顶栏）`#ebe8df`，纸面 `#fdfdfc`——两层故意分开。深色 `sunken` `#141413`，fence 比纸面再沉一档。

## 深色不是把浅色取反

1. **深色下侧边栏 `#262626` 比正文区 `#1f1f1e` 更亮**。
2. **行内代码底在深色下是中性白叠加，不是品牌橙**。

深色字色阶：`text` 暖灰正文、`ink` 纯白给标题；`text_muted` / `text_soft` 略抬。

## 题头署名 vs 正文引用

`#write h1 + blockquote` = lede / byline（去左边线、`type.small` + muted）。正文里的 `>` 仍走左边线。

## 表格

`th` 用 `--hk-ink` + 极淡 `table_th_bg`（浅 4% / 深 5%）；表宽跟正文栏（不破栏）。`cell_pad` 约 `0.68rem 0.85rem`。开篇 `#write h1 ~ h2:first-of-type` 额外 `+0.55rem` 顶距。

## 改完必做

1. `python3 scripts/build.py`
2. `./scripts/install.sh`
3. **`Cmd+Q` 完全退出 Typora 再重开**
4. 若改了配色，用 `verify_render.py --vars ...` 确认 computed 值
5. 改了排版后更新 `docs/screenshot*.png`（必须在真 Typora 窗口截）
