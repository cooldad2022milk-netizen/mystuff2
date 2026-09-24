"""
Generates the small art assets: ability-wheel icons, item sprites, particles, chain/cord textures,
the crossbow bolt GeckoLib model, item models and particle definitions.
"""
import json
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "models"))
from csmgen.geo import Atlas, Model, Anim, save_animations, norm  # noqa: E402
from csmgen.tex import paint_atlas  # noqa: E402

ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "src", "main", "resources")
ASSETS = os.path.join(RES, "assets", "csm")


def p(*parts):
    path = os.path.join(ASSETS, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


# ----------------------------------------------------------------------------- ability icons
S = 128  # drawn big, downsampled to 32 for smooth edges


def icon_canvas(bg1, bg2):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for r in range(60, 0, -1):
        t = r / 60
        c = tuple(int(bg1[i] * t + bg2[i] * (1 - t)) for i in range(3)) + (255,)
        d.ellipse([64 - r, 64 - r, 64 + r, 64 + r], fill=c)
    d.ellipse([4, 4, 124, 124], outline=(20, 8, 8, 255), width=5)
    return img, d


def finish(img, name):
    img = img.resize((32, 32), Image.LANCZOS)
    img.save(p("textures", "gui", "ability", name + ".png"))


def poly(d, pts, fill, outline=(15, 10, 10, 255), width=3):
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=outline, width=width)


def saw_bar(d, x0, y0, x1, y1, w=16):
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang) * w / 2, math.cos(ang) * w / 2
    pts = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
    poly(d, pts, (200, 205, 212, 255))
    d.ellipse([x1 - w / 2, y1 - w / 2, x1 + w / 2, y1 + w / 2], fill=(200, 205, 212, 255), outline=(15, 10, 10, 255), width=3)
    L = math.hypot(x1 - x0, y1 - y0)
    for i in range(1, int(L / 9)):
        t = i * 9 / L
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for s in (1, -1):
            tx, ty = cx + nx * s * 1.35, cy + ny * s * 1.35
            d.polygon([(tx - 3, ty - 3), (tx + 3, ty - 3), (tx, ty + 3)], fill=(60, 60, 66, 255))


def heart_shape(d, cx, cy, s, fill, outline=(20, 5, 5, 255)):
    pts = []
    for i in range(64):
        t = i / 64 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * s, cy + y * s))
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=outline, width=4)


def flame(d, cx, cy, s, colors=((255, 90, 10), (255, 190, 40), (255, 250, 200))):
    for k, col in enumerate(colors):
        f = 1 - k * 0.3
        pts = [(cx, cy - 40 * s * f), (cx + 18 * s * f, cy - 5 * s * f), (cx + 12 * s * f, cy + 20 * s * f),
               (cx, cy + 26 * s * f), (cx - 12 * s * f, cy + 20 * s * f), (cx - 18 * s * f, cy - 5 * s * f)]
        d.polygon(pts, fill=col + (255,))


def arrow_shape(d, x0, y0, x1, y1, col=(225, 228, 235, 255)):
    d.line([(x0, y0), (x1, y1)], fill=(60, 50, 44, 255), width=7)
    ang = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 + math.cos(ang) * 16, y1 + math.sin(ang) * 16)
    l = (x1 + math.cos(ang + 2.4) * 10, y1 + math.sin(ang + 2.4) * 10)
    r = (x1 + math.cos(ang - 2.4) * 10, y1 + math.sin(ang - 2.4) * 10)
    poly(d, [tip, l, r], col, width=2)
    for s in (1, -1):
        fx = x0 + math.cos(ang) * 6
        fy = y0 + math.sin(ang) * 6
        d.polygon([(x0, y0), (fx + math.cos(ang + s * 2.2) * 12, fy + math.sin(ang + s * 2.2) * 12), (fx, fy)],
                  fill=(240, 240, 240, 255))


def blood_drops(d, pts):
    for x, y, r in pts:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(170, 10, 14, 255))
        d.polygon([(x - r * 0.7, y - r * 0.4), (x, y - r * 2.4), (x + r * 0.7, y - r * 0.4)], fill=(170, 10, 14, 255))


