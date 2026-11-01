# -*- coding: utf-8 -*-
"""
生成「语音倒计时播报器」应用图标。
设计：深色底 + 青色秒表圆环（右上开口＝倒计时进度）+ 指针 + 右下声波弧（语音播报）。
输出：assets/icons/icon-512.png / icon-192.png / icon-maskable-512.png / apple-touch-icon.png / favicon.png
      assets/icons/icon.svg
"""
import math
import os

from PIL import Image, ImageDraw

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons")

# ---------- 配色 ----------
BG_TOP = (23, 42, 62)
BG_BOT = (9, 18, 29)
CYAN = (34, 211, 238)
NEEDLE = (226, 250, 255)

# ---------- 几何（基准 512 画布）----------
CX, CY = 220.0, 240.0          # 秒表圆心
R = 138.0                      # 圆环中线半径
RING_W = 34.0                  # 环线宽
GAP_A, GAP_B = 30.0, 90.0      # 缺口：12 点起顺时针 30°~90°（右上）
HANDLE_W, HANDLE_H, HANDLE_R = 46.0, 32.0, 10.0
NEEDLE_LEN, NEEDLE_W = 100.0, 22.0
WAVE_RADII = (184.0, 224.0)    # 声波弧半径
WAVE_A, WAVE_B = 98.0, 144.0   # 声波角度范围（12 点起顺时针，右下）
WAVE_W = 25.0


def _polar(cx, cy, radius, deg):
    """12 点方向为 0°，顺时针为正。"""
    a = math.radians(deg)
    return cx + radius * math.sin(a), cy - radius * math.cos(a)


def _to_pillow(deg):
    """Pillow 角度：3 点方向为 0°，顺时针为正。"""
    return deg - 90.0


def draw_icon(size, ss, radius_ratio, content_scale, mode):
    S = size * ss
    k = S / 512.0

    # 背景（对角向渐变 + 圆角/全幅）
    grad = Image.linear_gradient("L").resize((S, S)).rotate(-32, expand=True)
    grad = grad.crop(((grad.width - S) // 2, (grad.height - S) // 2,
                      (grad.width - S) // 2 + S, (grad.height - S) // 2 + S))
    bg = Image.composite(Image.new("RGB", (S, S), BG_TOP), Image.new("RGB", (S, S), BG_BOT), grad)
    base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if radius_ratio > 0:
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, S - 1, S - 1], radius=int(radius_ratio * S), fill=255)
        base.paste(bg, (0, 0), mask)
    else:
        base.paste(bg, (0, 0))

    # 内容绘制在独立透明层，便于整体缩放/居中
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    if content_scale != 1.0:
        # 先按 512 坐标画到临时层，再缩放并居中
        tmp = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        _draw_content(td, k)
        new = int(S * content_scale)
        tmp = tmp.resize((new, new), Image.LANCZOS)
        # 内容包围盒中心（基准坐标）→ 移到画布中心
        bbox = tmp.getbbox()
        cx_now = (bbox[0] + bbox[2]) / 2.0
        cy_now = (bbox[1] + bbox[3]) / 2.0
        ox = int(S / 2 - cx_now)
        oy = int(S / 2 - cy_now)
        cbox = tmp.getbbox()
        layer.paste(tmp, (ox + cbox[0], oy + cbox[1]), tmp)
    else:
        _draw_content(d, k)
        # 内容中心对齐到画布视觉中心
        bbox = layer.getbbox()
        ox = int(S / 2 - (bbox[0] + bbox[2]) / 2.0)
        oy = int(S / 2 - (bbox[1] + bbox[3]) / 2.0)
        moved = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        moved.paste(layer, (ox, oy))
        layer = moved

    base = Image.alpha_composite(base, layer)
    return base.resize((size, size), Image.LANCZOS)


def _draw_content(d, k):
    cx, cy = CX * k, CY * k
    r, ring_w = R * k, RING_W * k

    # 声波弧（右下，两条，外淡内浓）
    for rad, alpha in zip(WAVE_RADII, (235, 165)):
        rr = rad * k
        x0, y0 = _polar(cx, cy, rr, 0)
        x1, y1 = _polar(cx, cy, rr, 0)
        bb = [cx - rr, cy - rr, cx + rr, cy + rr]
        d.arc(bb, _to_pillow(WAVE_A), _to_pillow(WAVE_B),
              fill=CYAN + (alpha,), width=int(WAVE_W * k))
        del x0, y0, x1, y1

    # 主圆环：从 90° 顺时针绕到 30°（右上留 60° 缺口）
    bb = [cx - r, cy - r, cx + r, cy + r]
    d.arc(bb, _to_pillow(GAP_B), _to_pillow(GAP_A), fill=CYAN + (255,), width=int(ring_w))

    # 顶部表柄
    hw, hh, hr = HANDLE_W * k, HANDLE_H * k, HANDLE_R * k
    handle_bottom = cy - (r + ring_w / 2) + 6 * k
    d.rounded_rectangle([cx - hw / 2, handle_bottom - hh, cx + hw / 2, handle_bottom],
                        radius=int(hr), fill=CYAN + (255,))

    # 指针（竖直向上，圆头）
    nw = NEEDLE_W * k
    tip_y = cy - NEEDLE_LEN * k
    d.line([cx, cy + 8 * k, cx, tip_y], fill=NEEDLE + (255,), width=int(nw))
    rad = nw / 2
    d.ellipse([cx - rad, tip_y - rad, cx + rad, tip_y + rad], fill=NEEDLE + (255,))
    d.ellipse([cx - rad, cy + 8 * k - rad, cx + rad, cy + 8 * k + rad], fill=NEEDLE + (255,))


