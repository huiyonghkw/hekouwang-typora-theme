# 字体策略与授权红线

## 三级降级

```
1  Anthropic Sans   仅当系统已装 —— 专有字体，绝不打包、绝不分发
2  Inter            随包分发，SIL OFL，latin 子集，100 KB   ← 绝大多数人看到的是这层
3  系统 UI 字体      兜底
```

字体栈里**西文族必须全部排在中文族之前**，否则中文字体会把西文一起吃掉。

## 为什么不打包中文字体

实测：Anthropic Sans 共 **581 字符，CJK 汉字 0 个**，连中文逗号「，」句号「。」都没有。

```python
from fontTools.ttLib import TTFont
f = TTFont("AnthropicSans-Romans-Variable-25x258.ttf")
cmap = f.getBestCmap()
print(len(cmap), len([c for c in cmap if 0x4E00 <= c <= 0x9FFF]))   # 581 0
```

所以中文**必然** fallback 到系统字体（macOS 上是苹方）——**这就是桌面端的真实机制**。
想 1:1 复刻就不该打包中文字体。对照：gallery 上另一套同类主题打包了 24 MB 全量
Noto Serif SC 把中文渲成宋体，反而偏离了原版，包体也从 100 KB 涨到 24 MB。

## 授权红线

Anthropic Sans / Serif 的 name 表里**只有 `Copyright 2025 Anthropic PBC`，没有任何 license
字段**（对照 Inter / Mozilla 的字体会明写 SIL OFL）。属专有品牌资产：

- ✗ 不打包进仓库
- ✗ 不提供提取脚本作为默认行为
- ✓ 通过 `local()` 探测系统已装的
- ✓ `install.sh --use-local-anthropic` 显式 opt-in，默认关闭，并在脚本头部写明风险

判断任何字体能否分发，先看 name 表：

```python
from fontTools.ttLib import TTFont
f = TTFont(path)
print(f['name'].getDebugName(0))    # copyright
print(f['name'].getDebugName(13))   # license —— 空的就是不能分发
```

## 两个版本别拿错

- 网上流传的 `AnthropicSansWebText.ttf`：静态**单字重 400**，粗体只能合成（发虚、边缘脏）
- Claude 桌面端自带的 `AnthropicSans-Romans-Variable-25x258.ttf`：**真可变**，
  wght 300–800 + opsz 16–48
- ⚠️ `AnthropicMonoVariable.ttf` **名字带 Variable，实测不是可变字体** —— 光看文件名会判错

## 字体不生效的三个原因

字体加载失败**不报错**，页面照常渲染、只是悄悄换成系统字体。用
`verify_render.py --fonts ...` 检测（它带 fallback 基准，能分辨）。

1. **`format()` 用了非标准值**。`format("truetype-variations")` 是早期实验语法，
   Typora 内嵌的老 Chromium 不认识，**整条 `src` 被丢弃**。新版 Chrome 认，所以
   headless 测全绿、Typora 里才暴露。→ 用 `woff2` 优先 + `truetype` 兜底，format 只用标准值。
2. **族名不一致**。字体栈里写的族名必须与 `@font-face` 的 `font-family` 完全一致。
   **改名时最容易漏**（改了 build.py 忘了改 tokens.json）。
3. **`src` 相对路径写错**。基准是 CSS 文件所在目录，不是 HTML。

## 转 woff2

```python
from fontTools.ttLib import TTFont
f = TTFont("in.ttf"); f.flavor = "woff2"; f.save("out.woff2")
```
实测 335 KB → 125 KB，且可变轴保留完好。
