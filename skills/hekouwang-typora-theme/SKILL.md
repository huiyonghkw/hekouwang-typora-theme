---
name: hekouwang-typora-theme-skill
slug: hekouwang-typora-theme-skill
displayName: Typora 主题工程（hekouwang）
summary: Typora theme engineering / CJK long-form markdown — tokens.json CSS build, color sampling, font probe. Free V2 light+dark; paid V1/V3–V6.
license: MIT
homepage: https://github.com/huiyonghkw/hekouwang-typora-theme
version: 1.3.2
description: >
  会勇禾口王 · Typora 主题工程 Skill。维护「hekouwang」主题（中文长文浅色 + 深色），
  并提供一套可复用的主题工程方法：CSS 由 tokens.json
  生成而非手写、构建时强制零 !important / 零 px 字号、从参照截图采样真实色值（而不是猜
  配色）、用 fallback 基准探针验证字体是否真的上屏。
  当需要：① 改 Typora 主题的配色/字号/行高/紧凑度/纸感；② 装主题或排查「改了 CSS 但
  Typora 里没变化 / 字体没生效 / 主题菜单多出奇怪条目」；③ 按某个 App 或网站的观感做
  一套新主题（采样它的真实色值）；④ 加深色版或新变体；⑤ 把主题发布到 theme.typora.io
  时使用。
  触发词：Typora 主题 / typora theme / 改主题配色 / 主题不生效 / 换肤 / Markdown 编辑器主题 /
  hekouwang 主题 / 主题字体没上屏 / 采样配色 / 做一套主题 / 提交 Typora 主题库。
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Typora 主题工程

本 skill 真源在仓库可见目录 `skills/hekouwang-typora-theme/`（本文件所在目录）。
`.claude/skills/hekouwang-typora-theme` 与 `.cursor/skills/hekouwang-typora-theme`
是指向本目录的符号链接，方便各端自动发现。
**放在 `skills/` 即表示可当项目 skill 安装 / 使用**：clone 打开本仓即可加载，不必再 clone 单独 skill 仓库。
工作区是仓库根的 `scripts/`、`theme/`、`demo/`。

## 30 秒速览

- **主题产物（公开仓 · 免费）**：`theme/hekouwang.css` + `hekouwang-dark.css`（= skill V2 编辑）
- **付费六套**（V1/V3–V6）不在公开树：色板 `palettes.paid.json` + 工艺 `craft_paid.py` 只随 ¥9.9 zip / 本机开发机。
- **别手改 CSS**，它是生成物。改 `scripts/tokens.json` → 跑 `scripts/build.py`（公开 clone 默认只出免费档）。
- **`dark` 段只覆盖 `color` / `alpha`**。构建断言行高 / 行宽 / 纸感在位。
- **开源仓库**：https://github.com/huiyonghkw/hekouwang-typora-theme （免费 V2 · MIT；付费见落地页 `#buy`）

## 最常用的三条命令

```bash
python3 scripts/build.py                    # → 浅色 + 深色 CSS（含自检）
./scripts/install.sh                        # 装进 Typora（自动备份到子目录）
python3 scripts/verify_render.py --css theme/hekouwang.css \
  --fonts "Hekouwang Sans,Hekouwang Sans Fb" --vars bg-color,text-color
```

## 铁律（这几条踩过，全是静默失败）

1. **改完 CSS 必须 `Cmd+Q` 完全退出 Typora 再重开。** 切换主题**不会**重新加载被修改的
   CSS 文件。不这么做，你会在一个用户根本没看到的版本上反复调参数。
2. **备份绝不能留在 themes 根目录。** Typora 把根目录下任何文件名含 `.css` 的文件都列进
   主题菜单，**包括 `.` 开头的隐藏文件**。备份必须进子目录（`install.sh` 已处理）。
3. **零 `!important`**。Typora 自己的 base.css 都不用，靠 `#write` 特异性就够。构建时断言。
4. **除根字号外零 `px` 字号**，否则 Typora 偏好里的字号调节失效。构建时断言。
5. **配色不许猜，要采样。** 见下。
6. **headless 全绿 ≠ Typora 里对。** 系统 Chrome 比 Typora 内嵌的 Chromium 新得多，
   最终验收必须在 Typora 里肉眼看。

## 采样，不要猜配色

做浅色版时我笃定页面底色是品牌米色 `#faf9f5`，采样后发现对话区是 `#fdfdfc` ——
`#faf9f5` 是**窗口/侧边栏**色，两者角色搞反了。深色版更极端：**深色下侧边栏比正文区更亮**，
与浅色模式的关系完全相反，靠"把浅色取反"推演一定会做错。

```bash
python3 scripts/sample_colors.py 参照截图.png                      # 按常见布局给候选
python3 scripts/sample_colors.py 图.png --box 700,640,1700,700 --label 正文背景
python3 scripts/sample_colors.py 图.png --text-box 690,300,1500,345 --label 正文文字
# 反解叠加色：底色 结果色 候选色 —— 三通道 alpha 一致的那个才是真的
python3 scripts/sample_colors.py --solve-alpha 1f1f1e 272725 ffffff,d97757
```

最后那条是判断"某个底色是品牌色浅铺还是中性叠加"的可靠办法。实测深色行内代码底：
白色叠加解出 0.036/0.036/0.031（一致 ✅），品牌橙解出 0.043/0.091/0.123（不一致 ❌）。

## 验证字体是否真的上屏

字体不生效**不会报错**，页面照常渲染、只是悄悄换成系统字体。判据必须带 fallback 基准：
量一个**不存在的字体**得到基准宽度，任何字体只要等于基准就说明它没生效。

```bash
python3 scripts/verify_render.py --css theme/hekouwang.css \
  --fonts "Hekouwang Sans,Hekouwang Sans Fb,Hekouwang Mono"
```

字体没生效的三个常见原因（都遇到过）：`format()` 用了 `truetype-variations` 这类非标准值导致
整条 `src` 被丢弃 / 字体栈里的族名与 `@font-face` 的 `font-family` 不一致（**改名时最常见**）/
`src` 相对路径写错（基准是 CSS 文件所在目录）。

## 按需展开

| 要做什么 | 读哪份 |
|---|---|
| 改配色、字号、行高、紧凑度 | [references/tokens.md](references/tokens.md) |
| Typora 选择器地图、官方规范、五个静默坑 | [references/typora-spec.md](references/typora-spec.md) |
| 字体策略、授权红线、三级降级 | [references/fonts.md](references/fonts.md) |
| 做一套全新主题 / 加变体 / 发布到主题库 | [references/workflow.md](references/workflow.md) |

## 目录

```
skills/hekouwang-typora-theme/   本 skill 真源（SKILL.md + references/）
.claude/skills/… · .cursor/skills/…   → 软链到上面，供工具发现
scripts/tokens.json      单一真相源（改这里）
scripts/build.py         公开仓默认生成免费 V2 两份 CSS；有付费色板时才出 V1/V3–V6
scripts/unlock.sh        买家装付费 zip
scripts/pack.sh          你打付费包（需本机 palettes.paid.json + craft_paid.py）
scripts/install.sh       装进 Typora（--use-local-anthropic 可选，默认关）
scripts/sample_colors.py 从截图采样真实色值
scripts/verify_render.py 渲染/字体验证探针
theme/                   成品 CSS 与随包字体（Inter, OFL）
demo/                    验收样张、字体诊断样张
```
