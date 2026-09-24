"""
Status effect icons (textures/mob_effect/<id>.png, 18x18, as vanilla draws them in the inventory and HUD):
  halloween - Cosmos's "Halloween": a pink cosmic swirl full of stars
  unhealing - a devil's wound that won't close: a dark gash, black at the edges, weeping blood
  severed   - a limb cut clean through: pale flesh, the red cut and the bone showing
"""
import math
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "src", "main", "resources", "assets", "csm", "textures", "mob_effect")
S = 18


def outline(img, color=(20, 10, 16, 255)):
    """A 1px dark outline round everything drawn, like vanilla's effect icons."""
    src = img.copy()
    px, out = src.load(), img.load()
    for y in range(S):
        for x in range(S):
            if px[x, y][3]:
                continue
            if any(0 <= x + dx < S and 0 <= y + dy < S and px[x + dx, y + dy][3] > 0
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[x, y] = color
    return img


def halloween():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = img.load()
    c = (S - 1) / 2
    for y in range(S):
        for x in range(S):
            dx, dy = x - c, y - c
            r = math.hypot(dx, dy)
            if r > 7.2:
                continue
            a = math.atan2(dy, dx)
            arm = (math.sin(2 * a - r * 0.9) + 1) / 2  # a two-armed spiral
            t = 1 - r / 7.2
            base = (120 + int(120 * arm), 40 + int(60 * arm * t), 130 + int(90 * t))
            px[x, y] = (min(255, base[0]), min(255, base[1]), min(255, base[2]), 255)
    d = ImageDraw.Draw(img)
    for x, y in ((5, 5), (12, 4), (4, 11), (13, 12), (9, 8)):
        d.point((x, y), fill=(255, 250, 255, 255))
        if (x, y) == (9, 8):
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                d.point((x + ox, y + oy), fill=(255, 220, 245, 255))
    return outline(img)


def unhealing():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # a ragged diagonal gash
    d.line([(3, 13), (8, 8), (14, 4)], fill=(40, 6, 14, 255), width=5)
    d.line([(4, 12), (8, 8), (13, 5)], fill=(150, 14, 24, 255), width=3)
    d.line([(5, 11), (8, 8), (12, 6)], fill=(230, 60, 60, 255), width=1)
    # weeping blood
    for x, y0, y1 in ((6, 12, 16), (10, 9, 14), (13, 6, 10)):
        d.line([(x, y0), (x, y1)], fill=(170, 16, 26, 255), width=1)
        d.point((x, y1), fill=(220, 40, 40, 255))
    return outline(img)


def severed():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # an arm, cut in two with a gap between the halves
    d.polygon([(1, 12), (6, 7), (9, 10), (4, 15)], fill=(226, 180, 150, 255))
    d.polygon([(9, 6), (12, 3), (17, 8), (14, 11)], fill=(226, 180, 150, 255))
    # the cut faces: red flesh round a white bone
    d.line([(6, 7), (9, 10)], fill=(190, 20, 30, 255), width=2)
    d.line([(9, 6), (12, 9)], fill=(190, 20, 30, 255), width=2)
    d.point((8, 9), fill=(245, 240, 225, 255))
    d.point((10, 7), fill=(245, 240, 225, 255))
    # blood flying off the cut
    for x, y in ((11, 12), (12, 14), (8, 13), (14, 13)):
        d.point((x, y), fill=(200, 24, 34, 255))
    return outline(img)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("halloween", halloween), ("unhealing", unhealing), ("severed", severed)):
        fn().save(os.path.join(OUT, name + ".png"))
    print("effect icons ->", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
