# tokens.json — 调参口径

CSS 是生成物，**所有视觉调整都在这个文件里**。改完跑 `python3 scripts/build.py`。

## 结构

```
_meta      主题名与 slug（slug 决定 CSS 文件名和 Typora 菜单显示名）
color      浅色配色
alpha      边框/分隔线的透明度阶
type       字号、行高、间距、标题字阶
font       三级字体栈
shape      圆角
layout     写作区内边距
dark       深色覆盖（只覆盖 color 和 alpha 两组）
```

## 紧凑度：调这几个就够

| token | 当前 | 管什么 |
|---|---|---|
| `type.body_lh` | `1.62` | 正文行高。**别低于 1.6**，中文会开始发闷 |
| `type.para_gap` | `0.78rem` | 段间距 |
| `type.block_gap` | `0.9rem` | 引用/代码块/表格/图的上下间距 |
| `type.rule_gap` | `1.5rem` | 分隔线上下 |
| `type.list_gap` | `0.16rem` | 列表项间距 |
| `type.cell_pad` | `0.42rem 0.7rem` | 表格单元格内边距 |
| `type.h*.mt` / `.mb` | 见文件 | 各级标题上下外边距 |
| `layout.write_pad_top` | `1.8rem` | 顶部留白 |

实测参考：从初版收紧两轮后，同一份文档高度减少 **18%**。想量化对比，用
`verify_render.py --screenshot` 前后各出一张图，比较内容底边 y 坐标。

## 字阶与字距

**大字号收紧字距是「精致感」的主要来源**，字号越大收得越多，小字号回到 0：

```
h1 1.8125rem  ls -0.022em
h2 1.375rem   ls -0.018em
h3 1.1563rem  ls -0.012em
h4 1.0625rem  ls -0.006em
h5/h6         ls 0
正文          ls 0
```

## 配色：派生关系

不要到处写死颜色，派生值由基色算出，这样换肤只改基色：

| 基色 token | 浅色 | 深色 | 派生出 |
|---|---|---|---|
| `border_base` | `#1f1e1d` 墨 | `#ffffff` 白 | 边框、分隔线、滚动条、代码块底 |
| `shadow_base` | `#1f1e1d` | `#000000` | 阴影（深色下 alpha 从 5% 提到 30%） |
| `code_bg_base` + `code_bg_alpha` | 品牌橙 11% | 白 5.5% | 行内代码底 |
| `accent` | `#d97757` | 同 | 链接、光标、勾选框、选中背景 |

**边框一律用基色叠透明度，不要用平铺灰。** 暖底上压一条 `#ccc` 会显脏显死；
`rgba(31,30,29,.14)` 才跟页面同色温。

## 深色不是把浅色取反

`dark` 段的值全部采样自参照 App 的深色模式。两条不能靠推演的事实：

1. **深色下侧边栏 `#262626` 比正文区 `#1f1f1e` 更亮**，与浅色模式（侧边栏更暗）正好相反。
2. **行内代码底在深色下是中性白叠加，不是品牌橙**。用 `sample_colors.py --solve-alpha`
   验证过：白色三通道 alpha 解出 0.036/0.036/0.031（一致），橙色 0.043/0.091/0.123（不一致）。

语法高亮色在深色下也必须整体提亮，否则在 `#1f1f1e` 上会糊成一团（见 build.py 里的三元表达式）。

## 改完必做

1. `python3 scripts/build.py` —— 看自检是否通过（0 个 `!important`、0 处 px 字号）
2. `./scripts/install.sh`
3. **`Cmd+Q` 完全退出 Typora 再重开**（切主题不重载 CSS）
4. 如果改了配色关系，用 `verify_render.py --vars ...` 确认 computed 值真的是你写的那个
