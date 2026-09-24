"""
Custom particle sprites (no vanilla particles are used anywhere in the mod).

Each particle type gets its sprites in assets/csm/textures/particle/ and a definition in
assets/csm/particles/<type>.json.  Sprites are drawn at 4x and downsampled for clean edges.
"""
import json
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "src", "main", "resources", "assets", "csm")
TEX = os.path.join(ASSETS, "textures", "particle")
DEF = os.path.join(ASSETS, "particles")
rng = random.Random(42)
nrng = np.random.default_rng(42)


def save(img, name):
    os.makedirs(TEX, exist_ok=True)
    img.save(os.path.join(TEX, name + ".png"))
    return "csm:" + name


def define(ptype, sprites):
    os.makedirs(DEF, exist_ok=True)
    with open(os.path.join(DEF, ptype + ".json"), "w") as f:
        json.dump({"textures": sprites}, f, indent=2)


def noise(n, scale):
    g = nrng.random((scale, scale))
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC), dtype=float) / 255


def radial(n, cx=0.5, cy=0.5, sx=1.0, sy=1.0):
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
    return np.sqrt(((xx - cx) / sx) ** 2 + ((yy - cy) / sy) ** 2)


def rgba(rgb, a):
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a, 0, 255)]).astype(np.uint8), "RGBA")


def ramp(t, stops):
    """t in [0,1] -> colour by piecewise-linear stops [(t, (r,g,b)), ...]"""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (t >= t0) & (t <= t1)
        f = ((t - t0) / max(t1 - t0, 1e-6))[m][:, None]
        out[m] = np.asarray(c0) * (1 - f) + np.asarray(c1) * f
    return out


def fire():
    names = []
    n = 32
    for k in range(8):
        life = k / 7
        yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
        wob = 0.08 * np.sin(yy * 9 + k * 1.7) * (1 - yy)
        width = (0.36 - 0.12 * life) * np.clip((yy - 0.05) / 0.85, 0, 1) ** 0.55
        d = np.abs(xx - 0.5 - wob) / np.maximum(width, 1e-3)
        body = np.clip(1 - d, 0, 1) * np.clip((yy - 0.04) * 3, 0, 1) * np.clip((1.02 - yy) * 5, 0, 1)
        turb = noise(n, 6 + k) * 0.55 + 0.45
        heat = np.clip(body * turb * (1.25 - 0.55 * life) - 0.05, 0, 1)
        col = ramp(heat, [(0, (120, 10, 0)), (0.3, (230, 60, 5)), (0.6, (255, 160, 30)), (0.85, (255, 235, 150)),
                          (1, (255, 255, 235))])
        a = np.clip(heat * 330, 0, 255)
        names.append(save(rgba(col, a), "fire_%d" % k))
    define("fire", names)


def blast():
    """Bomb Devil fireball: a billowing ball of fire, white-hot core early, ragged orange lobes as it burns out."""
    names = []
    n = 48
    for k in range(8):
        life = k / 7
        r = radial(n)
        yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
        ang = np.arctan2(yy - 0.5, xx - 0.5)
        lobes = 0.06 * np.sin(ang * 5 + k * 0.9) + 0.045 * np.sin(ang * 9 - k * 1.3)
        turb = noise(n, 5 + k) * 0.6 + noise(n, 11 + k) * 0.4
        radius = 0.3 + 0.13 * life + lobes * (0.4 + life)
        body = np.clip(1 - r / np.maximum(radius, 1e-3), 0, 1)
        heat = np.clip(body ** (0.6 + 0.5 * life) * (0.75 + 0.5 * turb) * (1.35 - 0.8 * life) - 0.04 * k, 0, 1)
        # the fireball hollows out into a burning ring as it expands
        hollow = np.clip(1 - np.abs(r - radius * 0.72) / (radius * 0.45), 0, 1) if life > 0.4 else 1.0
        heat = heat * (hollow if life > 0.4 else 1.0) + (heat * 0.35 if life > 0.4 else 0)
        col = ramp(np.clip(heat, 0, 1), [(0, (110, 16, 0)), (0.25, (220, 60, 8)), (0.55, (255, 150, 30)),
                                         (0.8, (255, 228, 140)), (1, (255, 255, 240))])
        a = np.clip(heat * 360, 0, 255)
        names.append(save(rgba(col, a), "blast_%d" % k))
    define("blast", names)