def icons():
    OR = ((250, 140, 50), (120, 40, 10))
    GR = ((150, 160, 180), (30, 32, 40))
    FR = ((250, 120, 40), (70, 12, 6))

    img, d = icon_canvas(*OR)  # pull cord
    d.line([(40, 30), (64, 64)], fill=(20, 20, 20, 255), width=6)
    poly(d, [(18, 20), (62, 20), (62, 34), (18, 34)], (30, 30, 34, 255))
    heart_shape(d, 70, 78, 2.0, (170, 20, 24, 255))
    d.line([(64, 64), (70, 70)], fill=(20, 20, 20, 255), width=6)
    finish(img, "pull_cord")

    img, d = icon_canvas(*OR)  # slash
    saw_bar(d, 26, 100, 100, 26)
    d.arc([10, 10, 118, 118], 200, 340, fill=(255, 255, 255, 230), width=6)
    blood_drops(d, [(90, 96, 6), (100, 80, 4)])
    finish(img, "chainsaw_slash")

    img, d = icon_canvas(*OR)  # headsaw charge
    d.ellipse([22, 50, 76, 104], fill=(236, 112, 34, 255), outline=(20, 10, 10, 255), width=4)
    for i in range(6):
        x = 30 + i * 7
        d.polygon([(x, 84), (x + 6, 84), (x + 3, 94)], fill=(250, 245, 230, 255))
    saw_bar(d, 56, 60, 112, 34, 14)
    for k in range(3):
        d.line([(10, 50 + k * 16), (26, 50 + k * 16)], fill=(255, 255, 255, 200), width=4)
    finish(img, "headsaw_charge")

    img, d = icon_canvas(*OR)  # chain grapple
    for i in range(8):
        cx, cy = 22 + i * 11, 100 - i * 10
        if i % 2 == 0:
            d.ellipse([cx - 8, cy - 5, cx + 8, cy + 5], outline=(210, 214, 220, 255), width=4)
        else:
            d.ellipse([cx - 5, cy - 8, cx + 5, cy + 8], outline=(160, 164, 170, 255), width=4)
    poly(d, [(104, 16), (112, 44), (92, 30)], (230, 232, 236, 255))
    finish(img, "chain_grapple")

    img, d = icon_canvas(*OR)  # rip & tear
    saw_bar(d, 20, 90, 108, 90, 18)
    saw_bar(d, 64, 18, 64, 110, 18)
    blood_drops(d, [(40, 60, 8), (88, 50, 6), (80, 110, 7), (30, 110, 5)])
    finish(img, "rip_and_tear")

    img, d = icon_canvas(*OR)  # leg saw spin
    d.arc([16, 16, 112, 112], 0, 300, fill=(255, 255, 255, 220), width=7)
    d.polygon([(112, 64), (98, 50), (122, 46)], fill=(255, 255, 255, 230))
    poly(d, [(54, 30), (72, 30), (70, 92), (56, 92)], (40, 40, 52, 255))
    saw_bar(d, 70, 70, 112, 88, 12)
    saw_bar(d, 56, 70, 16, 88, 12)
    finish(img, "leg_saw_spin")

    img, d = icon_canvas((200, 30, 30), (50, 4, 6))  # blood drink
    d.polygon([(40, 30), (88, 30), (80, 108), (48, 108)], fill=(230, 235, 240, 120), outline=(240, 240, 240, 255))
    d.polygon([(46, 60), (82, 60), (78, 104), (50, 104)], fill=(170, 10, 14, 255))
    blood_drops(d, [(64, 22, 7)])
    finish(img, "blood_drink")

    img, d = icon_canvas(*GR)  # pull arrow (from the right eye)
    d.ellipse([20, 40, 108, 88], fill=(230, 220, 210, 255), outline=(20, 20, 20, 255), width=4)
    d.ellipse([50, 50, 78, 78], fill=(30, 10, 10, 255))
    arrow_shape(d, 66, 64, 108, 16)
    blood_drops(d, [(60, 96, 6), (72, 104, 4)])
    finish(img, "pull_arrow")

    img, d = icon_canvas(*GR)  # volley
    for k in range(-1, 2):
        arrow_shape(d, 20, 64 + k * 26, 96, 64 + k * 26 * 0.4)
    finish(img, "crossbow_volley")

    img, d = icon_canvas(*GR)  # piercing bolt
    d.ellipse([60, 40, 100, 88], fill=(20, 20, 24, 255), outline=(200, 200, 210, 255), width=6)
    d.line([(10, 64), (70, 64)], fill=(255, 120, 90, 255), width=12)
    arrow_shape(d, 16, 64, 96, 64, (255, 200, 180, 255))
    finish(img, "piercing_bolt")

    img, d = icon_canvas(*GR)  # flash step
    for k, a in enumerate((70, 140, 220)):
        d.polygon([(20 + k * 8, 40 + k * 16), (100, 30 + k * 18), (100, 36 + k * 18), (20 + k * 8, 46 + k * 16)],
                  fill=(255, 255, 255, a))
    poly(d, [(82, 20), (110, 64), (82, 108), (96, 64)], (230, 232, 238, 255))
    finish(img, "flash_step")

    img, d = icon_canvas(*GR)  # arrow storm
    for k in range(7):
        x = 22 + k * 14
        arrow_shape(d, x, 10 + (k % 2) * 12, x, 70 + (k % 3) * 10)
    d.ellipse([20, 96, 108, 116], outline=(255, 90, 60, 255), width=4)
    finish(img, "arrow_storm")

    img, d = icon_canvas(*FR)  # bite molar
    for i in range(4):
        poly(d, [(24 + i * 20, 40), (40 + i * 20, 40), (38 + i * 20, 64), (26 + i * 20, 64)], (245, 240, 225, 255))
        poly(d, [(26 + i * 20, 72), (38 + i * 20, 72), (40 + i * 20, 96), (24 + i * 20, 96)], (245, 240, 225, 255))
    poly(d, [(64, 44), (80, 44), (78, 64), (66, 64)], (255, 200, 60, 255))
    flame(d, 100, 40, 0.45)
    finish(img, "bite_molar")

    img, d = icon_canvas(*FR)  # flame stream
    poly(d, [(10, 56), (44, 56), (44, 72), (10, 72)], (70, 70, 76, 255))
    for k in range(5):
        r = 10 + k * 7
        d.ellipse([48 + k * 14 - r / 2, 64 - r, 48 + k * 14 + r / 2 + 8, 64 + r],
                  fill=(255, 110 + k * 25, 20, 220))
    finish(img, "flame_stream")

    img, d = icon_canvas(*FR)  # napalm shot
    d.ellipse([54, 30, 104, 80], fill=(255, 120, 20, 255), outline=(60, 10, 0, 255), width=4)
    d.ellipse([66, 42, 90, 66], fill=(255, 230, 140, 255))
    for k in range(3):
        d.line([(20 + k * 10, 100 - k * 8), (56, 70)], fill=(255, 160, 40, 200), width=5)
    flame(d, 40, 110, 0.35)
    finish(img, "napalm_shot")

    img, d = icon_canvas(*FR)  # inferno burst
    for k in range(12):
        a = k / 12 * 2 * math.pi
        flame(d, 64 + math.cos(a) * 38, 70 + math.sin(a) * 30, 0.25)
    poly(d, [(56, 40), (72, 40), (70, 80), (58, 80)], (70, 70, 76, 255))
    finish(img, "inferno_burst")

    img, d = icon_canvas(*FR)  # conflagration
    d.arc([14, 14, 114, 114], 0, 320, fill=(255, 200, 60, 255), width=8)
    for k in range(6):
        a = k / 6 * 2 * math.pi
        flame(d, 64 + math.cos(a) * 30, 72 + math.sin(a) * 30, 0.3)
    flame(d, 64, 72, 0.5)
    finish(img, "conflagration")

    img, d = icon_canvas((255, 140, 60), (60, 10, 6))  # molar regeneration
    heart_shape(d, 64, 66, 2.6, (200, 30, 30, 255))
    d.rectangle([58, 44, 70, 88], fill=(255, 255, 255, 255))
    d.rectangle([42, 60, 86, 72], fill=(255, 255, 255, 255))
    flame(d, 100, 30, 0.35)
    finish(img, "molar_regeneration")


def whip_line(d, pts, w0=9, w1=2, col=(212, 84, 66, 255), dark=(110, 30, 26, 255)):
    """Tapered whip along a polyline (smoothed with a Catmull-Rom pass)."""
    fine = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        for s in range(8):
            t = s / 8
            fine.append(tuple(0.5 * ((2 * P[i][k]) + (-P[i - 1][k] + P[i + 1][k]) * t
                                     + (2 * P[i - 1][k] - 5 * P[i][k] + 4 * P[i + 1][k] - P[i + 2][k]) * t * t
                                     + (-P[i - 1][k] + 3 * P[i][k] - 3 * P[i + 1][k] + P[i + 2][k]) * t ** 3)
                              for k in range(2)))
    fine.append(pts[-1])
    n = len(fine)
    for i in range(n - 1):
        w = w0 + (w1 - w0) * i / (n - 1)
        d.line([fine[i], fine[i + 1]], fill=dark, width=int(w + 3))
    for i in range(n - 1):
        w = w0 + (w1 - w0) * i / (n - 1)
        d.line([fine[i], fine[i + 1]], fill=col, width=max(int(w), 1))
    x, y = fine[-1]
    d.polygon([(x - 4, y - 4), (x + 5, y), (x - 4, y + 4)], fill=(250, 220, 200, 255))


def crack_star(d, cx, cy, r, col=(255, 255, 255, 240)):
    for k in range(8):
        a = k / 8 * 2 * math.pi
        rr = r if k % 2 == 0 else r * 0.55
        d.line([(cx, cy), (cx + math.cos(a) * rr, cy + math.sin(a) * rr)], fill=col, width=3)


def bomb_shape(d, cx, cy, s=1.0, angle=0.0):
    rx, ry = 30 * s, 22 * s
    ca, sa = math.cos(angle), math.sin(angle)

    def R(x, y):
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)

    tail = [R(rx * 0.8, -ry * 0.9), R(rx * 1.55, -ry * 1.05), R(rx * 1.55, ry * 1.05), R(rx * 0.8, ry * 0.9)]
    d.polygon(tail, fill=(52, 52, 60, 255), outline=(12, 12, 14, 255))
    d.line([R(rx * 1.2, -ry), R(rx * 1.2, ry)], fill=(20, 20, 24, 255), width=3)
    egg = [R(math.cos(t) * rx * (1.0 if math.cos(t) < 0 else 0.92), math.sin(t) * ry) for t in
           np.linspace(0, 2 * math.pi, 40)]
    d.polygon(egg, fill=(40, 40, 48, 255), outline=(10, 10, 12, 255))
    d.line([R(-rx * 0.1, -ry * 0.98), R(-rx * 0.1, ry * 0.98)], fill=(96, 96, 106, 255), width=int(4 * s) + 1)
    d.ellipse([R(-rx * 0.62, -ry * 0.62)[0] - 5 * s, R(-rx * 0.62, -ry * 0.62)[1] - 3 * s,
               R(-rx * 0.62, -ry * 0.62)[0] + 7 * s, R(-rx * 0.62, -ry * 0.62)[1] + 3 * s], fill=(130, 130, 144, 255))
    for i in range(5):
        x = -rx * 0.95 + i * 5 * s
        d.rectangle([R(x, ry * 0.2)[0] - 2 * s, R(x, ry * 0.2)[1], R(x, ry * 0.2)[0] + 2 * s, R(x, ry * 0.2)[1] + 7 * s],
                    fill=(236, 230, 214, 255))


def boom(d, cx, cy, r):
    pts = []
    for k in range(18):
        a = k / 18 * 2 * math.pi
        rr = r * (1.0 if k % 2 == 0 else 0.62)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=(255, 120, 20, 255), outline=(120, 30, 0, 255))
    pts2 = [(cx + (x - cx) * 0.6, cy + (y - cy) * 0.6) for x, y in pts]
    d.polygon(pts2, fill=(255, 220, 90, 255))
    d.ellipse([cx - r * 0.22, cy - r * 0.22, cx + r * 0.22, cy + r * 0.22], fill=(255, 255, 230, 255))