SVG_TMPL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="语音倒计时播报器">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0.6" y2="1">
      <stop offset="0" stop-color="#172A3E"/>
      <stop offset="1" stop-color="#09121D"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="{rx}" fill="url(#bg)"/>
  <g fill="none" stroke-linecap="round">
    <path d="{wave1}" stroke="#22D3EE" stroke-opacity="0.92" stroke-width="{ww}"/>
    <path d="{wave2}" stroke="#22D3EE" stroke-opacity="0.65" stroke-width="{ww}"/>
    <path d="{ring}"  stroke="#22D3EE" stroke-width="{rw}"/>
  </g>
  <rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="{hr}" fill="#22D3EE"/>
  <path d="M{cx} {nb} V {nt}" stroke="#E2FAFF" stroke-width="{nw}" stroke-linecap="round"/>
</svg>
"""


def _arc_path(cx, cy, radius, a0, a1, sweep=1, large=0):
    x0, y0 = _polar(cx, cy, radius, a0)
    x1, y1 = _polar(cx, cy, radius, a1)
    return f"M{x0:.1f} {y0:.1f} A{radius:.1f} {radius:.1f} 0 {large} {sweep} {x1:.1f} {y1:.1f}"


def build_svg(maskable=False):
    cx, cy = 256.0, 256.0
    scale = 0.78 if maskable else 1.0
    # 内容包围盒中心（基准 (220,240) 系）→ 画布中心
    pad_x = cx - 243.5
    pad_y = cy - 237.0
    cx = CX + pad_x
    cy = CY + pad_y
    r, rw = R, RING_W
    if maskable:
        content = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        del content

    def sc(v):
        return v * scale if maskable else v

    ring = _arc_path(cx, cy, sc(r), GAP_B, GAP_B + 300, sweep=1, large=1)
    w1 = _arc_path(cx, cy, sc(WAVE_RADII[0]), WAVE_A, WAVE_B)
    w2 = _arc_path(cx, cy, sc(WAVE_RADII[1]), WAVE_A, WAVE_B)
    hb = cy - (sc(r) + sc(rw) / 2) + 6 * scale
    return SVG_TMPL.format(
        rx=0 if maskable else 112,
        ring=ring, wave1=w1, wave2=w2,
        ww=f"{sc(WAVE_W):.1f}", rw=f"{sc(rw):.1f}",
        hx=f"{cx - sc(HANDLE_W) / 2:.1f}", hy=f"{hb - sc(HANDLE_H):.1f}",
        hw=f"{sc(HANDLE_W):.1f}", hh=f"{sc(HANDLE_H):.1f}", hr=f"{sc(HANDLE_R):.1f}",
        cx=f"{cx:.1f}", nb=f"{cy + 8 * scale:.1f}",
        nt=f"{cy - sc(NEEDLE_LEN):.1f}", nw=f"{sc(NEEDLE_W):.1f}",
    )


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    normal = draw_icon(512, 3, 0.22, 1.0, "normal")
    normal.save(os.path.join(OUT_DIR, "icon-512.png"))
    normal.resize((192, 192), Image.LANCZOS).save(os.path.join(OUT_DIR, "icon-192.png"))
    normal.resize((180, 180), Image.LANCZOS).save(os.path.join(OUT_DIR, "apple-touch-icon.png"))
    normal.resize((64, 64), Image.LANCZOS).save(os.path.join(OUT_DIR, "favicon.png"))

    mask = draw_icon(512, 3, 0.0, 0.78, "maskable")
    mask.save(os.path.join(OUT_DIR, "icon-maskable-512.png"))

    with open(os.path.join(OUT_DIR, "icon.svg"), "w", encoding="utf-8") as f:
        f.write(build_svg(False))
    with open(os.path.join(OUT_DIR, "icon-maskable.svg"), "w", encoding="utf-8") as f:
        f.write(build_svg(True))

    for n in sorted(os.listdir(OUT_DIR)):
        print("  ->", n)


if __name__ == "__main__":
    main()
