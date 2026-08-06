# hekouwang

**体验站：** [huiyonghkw.github.io/hekouwang-typora-theme](https://huiyonghkw.github.io/hekouwang-typora-theme/)

给「一天要盯着 Markdown 好几个小时」的人用的 Typora 主题——按**中文长文**来排，不是按聊天气泡来排。

配色对齐内容工厂 **hekouwang-content-skill 六套视觉（V1–V6）**；阅读指标全套共用：`1rem` · `1.65` · `52em` · 纸感卡片。

## 免费 / 付费

| 档 | 主题菜单 | 说明 |
|---|---|---|
| **免费 · MIT** | **Hekouwang** / **Hekouwang Dark** | = skill **V2 编辑**（米白 / 米黑）。Gallery 入口也是这一档。公开仓只发这一档。 |
| **付费包 · ¥9.9** | **Hekouwang V1…V6**（各含 Dark） | skill 全矩阵：科技 / 编辑 / 财经 / 玻璃 / 紫 / 焰彩 · 浅+深共 12 份 CSS（V2 与免费档同一套文件） |

**怎么买：** 落地页购买区（微信/支付宝 · 微信 `hekouwang`，备注「Typora主题」）→ 我私发 zip → `./unlock.sh` 一键装进 Typora。

→ [huiyonghkw.github.io/hekouwang-typora-theme/#buy](https://huiyonghkw.github.io/hekouwang-typora-theme/#buy)

免费色板在 `scripts/palettes.json`；付费色板不进公开仓。阅读指标在 `scripts/tokens.json`。公开仓重建：`python3 scripts/build.py`（默认只出免费档）。

![中文验收样张](docs/screenshot-zh.png)

*中文样张（`demo/验收样张.md`）——题头署名、阅读指标、中英混排正文。*

![英文验收样张](docs/screenshot.png)

*英文样张（`demo/acceptance-sample.md`）——同一套指标，便于对照西文节奏。*

![代码块](docs/screenshot-fences-zh.png)

*连续代码块（Python / shell / CSS）——语法色克制，块与块之间有呼吸。*

*[English](README.md)*

---

## 设计取向

- **默认服务中文长文。** 汉字密、方块字，需要 ≥1.6 的行高和大约 40–50 字的行宽。
- **不用高饱和强调色。** 行内代码用低饱和色，一段里七八个 `` `code` `` 仍读得像文字。
- **层级靠字号、字重、间距，不靠彩色竖条。**
- **边框用墨色叠透明度**，不用平铺灰。
- **纸感画在 `#write` 上**（浅 / 深都有）：径向、大圆角、外阴影；侧栏 / gutter / 顶栏是更深一档的壳层。
- **六套皮肤 = skill 十二格**（每套黑/白两极），气质与公众号/小红书产出一致。

### 阅读指标

| Token | 值 | 用意 |
|---|---|---|
| `body_size` | `1rem` | 长时间写作不累 |
| `body_lh` | `1.65` | 中文密度需要更大行高 |
| `measure` | `52em` | 流体：`min(52em, calc(100% − gutter))` |
| `para_gap` | `0.78rem` | 段距紧凑但不糊成墙 |

### 六套菜单名

| Skill 格 | Typora 菜单 |
|---|---|
| V1 科技 | Hekouwang V1 / V1 Dark |
| V2 编辑（免费） | Hekouwang / Hekouwang Dark |
| V3 财经 | Hekouwang V3 / V3 Dark |
| V4 玻璃 | Hekouwang V4 / V4 Dark |
| V5 紫 | Hekouwang V5 / V5 Dark |
| V6 焰彩 | Hekouwang V6 / V6 Dark |

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

然后 **完全退出 Typora（Cmd+Q）再重开** —— 切换主题不会重载已改过的 CSS。在「主题」菜单选 **Hekouwang** 或 **Hekouwang Dark**。

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
- 在 **macOS** 上设计与测试（Windows / Linux 未测；尚无 Windows unibody 样式）

## 主题工程 Skill

维护本主题的 skill **就在本仓库** [`skills/`](skills/) 目录（不是另开 skill 仓）。clone / 打开本项目后，能加载项目 skill 的 Agent 可直接使用——token 驱动出 CSS、从截图采样配色、字体上屏探针。

**真源入口：**

- [`skills/hekouwang-typora-theme/SKILL.md`](skills/hekouwang-typora-theme/SKILL.md)

`.claude/skills/` 与 `.cursor/skills/` 是指向该目录的符号链接，供 Claude Code / Cursor 自动发现。clone 后**无需再单独安装 skill**。

## 授权

CSS 与脚本 MIT，见 [LICENSE](LICENSE)。Inter 为 SIL OFL 1.1。

受平静桌面阅读体验启发的独立作品，与 Anthropic PBC 无从属关系。"Claude" 与 "Anthropic" 是 Anthropic PBC 的商标。