def spear_shape(d, x0, y0, x1, y1, w=10, col=(226, 150, 118, 255)):
    """Shaft from (x0,y0) to a leaf blade ending at (x1,y1)."""
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    bl = min(L * 0.38, 38)
    bx, by = x1 - ux * bl, y1 - uy * bl
    d.line([(x0, y0), (bx, by)], fill=(40, 20, 16, 255), width=7)
    d.line([(x0, y0), (bx, by)], fill=(176, 104, 80, 255), width=4)
    blade = []
    for i in range(13):
        t = i / 12
        ww = w * (0.45 + 0.55 * math.sin(t / 0.32 * math.pi / 2)) if t < 0.32 else w * math.cos((t - 0.32) / 0.68 * math.pi / 2)
        blade.append((bx + ux * bl * t + nx * ww, by + uy * bl * t + ny * ww))
    blade += [(bx + ux * bl * t - nx * ww, by + uy * bl * t - ny * ww) for (t, ww) in
              [(i / 12, (w * (0.45 + 0.55 * math.sin((i / 12) / 0.32 * math.pi / 2)) if i / 12 < 0.32 else
                         w * math.cos((i / 12 - 0.32) / 0.68 * math.pi / 2))) for i in range(12, -1, -1)]]
    d.polygon(blade, fill=col, outline=(40, 18, 14, 255))
    d.line([(bx, by), (x1 - ux * 3, y1 - uy * 3)], fill=(255, 232, 214, 255), width=2)


def icons2():
    WH = ((250, 140, 116), (96, 24, 22))
    BO = ((255, 176, 70), (40, 28, 30))
    SP = ((120, 58, 46), (22, 10, 8))

    # ------------------------------------------------------------------ whip
    img, d = icon_canvas(*WH)  # snap fingers
    poly(d, [(40, 100), (40, 58), (54, 50), (78, 54), (78, 100)], (236, 190, 170, 255))
    poly(d, [(54, 50), (58, 24), (68, 22), (68, 54)], (236, 190, 170, 255))
    poly(d, [(64, 60), (90, 40), (98, 48), (76, 70)], (236, 190, 170, 255))
    crack_star(d, 76, 36, 22)
    for k in range(3):
        d.arc([84 - k * 6, 12 - k * 6, 124 + k * 6, 52 + k * 6], 200, 330, fill=(255, 255, 255, 180 - k * 50), width=3)
    finish(img, "snap_fingers")

    img, d = icon_canvas(*WH)  # lash
    whip_line(d, [(16, 108), (30, 70), (60, 44), (100, 36), (116, 16)])
    whip_line(d, [(24, 112), (48, 84), (84, 74), (112, 60)], 7, 2, (190, 66, 52, 255))
    crack_star(d, 114, 18, 12)
    blood_drops(d, [(98, 94, 6), (84, 106, 4)])
    finish(img, "whip_lash")

    img, d = icon_canvas(*WH)  # storm
    for k in range(5):
        a = k / 5 * 2 * math.pi
        pts = [(64 + math.cos(a + s * 0.35) * (10 + s * 12), 64 + math.sin(a + s * 0.35) * (10 + s * 12)) for s in range(5)]
        whip_line(d, pts, 7, 2)
    d.ellipse([54, 54, 74, 74], fill=(224, 96, 74, 255), outline=(90, 20, 16, 255), width=3)
    finish(img, "whip_storm")

    img, d = icon_canvas(*WH)  # snare
    whip_line(d, [(10, 110), (40, 80), (70, 70), (86, 64)], 8, 4)
    for k in range(4):
        d.arc([74 - k * 3, 30 + k * 4, 114 + k * 3, 74 + k * 4], 0, 360, fill=(212, 84, 66, 255), width=4)
    poly(d, [(88, 24), (100, 24), (104, 96), (84, 96)], (60, 60, 70, 255))
    for k in range(3):
        d.line([(30 - k * 6, 40 + k * 10), (56 - k * 6, 40 + k * 10)], fill=(255, 255, 255, 200), width=3)
    finish(img, "whip_snare")

    img, d = icon_canvas(*WH)  # swing
    d.rectangle([80, 8, 124, 26], fill=(90, 86, 90, 255), outline=(30, 30, 34, 255))
    whip_line(d, [(30, 104), (52, 70), (80, 40), (98, 22)], 7, 3)
    d.arc([10, 60, 70, 120], 120, 260, fill=(255, 255, 255, 200), width=4)
    finish(img, "whip_swing")

    img, d = icon_canvas(*WH)  # sonic crack
    whip_line(d, [(14, 100), (24, 40), (56, 20), (90, 44), (112, 62)], 8, 2)
    for k in range(4):
        r = 14 + k * 12
        d.arc([112 - r, 62 - r, 112 + r, 62 + r], 120, 240, fill=(255, 255, 255, 230 - k * 45), width=4)
    crack_star(d, 112, 62, 14)
    finish(img, "sonic_crack")

    # ------------------------------------------------------------------ bomb
    img, d = icon_canvas(*BO)  # pull pin
    d.rectangle([14, 74, 114, 90], fill=(20, 20, 22, 255))
    d.ellipse([54, 30, 94, 70], outline=(220, 222, 228, 255), width=7)
    d.line([(58, 66), (48, 82)], fill=(220, 222, 228, 255), width=5)
    d.polygon([(90, 26), (110, 10), (106, 30)], fill=(255, 240, 180, 255))
    for k in range(5):
        a = -0.5 + k * 0.3
        d.line([(74, 50), (74 + math.cos(a) * 44, 50 + math.sin(a) * 44 - 20)], fill=(255, 200, 80, 150), width=2)
    finish(img, "pull_pin")

    img, d = icon_canvas(*BO)  # explosive combo
    poly(d, [(14, 58), (56, 50), (62, 78), (14, 84)], (236, 196, 172, 255))
    boom(d, 82, 64, 36)
    finish(img, "explosive_combo")

    img, d = icon_canvas(*BO)  # spark flick
    poly(d, [(10, 96), (40, 70), (54, 78), (24, 108)], (236, 196, 172, 255))
    poly(d, [(40, 70), (58, 56), (64, 62), (54, 78)], (236, 196, 172, 255))
    for k in range(4):
        d.line([(62 + k * 9, 56 - k * 9), (68 + k * 9, 50 - k * 9)], fill=(255, 200, 80, 255), width=4)
    boom(d, 102, 24, 18)
    finish(img, "spark_flick")

    img, d = icon_canvas(*BO)  # blast propulsion
    poly(d, [(62, 20), (86, 44), (58, 72), (40, 54)], (60, 60, 70, 255))
    for cx, cy, r in ((34, 90, 22), (60, 104, 16), (18, 108, 14)):
        boom(d, cx, cy, r)
    for k in range(3):
        d.line([(92 + k * 8, 16 + k * 4), (112 + k * 4, 4 + k * 4)], fill=(255, 255, 255, 200), width=3)
    finish(img, "blast_propulsion")

    img, d = icon_canvas(*BO)  # torpedo
    d.polygon([(14, 52), (84, 52), (112, 64), (84, 76), (14, 76)], fill=(92, 100, 90, 255), outline=(20, 24, 20, 255))
    d.rectangle([60, 52, 68, 76], fill=(200, 36, 30, 255))
    d.polygon([(14, 52), (4, 40), (22, 52)], fill=(92, 100, 90, 255))
    d.polygon([(14, 76), (4, 88), (22, 76)], fill=(92, 100, 90, 255))
    boom(d, 116, 64, 12)
    finish(img, "torpedo")

    img, d = icon_canvas(*BO)  # head bomb
    bomb_shape(d, 58, 60, 1.0, -0.4)
    d.line([(40, 30), (34, 14)], fill=(150, 116, 70, 255), width=4)
    boom(d, 34, 12, 10)
    for k in range(3):
        d.arc([60 + k * 8, 70 + k * 8, 120 + k * 4, 124], 200, 300, fill=(255, 255, 255, 200 - k * 60), width=3)
    finish(img, "head_bomb")

    # ------------------------------------------------------------------ spear
    img, d = icon_canvas(*SP)  # pull spear (from the nape)
    d.ellipse([22, 40, 86, 104], fill=(236, 196, 170, 255), outline=(20, 10, 8, 255), width=3)
    d.rectangle([22, 36, 86, 60], fill=(40, 26, 20, 255))
    spear_shape(d, 70, 96, 116, 14, 9)
    blood_drops(d, [(72, 106, 6), (60, 114, 4)])
    finish(img, "pull_spear")

    img, d = icon_canvas(*SP)  # thrust
    spear_shape(d, 6, 64, 120, 64, 10)
    for k in range(3):
        d.line([(14, 44 + k * 20), (46, 44 + k * 20)], fill=(255, 255, 255, 190), width=3)
    finish(img, "spear_thrust")

    img, d = icon_canvas(*SP)  # throw
    spear_shape(d, 10, 118, 118, 10, 10)
    for k in range(4):
        d.line([(8 + k * 12, 92 - k * 12), (26 + k * 12, 110 - k * 12)], fill=(255, 255, 255, 170), width=2)
    finish(img, "spear_throw")

    img, d = icon_canvas(*SP)  # volley
    for k in range(6):
        x = 14 + k * 20
        spear_shape(d, x - 8, 118 - (k % 2) * 8, x + 12, 20 + (k % 2) * 10, 6)
    finish(img, "spear_volley")

    img, d = icon_canvas(*SP)  # impale
    poly(d, [(40, 20), (82, 20), (86, 108), (36, 108)], (70, 70, 80, 255))
    spear_shape(d, 118, 96, 10, 40, 9)
    blood_drops(d, [(24, 58, 7), (34, 72, 5), (50, 100, 6)])
    finish(img, "spear_impale")

    img, d = icon_canvas(*SP)  # eruption
    d.chord([6, 6, 122, 122], 25, 155, fill=(92, 70, 54, 255))
    for k in range(5):
        x = 16 + k * 24
        h = 40 + (k % 2) * 26
        spear_shape(d, x, 110, x + (k - 2) * 3, 100 - h, 7)
        d.polygon([(x - 10, 98), (x, 90), (x + 10, 98)], fill=(60, 44, 34, 255))
    finish(img, "spear_eruption")


