# eSIM 订购流程原型

KKday eSIM B2C 主题及订购流程改造的**可点击原型**，用于可用性测试。移动端，按 Figma 高保真还原，视觉基于 KKday Web Design System tokens。

线上（GitHub Pages）：https://rd-ued-yiyi.github.io/esim-ordering-prototype/

## 结构

- `index.html` — 自包含成品（资产全内联，直接部署即可），由构建脚本产出
- `src/template.html` — 可编辑模板，用 `{{TOKEN}}` 占位资产
- `build.py` — 把 `assets/` 内的 SVG/PNG 内联进模板，产出 `index.html`
- `assets/` — 从 Figma / 设计系统导出的图标、pictogram、hero 插画

## 更新

```bash
python3 build.py       # 重新生成 index.html
git add -A && git commit -m "update" && git push   # 触发 Pages 重新部署
```

## 进度

- [x] 第 1 页：主题落地页（hero / 目的地选择 / 为什么选 KKday / 安装指南 / FAQ）
- [ ] 后续订购流程页面
