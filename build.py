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

def strip_wh(markup):
    """去掉内联 SVG 的固定 width/height（保留 viewBox），尺寸交给 CSS，避免 iOS <img> 栅格化模糊。
    折叠为单行：内联 SVG 会被注入 JS 单引号字符串（ICONS_BIG），换行会导致语法错误。"""
    m = markup.replace(' preserveAspectRatio="none"', "").replace(' overflow="visible"', "")
    m = re.sub(r'(<svg\b[^>]*?)\s+width="[\d.]+"\s+height="[\d.]+"', r'\1', m, count=1)
    return re.sub(r'\s+', ' ', m).strip()

def raw_svg(name, folder="icons", recolor=None):
    """返回原始内联 <svg>（去掉固定 width/height，保留 viewBox），由 CSS 控制尺寸。
    内联矢量在 iOS Safari 下按显示分辨率栅格化，不会像 <img> data-URI 那样先按 intrinsic
    小尺寸栅格化再放大而糊。GitHub Pages 无 sanitizer，内联 SVG 可用（hero 亦为内联）。"""
    txt = (ROOT / "assets" / folder / f"{name}.svg").read_text(encoding="utf-8")
    if recolor:
        txt = txt.replace(f'fill="{recolor[0]}"', f'fill="{recolor[1]}"')
    txt = txt.replace(' preserveAspectRatio="none"', "").replace(' overflow="visible"', "")
    txt = re.sub(r'(<svg\b[^>]*?)\s+width="[\d.]+"\s+height="[\d.]+"', r'\1', txt, count=1)
    return re.sub(r'\s+', ' ', txt).strip()  # 单行：可安全注入 JS 字符串

def inline_svg_to_img(markup):
    """把一段内联 SVG 字符串转成 data-URI <img>（用于状态栏手绘图标）。"""
    w = re.search(r'width="([\d.]+)"', markup)
    h = re.search(r'height="([\d.]+)"', markup)
    wh = f' width="{w.group(1)}" height="{h.group(1)}"' if w and h else ""
    b64 = base64.b64encode(markup.strip().encode("utf-8")).decode()
    return f'<img alt="" src="data:image/svg+xml;base64,{b64}"{wh}>'

# 详情页小图标（Figma 无单独可导出的实体，按 16px 图框手绘，矢量占位 ~13px）
DET_FILE = '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="14" viewBox="0 0 12 14" fill="none"><path d="M1.5 0h6L12 4.5V12.5A1.5 1.5 0 0 1 10.5 14h-9A1.5 1.5 0 0 1 0 12.5v-11A1.5 1.5 0 0 1 1.5 0Z" fill="#26BEC9"/><path d="M7.5 0 12 4.5H8.5a1 1 0 0 1-1-1V0Z" fill="#8ADEE3"/></svg>'
DET_SPARK = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M9 0l1.2 3.8L14 5l-3.8 1.2L9 10 7.8 6.2 4 5l3.8-1.2L9 0Z" fill="#2EC4F2"/><path d="M3 8l.8 2.2L6 11l-2.2.8L3 14l-.8-2.2L0 11l2.2-.8L3 8Z" fill="#10D5E3"/></svg>'
DET_SMILE = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 13 13" fill="none"><circle cx="6.5" cy="6.5" r="5.75" stroke="#212121" stroke-width="1.5"/><circle cx="4.6" cy="5.2" r=".9" fill="#212121"/><circle cx="8.4" cy="5.2" r=".9" fill="#212121"/><path d="M4.2 8.2a3 3 0 0 0 4.6 0" stroke="#212121" stroke-width="1.3" stroke-linecap="round"/></svg>'
DET_NEUTRAL = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 13 13" fill="none"><circle cx="6.5" cy="6.5" r="5.75" stroke="#212121" stroke-width="1.5"/><circle cx="4.6" cy="5.2" r=".9" fill="#212121"/><circle cx="8.4" cy="5.2" r=".9" fill="#212121"/><path d="M4.3 8.8h4.4" stroke="#212121" stroke-width="1.3" stroke-linecap="round"/></svg>'
DET_SEND = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M17.6 2.4 2.6 8.2c-.5.2-.5.9 0 1.1l5.7 2 2 5.7c.2.5.9.5 1.1 0L17.6 2.4Z" stroke="#212121" stroke-width="1.4" stroke-linejoin="round"/><path d="M17.6 2.4 8.3 11.3" stroke="#212121" stroke-width="1.4" stroke-linecap="round"/></svg>'
DET_CHECK ='<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2.5 6.2 5 8.6l4.5-5" stroke="#13A3B6" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
DET_TICKET ='<svg xmlns="http://www.w3.org/2000/svg" width="22" height="20" viewBox="0 0 22 20" fill="none"><g transform="rotate(-12 11 10)"><path d="M2 5a1.5 1.5 0 0 1 1.5-1.5h15A1.5 1.5 0 0 1 20 5v3a2 2 0 0 0 0 4v3a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 2 15v-3a2 2 0 0 0 0-4V5Z" fill="#F0544C"/><path d="M11 5v10" stroke="#fff" stroke-width="1.2" stroke-dasharray="2 2"/></g><circle cx="19" cy="3" r="1.2" fill="#F5A623"/><circle cx="3.5" cy="16.5" r="1" fill="#26BEC9"/></svg>'

