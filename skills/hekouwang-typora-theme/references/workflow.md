# 工作流

## A. 改现有主题的视觉

```bash
# 1 改 tokens
$EDITOR scripts/tokens.json

# 2 生成（自带断言：0 个 !important、0 处 px 字号）
python3 scripts/build.py

# 3 装
./scripts/install.sh

# 4 ⚠️ 完全退出 Typora 再重开（切主题不重载 CSS）
```

改完如果涉及配色关系，用探针确认 computed 值真的是你写的那个：

```bash
python3 scripts/verify_render.py --css theme/hekouwang.css --vars bg-color,text-color,hk-code
```

**重构生成逻辑后必做回归**：确认已定稿变体的输出**字节级不变**。
```bash
git diff --quiet theme/hekouwang.css && echo "零差异，重构安全"
```

## B. 按某个 App / 网站的观感做新主题

核心是**采样，不要猜**。步骤：

1. **拿参照截图**。浅色一张、深色一张，要包含正文区、侧边栏、代码块。
2. **采样背景层**（大片纯色区域，占比 <60% 说明区域不纯，换一块）：
   ```bash
   python3 scripts/sample_colors.py 参照.png --box x0,y0,x1,y1 --label 正文背景
   ```
3. **采样文字层**（用 `--text-box`，它会排除背景取笔画众数；别用最亮/最暗极值点，
   那是抗锯齿峰值）。
4. **反解叠加色**（判断某个底色是品牌色浅铺还是中性叠加）：
   ```bash
   python3 scripts/sample_colors.py --solve-alpha 底色 结果色 候选1,候选2
   ```
   三通道 alpha 一致的那个才是真的。
5. **别按浅色推演深色**。实测反例：深色下侧边栏比正文区更亮，与浅色关系相反；
   行内代码底浅色是品牌橙、深色是中性白。两条推演都会推反。
6. 把采样值写进 `scripts/palettes.json`（免费档）或 `scripts/palettes.paid.json`（付费档），
   构建、验证。**不要写进 `tokens.json`** —— 那里只有阅读指标、字体栈与透明度阶，
   配色放在那儿会被 palette 整体覆盖，改了不生效（构建会直接报错拦下）。

**字体**：先查参照 App 用的字体能不能分发（见 references/fonts.md 的 name 表检查），
不能就找 OFL 替身，并做三级降级栈。

## C. 加一个新变体

公开主题的新实验变体在 `scripts/palettes.json` 的 `themes[]` 里加一项，
只写要覆盖的 `color` / `dark` / `paper` / `shape` / `syntax`：

```json
{
  "id": "sepia",
  "slug_suffix": "-sepia",
  "menu": "Hekouwang Sepia",
  "label": "V2 实验 · 纸色暖调",
  "tier": "free",
  "color": { "bg": "...", "border_base": "...", "shadow_base": "...", ... },
  "dark": { "color": { ... }, "alpha": { ... } },
  "paper": { "highlight": "...", "mid": "...", "shade": "...", "gutter": "..." },
  "shape": { "radius": "0", ... },
  "syntax": { "light": { ... }, "dark": { ... } }
}
```

构建器会自动为新变体输出浅色与深色两份 CSS（`hekouwang-sepia.css` /
`hekouwang-sepia-dark.css`），派生值按新的 `border_base` / `shadow_base` 自动重算，
不需要改模板。**阅读指标不用复制** —— 那在 `tokens.json` 的 `_presets.work`，所有变体共用。

付费主题走独立的 `scripts/palettes.paid.json`，不要把色板写回公开的 `tokens.json` 或 `palettes.json`。现有付费清单为 V1 / V2 Pro / V3–V6，`python3 scripts/build.py --tier paid` 会生成各自浅色与深色共 12 个 CSS；免费 V2 的 `hekouwang.css` / `hekouwang-dark.css` 独立保留。增删付费主题时同步 `pack.sh`、`unlock.sh`、`.gitignore` 与包内授权清单，并验收每个文件的 Typora 菜单名。

## D. 发布到 theme.typora.io

```bash
gh repo fork typora/theme.typora.io --clone=false
# 仓库很大（塞满历史缩略图），别整仓 clone，用 API 直接写文件：
FORK=<你的用户名>/theme.typora.io; BR=add-xxx-theme
BASE=$(gh api repos/$FORK/git/ref/heads/gh-pages --jq '.object.sha')
gh api repos/$FORK/git/refs -f ref="refs/heads/$BR" -f sha="$BASE"
gh api repos/$FORK/contents/_posts/YYYY-MM-DD-slug.md -X PUT \
  -f message="Add X theme" -f branch="$BR" \
  -f content="$(base64 -i post.md | tr -d '\n')"
gh api repos/$FORK/contents/thumbnails/slug.png -X PUT \
  -f message="Add thumbnail" -f branch="$BR" \
  -f content="$(base64 -i thumb.png | tr -d '\n')"
gh pr create --repo typora/theme.typora.io --base gh-pages --head <用户名>:$BR ...
```

post 的字段与 Notes 见 [typora-spec.md](typora-spec.md) 末节。
**如果 gallery 里已有目标相近的主题**，在 post 和 PR 里正面说明关系：是不是 fork、
差异在哪、给可复现的数字。主动挑明比被质疑后再解释有利。