# ----------------------------------------------------------------------------- katana / longsword / fiends
def katana_draw(d, x0, y0, x1, y1, w=6, col=(226, 230, 238, 255)):
    """Curved single-edged blade from (x0,y0) (guard) to (x1,y1) (tip) with tsuba and grip behind."""
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    pts_a, pts_b = [], []
    for i in range(13):
        t = i / 12
        bow = math.sin(t * math.pi) * L * 0.05
        cx, cy = x0 + ux * L * t + nx * bow, y0 + uy * L * t + ny * bow
        ww = w * (1 - 0.5 * t) if t < 0.92 else w * 0.46 * (1 - (t - 0.92) / 0.08)
        pts_a.append((cx + nx * ww * 0.5, cy + ny * ww * 0.5))
        pts_b.append((cx - nx * ww * 0.5, cy - ny * ww * 0.5))
    d.polygon(pts_a + pts_b[::-1], fill=col, outline=(40, 40, 50, 255))
    d.line(pts_b, fill=(255, 255, 255, 255), width=2)
    gx, gy = x0 - ux * 16, y0 - uy * 16
    d.line([(x0, y0), (gx, gy)], fill=(30, 26, 50, 255), width=int(w + 2))
    for k in range(4):
        t = (k + 0.5) / 4
        cx, cy = x0 - ux * 16 * t, y0 - uy * 16 * t
        d.line([(cx - nx * 4, cy - ny * 4), (cx + nx * 4, cy + ny * 4)], fill=(236, 230, 214, 255), width=2)
    d.ellipse([x0 - 7, y0 - 7, x0 + 7, y0 + 7], fill=(60, 60, 66, 255), outline=(212, 170, 70, 255), width=2)


def longsword_draw(d, x0, y0, x1, y1, w=10):
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    tipx, tipy = x1, y1
    bx, by = x1 - ux * w * 1.4, y1 - uy * w * 1.4
    poly(d, [(x0 + nx * w / 2, y0 + ny * w / 2), (bx + nx * w / 2, by + ny * w / 2), (tipx, tipy),
             (bx - nx * w / 2, by - ny * w / 2), (x0 - nx * w / 2, y0 - ny * w / 2)], (214, 218, 228, 255), width=2)
    d.line([(x0, y0), (bx, by)], fill=(150, 156, 168, 255), width=2)
    d.line([(x0 + nx * 13, y0 + ny * 13), (x0 - nx * 13, y0 - ny * 13)], fill=(90, 92, 104, 255), width=5)
    d.line([(x0, y0), (x0 - ux * 14, y0 - uy * 14)], fill=(52, 36, 30, 255), width=5)


def horn_draw(d, x, y, s, lean, col=(236, 112, 112, 255)):
    pts = []
    for i in range(9):
        t = i / 8
        pts.append((x + lean * 22 * s * t * t, y - 40 * s * t))
    for i in range(8):
        w = 7 * s * (1 - i / 8) + 1
        d.line([pts[i], pts[i + 1]], fill=col, width=int(w))


def shark_head_draw(d, cx, cy, s=1.0, eyes=0):
    body = [(cx - 44 * s, cy + 6 * s), (cx - 20 * s, cy - 22 * s), (cx + 26 * s, cy - 20 * s), (cx + 50 * s, cy - 2 * s),
            (cx + 30 * s, cy + 18 * s), (cx - 30 * s, cy + 20 * s)]
    poly(d, body, (112, 138, 160, 255))
    d.polygon([(cx - 6 * s, cy - 21 * s), (cx + 6 * s, cy - 50 * s), (cx + 20 * s, cy - 20 * s)], fill=(74, 96, 118, 255))
    d.polygon([(cx - 36 * s, cy + 8 * s), (cx + 34 * s, cy + 4 * s), (cx + 26 * s, cy + 16 * s), (cx - 26 * s, cy + 18 * s)],
              fill=(60, 14, 22, 255))
    for k in range(9):
        x = cx - 30 * s + k * 7 * s
        d.polygon([(x, cy + 6 * s), (x + 3.5 * s, cy + 13 * s), (x + 7 * s, cy + 6 * s)], fill=(242, 240, 232, 255))
    for k in range(eyes):
        d.ellipse([cx + (8 + k * 11) * s - 3, cy - 8 * s - 3, cx + (8 + k * 11) * s + 3, cy - 8 * s + 3], fill=(8, 8, 10, 255))


def mask_draw(d, cx, cy, s=1.0):
    d.rounded_rectangle([cx - 26 * s, cy - 30 * s, cx + 22 * s, cy + 20 * s], radius=int(8 * s), fill=(74, 176, 70, 255),
                        outline=(20, 50, 20, 255), width=3)
    d.polygon([(cx + 8 * s, cy - 2 * s), (cx + 58 * s, cy + 22 * s), (cx + 6 * s, cy + 16 * s)], fill=(214, 52, 38, 255),
              outline=(90, 20, 14, 255))
    d.polygon([(cx + 40 * s, cy + 14 * s), (cx + 58 * s, cy + 22 * s), (cx + 38 * s, cy + 20 * s)], fill=(240, 150, 40, 255))
    for ex in (-12, 6):
        d.ellipse([cx + (ex - 8) * s, cy - 20 * s, cx + (ex + 8) * s, cy - 4 * s], fill=(20, 22, 30, 255),
                  outline=(206, 166, 72, 255), width=3)


def brain_draw(d, cx, cy, r, col=(236, 150, 170, 255)):
    d.ellipse([cx - r, cy - r * 0.75, cx + r, cy + r * 0.75], fill=col, outline=(150, 60, 90, 255), width=2)
    for k in range(5):
        a = k / 5 * math.pi
        d.arc([cx - r * 0.8, cy - r * 0.5 + k * r * 0.2 - r * 0.3, cx + r * 0.8, cy - r * 0.2 + k * r * 0.2],
              200, 340, fill=(180, 80, 110, 255), width=2)