# 安装指南 tab 图标（iOS=Apple / Android=机器人 / 分享=share），深色内联矢量
GUIDE_APPLE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><path d="M17.05 12.65c-.03-2.5 2.04-3.7 2.13-3.76-1.16-1.7-2.97-1.93-3.61-1.96-1.54-.15-3 .9-3.78.9-.77 0-1.97-.88-3.24-.86-1.67.03-3.21.97-4.07 2.46-1.73 3-.44 7.45 1.24 9.9.82 1.2 1.8 2.54 3.08 2.5 1.24-.05 1.7-.8 3.2-.8 1.49 0 1.9.8 3.2.77 1.32-.02 2.16-1.22 2.97-2.43.94-1.4 1.32-2.75 1.34-2.82-.03-.01-2.57-.99-2.6-3.9Z" fill="#212121"/><path d="M14.86 5.2c.68-.83 1.14-1.98 1.02-3.13-.98.04-2.17.65-2.88 1.48-.63.73-1.19 1.9-1.04 3.02 1.1.08 2.22-.55 2.9-1.37Z" fill="#212121"/></svg>'
GUIDE_ANDROID = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><path d="M6 11a6 6 0 0 1 12 0v.5H6V11Z" fill="#212121"/><path d="M6 12.5h12V17a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 6 17v-4.5Z" fill="#212121"/><path d="m7.6 4.6 1.4 2.1M16.4 4.6l-1.4 2.1" stroke="#212121" stroke-width="1.3" stroke-linecap="round"/><circle cx="9.5" cy="9" r=".9" fill="#fff"/><circle cx="14.5" cy="9" r=".9" fill="#fff"/><rect x="8.6" y="18" width="1.8" height="3.4" rx=".9" fill="#212121"/><rect x="13.6" y="18" width="1.8" height="3.4" rx=".9" fill="#212121"/><rect x="3" y="12" width="1.8" height="5" rx=".9" fill="#212121"/><rect x="19.2" y="12" width="1.8" height="5" rx=".9" fill="#212121"/></svg>'
GUIDE_SHARE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"><circle cx="6" cy="12" r="2.6" stroke="#212121" stroke-width="1.6"/><circle cx="17.5" cy="5.5" r="2.6" stroke="#212121" stroke-width="1.6"/><circle cx="17.5" cy="18.5" r="2.6" stroke="#212121" stroke-width="1.6"/><path d="m8.3 10.8 6.9-3.9M8.3 13.2l6.9 3.9" stroke="#212121" stroke-width="1.6" stroke-linecap="round"/></svg>'

SB_SIGNAL ='<svg xmlns="http://www.w3.org/2000/svg" width="17" height="11" viewBox="0 0 17 11" fill="none"><rect x="0" y="7" width="3" height="4" rx="1" fill="#fff"/><rect x="4.5" y="5" width="3" height="6" rx="1" fill="#fff"/><rect x="9" y="2.5" width="3" height="8.5" rx="1" fill="#fff"/><rect x="13.5" y="0" width="3" height="11" rx="1" fill="#fff"/></svg>'
SB_WIFI = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" viewBox="0 0 16 12" fill="none"><path d="M8 11.2 1 4.4a10 10 0 0 1 14 0L8 11.2Z" fill="#fff" opacity=".35"/><path d="M8 11.2 4 7.3a5.6 5.6 0 0 1 8 0L8 11.2Z" fill="#fff"/></svg>'
SB_BATTERY = '<svg xmlns="http://www.w3.org/2000/svg" width="25" height="12" viewBox="0 0 25 12" fill="none"><rect x=".5" y=".5" width="21" height="11" rx="3" stroke="#fff" opacity=".4"/><rect x="2" y="2" width="18" height="8" rx="1.5" fill="#fff"/><path d="M23 4v4a2 2 0 0 0 0-4Z" fill="#fff" opacity=".5"/></svg>'

