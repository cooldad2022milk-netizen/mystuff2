"""
Procedural material painter for the hybrid texture atlases.

Every material registered on an Atlas gets a 64x64 cell painted with a hand-tuned
recipe (brushed metal, chipped paint, wet flesh, enamel teeth, chain links ...).
Emissive materials are also copied into a *_glowmask.png so GeckoLib's
AutoGlowingGeoLayer can make them glow.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _fbm(size, rng, octaves=((4, 0.45), (8, 0.3), (16, 0.17), (32, 0.08))):
    acc = np.zeros((size, size), dtype=float)
    total = 0.0
    for res, amp in octaves:
        grid = np.array([[rng.random() for _ in range(res)] for _ in range(res)], dtype=float)
        img = Image.fromarray((grid * 255).astype(np.uint8), "L").resize((size, size), Image.BICUBIC)
        acc += np.asarray(img, dtype=float) / 255.0 * amp
        total += amp
    acc /= total
    lo, hi = acc.min(), acc.max()
    return (acc - lo) / max(hi - lo, 1e-6)


def _clip(a):
    return np.clip(a, 0, 255).astype(np.uint8)


def _tint(base, shade):
    base = np.asarray(base, dtype=float)
    return shade[..., None] * base[None, None, :]


def paint(kind, color, rng, n=64, color2=None, **kw):
    col = np.asarray(color, dtype=float)
    f = _fbm(n, rng)
    f2 = _fbm(n, rng, ((16, 0.5), (32, 0.5)))
    yy, xx = np.mgrid[0:n, 0:n]
    alpha = np.full((n, n), 255.0)

    if kind == "metal":
        streak = np.array([rng.uniform(-0.07, 0.07) for _ in range(n)])[:, None]
        shade = 0.82 + 0.22 * f + streak + 0.06 * (f2 - 0.5)
        rgb = _tint(col, shade)
        img = Image.fromarray(_clip(rgb), "RGB")
        d = ImageDraw.Draw(img)
        for _ in range(kw.get("scratches", 9)):
            x0, y0 = rng.randrange(n), rng.randrange(n)
            ang = rng.uniform(-0.5, 0.5)
            ln = rng.randrange(4, 14)
            c = tuple(int(min(255, v * 1.35 + 20)) for v in col)
            d.line([(x0, y0), (x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln)], fill=c, width=1)
        rgb = np.asarray(img, dtype=float)
    elif kind == "painted":
        shade = 0.86 + 0.2 * f + 0.05 * (f2 - 0.5)
        rgb = _tint(col, shade)
        chip = f2 > 0.8
        under = np.asarray(color2 if color2 is not None else (70, 70, 74), dtype=float)
        rgb[chip] = under * (0.8 + 0.3 * f[chip, None])
        grime = np.clip((yy / n - 0.55) * 1.6, 0, 1) * (0.4 + 0.6 * f)
        rgb *= (1 - 0.35 * grime)[..., None]
    elif kind == "skin":
        shade = 0.9 + 0.14 * f + 0.05 * (f2 - 0.5)
        rgb = _tint(col, shade)
        speck = f2 > 0.9
        rgb[speck] *= 0.9
    elif kind == "flesh":
        shade = 0.7 + 0.45 * f
        rgb = _tint(col, shade)
        veins = np.abs(np.sin(xx * 0.35 + f * 9.0)) < 0.12
        rgb[veins] *= 0.6
        wet = (f2 > 0.88)
        rgb[wet] = np.minimum(255, rgb[wet] * 1.6 + 40)
    elif kind == "blood":
        shade = 0.55 + 0.5 * f
        rgb = _tint(col, shade)
        wet = f2 > 0.9
        rgb[wet] = np.minimum(255, rgb[wet] * 1.8 + 35)
    elif kind == "teeth":
        grad = 1.0 - 0.18 * (yy / n) ** 1.5
        shade = grad * (0.92 + 0.1 * f)
        rgb = _tint(col, shade)
        img = Image.fromarray(_clip(rgb), "RGB")
        d = ImageDraw.Draw(img)
        for _ in range(4):
            x0 = rng.randrange(n)
            d.line([(x0, 0), (x0 + rng.randrange(-3, 4), n)], fill=tuple(int(v * 0.86) for v in col), width=1)
        rgb = np.asarray(img, dtype=float)
    elif kind == "rubber":
        ridge = 0.06 * np.sin(yy * 1.6)
        shade = 0.85 + 0.2 * f2 + ridge
        rgb = _tint(col, shade)
    elif kind == "chain":
        shade = 0.75 + 0.2 * f
        rgb = _tint(col, shade)
        link = ((xx % 6) < 1) | ((yy % 6) < 1)
        rgb[link] *= 0.45
        rivet = ((xx % 6) == 3) & ((yy % 6) == 3)
        rgb[rivet] = np.minimum(255, rgb[rivet] * 1.8 + 30)
    elif kind == "rust":
        c2 = np.asarray(color2 if color2 is not None else (60, 38, 24), dtype=float)
        mix = f[..., None]
        rgb = col[None, None, :] * (1 - mix) + c2[None, None, :] * mix
        rgb *= (0.85 + 0.25 * f2)[..., None]
    elif kind == "glow":
        c2 = np.asarray(color2 if color2 is not None else (255, 240, 170), dtype=float)
        mix = np.clip(f * 1.2 - 0.1, 0, 1)[..., None]
        rgb = col[None, None, :] * (1 - mix) + c2[None, None, :] * mix
    elif kind == "void":
        rgb = _tint(col, 0.7 + 0.5 * f)
    elif kind == "bone":
        rgb = _tint(col, 0.88 + 0.14 * f)
        pores = f2 > 0.93
        rgb[pores] *= 0.8
    elif kind == "stripes":
        c2 = np.asarray(color2 if color2 is not None else (25, 25, 25), dtype=float)
        band = ((xx + yy) // 6) % 2 == 0
        rgb = np.where(band[..., None], col[None, None, :], c2[None, None, :]) * (0.85 + 0.2 * f)[..., None]
    elif kind == "gauge":
        img = Image.new("RGB", (n, n), tuple(int(v) for v in col))
        d = ImageDraw.Draw(img)
        cx = cy = n / 2
        for i in range(12):
            a = math.radians(-225 + i * 270 / 11)
            d.line([(cx + math.cos(a) * n * 0.33, cy + math.sin(a) * n * 0.33),
                    (cx + math.cos(a) * n * 0.44, cy + math.sin(a) * n * 0.44)], fill=(20, 20, 20), width=2)
        d.arc([n * 0.1, n * 0.1, n * 0.9, n * 0.9], 30, 60, fill=(200, 30, 20), width=4)
        d.line([(cx, cy), (cx + n * 0.3, cy - n * 0.12)], fill=(180, 10, 10), width=2)
        rgb = np.asarray(img, dtype=float) * (0.9 + 0.1 * f)[..., None]
    elif kind == "fiber":
        rgb = _tint(col, 0.85 + 0.15 * np.sin(xx * 2.2 + yy * 0.7) * 0.5 + 0.1 * f)
    elif kind == "feather":
        c2 = np.asarray(color2 if color2 is not None else (150, 20, 20), dtype=float)
        barb = (np.sin(yy * 1.3 + xx * 0.6) > 0)
        rgb = np.where(barb[..., None], col[None, None, :], c2[None, None, :] * 0.9 + col[None, None, :] * 0.1)
        rgb = rgb * (0.9 + 0.12 * f)[..., None]
    elif kind == "braid":
        # plaited leather: interleaved diagonal strands with dark gaps
        c2 = np.asarray(color2 if color2 is not None else col * 0.6, dtype=float)
        a = ((xx + yy) // 3) % 2 == 0
        b = ((xx - yy) // 3) % 2 == 0
        strand = np.where((a ^ b)[..., None], col[None, None, :], c2[None, None, :])
        gap = (((xx + yy) % 3) == 0) | (((xx - yy) % 3) == 0)
        rgb = strand * (0.88 + 0.2 * f)[..., None]
        rgb[gap] *= 0.72
    elif kind == "gloss":
        # lacquered casing: smooth, dark, with sparse bright specular flecks
        rgb = _tint(col, 0.9 + 0.14 * f)
        spec = f2 > 0.93
        rgb[spec] = np.minimum(255, rgb[spec] * 1.9 + 45)
    elif kind == "fuse":
        # twisted fuse cord
        c2 = np.asarray(color2 if color2 is not None else col * 0.55, dtype=float)
        twist = ((xx * 2 + yy) // 4) % 2 == 0
        rgb = np.where(twist[..., None], col[None, None, :], c2[None, None, :]) * (0.85 + 0.25 * f)[..., None]
    elif kind == "ringeye":
        # a Horseman's eye (Makima, Nayuta, Yoru, Fami): white of the eye, iris ringed with concentric circles
        img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        sclera = kw.get("sclera", (246, 244, 238))
        d.ellipse([1, n * 0.14, n - 2, n * 0.86], fill=tuple(sclera) + (255,))
        iris = tuple(int(v) for v in col)
        ring = tuple(int(v) for v in (color2 if color2 is not None else (190, 30, 30)))
        r0 = n * 0.36
        cx = cy = n / 2
        d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=iris + (255,))
        rings = kw.get("rings", 3)
        for k in range(rings):
            r = r0 * (1 - (k + 0.5) / (rings + 0.6))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ring + (255,), width=max(2, n // 28))
        pr = r0 * 0.14
        d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=ring + (255,))
        # upper lid shadow
        d.arc([1, n * 0.14, n - 2, n * 0.86], 190, 350, fill=(40, 24, 24, 255), width=max(2, n // 20))
        out = np.asarray(img, dtype=np.uint8)
        return out
    elif kind == "decal":
        # arbitrary drawn marking: kw["draw"](ImageDraw, n) paints on a transparent cell
        img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        kw["draw"](ImageDraw.Draw(img), n)
        return np.asarray(img, dtype=np.uint8)
    else:  # solid
        rgb = _tint(col, 0.92 + 0.1 * f)

    out = np.dstack([_clip(rgb), _clip(alpha)])
    return out


def paint_atlas(atlas, path, glow_path=None, seed=3):
    rng = random.Random(seed)
    img = np.zeros((atlas.size, atlas.size, 4), dtype=np.uint8)
    glow = np.zeros_like(img)
    any_glow = False
    for name, (idx, spec) in atlas.materials.items():
        x, y, w, h = atlas.region(name)
        spec = dict(spec)
        kind = spec.pop("kind", "solid")
        color = spec.pop("color", (128, 128, 128))
        emissive = spec.pop("emissive", False)
        cell = paint(kind, color, rng, n=w, **spec)
        img[y:y + h, x:x + w] = cell
        if emissive:
            glow[y:y + h, x:x + w] = cell
            any_glow = True
    Image.fromarray(img, "RGBA").save(path)
    if glow_path:
        # GeckoLib rejects a glowmask without a single opaque pixel, so always mark the (never sampled)
        # bottom-right texel of the last atlas cell.
        if not any_glow:
            glow[-1, -1] = (255, 255, 255, 255)
        Image.fromarray(glow, "RGBA").save(glow_path)
    return img