def pistol_draw(d, x, y, s=1.0, facing=1):
    f = facing
    d.rectangle([x, y, x + f * 44 * s, y + 10 * s] if f > 0 else [x + f * 44 * s, y, x, y + 10 * s], fill=(56, 58, 64, 255),
                outline=(20, 20, 24, 255))
    d.polygon([(x + f * 4 * s, y + 10 * s), (x + f * 14 * s, y + 10 * s), (x + f * 10 * s, y + 30 * s),
               (x - f * 2 * s, y + 28 * s)], fill=(40, 40, 44, 255))
    d.ellipse([x + f * 42 * s - 3, y + 2 * s, x + f * 42 * s + 3, y + 8 * s], fill=(0, 0, 0, 255))


def star_burst(d, cx, cy, r, col=(255, 200, 240, 255), n=10):
    for k in range(n):
        a = k / n * 2 * math.pi
        rr = r if k % 2 == 0 else r * 0.45
        d.line([(cx, cy), (cx + math.cos(a) * rr, cy + math.sin(a) * rr)], fill=col, width=3)
    d.ellipse([cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2], fill=(255, 255, 255, 255))


def tracer(d, x0, y0, x1, y1):
    d.line([(x0, y0), (x1, y1)], fill=(255, 220, 120, 230), width=3)
    d.ellipse([x0 - 6, y0 - 6, x0 + 6, y0 + 6], fill=(255, 240, 180, 255))