def png_datauri(name):
    b = (ROOT / "assets" / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode()

def svg_datauri(markup):
    """返回裸 data-URI 字符串（不包 <img>），供 JS 里当 src 用（评论实拍缩图）。"""
    return "data:image/svg+xml;base64," + base64.b64encode(markup.strip().encode("utf-8")).decode()

# 旅客实拍缩图：矢量场景缩图（任意尺寸清晰，自包含无需外链图片）
SHOTS = [
    # 海滩
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80"><defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8FD3E8"/><stop offset="1" stop-color="#D6F0F5"/></linearGradient></defs><rect width="80" height="80" fill="url(#s)"/><circle cx="60" cy="20" r="9" fill="#FFE08A"/><path d="M0 52 Q40 44 80 52 V64 H0Z" fill="#3FA9C9"/><path d="M0 62 Q40 56 80 62 V80 H0Z" fill="#EAD9A8"/></svg>',
    # 雪山
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80"><defs><linearGradient id="m" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFE3F2"/><stop offset="1" stop-color="#EAF6FB"/></linearGradient></defs><rect width="80" height="80" fill="url(#m)"/><circle cx="22" cy="20" r="7" fill="#FFE7A6"/><path d="M-4 80 L26 34 L44 62 Z" fill="#7FA8BF"/><path d="M20 42 L26 34 L32 42 L28 45 L24 42Z" fill="#fff"/><path d="M30 80 L58 40 L86 80 Z" fill="#5E8AA6"/><path d="M52 48 L58 40 L64 48 L60 51 L56 48Z" fill="#fff"/></svg>',
    # 城市夜景
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80"><defs><linearGradient id="c" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3B4E76"/><stop offset="1" stop-color="#8A6E9E"/></linearGradient></defs><rect width="80" height="80" fill="url(#c)"/><circle cx="62" cy="18" r="6" fill="#FDF3C4"/><g fill="#2A3556"><rect x="6" y="44" width="12" height="36"/><rect x="22" y="34" width="14" height="46"/><rect x="40" y="48" width="12" height="32"/><rect x="56" y="38" width="16" height="42"/></g><g fill="#FFD86B"><rect x="26" y="40" width="3" height="3"/><rect x="32" y="40" width="3" height="3"/><rect x="60" y="44" width="3" height="3"/><rect x="66" y="44" width="3" height="3"/></g></svg>',
    # 鸟居（日本）
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80"><defs><linearGradient id="t" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F5C6B0"/><stop offset="1" stop-color="#F8E3D2"/></linearGradient></defs><rect width="80" height="80" fill="url(#t)"/><path d="M0 66 Q40 60 80 66 V80 H0Z" fill="#9CC38F"/><g fill="#C7452E"><rect x="16" y="26" width="48" height="7" rx="1"/><rect x="20" y="34" width="40" height="4"/><rect x="22" y="30" width="7" height="40"/><rect x="51" y="30" width="7" height="40"/></g></svg>',
    # 机窗云海
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80"><defs><linearGradient id="k" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6FA8DC"/><stop offset="1" stop-color="#C9E2F5"/></linearGradient></defs><rect width="80" height="80" fill="url(#k)"/><ellipse cx="26" cy="58" rx="26" ry="10" fill="#fff" opacity=".85"/><ellipse cx="58" cy="64" rx="24" ry="9" fill="#fff" opacity=".9"/><path d="M44 24 l18 8 -16 3 -3 9 -4 -10 -8 -2 Z" fill="#F2F6FA"/></svg>',
    # 街灯灯笼
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80"><defs><linearGradient id="l" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7A3B4E"/><stop offset="1" stop-color="#C56B5C"/></linearGradient></defs><rect width="80" height="80" fill="url(#l)"/><g><ellipse cx="20" cy="30" rx="8" ry="10" fill="#F7B267"/><ellipse cx="44" cy="22" rx="7" ry="9" fill="#F4845F"/><ellipse cx="64" cy="34" rx="8" ry="10" fill="#F7B267"/></g><rect x="0" y="8" width="80" height="2" fill="#4A2530"/></svg>',
]

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
    "{{IC_locationDark}}": svg("locationLine", recolor=("#26BEC9", "#212121")),
    "{{IC_earthLine}}":    svg("earthLine"),
    "{{IC_earthCyan}}":    svg("earthLine", recolor=("#212121", "#26BEC9")),
    "{{IC_plus}}":         svg("plus"),
    "{{IC_plusCyan}}":     svg("plus", recolor=("#212121", "#26BEC9")),
    "{{IC_trash}}":        svg("trash"),
    "{{IC_trashLight}}":   svg("trash", recolor=("#727272", "#9C9DA0")),
    "{{IC_locationSearch}}": svg("locationSearch"),
    "{{IC_crossCircle}}":  svg("crossCircle"),
    "{{IC_globe}}":        svg("globe"),
    "{{IC_globeSel}}":     svg("globeSel"),
    "{{IC_info}}":         svg("info"),
    "{{IC_flash}}":        svg("flash"),
    "{{IC_currencyReload}}": svg("currencyReload"),
    "{{IC_currencyReloadDark}}": svg("currencyReloadDark"),
    "{{IC_checkCircleLine}}": svg("checkCircleLine"),
    "{{IC_calendar}}":     svg("calendar"),
    "{{IC_crossCircleLine}}": svg("crossCircleLine"),
    "{{IC_swapVertical}}": svg("swapVertical"),
    "{{IC_pencil}}":       svg("pencil"),
    "{{IC_filter}}":       svg("filter"),
    "{{IC_apple}}":        strip_wh(GUIDE_APPLE),
    "{{IC_android}}":      strip_wh(GUIDE_ANDROID),
    "{{IC_share}}":        strip_wh(GUIDE_SHARE),
    "{{IC_file}}":         inline_svg_to_img(DET_FILE),
    "{{IC_spark}}":        inline_svg_to_img(DET_SPARK),
    "{{IC_smile}}":        inline_svg_to_img(DET_SMILE),
    "{{IC_neutral}}":      inline_svg_to_img(DET_NEUTRAL),
    "{{IC_checkSm}}":      inline_svg_to_img(DET_CHECK),
    "{{IC_send}}":         inline_svg_to_img(DET_SEND),
    "{{IC_couponPicto}}":  raw_svg("coupon-picto", "detail"),  # 内联矢量，避免 iOS 下 <img> 栅格化模糊
    # 优惠横幅票券：内联矢量（切角/虚线在 iOS 下不再糊）
    "{{IC_ticket1}}":      raw_svg("ticket1", "detail"),
    "{{IC_ticket1dash}}":  raw_svg("ticket1-dash", "detail"),
    "{{IC_ticket2}}":      raw_svg("ticket2", "detail"),
    "{{IC_ticket2dash}}":  raw_svg("ticket2-dash", "detail"),
    # 详情大号政策/费用图标：内联矢量，CSS 定 20px，清晰不缩小
    "{{IP_flash}}":        raw_svg("flash"),
    "{{IP_send}}":         strip_wh(DET_SEND),
    "{{IP_reload}}":       raw_svg("currencyReload"),
    "{{IP_reloadDark}}":   raw_svg("currencyReloadDark"),
    "{{IP_checkLine}}":    raw_svg("checkCircleLine"),
    "{{IP_calendar}}":     raw_svg("calendar"),
    "{{IP_crossLine}}":    raw_svg("crossCircleLine"),
    "{{IP_earth}}":        raw_svg("earthLine"),
    "{{IP_location}}":     raw_svg("locationLine", recolor=("#26BEC9", "#212121")),  # 目的地行改用地点 pin（深色）
    # 筛选 pill 选中态 cyan 图标变体
    "{{IC_arrowDownCyan}}": svg("arrowDown", recolor=("#212121", "#13A3B6")),
    "{{IC_filterCyan}}":   svg("filter", recolor=("#212121", "#13A3B6")),
    "{{IC_arrowSmRight}}": svg("arrow-sm", "detail"),
    "{{SHOTS_JSON}}":      "[" + ",".join('"' + svg_datauri(s) + '"' for s in SHOTS) + "]",
    "{{IMG_GUIDE1}}":      png_datauri("detail/guide1.png"),
    "{{IMG_GUIDE2}}":      png_datauri("detail/guide2.png"),
    "{{IMG_GUIDE3}}":      png_datauri("detail/guide3.png"),
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
