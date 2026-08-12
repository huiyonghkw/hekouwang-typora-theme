# hekouwang

**体验站：** [huiyonghkw.github.io/hekouwang-typora-theme](https://huiyonghkw.github.io/hekouwang-typora-theme/)

给「一天要盯着 Markdown 好几个小时」的人用的 Typora 主题——按**中文长文**来排，不是按聊天气泡来排。

配色对齐内容工厂 **hekouwang-content-skill 六套视觉（V1–V6）**；阅读指标全套共用：`1rem` · `1.65` · `52em` · 纸感卡片。

## 免费 / 付费

| 档 | 主题菜单 | 说明 |
|---|---|---|
| **免费 · MIT** | **Hekouwang** / **Hekouwang Dark** | = skill **V2 编辑**（米白 / 米黑）。Gallery 入口也是这一档。公开仓只发这一档。 |
| **付费包 · ¥9.9** | **Hekouwang V1…V6**（各含 Dark） | skill 矩阵里的科技 / 财经 / 玻璃 / 紫 / 焰彩（+ 与免费同文件的 V2）· 浅+深；**色板与工艺不进公开仓**，只随 zip 私发 |

**怎么买：** 落地页购买区（微信/支付宝 · 微信 `hekouwang`，备注「Typora主题」）→ 我私发 zip → 按落地页 [装付费包](https://huiyonghkw.github.io/hekouwang-typora-theme/#unlock) 一键装进 Typora。

→ [huiyonghkw.github.io/hekouwang-typora-theme/#buy](https://huiyonghkw.github.io/hekouwang-typora-theme/#buy)

免费色板在 `scripts/palettes.json`；付费色板不进公开仓。阅读指标在 `scripts/tokens.json`。公开仓重建：`python3 scripts/build.py`（默认只出免费档）。

*[English](README.md)*

## 30 秒验收

```bash
python3 scripts/build.py                    # 生成浅色+深色 CSS
./scripts/install.sh                        # 装进 Typora（自动备份）
python3 scripts/verify_render.py --css theme/hekouwang.css --fonts "Hekouwang Sans,Hekouwang Sans Fb" --vars bg-color,text-color
```

联系付费包：**微信 hekouwang**（备注「Typora主题」）· GitHub **@huiyonghkw**

---

## 免费档 · 真机（V2 编辑）

公开仓 / Gallery 就是这一档：**Hekouwang** / **Hekouwang Dark**。同一套阅读指标，暖米白纸感。

![免费 V2 · 中文验收样张](docs/screenshot-zh.png)

*免费 V2 · `demo/验收样张.md` — 题头、阅读指标、中英混排。*

![免费 V2 · 英文样张](docs/screenshot.png)

*免费 V2 · `demo/acceptance-sample.md` — 同一指标，对照西文节奏。*

![免费 V2 · 代码块](docs/screenshot-fences-zh.png)

*免费 V2 · 连续 fences — 语法色克制，块与块之间有呼吸。*

![免费 V2 · 整窗](docs/screenshot-window.png)

*免费 V2 · 侧栏 / 文件树 / 纸感编辑区同屏。*

---

## 付费包 · 真机（V1 / V3–V6）

下面都是 Typora 真机截图（`demo/验收样张.md`）。**指标与免费档相同**（`1rem` · `1.65` · `52em` · 纸感），差在 skill 配色 + 付费阅读工艺。V2 与免费档同一套文件，这里不再重复。

| Skill | 一眼差在哪 | 浅色 | 深色 |
|---|---|---|---|
| **V1 科技** | 冷调绿紫 · 文档站感 | [V1.png](docs/V1.png) | [V1-Dark.png](docs/V1-Dark.png) |
| **V3 财经** | Material 蓝 · 数据感 | [V3.png](docs/V3.png) | [V3-Dark.jpeg](docs/V3-Dark.jpeg) |
| **V4 玻璃** | 雾白 / 近黑 · 轻量 | [V4.png](docs/V4.png) | [V4-Dark.png](docs/V4-Dark.png) |
| **V5 紫 HUD** | **紫 × 青**（链接/引用走青） | [V5.png](docs/V5.png) | [V5-Dark.jpeg](docs/V5-Dark.jpeg) |
| **V6 焰彩** | **紫 × 橙 × 粉**（H1 焰彩渐变字） | [V6.png](docs/V6.png) | [V6-Dark.jpeg](docs/V6-Dark.jpeg) |

### V1 科技

![V1 科技 · 浅色](docs/V1.png)

*Hekouwang V1 — 冷亮底，绿紫语义。*

![V1 科技 · 深色](docs/V1-Dark.png)

*Hekouwang V1 Dark — 近黑壳 + 青绿强调。*

### V3 财经

![V3 财经 · 浅色](docs/V3.png)

*Hekouwang V3 — Material 蓝，偏报表/看板阅读。*

![V3 财经 · 深色](docs/V3-Dark.jpeg)

*Hekouwang V3 Dark。*

### V4 玻璃

![V4 玻璃 · 浅色](docs/V4.png)

*Hekouwang V4 — 雾白纸面，轻量系统蓝。*

![V4 玻璃 · 深色](docs/V4-Dark.png)

*Hekouwang V4 Dark。*

### V5 紫 · 发布会 HUD（紫 × 青）

跟 V6 都偏紫，但副色是 **青** `#0ea5a0` / `#6fe0e0`：链接、引用边、H2 底线走青，不是焰彩。

![V5 紫 HUD · 浅色](docs/V5.png)

*Hekouwang V5 — 淡紫壳 + 白纸卡；链接为青绿。*

![V5 紫 HUD · 深色](docs/V5-Dark.jpeg)

*Hekouwang V5 Dark — 近黑紫底 `#0a0716`，青作数据点缀。*

### V6 焰彩（紫 × 橙 × 粉）

skill 焰彩三停靠：主紫 + **焰橙** `#ff8a3d` + **焰粉** `#ff4f8b`。H1 渐变字、H2/分割线三色，链接走橙——和 V5 的「青 HUD」一眼能分。

![V6 焰彩 · 浅色](docs/V6.png)

*Hekouwang V6 — 白纸卡；标题紫→橙→粉。*

![V6 焰彩 · 深色](docs/V6-Dark.jpeg)

*Hekouwang V6 Dark — 深紫底 `#170a30`，焰彩点缀。*

---

## 设计取向

- **默认服务中文长文。** 汉字密、方块字，需要 ≥1.6 的行高和大约 40–50 字的行宽。
- **不用高饱和强调色。** 行内代码用低饱和色，一段里七八个 `` `code` `` 仍读得像文字。
- **层级靠字号、字重、间距，不靠彩色竖条。**
- **边框用墨色叠透明度**，不用平铺灰。
- **纸感画在 `#write` 上**（浅 / 深都有）：径向、大圆角、外阴影；侧栏 / gutter / 顶栏是更深一档的壳层。
- **导出 PDF 整页一色 + 精装块。** 画布跟 gutter 同色（浅色 `#ebe8df` / 深色跟正文底），禁止内容区单独铺纯白（会出「外圈底色 + 中间白柱」）。导出时：H2 签名线、抬升 fence、圆角表、渐变 HR；**V1–V6 浅/深十二套共用同一套导出精装**（配色跟各皮肤走）。
- **付费六套皮肤 = skill 十二格里除免费 V2 外的部分**（每套黑/白两极）；公开仓 / Gallery 只发 V2。气质与公众号/小红书产出一致。

### 导出 PDF

Typora PDF = 独立 HTML（`body.typora-export`）再 `printToPDF`。本主题对导出做了两件事：

1. **压平纸感浮卡片**：`#write` 去圆角/外阴影，画布与正文同色（`@page` 也同色）。
2. **精装块级**：H2 底部品牌色签名线（⛔ 不用左边彩色竖条）、标题 fence 抬升为略亮于画布的纸面卡、表格圆角容器 + 浅表头 + 斑马纹、分隔线中间淡入。

改主题 CSS 后必须 **Cmd+Q 完全退出再重开**，否则导出仍是旧样式。

| 套 | 浅色画布 | 深色画布 |
|---|---|---|
| V2 免费 | `#ebe8df` | `#1f1f1e` |
| V1 / V3–V6 | 各皮肤 gutter | 各皮肤正文底 |

![浅色 PDF / 纸感验收](docs/screenshot-pdf-light.png)

*浅色 · `demo/验收样张.md` — 画布米色、阅读面纸感，无「外圈底色 + 中间白柱」。*

---

### 阅读指标

| Token | 值 | 用意 |
|---|---|---|
| `body_size` | `1rem` | 长时间写作不累 |
| `body_lh` | `1.65` | 中文密度需要更大行高 |
| `measure` | `52em` | 流体：`min(52em, calc(100% − gutter))` |
| `para_gap` | `0.78rem` | 段距紧凑但不糊成墙 |

### 六套菜单名

| Skill 格 | Typora 菜单 | 辨识 |
|---|---|---|
| V1 科技 | Hekouwang V1 / V1 Dark | 冷调绿紫 |
| V2 编辑（免费） | Hekouwang / Hekouwang Dark | 暖米白 / 米黑 |
| V3 财经 | Hekouwang V3 / V3 Dark | Material 蓝 |
| V4 玻璃 | Hekouwang V4 / V4 Dark | 雾白 / 近黑 |
| V5 紫 HUD | Hekouwang V5 / V5 Dark | **紫 × 青** |
| V6 焰彩 | Hekouwang V6 / V6 Dark | **紫 × 橙 × 粉** |

---

## 中英混排

Anthropic Sans 实测 **581 字符、CJK 汉字 0 个**（连中文标点都没有）。中文必然走系统字体（macOS 上是苹方）。主题用「西文字体 + 系统中文」配对，**不打包中文字体**。

| 层 | 字体 | 是否随包分发 |
|---|---|---|
| 1 | Anthropic Sans（仅当你系统里已有） | 否 —— 专有字体 |
| 2 | **Inter** 可变，latin 子集，约 100 KB | 是 —— SIL OFL |
| 3 | 系统界面字体 | — |

绝大多数人看到的是第 2 层，截图也按第 2 层校对。

## 安装（免费 V2）

```bash
git clone https://github.com/huiyonghkw/hekouwang-typora-theme.git
cd hekouwang-typora-theme
./scripts/install.sh
```

或手动把 `theme/hekouwang.css`、`theme/hekouwang-dark.css` 和 `theme/hekouwang/` 目录复制进 Typora 主题文件夹（偏好设置 → 打开主题文件夹）。

然后 **完全退出 Typora 再重开** —— 切换主题不会重载已改过的 CSS。在「主题」菜单选 **Hekouwang** 或 **Hekouwang Dark**。

### Windows 安装与阅读兼容

主题从构建层支持 Typora 的 `body.os-windows`：西文优先随包的 Inter，中文优先「微软雅黑 UI / 微软雅黑」，代码优先 Cascadia Mono / Cascadia Code / Consolas；不会分发体积大且授权边界复杂的 CJK 字体。

在 PowerShell 中运行：

```powershell
git clone https://github.com/huiyonghkw/hekouwang-typora-theme.git
cd hekouwang-typora-theme
.\scripts\install-windows.ps1
```

若执行策略阻止本地脚本，可仅对这次安装运行 `powershell -ExecutionPolicy Bypass -File .\scripts\install-windows.ps1`，不会修改系统执行策略。

安装器默认写入 `%APPDATA%\Typora\themes`，会把同名旧 CSS 备份到 `.hekouwang-backups` 子目录（不会污染 Typora 主题菜单）。若你的 Typora 主题目录不在默认位置：

```powershell
.\scripts\install-windows.ps1 -ThemeDir 'D:\your\Typora\themes'
```

完全退出并重开 Typora 后选择 **Hekouwang** 或 **Hekouwang Dark**。Windows 真机发布前，必须逐项验收编辑/源码/专注模式、中英混排、代码/表格/Mermaid，以及 PDF、HTML、图片导出；Chrome 预检不能替代 Typora 真机。

### 付费包（V1 / V3–V6）

付款与交付只写在落地页（换渠道不用改脚本）：[#buy](https://huiyonghkw.github.io/hekouwang-typora-theme/#buy)。

收到 zip 后：

```bash
./scripts/unlock.sh ~/Downloads/hekouwang-typora-theme-pack-YYYYMMDD.zip
# 或解压后在包内：./unlock.sh
```

（我这边打包装：`./scripts/pack.sh` → 桌面 zip，微信私发。）

## 定制

别改 CSS，它是生成物。改 `scripts/tokens.json` 后：

```bash
python3 scripts/build.py          # 公开仓默认只出免费档
# → theme/hekouwang.css
# → theme/hekouwang-dark.css
./scripts/install.sh
```

Windows 改为运行 `scripts\install-windows.ps1`，不要在 Windows 上执行 macOS 安装脚本。

`dark` 段只覆盖 `color` / `alpha`；边框与浅底由 `border_base` / `shadow_base` 派生。

构建会检查：

- **零 `!important`**
- **除根字号外零 `px` 字号**
- 浅 / 深 work CSS 都带纸感指标

## 与 Gallery「Claude Theme」的差异

Gallery 里已有 [Claude Theme](https://theme.typora.io/theme/Claude-Theme/)，目标相近。本主题是**独立实现，不是 fork**。

| | Gallery Claude Theme | hekouwang |
|---|---|---|
| 写法 | 手写约 3158 行 | token 生成 |
| `!important` | 397 处 | **0**（构建强制） |
| 字号 | 部分 `px` | 除根字号外全 `rem` |
| 打包字体 | ~24 MB（含全量 Noto Serif SC） | **~100 KB**（Inter latin） |
| Anthropic 字体 | 再分发 | **不打包**；`local()` + Inter |
| 正文中文 | Noto Serif SC（宋） | 系统无衬线 |
| 西文字重 | 单一 400，粗体合成 | 真可变 **300–800** + `opsz` |
| 界面 | 主要编辑区 | 侧栏、文件树、大纲、搜索、专注模式 |

**中文。** 桌面端没有 CJK 字形时，正确做法是**不打包**中文衬线。

**底色。** `#faf9f5` 常常是窗口色；编辑区更接近 `#fdfdfc`，壳层比纸面略深一档。

## 字体与授权

本仓库**不包含、不再分发任何 Anthropic 字体**。

`./scripts/install.sh --use-local-anthropic` 可从本机已安装的 Claude 桌面端复制字体到*你自己的*主题目录，仅供个人使用，**默认关闭**。拿不准就别开 —— Inter 兜底才是默认预期。

## 状态

- 浅色 + 深色：完成
- 深色色值：**采样**，不是浅色取反
- macOS 已完成真机设计验收；Windows 有独立字体、渲染和安装层，待 Win10 / Win11 Typora 真机回归签收

## 主题工程 Skill

维护本主题的 skill **就在本仓库** [`skills/`](skills/) 目录（不是另开 skill 仓）。clone / 打开本项目后，能加载项目 skill 的 Agent 可直接使用——token 驱动出 CSS、从截图采样配色、字体上屏探针。

**真源入口：**

- [`skills/hekouwang-typora-theme/SKILL.md`](skills/hekouwang-typora-theme/SKILL.md)

`.claude/skills/` 与 `.cursor/skills/` 是指向该目录的符号链接，供 Claude Code / Cursor 自动发现。clone 后**无需再单独安装 skill**。

## 授权

- **免费 V2**（`hekouwang.css` / Dark）与脚本：MIT，见 [LICENSE](LICENSE)。Inter 为 SIL OFL 1.1。
- **付费主题包**：个人使用，见包内 [LICENSE-PRO.txt](LICENSE-PRO.txt)；请勿二次分发。

受平静桌面阅读体验启发的独立作品，与 Anthropic PBC 无从属关系。"Claude" 与 "Anthropic" 是 Anthropic PBC 的商标。