def icons3():
    KT = ((214, 214, 226), (60, 14, 20))
    LS = ((160, 166, 186), (26, 26, 34))
    BL = ((236, 70, 80), (56, 4, 10))
    SH = ((120, 176, 214), (12, 28, 50))
    VI = ((120, 206, 104), (18, 48, 20))
    CO = ((236, 140, 206), (40, 16, 70))
    GU = ((176, 176, 186), (28, 28, 34))
    SKIN = (228, 190, 160, 255)

    # ------------------------------------------------------------------ katana
    img, d = icon_canvas(*KT)  # pull off the left hand
    poly(d, [(18, 70), (56, 62), (60, 84), (22, 92)], SKIN)
    d.rectangle([56, 60, 64, 88], fill=(150, 20, 24, 255))
    katana_draw(d, 64, 74, 114, 20, 7)
    poly(d, [(70, 92), (96, 88), (100, 108), (74, 112)], SKIN)
    blood_drops(d, [(58, 100, 5), (66, 112, 4)])
    finish(img, "pull_left_hand")
    img, d = icon_canvas(*KT)  # sword-draw dash
    for k in range(4):
        d.line([(10, 40 + k * 14), (78, 40 + k * 14)], fill=(255, 255, 255, 170 - k * 30), width=3)
    katana_draw(d, 70, 90, 120, 50, 6)
    d.line([(18, 104), (110, 24)], fill=(200, 16, 24, 255), width=5)
    finish(img, "sword_draw_dash")
    img, d = icon_canvas(*KT)  # twin slash
    katana_draw(d, 26, 104, 108, 26, 6)
    katana_draw(d, 102, 104, 20, 26, 6)
    blood_drops(d, [(64, 70, 7)])
    finish(img, "twin_slash")
    img, d = icon_canvas(*KT)  # blade flurry
    for k in range(5):
        a = math.radians(-60 + k * 30)
        d.arc([14 + k * 3, 14 + k * 3, 114 - k * 3, 114 - k * 3], 200 + k * 25, 250 + k * 25, fill=(255, 255, 255, 220), width=4)
    katana_draw(d, 40, 96, 104, 36, 6)
    finish(img, "blade_flurry")
    img, d = icon_canvas(*KT)  # iai counter
    katana_draw(d, 30, 84, 100, 84, 6)
    d.rectangle([20, 78, 38, 90], fill=(20, 20, 26, 255))
    crack_star(d, 64, 44, 18)
    finish(img, "iai_counter")

    # ------------------------------------------------------------------ longsword
    img, d = icon_canvas(*LS)  # pull off the right hand
    poly(d, [(72, 70), (110, 62), (112, 84), (76, 92)], SKIN)
    longsword_draw(d, 60, 76, 14, 18, 10)
    blood_drops(d, [(66, 96, 5)])
    finish(img, "pull_right_hand")
    img, d = icon_canvas(*LS)  # cleave
    longsword_draw(d, 64, 20, 64, 104, 12)
    d.arc([20, 30, 108, 118], 200, 340, fill=(255, 255, 255, 200), width=5)
    finish(img, "longsword_cleave")
    img, d = icon_canvas(*LS)  # whirl
    d.arc([12, 12, 116, 116], 0, 300, fill=(255, 255, 255, 220), width=6)
    longsword_draw(d, 64, 64, 112, 64, 9)
    longsword_draw(d, 64, 64, 16, 64, 9)
    finish(img, "blade_whirl")
    img, d = icon_canvas(*LS)  # lunge
    for k in range(3):
        d.line([(10, 48 + k * 16), (44, 48 + k * 16)], fill=(255, 255, 255, 190), width=3)
    longsword_draw(d, 40, 64, 120, 64, 10)
    finish(img, "longsword_lunge")
    img, d = icon_canvas(*LS)  # cross guard
    longsword_draw(d, 28, 100, 100, 28, 9)
    longsword_draw(d, 100, 100, 28, 28, 9)
    crack_star(d, 64, 64, 14)
    finish(img, "cross_guard")

    # ------------------------------------------------------------------ blood
    img, d = icon_canvas(*BL)  # awakening: horns grow
    d.ellipse([34, 56, 94, 116], fill=SKIN)
    horn_draw(d, 48, 62, 1.3, -1)
    horn_draw(d, 80, 62, 1.3, 1)
    horn_draw(d, 38, 80, 0.7, -1.5)
    horn_draw(d, 90, 80, 0.7, 1.5)
    blood_drops(d, [(64, 104, 6)])
    finish(img, "blood_awakening")
    img, d = icon_canvas(*BL)  # hammer
    d.line([(34, 104), (80, 46)], fill=(150, 10, 18, 255), width=7)
    d.polygon([(62, 26), (100, 56), (82, 76), (44, 46)], fill=(196, 24, 32, 255), outline=(80, 0, 6, 255))
    blood_drops(d, [(30, 60, 6), (100, 96, 7)])
    finish(img, "blood_hammer")
    img, d = icon_canvas(*BL)  # spear
    spear_shape(d, 10, 118, 116, 12, 9, col=(210, 30, 40, 255))
    blood_drops(d, [(40, 60, 5), (90, 100, 5)])
    finish(img, "blood_spear")
    img, d = icon_canvas(*BL)  # scythe
    d.line([(92, 114), (62, 22)], fill=(150, 10, 18, 255), width=7)
    for k in range(5):
        d.arc([14 + k * 3, 10 + k * 3, 112 - k * 3, 100 - k * 3], 196, 262, fill=(196 - k * 12, 24, 32, 255), width=5)
    d.arc([12, 8, 114, 102], 196, 262, fill=(255, 120, 110, 255), width=2)
    finish(img, "blood_scythe")
    img, d = icon_canvas(*BL)  # blood control
    poly(d, [(14, 60), (46, 52), (50, 76), (16, 84)], SKIN)
    for k in range(4):
        d.arc([46 + k * 6, 30 + k * 4, 112, 100 - k * 4], 250, 110 + 360, fill=(190, 16, 24, 255), width=3)
    d.ellipse([88, 50, 112, 78], fill=(40, 40, 50, 255))
    finish(img, "blood_control")
    img, d = icon_canvas(*BL)  # blood rain
    for k in range(9):
        x = 18 + k * 11
        y = 20 + (k % 3) * 12
        d.line([(x, y), (x - 6, y + 46)], fill=(200, 20, 30, 255), width=4)
        d.polygon([(x - 9, y + 44), (x - 6, y + 56), (x - 2, y + 44)], fill=(240, 60, 60, 255))
    finish(img, "blood_rain")

    # ------------------------------------------------------------------ shark
    img, d = icon_canvas(*SH)  # shark devil
    shark_head_draw(d, 64, 70, 1.05, eyes=3)
    finish(img, "shark_devil")
    img, d = icon_canvas(*SH)  # ground swim
    d.rectangle([4, 76, 124, 124], fill=(100, 74, 50, 255))
    d.polygon([(40, 76), (72, 20), (92, 76)], fill=(74, 96, 118, 255), outline=(20, 30, 40, 255))
    for k in range(5):
        d.ellipse([20 + k * 18, 70 - (k % 2) * 6, 30 + k * 18, 80 - (k % 2) * 6], fill=(130, 100, 70, 255))
    finish(img, "ground_swim")
    img, d = icon_canvas(*SH)  # bite
    shark_head_draw(d, 60, 64, 1.0)
    blood_drops(d, [(100, 96, 6), (86, 106, 4)])
    finish(img, "shark_bite")
    img, d = icon_canvas(*SH)  # ambush
    d.rectangle([4, 86, 124, 124], fill=(100, 74, 50, 255))
    d.polygon([(40, 90), (64, 26), (88, 90)], fill=(112, 138, 160, 255), outline=(20, 30, 40, 255))
    for k in range(4):
        d.polygon([(46 + k * 10, 60), (51 + k * 10, 70), (56 + k * 10, 60)], fill=(242, 240, 232, 255))
    for k in range(6):
        d.ellipse([12 + k * 20, 78, 22 + k * 20, 88], fill=(130, 100, 70, 255))
    finish(img, "shark_ambush")
    img, d = icon_canvas(*SH)  # shark form
    poly(d, [(12, 58), (40, 40), (96, 44), (118, 58), (96, 70), (40, 72)], (112, 138, 160, 255))
    for k in range(4):
        d.line([(40 + k * 16, 70), (32 + k * 16, 104)], fill=(74, 96, 118, 255), width=5)
    d.polygon([(60, 42), (70, 18), (82, 44)], fill=(74, 96, 118, 255))
    finish(img, "shark_form")
    img, d = icon_canvas(*SH)  # blood scent
    shark_head_draw(d, 50, 70, 0.7)
    for k in range(3):
        d.arc([60 + k * 10, 30 + k * 6, 120 - k * 4, 110 - k * 6], 290, 70, fill=(200, 20, 30, 220), width=3)
    blood_drops(d, [(104, 40, 6)])
    finish(img, "blood_scent")

    # ------------------------------------------------------------------ violence
    img, d = icon_canvas(*VI)  # remove mask
    mask_draw(d, 58, 66, 0.9)
    d.arc([10, 10, 118, 118], 200, 300, fill=(255, 255, 255, 200), width=4)
    finish(img, "remove_mask")
    img, d = icon_canvas(*VI)  # violent punch
    poly(d, [(14, 54), (70, 46), (80, 82), (18, 90)], SKIN)
    for k in range(4):
        d.rectangle([66, 48 + k * 9, 84, 55 + k * 9], fill=(200, 160, 136, 255), outline=(90, 60, 40, 255))
    crack_star(d, 100, 64, 22)
    finish(img, "violent_punch")
    img, d = icon_canvas(*VI)  # crushing kick
    poly(d, [(50, 12), (78, 12), (82, 84), (48, 84)], (60, 60, 70, 255))
    poly(d, [(40, 84), (90, 84), (94, 98), (36, 98)], (40, 30, 26, 255))
    for k in range(6):
        a = math.radians(200 + k * 28)
        d.line([(64, 104), (64 + math.cos(a) * 50, 104 + math.sin(a) * -18)], fill=(80, 60, 40, 255), width=3)
    finish(img, "crushing_kick")
    img, d = icon_canvas(*VI)  # mouth arm
    d.ellipse([16, 36, 70, 94], fill=(204, 176, 156, 255), outline=(40, 30, 26, 255), width=3)
    for ex, ey in ((30, 52), (48, 52), (32, 64), (50, 64)):
        d.rectangle([ex, ey, ex + 8, ey + 6], fill=(4, 4, 6, 255))
    d.line([(58, 78), (104, 72)], fill=(196, 150, 130, 255), width=12)
    d.rectangle([100, 62, 120, 84], fill=SKIN, outline=(90, 60, 40, 255))
    finish(img, "mouth_arm")
    img, d = icon_canvas(*VI)  # rampage
    for k in range(3):
        crack_star(d, 36 + k * 28, 44 + (k % 2) * 36, 16)
    poly(d, [(12, 96), (44, 90), (46, 108), (14, 114)], SKIN)
    finish(img, "rampage")

    # ------------------------------------------------------------------ cosmos
    img, d = icon_canvas(*CO)  # open the cosmos
    brain_draw(d, 64, 70, 30)
    d.ellipse([18, 26, 110, 50], outline=(200, 170, 255, 255), width=3)
    for k in range(6):
        a = k / 6 * 2 * math.pi
        star_burst(d, 64 + math.cos(a) * 46, 38 + math.sin(a) * 12, 6)
    finish(img, "open_cosmos")
    img, d = icon_canvas(*CO)  # halloween
    from PIL import ImageFont
    font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 38)
    for k, word in enumerate(("HALLO", "WEEN")):
        d.text((64, 44 + k * 38), word, fill=(255, 170, 220, 255), font=font, anchor="mm", stroke_width=3,
               stroke_fill=(60, 10, 60, 255))
    star_burst(d, 100, 100, 14)
    finish(img, "halloween")
    img, d = icon_canvas(*CO)  # all-out halloween
    for k in range(4):
        d.arc([8 + k * 12, 8 + k * 12, 120 - k * 12, 120 - k * 12], k * 40, k * 40 + 250, fill=(220, 160, 255, 220), width=3)
    brain_draw(d, 64, 64, 18)
    finish(img, "all_out_halloween")
    img, d = icon_canvas(*CO)  # infinite knowledge
    d.polygon([(20, 40), (64, 52), (108, 40), (108, 96), (64, 108), (20, 96)], fill=(240, 232, 214, 255),
              outline=(80, 50, 30, 255))
    d.line([(64, 52), (64, 108)], fill=(80, 50, 30, 255), width=3)
    for k in range(5):
        star_burst(d, 30 + k * 17, 24 + (k % 2) * 8, 6)
    finish(img, "infinite_knowledge")
    img, d = icon_canvas(*CO)  # mind collapse
    brain_draw(d, 64, 64, 34)
    for k in range(6):
        a = k / 6 * 2 * math.pi
        d.line([(64, 64), (64 + math.cos(a) * 52, 64 + math.sin(a) * 52)], fill=(40, 10, 50, 255), width=4)
    finish(img, "mind_collapse")

    # ------------------------------------------------------------------ gun
    img, d = icon_canvas(*GU)  # gun devil
    d.ellipse([28, 30, 100, 110], fill=(214, 172, 146, 255))
    pistol_draw(d, 64, 56, 1.0)
    for k in range(6):
        a = math.radians(150 + k * 45)
        d.line([(64, 62), (64 + math.cos(a) * 24, 62 + math.sin(a) * 22)], fill=(40, 10, 16, 255), width=2)
    for k in range(3):
        d.line([(34 + k * 18, 30), (26 + k * 22, 6)], fill=(60, 60, 66, 255), width=6)
    finish(img, "gun_devil")
    img, d = icon_canvas(*GU)  # carbine burst
    d.rectangle([12, 54, 76, 72], fill=(30, 30, 34, 255))
    d.rectangle([40, 72, 52, 96], fill=(150, 128, 92, 255))
    for k in range(3):
        tracer(d, 80 + k * 4, 62 + (k - 1) * 4, 124, 60 + (k - 1) * 10)
    finish(img, "carbine_burst")
    img, d = icon_canvas(*GU)  # headshot
    d.ellipse([10, 30, 70, 100], fill=(214, 172, 146, 255))
    pistol_draw(d, 40, 54, 0.8)
    d.line([(80, 60), (124, 60)], fill=(255, 220, 120, 255), width=6)
    crack_star(d, 80, 60, 14)
    finish(img, "gun_headshot")
    img, d = icon_canvas(*GU)  # bullet storm
    for k in range(10):
        a = k / 10 * 2 * math.pi
        tracer(d, 64 + math.cos(a) * 14, 64 + math.sin(a) * 14, 64 + math.cos(a) * 56, 64 + math.sin(a) * 56)
    d.ellipse([52, 52, 76, 76], fill=(60, 60, 66, 255))
    finish(img, "bullet_storm")
    img, d = icon_canvas(*GU)  # massacre
    for k in range(7):
        x = 14 + k * 16
        d.rectangle([x, 86, x + 8, 110], fill=(80, 80, 90, 255))
        d.ellipse([x - 1, 76, x + 9, 86], fill=(80, 80, 90, 255))
        tracer(d, 64, 22, x + 4, 84)
    finish(img, "massacre")


