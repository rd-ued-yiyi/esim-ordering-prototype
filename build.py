#!/usr/bin/env python3
"""把 assets/ 内的 SVG / PNG 内联进 src/template.html，产出自包含 index.html。"""
import base64, re, pathlib

ROOT = pathlib.Path(__file__).parent
TPL = (ROOT / "src" / "template.html").read_text(encoding="utf-8")

def svg(name, folder="icons", recolor=None):
    """把 SVG 转成 data-URI <img>。内联 <svg> 会被 Artifact 的 sanitizer 过滤掉，
    data-URI <img> 是官方支持的自包含方式，任何环境都不会被剥离。
    recolor=(旧色, 新色) 用于同一图标的不同颜色变体（如 arrowRight 的 cyan/深色版）。"""
    txt = (ROOT / "assets" / folder / f"{name}.svg").read_text(encoding="utf-8")
    txt = txt.replace(' preserveAspectRatio="none"', "")
    if recolor:
        txt = txt.replace(f'fill="{recolor[0]}"', f'fill="{recolor[1]}"')
    # 取 intrinsic 宽高，让 <img> 以原始尺寸在 .ic 盒内居中（保持比例不变形）
    w = re.search(r'width="([\d.]+)"', txt)
    h = re.search(r'height="([\d.]+)"', txt)
    wh = ""
    if w and h:
        wh = f' width="{float(w.group(1)):.2f}" height="{float(h.group(1)):.2f}"'
    b64 = base64.b64encode(txt.strip().encode("utf-8")).decode()
    return f'<img alt="" src="data:image/svg+xml;base64,{b64}"{wh}>'

def inline_svg_to_img(markup):
    """把一段内联 SVG 字符串转成 data-URI <img>（用于状态栏手绘图标）。"""
    w = re.search(r'width="([\d.]+)"', markup)
    h = re.search(r'height="([\d.]+)"', markup)
    wh = f' width="{w.group(1)}" height="{h.group(1)}"' if w and h else ""
    b64 = base64.b64encode(markup.strip().encode("utf-8")).decode()
    return f'<img alt="" src="data:image/svg+xml;base64,{b64}"{wh}>'

SB_SIGNAL = '<svg xmlns="http://www.w3.org/2000/svg" width="17" height="11" viewBox="0 0 17 11" fill="none"><rect x="0" y="7" width="3" height="4" rx="1" fill="#fff"/><rect x="4.5" y="5" width="3" height="6" rx="1" fill="#fff"/><rect x="9" y="2.5" width="3" height="8.5" rx="1" fill="#fff"/><rect x="13.5" y="0" width="3" height="11" rx="1" fill="#fff"/></svg>'
SB_WIFI = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" viewBox="0 0 16 12" fill="none"><path d="M8 11.2 1 4.4a10 10 0 0 1 14 0L8 11.2Z" fill="#fff" opacity=".35"/><path d="M8 11.2 4 7.3a5.6 5.6 0 0 1 8 0L8 11.2Z" fill="#fff"/></svg>'
SB_BATTERY = '<svg xmlns="http://www.w3.org/2000/svg" width="25" height="12" viewBox="0 0 25 12" fill="none"><rect x=".5" y=".5" width="21" height="11" rx="3" stroke="#fff" opacity=".4"/><rect x="2" y="2" width="18" height="8" rx="1.5" fill="#fff"/><path d="M23 4v4a2 2 0 0 0 0-4Z" fill="#fff" opacity=".5"/></svg>'

def png_datauri(name):
    b = (ROOT / "assets" / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode()

subs = {
    "{{HERO_SVG}}":        (ROOT / "assets" / "hero" / "hero-scene.svg").read_text(encoding="utf-8"),
    "{{IC_back}}":         svg("back"),
    "{{IC_location}}":     svg("location"),
    "{{IC_arrowRight}}":   svg("arrowRight"),
    "{{IC_arrowRightSm}}": svg("arrowRightSm"),
    "{{IC_fire}}":         svg("fire"),
    "{{IC_checkCircle}}":  svg("checkCircle"),
    "{{IC_star}}":         svg("star"),
    "{{IC_locationArrow}}":svg("locationArrow"),
    "{{IC_arrowDown}}":    svg("arrowDown"),
    "{{IC_question}}":     svg("question"),
    "{{IC_arrowRightDark}}": svg("arrowRight", recolor=("#26BEC9", "#212121")),
    "{{IC_cross}}":        svg("cross"),
    "{{IC_search}}":       svg("search"),
    "{{IC_locationLine}}": svg("locationLine"),
    "{{IC_locationGrey}}": svg("locationLine", recolor=("#26BEC9", "#9C9DA0")),
    "{{IC_earthLine}}":    svg("earthLine"),
    "{{IC_plus}}":         svg("plus"),
    "{{IC_trash}}":        svg("trash"),
    "{{IC_globe}}":        svg("globe"),
    "{{IC_info}}":         svg("info"),
    "{{PICTO_tours}}":     svg("picto_tours", "picto"),
    "{{PICTO_cruise}}":    svg("picto_cruise", "picto"),
    "{{PICTO_travel}}":    svg("picto_travel", "picto"),
}

out = TPL
for k, v in subs.items():
    out = out.replace(k, v)

# 校验没有残留 token
leftover = re.findall(r"\{\{[^}]+\}\}", out)
if leftover:
    raise SystemExit(f"未替换的 token: {set(leftover)}")

# 包成完整 HTML 文档：直接静态托管（GitHub Pages）时必须有 doctype + viewport meta，
# 否则手机浏览器会按桌面宽度渲染再缩小，页面变成窄窄一条。
DOC = (
    "<!doctype html>\n"
    '<html lang="zh-Hans">\n'
    "<head>\n"
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    '<meta name="theme-color" content="#26BEC9">\n'
    "<title>eSIM · KKday</title>\n"
    "</head>\n"
    "<body>\n"
    f"{out}\n"
    "</body>\n"
    "</html>\n"
)

(ROOT / "index.html").write_text(DOC, encoding="utf-8")
print(f"index.html 生成完成 ({len(DOC):,} 字符)")