def cosmos_bits():
    """Cosmo: four-point twinkling stars, and her one word."""
    names = []
    for k in range(3):
        n = 16
        yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
        dx, dy = np.abs(xx - 0.5), np.abs(yy - 0.5)
        arms = np.clip(1 - (dx * dy) * (60 + 20 * k), 0, 1) * np.clip(1 - np.maximum(dx, dy) / 0.5, 0, 1)
        core = np.clip(1 - radial(n) / (0.16 + 0.03 * k), 0, 1)
        a = np.clip(arms * 1.2 + core, 0, 1)
        col = ramp(a, [(0, (200, 170, 255)), (0.6, (255, 230, 250)), (1, (255, 255, 255))])
        names.append(save(rgba(col, a * 255), "star_%d" % k))
    define("star", names)
    from PIL import ImageFont
    font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 44)
    words = []
    for k, col in enumerate(((255, 160, 220), (220, 170, 255))):
        img = Image.new("RGBA", (256, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((128, 32), "Halloween", fill=col + (255,), font=font, anchor="mm", stroke_width=4,
               stroke_fill=(40, 6, 50, 230))
        # the atlas wants square sprites: centre the word on a square canvas
        sq = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        sq.paste(img, (0, 96), img)
        words.append(save(sq.resize((64, 64), Image.LANCZOS), "halloween_%d" % k))
    define("halloween", words)


def clods():
    names = []
    for k in range(3):
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cx, cy = 16 + rng.uniform(-2, 2), 16 + rng.uniform(-2, 2)
        pts = [(cx + math.cos(a) * rng.uniform(8, 13), cy + math.sin(a) * rng.uniform(8, 13))
               for a in np.linspace(0, 2 * math.pi, 8)[:-1]]
        base = [(110, 80, 52), (92, 66, 44), (86, 118, 56)][k]
        d.polygon(pts, fill=base + (255,), outline=(50, 36, 24, 255))
        d.ellipse([cx - 4, cy - 5, cx + 2, cy], fill=tuple(min(255, c + 30) for c in base) + (255,))
        names.append(save(img.resize((8, 8), Image.LANCZOS), "clod_%d" % k))
    define("clod", names)


def smoke(prefix, base, count=4, n=32, dark=True):
    names = []
    for k in range(count):
        f = k / max(count - 1, 1)
        r = radial(n)
        blob = np.exp(-(r / (0.2 + 0.07 * f)) ** 2)
        detail = noise(n, 3) * 0.7 + noise(n, 4) * 0.3
        dens = np.clip(blob * (0.75 + 0.35 * detail), 0, 1)
        dens = np.asarray(Image.fromarray((dens * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)),
                          dtype=float) / 255
        shade = (0.85 + 0.2 * detail)[..., None] * np.asarray(base)[None, None, :]
        a = dens * (235 - 80 * f)
        names.append(save(rgba(shade, a), "%s_%d" % (prefix, k)))
    define(prefix, names)


def dots(prefix, colors, sizes, glow=True, n=8):
    names = []
    for k, (c, s) in enumerate(zip(colors, sizes)):
        r = radial(n)
        core = np.clip(1 - r / s, 0, 1)
        a = (core ** (0.6 if glow else 0.2)) * 255
        col = np.ones((n, n, 3)) * np.asarray(c)
        col = col * (0.7 + 0.3 * core[..., None]) + (255 - col) * (core[..., None] ** 3) * 0.6
        names.append(save(rgba(col, a), "%s_%d" % (prefix, k)))
    define(prefix, names)


def spark():
    n = 8
    r = radial(n, sx=1.0, sy=0.45)
    core = np.clip(1 - r / 0.5, 0, 1)
    col = ramp(core, [(0, (255, 120, 20)), (0.6, (255, 220, 120)), (1, (255, 255, 255))])
    define("spark", [save(rgba(col, core ** 0.5 * 255), "spark")])


def charge():
    n = 16
    r = radial(n)
    core = np.clip(1 - r / 0.5, 0, 1)
    col = ramp(core, [(0, (200, 10, 20)), (0.6, (255, 90, 70)), (1, (255, 240, 230))])
    define("charge", [save(rgba(col, core ** 1.2 * 255), "charge")])


def slash():
    """Chainsaw cut crescent: white-hot core, blood-red rim, torn saw-tooth outer edge."""
    names = []
    n = 64
    S = n * 4
    for k in range(6):
        grow = min(1, (k + 1) / 3)
        fade = 1 if k < 3 else 1 - (k - 2) / 4
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        sweep = 200 * grow
        start = 170
        for layer, (width, col) in enumerate(((38, (150, 8, 14)), (24, (230, 40, 30)), (10, (255, 240, 225)))):
            d.arc([S * 0.08, S * 0.08, S * 0.92, S * 0.92], start, start + sweep, fill=col + (int(255 * fade),),
                  width=int(width * (1 - 0.3 * (k / 5))))
        # saw teeth along the outer rim
        for i in range(int(22 * grow)):
            a = math.radians(start + sweep * (i + 0.5) / max(int(22 * grow), 1))
            R0, R1 = S * 0.42, S * 0.49
            p = (S / 2 + math.cos(a) * R0, S / 2 + math.sin(a) * R0)
            q = (S / 2 + math.cos(a + 0.05) * R1, S / 2 + math.sin(a + 0.05) * R1)
            r2 = (S / 2 + math.cos(a + 0.09) * R0, S / 2 + math.sin(a + 0.09) * R0)
            d.polygon([p, q, r2], fill=(120, 6, 10, int(230 * fade)))
        img = img.filter(ImageFilter.GaussianBlur(1.2)).resize((n, n), Image.LANCZOS)
        names.append(save(img, "slash_%d" % k))
    define("slash", names)


def shockwave():
    n = 64
    r = radial(n)
    ring = np.exp(-((r - 0.42) / 0.05) ** 2) + 0.35 * np.exp(-((r - 0.36) / 0.09) ** 2)
    a = np.clip(ring, 0, 1) * 255
    col = np.ones((n, n, 3)) * 255
    define("shockwave", [save(rgba(col, a), "shockwave")])


def speed_line():
    w, h = 32, 8
    yy, xx = np.mgrid[0:h, 0:w]
    tx = xx / (w - 1)
    ty = np.abs(yy - (h - 1) / 2) / ((h - 1) / 2)
    a = np.clip(1 - ty ** 2, 0, 1) * np.clip(np.sin(tx * math.pi) * 1.4, 0, 1) * 255
    col = np.ones((h, w, 3)) * np.array([240, 245, 255])
    define("speed_line", [save(rgba(col, a), "speed_line")])
    define("whip_trail", ["csm:speed_line"])
    define("bullet", ["csm:speed_line"])


def impact():
    """Manga impact burst: jagged black spikes around a white/red flash."""
    names = []
    n = 64
    S = n * 4
    for k in range(3):
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        c = S / 2
        spikes = 18
        grow = 0.55 + 0.25 * k
        alpha = 255 - 70 * k
        spikes = 26
        for i in range(spikes):
            a = i / spikes * 2 * math.pi + rng.uniform(-0.1, 0.1)
            r0 = S * rng.uniform(0.14, 0.24) * (1 + 0.3 * k)
            r1 = S * 0.5 * rng.uniform(0.75, 1.0)
            wdt = rng.uniform(0.012, 0.03)
            p1 = (c + math.cos(a - wdt) * r1, c + math.sin(a - wdt) * r1)
            p2 = (c + math.cos(a) * r0, c + math.sin(a) * r0)
            p3 = (c + math.cos(a + wdt) * r1, c + math.sin(a + wdt) * r1)
            d.polygon([p1, p2, p3], fill=(255, 255, 255, alpha) if i % 3 else (20, 14, 16, alpha))
        R = S * (0.06 - 0.015 * k)
        d.ellipse([c - R, c - R, c + R, c + R], fill=(255, 250, 240, alpha))
        names.append(save(img.resize((n, n), Image.LANCZOS), "impact_%d" % k))
    define("impact", names)


def shards():
    names = []
    for k in range(3):
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        pts = [(rng.uniform(4, 12), rng.uniform(4, 12)), (rng.uniform(20, 28), rng.uniform(2, 10)),
               (rng.uniform(22, 30), rng.uniform(20, 28)), (rng.uniform(6, 14), rng.uniform(22, 30))][: 3 + k % 2]
        d.polygon(pts, fill=(170, 175, 186, 255), outline=(60, 62, 70, 255))
        d.line([pts[0], pts[1]], fill=(240, 244, 250, 255), width=2)
        names.append(save(img.resize((8, 8), Image.LANCZOS), "shard_%d" % k))
    define("shard", names)


def gore():
    names = []
    for k in range(3):
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cx, cy = 16 + rng.uniform(-3, 3), 16 + rng.uniform(-3, 3)
        pts = [(cx + math.cos(a) * rng.uniform(7, 13), cy + math.sin(a) * rng.uniform(7, 13))
               for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
        d.polygon(pts, fill=(130, 14, 20, 255), outline=(60, 4, 8, 255))
        d.ellipse([cx - 4, cy - 5, cx + 3, cy + 1], fill=(205, 90, 100, 255))
        d.point([(cx - 2, cy - 3)], fill=(255, 200, 200, 255))
        names.append(save(img.resize((8, 8), Image.LANCZOS), "gore_%d" % k))
    define("gore", names)


def blood():
    names = []
    for k in range(3):
        n = 16
        r = radial(n, 0.5, 0.55, 1.0, 1.15)
        drop = np.clip(1 - r / (0.22 + 0.06 * k), 0, 1)
        col = ramp(drop, [(0, (90, 0, 6)), (0.5, (175, 10, 18)), (1, (215, 30, 34))])
        hl = np.clip(1 - radial(n, 0.4, 0.42) / 0.09, 0, 1)
        col = col + hl[..., None] * 140
        names.append(save(rgba(col, (drop > 0) * 255), "blood_%d" % k))
    n = 16
    r = radial(n, sx=1.0, sy=0.6)
    splat = np.clip(1 - r / 0.42, 0, 1) + 0.6 * np.clip(1 - radial(n, 0.22, 0.4) / 0.12, 0, 1) \
        + 0.6 * np.clip(1 - radial(n, 0.8, 0.62) / 0.1, 0, 1)
    col = ramp(np.clip(splat, 0, 1), [(0, (80, 0, 6)), (1, (160, 10, 16))])
    names.append(save(rgba(col, (splat > 0.05) * 235), "blood_3"))
    define("blood", names)
    smoke("blood_mist", (170, 14, 20), count=3, n=16)


if __name__ == "__main__":
    fire()
    blast()
    cosmos_bits()
    clods()
    smoke("smoke", (46, 42, 42))
    smoke("exhaust", (120, 124, 136))
    smoke("ink", (16, 12, 24))
    dots("ember", [(255, 150, 40), (255, 90, 20)], [0.35, 0.28])
    spark()
    charge()
    slash()
    shockwave()
    speed_line()
    impact()
    shards()
    gore()
    blood()
    print("particles:", sorted(f[:-5] for f in os.listdir(DEF)))