def items2():
    # Katana Devil heart - a tsuba and blade through it
    img = px_heart((190, 190, 200), (90, 90, 100), (240, 240, 250))
    pix = img.load()
    for i in range(13):
        pix[2 + i, 13 - i] = (236, 238, 244, 255)
    for x, y in ((6, 9), (7, 8), (8, 9), (7, 10)):
        pix[x, y] = (60, 60, 66, 255)
    img.save(p("textures", "item", "katana_devil_heart.png"))
    # Longsword Devil heart - a broad blade through it
    img = px_heart((120, 126, 144), (60, 64, 76), (200, 206, 220))
    pix = img.load()
    for y in range(0, 16):
        pix[7, y] = (220, 224, 234, 255)
        if 2 < y < 14:
            pix[8, y] = (180, 184, 196, 255)
    for x in range(4, 12):
        pix[x, 12] = (90, 92, 104, 255)
    img.save(p("textures", "item", "longsword_devil_heart.png"))

    def remains(base, dark, light, extra):
        img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        pix = img.load()
        rng = random.Random(hash(extra) & 0xFFFF)
        for y in range(16):
            for x in range(16):
                dx, dy = (x - 7.5) / 6.5, (y - 8.5) / 5.5
                r = dx * dx + dy * dy + 0.15 * math.sin(x * 1.7 + y * 0.9)
                if r < 1.0:
                    col = dark if r > 0.7 else (light if rng.random() < 0.12 else base)
                    pix[x, y] = col + (255,)
        return img, pix

    # Blood Devil's remains: a crimson lump with two small red horns
    img, pix = remains((170, 14, 24), (90, 4, 10), (230, 60, 60), "blood")
    for x, y in ((5, 3), (5, 2), (4, 1), (10, 3), (10, 2), (11, 1)):
        pix[x, y] = (236, 112, 112, 255)
    img.save(p("textures", "item", "blood_devil_remains.png"))
    # Shark Devil's remains: a grey-blue chunk with a fin and teeth
    img, pix = remains((112, 138, 160), (70, 90, 110), (200, 214, 226), "shark")
    for y in range(1, 6):
        for x in range(7, 7 + (6 - y)):
            pix[x, y] = (74, 96, 118, 255)
    for x in range(3, 13, 2):
        pix[x, 11] = (240, 240, 232, 255)
    img.save(p("textures", "item", "shark_devil_remains.png"))
    # Violence Devil's remains: flesh and a green beak mask shard
    img, pix = remains((196, 150, 130), (120, 80, 64), (230, 200, 180), "violence")
    for x, y in ((9, 6), (10, 6), (11, 7), (12, 8), (10, 7), (11, 8), (9, 7)):
        pix[x, y] = (74, 176, 70, 255)
    pix[12, 9] = (214, 52, 38, 255)
    pix[13, 9] = (214, 52, 38, 255)
    img.save(p("textures", "item", "violence_devil_remains.png"))
    # Cosmos Devil's remains: pink brain matter flecked with stars
    img, pix = remains((236, 150, 170), (180, 90, 120), (255, 220, 240), "cosmos")
    for x, y in ((4, 7), (8, 5), (11, 9), (6, 11)):
        pix[x, y] = (255, 250, 200, 255)
    img.save(p("textures", "item", "cosmos_devil_remains.png"))
    # Gun Devil's flesh: a lump of flesh bristling with gun barrels
    img, pix = remains((150, 40, 40), (90, 20, 20), (200, 80, 80), "gun")
    for i in range(5):
        pix[3 + i, 3 - i // 2] = (60, 62, 68, 255)
        pix[9 + i // 2, 2 + i] = (60, 62, 68, 255)
        pix[12, 8 + i // 2] = (60, 62, 68, 255)
    img.save(p("textures", "item", "gun_devil_flesh.png"))

    for name in ("katana_devil_heart", "longsword_devil_heart", "blood_devil_remains", "shark_devil_remains",
                 "violence_devil_remains", "cosmos_devil_remains", "gun_devil_flesh"):
        with open(p("models", "item", name + ".json"), "w") as f:
            json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "csm:item/" + name}}, f, indent=2)


