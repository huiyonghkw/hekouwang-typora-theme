# hekouwang · Typora long-form reading theme

Hekouwang turns Markdown into a calm, coherent reading surface for long-form writing—especially mixed CJK and Latin documents.

[中文产品说明](README.md) · [Live site](https://huiyonghkw.github.io/hekouwang-typora-theme/) · [Technical notes](README.zh.md)

## What it is

- CJK-oriented reading metrics: `1rem` body size, `1.65` leading, and a fluid `52em` measure.
- Quiet hierarchy through size, weight, and space—not colored left bars or heavy chrome.
- A complete surface for editing, focus mode, code, tables, sidebars, and PDF export.
- Inter for bundled Latin glyphs; system CJK fonts for small distribution size and clear licensing.
- A dedicated Windows layer using Typora's `body.os-windows`: Microsoft YaHei UI / Microsoft YaHei for CJK and Cascadia Mono / Cascadia Code for code.

## Install

macOS:

```bash
git clone https://github.com/huiyonghkw/hekouwang-typora-theme.git
cd hekouwang-typora-theme
./scripts/install.sh
```

Windows PowerShell:

```powershell
git clone https://github.com/huiyonghkw/hekouwang-typora-theme.git
cd hekouwang-typora-theme
.\scripts\install-windows.ps1
```

If local policy blocks the script, run `powershell -ExecutionPolicy Bypass -File .\scripts\install-windows.ps1`; it applies only to that process and does not change the system policy.

Restart Typora completely, then choose **Hekouwang** or **Hekouwang Dark**. The Windows installer targets `%APPDATA%\Typora\themes`; use `-ThemeDir` for a custom location.

## Editions

| Edition | Themes | Notes |
|---|---|---|
| Free · MIT | Hekouwang / Hekouwang Dark | Complete V2 editorial reading experience. |
| Paid · ¥9.9 | Hekouwang V1–V6 (+ Dark) | Six visual systems built on the same reading metrics. |

See the [live site](https://huiyonghkw.github.io/hekouwang-typora-theme/#buy) for the paid pack. The Chinese README is the canonical product page; see [README.zh.md](README.zh.md) for engineering detail.

## License

Free V2 and scripts are [MIT](LICENSE); bundled Inter is SIL OFL 1.1. Paid packs are personal-use only. No Anthropic font is included or redistributed.
