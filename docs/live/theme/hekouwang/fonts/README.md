# fonts/ — 可分发字体（随开源包一起走）

- `inter-latin-wght-normal.woff2` / `inter-latin-wght-italic.woff2`
  Inter 可变字体 latin 子集，wght 100–900。授权见 `OFL.txt`（SIL Open Font License 1.1，允许再分发）。
  只取 latin 子集是因为中文由系统字体承担，不需要打包 CJK。

对照 `../fonts-local/`：那里放的是 Anthropic 专有字体，**不可分发**，已被 .gitignore 排除。
主题的字体栈是「Anthropic（本机有才用）→ Inter（随包分发）→ 系统字体」三级降级，
所以三种情况下都能正常显示，只是精确度递减。