# ----------------------------------------------------------------------------- items (16x16 pixel art)
def px_heart(base, dark, light, cord=None):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    mask = [
        "................",
        "................",
        "...XXX...XXX....",
        "..XXXXX.XXXXX...",
        ".XXXXXXXXXXXXX..",
        ".XXXXXXXXXXXXX..",
        ".XXXXXXXXXXXXX..",
        ".XXXXXXXXXXXXX..",
        "..XXXXXXXXXXX...",
        "...XXXXXXXXX....",
        "....XXXXXXX.....",
        ".....XXXXX......",
        "......XXX.......",
        ".......X........",
        "................",
        "................",
    ]
    pix = img.load()
    for y, row in enumerate(mask):
        for x, ch in enumerate(row):
            if ch == "X":
                edge = any(0 <= x + dx < 16 and 0 <= y + dy < 16 and mask[y + dy][x + dx] != "X"
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                col = dark if edge else base
                if (x + y) % 5 == 0 and not edge:
                    col = dark
                pix[x, y] = col + (255,)
    for x, y in ((3, 4), (4, 3), (3, 5), (10, 4)):
        pix[x, y] = light + (255,)
    # aorta stubs
    for x, y in ((6, 1), (7, 1), (6, 2), (9, 1), (9, 2)):
        pix[x, y] = dark + (255,)
    return img


def items():
    red = (172, 20, 26)
    dk = (92, 8, 12)
    lt = (236, 90, 90)
    # Chainsaw Devil heart - Pochita's starter cord sticking out of it
    img = px_heart((214, 96, 30), (120, 44, 12), (255, 170, 90))
    pix = img.load()
    for x, y in ((12, 5), (13, 4), (14, 3)):
        pix[x, y] = (30, 30, 30, 255)
    for x in range(12, 16):
        pix[x, 2] = (40, 40, 44, 255)
    pix[15, 1] = (40, 40, 44, 255)
    pix[12, 1] = (40, 40, 44, 255)
    for x, y in ((6, 7), (8, 8), (5, 9)):
        pix[x, y] = (150, 20, 20, 255)
    img.save(p("textures", "item", "chainsaw_devil_heart.png"))

    # Crossbow Devil heart - arrow skewering it
    img = px_heart((120, 124, 136), (54, 56, 64), (210, 214, 222))
    pix = img.load()
    for i in range(12):
        x, y = 1 + i, 13 - i
        if 0 <= x < 16 and 0 <= y < 16:
            pix[x, y] = (80, 66, 56, 255)
    for x, y in ((13, 1), (14, 1), (14, 2), (12, 0)):
        pix[x, y] = (236, 238, 242, 255)
    for x, y in ((0, 14), (1, 15), (0, 15)):
        pix[x, y] = (240, 240, 240, 255)
    pix[7, 7] = (160, 16, 16, 255)
    img.save(p("textures", "item", "crossbow_devil_heart.png"))

    # Flamethrower Devil heart - a valve on top, flames licking out
    img = px_heart((150, 36, 28), (70, 14, 10), (232, 190, 40))
    pix = img.load()
    for x, y in ((7, 0), (7, 1), (8, 1), (6, 1)):
        pix[x, y] = (204, 160, 70, 255)
    for x, y, c in ((12, 1, (255, 200, 60)), (13, 0, (255, 120, 20)), (12, 0, (255, 120, 20)),
                    (2, 1, (255, 200, 60)), (1, 0, (255, 120, 20)), (3, 0, (255, 150, 40))):
        pix[x, y] = c + (255,)
    for x in range(3, 12):
        if pix[x, 7][3] > 0:
            pix[x, 7] = (232, 188, 30, 255) if x % 2 else (30, 30, 30, 255)
    img.save(p("textures", "item", "flamethrower_devil_heart.png"))

    # Whip Devil heart - coral, a whip coiled round it with a cracker tip
    img = px_heart((224, 96, 74), (132, 40, 32), (250, 170, 150))
    pix = img.load()
    for x, y in ((1, 10), (2, 9), (3, 9), (4, 10), (5, 11), (6, 11), (7, 10), (8, 9), (9, 9), (10, 10), (11, 11),
                 (12, 11), (13, 10), (14, 9), (15, 8)):
        pix[x, y] = (150, 44, 36, 255)
    pix[15, 7] = (250, 224, 204, 255)
    pix[14, 7] = (250, 224, 204, 255)
    img.save(p("textures", "item", "whip_devil_heart.png"))

    # Bomb Devil heart - glossy black, grenade pin ring on top, lit fuse
    img = px_heart((44, 44, 52), (14, 14, 18), (140, 140, 156))
    pix = img.load()
    for x, y in ((5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7)):
        pix[x, y] = (96, 96, 106, 255)
    for x, y in ((12, 0), (13, 0), (14, 1), (14, 2), (13, 3), (12, 3), (11, 2), (11, 1)):
        pix[x, y] = (210, 212, 218, 255)
    for x, y in ((3, 2), (2, 1)):
        pix[x, y] = (150, 116, 70, 255)
    pix[1, 0] = (255, 200, 60, 255)
    pix[2, 0] = (255, 120, 20, 255)
    img.save(p("textures", "item", "bomb_devil_heart.png"))

    # Spear Devil heart - dark reddish-brown, skewered by a spear
    img = px_heart((112, 54, 42), (56, 26, 20), (196, 150, 128))
    pix = img.load()
    for x in range(0, 16):
        if x < 13:
            pix[x, 8] = (78, 40, 32, 255)
    for x, y in ((12, 7), (12, 9), (13, 7), (13, 8), (13, 9), (14, 8), (15, 8)):
        pix[x, y] = (200, 160, 140, 255)
    pix[6, 9] = (160, 16, 16, 255)
    pix[4, 9] = (160, 16, 16, 255)
    img.save(p("textures", "item", "spear_devil_heart.png"))

    px_heart(red, dk, lt).save(p("textures", "item", "human_heart.png"))

    # blood vial
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pix = img.load()
    glass = (200, 220, 230, 160)
    for y in range(4, 15):
        for x in range(4, 12):
            edge = x in (4, 11) or y == 14
            if y < 7 and x not in range(6, 10):
                continue
            pix[x, y] = (180, 200, 210, 220) if edge else ((150, 10, 16, 255) if y >= 8 else glass)
    for x in range(6, 10):
        pix[x, 3] = (120, 80, 50, 255)
        pix[x, 2] = (140, 100, 60, 255)
    pix[6, 10] = (230, 80, 80, 255)
    pix[6, 11] = (200, 40, 40, 255)
    img.save(p("textures", "item", "blood_vial.png"))

    for name in ("chainsaw_devil_heart", "crossbow_devil_heart", "flamethrower_devil_heart", "whip_devil_heart",
                 "bomb_devil_heart", "spear_devil_heart", "human_heart", "blood_vial"):
        with open(p("models", "item", name + ".json"), "w") as f:
            json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "csm:item/" + name}}, f, indent=2)


# ----------------------------------------------------------------------------- particles & misc textures
def particles():
    rng = random.Random(4)
    for i in range(3):
        img = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        r = 1.5 + i * 0.8
        d.ellipse([4 - r, 4 - r, 4 + r, 4 + r], fill=(150, 8, 12, 255))
        d.point((int(4 - r / 2), int(4 - r / 2)), fill=(230, 70, 70, 255))
        img.save(p("textures", "particle", "blood_%d.png" % i))
    img = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([1, 2, 7, 6], fill=(120, 6, 10, 230))
    for _ in range(5):
        x, y = rng.randrange(8), rng.randrange(8)
        d.point((x, y), fill=(140, 8, 12, 220))
    img.save(p("textures", "particle", "blood_3.png"))
    with open(p("particles", "blood.json"), "w") as f:
        json.dump({"textures": ["csm:blood_0", "csm:blood_1", "csm:blood_2", "csm:blood_3"]}, f, indent=2)

    # chain link (oval ring), hook head, starter cord
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 0, 13, 15], outline=(70, 72, 80, 255), width=3)
    d.arc([2, 0, 13, 15], 200, 300, fill=(200, 204, 212, 255), width=1)
    img.save(p("textures", "entity", "chain_link.png"))
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(8, 0), (14, 9), (10, 9), (10, 15), (6, 15), (6, 9), (2, 9)], fill=(190, 194, 202, 255),
              outline=(40, 40, 46, 255))
    img.save(p("textures", "entity", "chain_hook.png"))
    img = Image.new("RGBA", (16, 16), (24, 24, 26, 255))
    pix = img.load()
    for y in range(16):
        for x in range(16):
            v = 24 + (6 if (y // 2) % 2 == 0 else 0) + (x % 3 == 0) * 4
            pix[x, y] = (v, v, v + 2, 255)
    img.save(p("textures", "hybrid", "cord.png"))


# ----------------------------------------------------------------------------- crossbow bolt (GeckoLib)
def bolt():
    atlas = Atlas(128, 32)
    atlas.add("shaft", kind="metal", color=(70, 64, 60), scratches=2)
    atlas.add("head", kind="metal", color=(228, 232, 238), scratches=3)
    atlas.add("fletch", kind="feather", color=(240, 238, 232), color2=(150, 18, 22))
    atlas.add("glow", kind="glow", color=(255, 80, 50), color2=(255, 235, 200), emissive=True)
    m = Model("csm.crossbow_bolt", atlas, density=2.0, seed=3)
    b = m.bone("bolt", pivot=(0, 0, 0))
    b.cylinder((0, 0, 0.5), (0, 0, 1), 0.3, 9.0, "shaft", segments=6)
    b.spike((0, 0, -3.9), (0, 0, -1), 2.4, 1.3, 0.35, "head", steps=4, up=(0, 1, 0))
    b.spike((0, 0, -3.9), (0, 0, -1), 2.0, 1.1, 0.35, "head", steps=3, up=(1, 0, 0))
    for k in range(3):
        a = math.radians(k * 120)
        up = np.array([math.cos(a), math.sin(a), 0])
        b.obox(np.array([0, 0, 4.2]) + up * 0.55, (0, 0, 1), (0.08, 2.4, 0.9), "fletch", up=up)
    g = m.bone("glow", parent="bolt", pivot=(0, 0, 0))
    g.cylinder((0, 0, 0.3), (0, 0, 1), 0.55, 8.0, "glow", segments=6)
    g.spike((0, 0, -3.8), (0, 0, -1), 2.8, 1.8, 0.8, "glow", steps=3, up=(0, 1, 0))
    m.save(p("geo", "entity", "crossbow_bolt.geo.json"))
    paint_atlas(atlas, p("textures", "entity", "crossbow_bolt.png"), p("textures", "entity", "crossbow_bolt_glowmask.png"),
                seed=2)
    idle = Anim("idle", 1.0, loop=True)
    save_animations(p("animations", "entity", "crossbow_bolt.animation.json"), [idle])


if __name__ == "__main__":
    icons()
    icons2()
    icons3()
    items()
    items2()
    particles()
    bolt()
    print("assets generated")
