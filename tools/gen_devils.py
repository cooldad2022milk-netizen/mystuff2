"""
Art and item models for the full devils: essence item textures, spawn egg models, ability icons for the devils' moves,
and the chain particle. Text and loot tables come from devil_data.py via gen_data.py.
"""
import json
import math
import os
import random

from PIL import Image, ImageDraw

import devil_data
from gen_assets import p, icon_canvas, finish, poly, blood_drops, crack_star

SKIN = (236, 206, 186, 255)


# ----------------------------------------------------------------------------- items
def essence_texture(d):
    """A devil's essence: a dark, pulsing lump in the devil's colour with a bright core and veins."""
    col = d["color"]
    rng = random.Random(d["id"])
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pix = img.load()
    dark = tuple(max(0, int(c * 0.35)) for c in col)
    mid = tuple(int(c * 0.75) for c in col)
    light = tuple(min(255, int(c * 1.25 + 30)) for c in col)
    for y in range(16):
        for x in range(16):
            dx, dy = (x - 7.5) / 6.4, (y - 8.0) / 6.8
            wob = 0.12 * math.sin(x * 1.3 + y * 0.7 + rng.random())
            r = dx * dx + dy * dy + wob
            if r < 1.0:
                if r > 0.72:
                    c = dark
                elif r < 0.12:
                    c = (255, 250, 230)
                elif r < 0.3:
                    c = light
                else:
                    c = mid if rng.random() > 0.15 else dark
                pix[x, y] = c + (255,)
    # dark veins crawling over it
    for _ in range(3):
        x, y = rng.randrange(4, 12), rng.randrange(4, 12)
        for _ in range(4):
            if 0 <= x < 16 and 0 <= y < 16 and pix[x, y][3] > 0:
                pix[x, y] = dark + (255,)
            x += rng.choice((-1, 0, 1))
            y += rng.choice((-1, 0, 1))
    return img


def contract_texture(c):
    """A devil's contract: an old sheet of paper with a few lines of writing, the devil's mark and a bloody thumbprint."""
    rng = random.Random(c["id"])
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pix = img.load()
    paper, edge, ink = (232, 220, 188, 255), (192, 174, 138, 255), (70, 60, 56, 255)
    for y in range(1, 15):
        for x in range(3, 13):
            if (x, y) in ((12, 1), (3, 14)):
                continue  # dog-eared corners
            shade = rng.randint(-10, 6)
            pix[x, y] = tuple(max(0, min(255, v + shade)) for v in paper[:3]) + (255,)
    for y in range(1, 15):
        pix[3, y] = edge if y != 14 else (0, 0, 0, 0)
        pix[12, y] = edge if y != 1 else (0, 0, 0, 0)
    for x in range(4, 12):
        pix[x, 1] = edge if x != 12 else pix[x, 1]
        pix[x, 14] = edge
    for y in (3, 5):  # lines of writing
        for x in range(5, 11):
            if rng.random() < 0.75:
                pix[x, y] = ink

    def put(pts, col):
        for x, y in pts:
            pix[x, y] = col
    WHITE, RED, DARK = (250, 248, 240, 255), (200, 30, 30, 255), (40, 30, 30, 255)
    if c["id"] == "fox_head":        # a white fox's head with red eyes
        put([(5, 7), (10, 7), (5, 8), (6, 8), (9, 8), (10, 8)], WHITE)
        put([(x, y) for y in (9, 10) for x in range(5, 11)] + [(x, 11) for x in range(6, 10)] + [(7, 12), (8, 12)],
            WHITE)
        put([(6, 9), (9, 9)], RED)
        put([(7, 12), (8, 12)], DARK)
    elif c["id"] == "fox_paw":       # a paw print
        put([(5, 8), (7, 7), (9, 7), (11, 8)], DARK)
        put([(x, y) for y in (10, 11) for x in range(6, 11)] + [(7, 12), (8, 12), (9, 12)], DARK)
    elif c["id"] == "curse":         # a rusty nail
        put([(5, 7), (6, 7), (7, 7), (6, 8)], (110, 96, 86, 255))
        put([(7, 9), (8, 10), (9, 11), (10, 12)], (140, 90, 60, 255))
        put([(8, 9), (9, 10)], (100, 66, 44, 255))
    elif c["id"] == "future":        # a ringed eye
        put([(5, 9), (6, 8), (7, 8), (8, 8), (9, 8), (10, 9), (6, 10), (7, 10), (8, 10), (9, 10)], DARK)
        put([(6, 9), (9, 9)], WHITE)
        put([(7, 9), (8, 9)], (236, 190, 60, 255))
        put([(7, 9)], (190, 50, 30, 255))
    elif c["id"] == "ghost":         # a pale hand
        put([(6, 7), (7, 7), (8, 7), (9, 7), (6, 8), (7, 8), (8, 8), (9, 8)], (206, 206, 232, 255))
        put([(x, y) for y in (9, 10, 11) for x in range(6, 10)] + [(10, 9), (10, 10)], (214, 214, 238, 255))
        put([(7, 12), (8, 12)], (190, 190, 220, 255))
    # the bloody thumbprint that sealed it
    put([(10, 12), (11, 12), (10, 13), (11, 13)], RED)
    put([(11, 11)], (160, 20, 20, 255))
    return img


def items():
    for d in devil_data.DEVILS:
        if "contract" not in d:
            name = devil_data.essence_item(d)
            essence_texture(d).save(p("textures", "item", name + ".png"))
            with open(p("models", "item", name + ".json"), "w") as f:
                json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "csm:item/" + name}}, f, indent=2)
        with open(p("models", "item", d["entity"] + "_spawn_egg.json"), "w") as f:
            json.dump({"parent": "minecraft:item/template_spawn_egg"}, f, indent=2)
    for c in devil_data.CONTRACTS:
        contract_texture(c).save(p("textures", "item", c["item"] + ".png"))
        with open(p("models", "item", c["item"] + ".json"), "w") as f:
            json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "csm:item/" + c["item"]}}, f,
                      indent=2)


# ----------------------------------------------------------------------------- icons
def ring_eye(d, cx, cy, r):
    d.ellipse([cx - r * 1.5, cy - r, cx + r * 1.5, cy + r], fill=(246, 244, 238, 255), outline=(30, 20, 20, 255), width=3)
    d.ellipse([cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8], fill=(236, 196, 60, 255))
    for k in range(3):
        rr = r * 0.8 * (1 - (k + 0.5) / 3.6)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(196, 42, 34, 255), width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(196, 42, 34, 255))


def chain_links(d, x0, y0, x1, y1, n, w=12):
    for k in range(n):
        t = (k + 0.5) / n
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        ang = math.atan2(y1 - y0, x1 - x0)
        L, W = (x1 - x0, y1 - y0), w
        seg = math.hypot(*L) / n * 0.7
        dx, dy = math.cos(ang) * seg, math.sin(ang) * seg
        if k % 2 == 0:
            d.ellipse([cx - abs(dx) - W / 2, cy - abs(dy) - W / 2, cx + abs(dx) + W / 2, cy + abs(dy) + W / 2],
                      outline=(200, 202, 210, 255), width=4)
        else:
            d.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=(150, 152, 160, 255), width=6)


def bat_head(d, cx, cy, s=1.0, open_mouth=False):
    col = (112, 80, 142, 255)
    poly(d, [(cx - 30 * s, cy - 8 * s), (cx - 38 * s, cy - 50 * s), (cx - 12 * s, cy - 22 * s)], col)
    poly(d, [(cx + 30 * s, cy - 8 * s), (cx + 38 * s, cy - 50 * s), (cx + 12 * s, cy - 22 * s)], col)
    d.ellipse([cx - 30 * s, cy - 30 * s, cx + 30 * s, cy + 26 * s], fill=col, outline=(30, 10, 30, 255), width=3)
    for sx in (-1, 1):
        d.ellipse([cx + sx * 12 * s - 7 * s, cy - 14 * s, cx + sx * 12 * s + 7 * s, cy], fill=(40, 8, 12, 255))
        d.ellipse([cx + sx * 12 * s - 2 * s, cy - 11 * s, cx + sx * 12 * s + 2 * s, cy - 7 * s], fill=(230, 40, 40, 255))
    if open_mouth:
        d.ellipse([cx - 14 * s, cy + 2 * s, cx + 14 * s, cy + 22 * s], fill=(60, 12, 24, 255))
    for k in range(5):
        x = cx - 10 * s + k * 5 * s
        poly(d, [(x - 2 * s, cy + 4 * s), (x + 2 * s, cy + 4 * s), (x, cy + 11 * s)], (240, 236, 224, 255),
             outline=(60, 40, 40, 255), width=1)


def wing(d, x, y, s, flip=1):
    col = (72, 46, 90, 255)
    pts = [(x, y), (x + flip * 50 * s, y - 30 * s), (x + flip * 58 * s, y + 10 * s), (x + flip * 44 * s, y + 4 * s),
           (x + flip * 40 * s, y + 24 * s), (x + flip * 26 * s, y + 14 * s), (x + flip * 18 * s, y + 30 * s)]
    poly(d, pts, col)


def icons():
    CT = ((226, 120, 100), (60, 10, 12))
    BA = ((150, 110, 180), (24, 12, 40))
    DV = ((150, 150, 150), (20, 16, 20))

    # ------------------------------------------------------------------ manifest (every monster devil)
    img, d = icon_canvas(*DV)
    poly(d, [(64, 20), (100, 60), (86, 110), (42, 110), (28, 60)], (60, 20, 24, 255))
    for k in range(7):
        a = math.radians(k * 51)
        d.line([(64, 64), (64 + math.cos(a) * 56, 64 + math.sin(a) * 56)], fill=(200, 20, 30, 255), width=4)
    d.ellipse([44, 44, 84, 84], fill=(20, 8, 10, 255))
    for sx in (-1, 1):
        d.ellipse([64 + sx * 10 - 5, 56, 64 + sx * 10 + 5, 66], fill=(255, 60, 50, 255))
    finish(img, "manifest")

    # ------------------------------------------------------------------ Makima
    img, d = icon_canvas(*CT)  # the Control Devil's eyes
    ring_eye(d, 64, 64, 26)
    finish(img, "control_devil")
    img, d = icon_canvas(*CT)  # bang: finger gun
    poly(d, [(18, 76), (70, 70), (104, 58), (108, 66), (72, 82), (60, 96), (24, 96)], SKIN)
    d.line([(108, 62), (122, 56)], fill=(255, 80, 60, 255), width=3)
    crack_star(d, 104, 34, 14)
    finish(img, "control_bang")
    img, d = icon_canvas(*CT)  # chains
    chain_links(d, 20, 108, 100, 24, 7)
    chain_links(d, 108, 108, 44, 30, 6)
    finish(img, "control_chains")
    img, d = icon_canvas(*CT)  # domination: the eye over bowed heads
    ring_eye(d, 64, 44, 16)
    for k in range(5):
        x = 22 + k * 21
        d.ellipse([x - 8, 88, x + 8, 104], fill=(40, 30, 30, 255))
        d.line([(x, 60), (x, 88)], fill=(200, 40, 40, 200), width=2)
    finish(img, "control_domination")
    img, d = icon_canvas(*CT)  # kneel
    poly(d, [(64, 106), (38, 70), (54, 70), (54, 22), (74, 22), (74, 70), (90, 70)], (240, 236, 230, 255))
    d.line([(20, 110), (108, 110)], fill=(30, 10, 10, 255), width=5)
    finish(img, "control_kneel")
    img, d = icon_canvas(*CT)  # the Prime Minister's contract
    d.rectangle([36, 20, 92, 108], fill=(244, 238, 222, 255), outline=(40, 30, 30, 255), width=3)
    for k in range(6):
        d.line([(44, 34 + k * 10), (84, 34 + k * 10)], fill=(90, 80, 80, 255), width=2)
    d.ellipse([66, 86, 90, 106], fill=(190, 20, 30, 255))
    finish(img, "control_contract")

    # ------------------------------------------------------------------ Bat Devil
    img, d = icon_canvas(*BA)  # blood bite
    bat_head(d, 64, 70, 1.1, open_mouth=True)
    blood_drops(d, [(56, 100, 5), (72, 104, 4)])
    finish(img, "bat_bite")
    img, d = icon_canvas(*BA)  # air cannon
    bat_head(d, 40, 70, 0.8)
    d.rectangle([54, 66, 84, 84], fill=(150, 70, 100, 255), outline=(40, 10, 20, 255), width=3)
    for k in range(3):
        d.arc([80 + k * 10, 48 - k * 4, 104 + k * 12, 102 + k * 4], -60, 60, fill=(230, 240, 255, 255), width=4)
    finish(img, "bat_air_cannon")
    img, d = icon_canvas(*BA)  # swoop
    wing(d, 64, 56, 0.9, 1)
    wing(d, 64, 56, 0.9, -1)
    d.ellipse([52, 44, 76, 72], fill=(112, 80, 142, 255))
    for k in range(3):
        d.line([(30 + k * 12, 18), (50 + k * 12, 40)], fill=(255, 255, 255, 180), width=3)
    d.line([(64, 72), (64, 104)], fill=(255, 255, 255, 200), width=3)
    finish(img, "bat_swoop")
    img, d = icon_canvas(*BA)  # screech
    bat_head(d, 44, 70, 0.8, open_mouth=True)
    for k in range(4):
        d.arc([56 - k * 4, 30 - k * 10, 96 + k * 10, 110 + k * 10], -50, 50, fill=(255, 255, 255, 230 - k * 40), width=4)
    finish(img, "bat_screech")



def icons_early():
    LE = ((150, 110, 124), (30, 14, 22))
    ZO = ((150, 170, 110), (26, 34, 16))
    TO = ((240, 110, 90), (60, 8, 6))
    SC = ((190, 150, 120), (40, 24, 18))
    TEETH = (236, 228, 206, 255)

    def maw(d, cx, cy, w, h):
        d.ellipse([cx - w, cy - h, cx + w, cy + h], fill=(40, 8, 16, 255), outline=(150, 60, 76, 255), width=4)
        for k in range(5):
            x = cx - w * 0.7 + k * w * 0.35
            d.rectangle([x - 5, cy - h + 2, x + 5, cy - h + 14], fill=TEETH)
            d.rectangle([x - 5, cy + h - 14, x + 5, cy + h - 2], fill=TEETH)

    img, d = icon_canvas(*LE)  # piercing tongue
    maw(d, 38, 64, 26, 22)
    poly(d, [(50, 60), (118, 56), (122, 64), (50, 70)], (176, 64, 84, 255))
    blood_drops(d, [(114, 80, 5)])
    finish(img, "leech_tongue")
    img, d = icon_canvas(*LE)  # sucker grab
    for s_ in (-1, 1):
        pts = [(64 + s_ * 10, 40), (64 + s_ * 40, 30), (64 + s_ * 50, 70), (64 + s_ * 20, 100)]
        d.line(pts, fill=(104, 84, 92, 255), width=10, joint="curve")
        for x, y in pts[1:]:
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(190, 120, 130, 255))
    finish(img, "leech_grab")
    img, d = icon_canvas(*LE)  # devour
    maw(d, 64, 64, 44, 36)
    finish(img, "leech_devour")
    img, d = icon_canvas(*LE)  # drain
    maw(d, 64, 50, 30, 20)
    blood_drops(d, [(52, 90, 7), (66, 100, 6), (80, 88, 5)])
    finish(img, "leech_drain")

    img, d = icon_canvas(*ZO)  # infectious bite
    maw(d, 64, 64, 36, 26)
    poly(d, [(20, 30), (40, 20), (34, 42)], (122, 138, 90, 255))
    finish(img, "zombie_bite")
    img, d = icon_canvas(*ZO)  # horde
    for k in range(3):
        x = 30 + k * 34
        d.ellipse([x - 12, 40 + (k % 2) * 10, x + 12, 64 + (k % 2) * 10], fill=(122, 138, 90, 255))
        d.rectangle([x - 10, 64 + (k % 2) * 10, x + 10, 104], fill=(90, 100, 70, 255))
        d.line([(x - 8, 70 + (k % 2) * 10), (x - 22, 80)], fill=(122, 138, 90, 255), width=6)
    finish(img, "zombie_horde")
    img, d = icon_canvas(*ZO)  # brain tendrils
    d.ellipse([40, 30, 88, 66], fill=(214, 150, 160, 255), outline=(120, 60, 70, 255), width=3)
    for k in range(6):
        a = math.radians(-160 + k * 28)
        d.line([(64, 56), (64 + math.cos(a) * 56, 56 - math.sin(a) * 50)], fill=(150, 74, 90, 255), width=5)
    finish(img, "zombie_tendrils")
    img, d = icon_canvas(*ZO)  # feast
    maw(d, 64, 56, 34, 24)
    blood_drops(d, [(50, 94, 6), (64, 104, 7), (78, 94, 6)])
    finish(img, "zombie_feast")

    def tomato(d, cx, cy, r):
        d.ellipse([cx - r, cy - r * 0.9, cx + r, cy + r * 0.9], fill=(214, 44, 32, 255), outline=(90, 10, 10, 255),
                  width=3)
        for k in range(5):
            a = math.radians(k * 72 - 90)
            poly(d, [(cx, cy - r * 0.85), (cx + math.cos(a) * r * 0.45, cy - r * 0.85 + math.sin(a) * r * 0.3 - 6),
                     (cx + math.cos(a + 0.4) * r * 0.2, cy - r * 0.85)], (64, 132, 54, 255), outline=(30, 70, 30, 255),
                 width=1)
        for dx, dy in ((-0.45, -0.2), (0.4, 0.1), (-0.1, 0.45), (0.45, -0.4)):
            ex, ey = cx + dx * r, cy + dy * r
            d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=(238, 234, 220, 255))
            d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(12, 10, 10, 255))
    img, d = icon_canvas(*TO)  # arm slam
    tomato(d, 64, 50, 30)
    d.line([(40, 70), (26, 104)], fill=(214, 176, 150, 255), width=8)
    d.line([(88, 70), (102, 104)], fill=(214, 176, 150, 255), width=8)
    d.line([(14, 110), (114, 110)], fill=(255, 255, 255, 200), width=4)
    finish(img, "tomato_slam")
    img, d = icon_canvas(*TO)  # seeds
    tomato(d, 44, 64, 26)
    for k in range(5):
        x, y = 84 + k * 7, 50 + (k * 13) % 30
        d.ellipse([x - 4, y - 3, x + 4, y + 3], fill=(236, 214, 150, 255))
    finish(img, "tomato_seeds")
    img, d = icon_canvas(*TO)  # burst
    tomato(d, 64, 64, 26)
    for k in range(10):
        a = math.radians(k * 36)
        d.line([(64 + math.cos(a) * 34, 64 + math.sin(a) * 34), (64 + math.cos(a) * 52, 64 + math.sin(a) * 52)],
               fill=(200, 20, 20, 255), width=5)
    finish(img, "tomato_burst")
    img, d = icon_canvas(*TO)  # many hands
    tomato(d, 64, 40, 22)
    for k in range(4):
        x = 24 + k * 27
        d.line([(64, 56), (x, 96)], fill=(214, 176, 150, 255), width=7)
        d.ellipse([x - 8, 92, x + 8, 106], fill=(214, 176, 150, 255))
    finish(img, "tomato_grab")

    def cuke(d, cx, cy, s=1.0):
        d.rounded_rectangle([cx - 20 * s, cy - 40 * s, cx + 20 * s, cy + 40 * s], radius=18 * s,
                            fill=(150, 108, 88, 255), outline=(60, 40, 30, 255), width=3)
        for k in range(8):
            y = cy - 30 * s + k * 9 * s
            sx = -1 if k % 2 else 1
            d.line([(cx + sx * 20 * s, y), (cx + sx * 30 * s, y - 4 * s)], fill=(216, 180, 156, 255), width=4)
        d.ellipse([cx - 9 * s, cy - 20 * s, cx + 9 * s, cy - 2 * s], fill=(226, 214, 190, 255))
        d.ellipse([cx - 6 * s, cy - 15 * s, cx - 1 * s, cy - 10 * s], fill=(16, 10, 10, 255))
        d.ellipse([cx + 1 * s, cy - 15 * s, cx + 6 * s, cy - 10 * s], fill=(16, 10, 10, 255))
    img, d = icon_canvas(*SC)  # finger grab
    cuke(d, 50, 64, 0.9)
    for k in range(4):
        d.line([(76, 50 + k * 8), (112, 44 + k * 10)], fill=(216, 180, 156, 255), width=5)
    finish(img, "seacu_grab")
    img, d = icon_canvas(*SC)  # spew guts
    cuke(d, 44, 70, 0.8)
    d.line([(44, 36), (70, 20), (100, 40), (112, 76)], fill=(190, 110, 120, 255), width=9, joint="curve")
    finish(img, "seacu_spew")
    img, d = icon_canvas(*SC)  # body slam
    cuke(d, 64, 64, 0.9)
    d.line([(20, 112), (108, 112)], fill=(255, 255, 255, 220), width=5)
    finish(img, "seacu_slam")
    img, d = icon_canvas(*SC)  # regenerate
    cuke(d, 64, 64, 0.9)
    d.rectangle([92, 20, 104, 52], fill=(90, 220, 90, 255))
    d.rectangle([82, 30, 114, 42], fill=(90, 220, 90, 255))
    finish(img, "seacu_regen")


def icons_big():
    ET = ((220, 170, 150), (60, 20, 16))
    DA = ((120, 110, 150), (6, 4, 12))
    GD = ((200, 190, 160), (40, 30, 20))
    TY = ((190, 210, 230), (30, 40, 60))

    def infinity(d, cx, cy, r, col=(196, 140, 124, 255)):
        for s_ in (-1, 1):
            d.ellipse([cx + s_ * r - r * 0.9, cy - r * 0.8, cx + s_ * r + r * 0.9, cy + r * 0.8], outline=col,
                      width=int(r * 0.45))
    img, d = icon_canvas(*ET)  # infinite floor
    infinity(d, 64, 64, 24)
    d.text((52, 54), "8:18", fill=(255, 255, 255, 255))
    finish(img, "eternity_loop")
    img, d = icon_canvas(*ET)  # tide
    for k in range(6):
        x = 20 + k * 17
        d.line([(x, 108), (x + 10, 60 - (k % 2) * 16)], fill=(214, 170, 150, 255), width=8)
        d.ellipse([x + 4, 50 - (k % 2) * 16, x + 18, 64 - (k % 2) * 16], fill=(214, 170, 150, 255))
    finish(img, "eternity_tide")
    img, d = icon_canvas(*ET)  # swallow
    infinity(d, 64, 58, 20)
    d.ellipse([46, 82, 82, 104], fill=(50, 10, 16, 255))
    finish(img, "eternity_swallow")
    img, d = icon_canvas(*ET)  # endless
    infinity(d, 64, 64, 22, col=(120, 220, 120, 255))
    finish(img, "eternity_endless")

    img, d = icon_canvas(*DA)  # severance
    for s_ in (-1, 1):
        d.line([(64 + s_ * 18, 50), (64 + s_ * 44, 80)], fill=(90, 80, 90, 255), width=10)
        blood_drops(d, [(64 + s_ * 20, 56, 6)])
    d.line([(20, 40), (108, 40)], fill=(255, 255, 255, 230), width=3)
    finish(img, "darkness_sever")
    img, d = icon_canvas(*DA)  # hell's darkness
    d.ellipse([20, 20, 108, 108], fill=(4, 2, 8, 255))
    for sx in (-1, 1):
        d.ellipse([64 + sx * 14 - 4, 58, 64 + sx * 14 + 4, 66], fill=(150, 120, 255, 255))
    finish(img, "darkness_hell")
    img, d = icon_canvas(*DA)  # unseen cut
    d.line([(16, 104), (112, 24)], fill=(220, 210, 255, 255), width=4)
    blood_drops(d, [(60, 70, 6), (74, 58, 5)])
    finish(img, "darkness_cut")
    img, d = icon_canvas(*DA)  # rake
    for k in range(4):
        d.line([(34 + k * 16, 22), (24 + k * 16, 106)], fill=(200, 190, 220, 255), width=5)
    finish(img, "darkness_rake")

    def barrel(d, x0, y0, x1, y1, w=10):
        d.line([(x0, y0), (x1, y1)], fill=(50, 52, 60, 255), width=w)
        d.ellipse([x1 - w / 2, y1 - w / 2, x1 + w / 2, y1 + w / 2], fill=(20, 20, 24, 255))
    img, d = icon_canvas(*GD)  # massacre
    d.ellipse([48, 44, 80, 76], fill=(214, 204, 184, 255))
    for k in range(10):
        a = math.radians(k * 36)
        d.line([(64 + math.cos(a) * 20, 60 + math.sin(a) * 20), (64 + math.cos(a) * 56, 60 + math.sin(a) * 56)],
               fill=(255, 200, 80, 255), width=2)
    finish(img, "gundevil_massacre")
    img, d = icon_canvas(*GD)  # rifle volley
    barrel(d, 20, 90, 100, 40, 14)
    barrel(d, 28, 104, 108, 54, 14)
    crack_star(d, 104, 36, 10)
    finish(img, "gundevil_volley")
    img, d = icon_canvas(*GD)  # belt lash
    for k in range(3):
        d.arc([14 + k * 8, 14 + k * 8, 114 - k * 8, 114 - k * 8], 200, 340, fill=(206, 164, 82, 255), width=6)
    finish(img, "gundevil_belts")
    img, d = icon_canvas(*GD)  # bullet storm
    for k in range(8):
        a = math.radians(k * 45 + 20)
        barrel(d, 64, 64, 64 + math.cos(a) * 44, 64 + math.sin(a) * 44, 8)
    finish(img, "gundevil_storm")

    img, d = icon_canvas(*TY)  # charge
    d.ellipse([34, 30, 84, 100], fill=(196, 168, 160, 255))
    for k in range(4):
        d.line([(90, 40 + k * 16), (118, 40 + k * 16)], fill=(255, 255, 255, 220), width=4)
    finish(img, "typhoon_charge")
    img, d = icon_canvas(*TY)  # gale
    for k in range(4):
        d.arc([10 + k * 12, 30, 70 + k * 12, 100], -40, 40, fill=(245, 250, 255, 255), width=5)
    finish(img, "typhoon_gale")
    img, d = icon_canvas(*TY)  # tornado
    for k in range(6):
        w = 44 - k * 6
        d.ellipse([64 - w, 20 + k * 15, 64 + w, 30 + k * 15], outline=(245, 250, 255, 255), width=4)
    finish(img, "typhoon_tornado")
    img, d = icon_canvas(*TY)  # hurl
    d.polygon([(40, 40), (70, 30), (84, 56), (58, 70), (36, 60)], fill=(120, 110, 100, 255))
    for k in range(3):
        d.line([(30 - k * 6, 70 + k * 10), (60, 60)], fill=(255, 255, 255, 180), width=3)
    finish(img, "typhoon_hurl")


def icons_contract():
    FX = ((226, 120, 90), (60, 20, 14))
    CU = ((210, 200, 176), (30, 26, 22))
    FU = ((220, 190, 120), (40, 30, 20))
    GH = ((230, 224, 240), (60, 50, 80))
    FUR = (244, 240, 230, 255)
    BONE = (226, 218, 196, 255)

    def fox_head(d, cx, cy, s=1.0, open_mouth=True):
        poly(d, [(cx - 26 * s, cy - 10 * s), (cx - 34 * s, cy - 46 * s), (cx - 8 * s, cy - 22 * s)], FUR)
        poly(d, [(cx + 26 * s, cy - 10 * s), (cx + 34 * s, cy - 46 * s), (cx + 8 * s, cy - 22 * s)], FUR)
        poly(d, [(cx - 28 * s, cy - 18 * s), (cx + 28 * s, cy - 18 * s), (cx + 6 * s, cy + 30 * s),
                 (cx - 6 * s, cy + 30 * s)], FUR, outline=(90, 50, 30, 255), width=2)
        if open_mouth:
            poly(d, [(cx - 12 * s, cy + 6 * s), (cx + 12 * s, cy + 6 * s), (cx + 4 * s, cy + 28 * s),
                     (cx - 4 * s, cy + 28 * s)], (90, 14, 20, 255))
            for k in range(4):
                x = cx - 9 * s + k * 6 * s
                poly(d, [(x - 2 * s, cy + 7 * s), (x + 2 * s, cy + 7 * s), (x, cy + 13 * s)], (246, 242, 230, 255),
                     outline=(60, 40, 40, 255), width=1)
        d.ellipse([cx - 4 * s, cy + 26 * s, cx + 4 * s, cy + 33 * s], fill=(30, 22, 22, 255))
        for sx, sy, r in ((-12, -8, 6), (12, -8, 6), (0, -14, 4), (-20, -14, 3), (20, -14, 3), (-6, -22, 3),
                          (6, -22, 3)):
            ring_eye(d, cx + sx * s, cy + sy * s, r * s)

    img, d = icon_canvas(*FX)  # kon - the hand sign and the jaws
    fox_head(d, 76, 60, 1.1)
    d.ellipse([10, 84, 40, 116], fill=SKIN)
    d.rectangle([14, 70, 20, 90], fill=SKIN)
    d.rectangle([32, 70, 38, 90], fill=SKIN)
    finish(img, "fox_kon")
    img, d = icon_canvas(*FX)  # eyed claw
    for k in range(3):
        d.line([(40 + k * 18, 20), (26 + k * 18, 108)], fill=(255, 255, 255, 230), width=5)
    ring_eye(d, 64, 64, 10)
    finish(img, "fox_claw")
    img, d = icon_canvas(*FX)  # pounce
    d.arc([14, 30, 114, 130], 200, 340, fill=(255, 255, 255, 200), width=4)
    fox_head(d, 96, 50, 0.7)
    finish(img, "fox_pounce")
    img, d = icon_canvas(*FX)  # devour
    fox_head(d, 64, 56, 1.3)
    blood_drops(d, [(56, 104, 6), (72, 110, 5)])
    finish(img, "fox_devour")

    def skull(d, cx, cy, s=1.0):
        d.ellipse([cx - 22 * s, cy - 26 * s, cx + 22 * s, cy + 16 * s], fill=BONE, outline=(60, 50, 40, 255), width=2)
        for sx in (-1, 1):
            d.ellipse([cx + sx * 9 * s - 7 * s, cy - 10 * s, cx + sx * 9 * s + 7 * s, cy + 2 * s], fill=(16, 12, 14, 255))
            d.ellipse([cx + sx * 9 * s - 1.5 * s, cy - 5.5 * s, cx + sx * 9 * s + 1.5 * s, cy - 2.5 * s],
                      fill=(255, 244, 220, 255))
            poly(d, [(cx + sx * 16 * s, cy - 20 * s), (cx + sx * 34 * s, cy - 42 * s), (cx + sx * 22 * s, cy - 14 * s)],
                 (90, 80, 70, 255))
        d.rectangle([cx - 14 * s, cy + 10 * s, cx + 14 * s, cy + 22 * s], fill=BONE, outline=(60, 50, 40, 255))
        for k in range(6):
            x = cx - 12 * s + k * 4.8 * s
            d.line([(x, cy + 10 * s), (x, cy + 22 * s)], fill=(60, 50, 40, 255), width=1)

    def nail(d, x0, y0, x1, y1):
        d.line([(x0, y0), (x1, y1)], fill=(110, 96, 86, 255), width=6)
        d.line([(x0 - 8, y0 + 4), (x0 + 8, y0 - 4)], fill=(80, 70, 64, 255), width=6)

    img, d = icon_canvas(*CU)  # the nail
    nail(d, 30, 30, 96, 96)
    for k in range(3):
        d.ellipse([88 + k * 10, 20, 96 + k * 10, 28], fill=(200, 30, 30, 255))
    finish(img, "curse_nail")
    img, d = icon_canvas(*CU)  # crushing grip
    for k in range(4):
        d.line([(30 + k * 18, 104), (34 + k * 16, 40), (60 + k * 6, 26)], fill=BONE, width=8, joint="curve")
    d.ellipse([46, 60, 82, 96], fill=(120, 30, 30, 255))
    finish(img, "curse_grip")
    img, d = icon_canvas(*CU)  # hex
    skull(d, 64, 64, 1.4)
    finish(img, "curse_hex")
    img, d = icon_canvas(*CU)  # grave hands
    d.rectangle([0, 96, 128, 128], fill=(70, 56, 44, 255))
    for x in (24, 64, 104):
        d.line([(x, 100), (x, 60)], fill=BONE, width=7)
        for k in range(4):
            d.line([(x, 62), (x - 12 + k * 8, 40)], fill=BONE, width=4)
    finish(img, "curse_rise")

    def big_eye(d, cx, cy, r):
        d.ellipse([cx - r * 1.6, cy - r, cx + r * 1.6, cy + r], fill=(246, 238, 210, 255), outline=(60, 40, 30, 255),
                  width=3)
        d.ellipse([cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8], fill=(236, 196, 70, 255))
        for k in range(3):
            rr = r * 0.8 * (1 - (k + 0.5) / 3.6)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(120, 60, 20, 255), width=3)

    img, d = icon_canvas(*FU)  # foresight
    big_eye(d, 64, 64, 22)
    for k in range(3):
        d.arc([30 - k * 10, 30 - k * 10, 98 + k * 10, 98 + k * 10], -30, 30, fill=(255, 255, 255, 180), width=3)
    finish(img, "future_foresight")
    img, d = icon_canvas(*FU)  # glimpse of death
    big_eye(d, 64, 48, 16)
    d.line([(40, 96), (88, 96)], fill=(30, 20, 20, 255), width=4)
    poly(d, [(56, 96), (64, 76), (72, 96)], (30, 20, 20, 255))
    blood_drops(d, [(64, 110, 6)])
    finish(img, "future_glimpse")
    img, d = icon_canvas(*FU)  # long reach
    d.line([(10, 110), (40, 70), (80, 60), (112, 24)], fill=(96, 78, 64, 255), width=10, joint="curve")
    for k in range(4):
        d.line([(112, 24), (100 + k * 8, 6)], fill=(206, 196, 176, 255), width=4)
    finish(img, "future_reach")
    img, d = icon_canvas(*FU)  # future's the best
    for sx in (-1, 1):
        d.line([(64 + sx * 14, 70), (64 + sx * 36, 30), (64 + sx * 44, 14)], fill=(96, 78, 64, 255), width=8,
               joint="curve")
    d.ellipse([46, 56, 82, 100], fill=(206, 196, 176, 255))
    d.arc([52, 70, 76, 92], 20, 160, fill=(40, 8, 12, 255), width=4)
    for k in range(5):
        x = 44 + k * 10
        poly(d, [(x, 56), (x + 4, 38), (x + 8, 56)], (226, 214, 180, 255))
    finish(img, "future_best")

    GHOST = (226, 224, 236, 255)
    img, d = icon_canvas(*GH)  # strangle
    d.ellipse([44, 20, 84, 64], fill=(180, 170, 200, 255))
    for sx in (-1, 1):
        for k in range(4):
            y = 60 + k * 6
            d.line([(64 + sx * 34, y), (64 + sx * 6, y + 2)], fill=GHOST, width=5)
    d.line([(64, 94), (64, 118)], fill=(180, 170, 200, 255), width=10)
    finish(img, "ghost_strangle")
    img, d = icon_canvas(*GH)  # snatch
    d.arc([10, 10, 118, 118], 180, 330, fill=GHOST, width=6)
    for k in range(5):
        d.line([(100, 40), (112 - k * 6, 18 + k * 2)], fill=GHOST, width=4)
    finish(img, "ghost_snatch")
    img, d = icon_canvas(*GH)  # intangible
    d.ellipse([40, 20, 88, 80], fill=(226, 224, 236, 110))
    d.rectangle([48, 60, 80, 112], fill=(226, 224, 236, 90))
    d.ellipse([52, 38, 60, 48], fill=(40, 30, 40, 255))
    finish(img, "ghost_intangible")
    img, d = icon_canvas(*GH)  # smell fear
    d.ellipse([34, 30, 94, 94], fill=GHOST)
    d.ellipse([46, 48, 58, 58], fill=(70, 50, 44, 255))
    d.ellipse([70, 48, 82, 58], fill=(12, 10, 18, 255))
    for k in range(3):
        d.arc([20 - k * 8, 16 - k * 8, 108 + k * 8, 108 + k * 8], 200, 250, fill=(255, 220, 230, 200), width=3)
        d.arc([20 - k * 8, 16 - k * 8, 108 + k * 8, 108 + k * 8], 290, 340, fill=(255, 220, 230, 200), width=3)
    finish(img, "ghost_fear")


def icons_contract_moves():
    """The moves a contractor borrows (contract.ContractAbilities)."""
    FX = ((226, 120, 90), (60, 20, 14))
    CU = ((210, 200, 176), (30, 26, 22))
    FU = ((220, 190, 120), (40, 30, 20))
    GH = ((200, 196, 226), (40, 36, 70))
    FUR = (244, 240, 230, 255)
    BONE = (226, 218, 196, 255)
    GHOST = (226, 224, 240, 170)

    def fox_sign(d, x, y, s=1.0):
        """Aki's hand sign: middle and ring fingers pressed to the thumb (the snout), index and pinky up (the ears)."""
        d.ellipse([x - 12 * s, y - 6 * s, x + 12 * s, y + 18 * s], fill=SKIN, outline=(90, 60, 50, 255), width=2)
        for dx in (-9, 9):
            poly(d, [(x + (dx - 3) * s, y - 2 * s), (x + (dx + 3) * s, y - 2 * s), (x + dx * s, y - 22 * s)], SKIN,
                 outline=(90, 60, 50, 255), width=2)
        poly(d, [(x - 6 * s, y + 4 * s), (x + 6 * s, y + 4 * s), (x, y - 10 * s + 30 * s)], SKIN,
             outline=(90, 60, 50, 255), width=2)

    def fox_face(d, cx, cy, s):
        for sx in (-1, 1):
            poly(d, [(cx + sx * 26 * s, cy - 10 * s), (cx + sx * 34 * s, cy - 46 * s), (cx + sx * 8 * s, cy - 22 * s)],
                 FUR)
        poly(d, [(cx - 30 * s, cy - 18 * s), (cx + 30 * s, cy - 18 * s), (cx + 8 * s, cy + 22 * s),
                 (cx - 8 * s, cy + 22 * s)], FUR, outline=(90, 70, 60, 255), width=2)
        for sx, sy, r in ((-13, -6, 6), (13, -6, 6), (0, -14, 4), (-22, -14, 3), (22, -14, 3), (-7, -24, 3),
                          (7, -24, 3)):
            ring_eye(d, cx + sx * s, cy + sy * s, r * s)

    # Kon: the head alone, jaws gaping, out of nowhere - and the hand sign that calls it
    img, d = icon_canvas(*FX)
    d.ellipse([34, 8, 118, 92], fill=(30, 10, 16, 200))  # the dark it comes out of
    fox_face(d, 76, 44, 1.0)
    poly(d, [(56, 58), (96, 58), (86, 100), (66, 100)], (100, 16, 24, 255))
    for k in range(5):
        x = 60 + k * 8
        poly(d, [(x - 3, 58), (x + 3, 58), (x, 70)], (246, 242, 230, 255), outline=(60, 40, 40, 255), width=1)
        poly(d, [(x - 3, 100), (x + 3, 100), (x, 88)], (246, 242, 230, 255), outline=(60, 40, 40, 255), width=1)
    fox_sign(d, 28, 92, 0.9)
    finish(img, "contract_kon")

    def paw(d, cx, cy, s, down=True):
        # the forearm reaching out of nowhere, eyes all over it, and the claws
        arm = [(cx - 16 * s, cy - 60 * s), (cx + 16 * s, cy - 60 * s), (cx + 22 * s, cy), (cx - 22 * s, cy)]
        poly(d, arm, FUR, outline=(90, 70, 60, 255), width=2)
        d.ellipse([cx - 28 * s, cy - 14 * s, cx + 28 * s, cy + 16 * s], fill=FUR, outline=(90, 70, 60, 255), width=2)
        for k in range(4):
            x = cx - 18 * s + k * 12 * s
            poly(d, [(x - 3 * s, cy + 12 * s), (x + 3 * s, cy + 12 * s), (x, cy + 26 * s)], (40, 30, 28, 255))
        for ex, ey in ((-6, -40), (6, -26), (-8, -8), (10, -2)):
            ring_eye(d, cx + ex * s, cy + ey * s, 4 * s)

    img, d = icon_canvas(*FX)  # paw slam, from above
    d.ellipse([34, 0, 94, 24], fill=(30, 10, 16, 200))
    paw(d, 64, 74, 1.0)
    d.line([(20, 114), (108, 114)], fill=(60, 40, 30, 255), width=6)
    blood_drops(d, [(40, 106, 4), (90, 108, 4)])
    finish(img, "contract_paw_slam")
    img, d = icon_canvas(*FX)  # paw swipe, sideways
    d.arc([14, 14, 114, 114], 200, 340, fill=(255, 255, 255, 220), width=5)
    rot = Image.new("RGBA", img.size, (0, 0, 0, 0))
    paw(ImageDraw.Draw(rot), 64, 90, 0.9)
    img.alpha_composite(rot.rotate(70, center=(64, 64)))
    finish(img, "contract_paw_swipe")

    # the nail, three stabs, and the mouth counting down
    img, d = icon_canvas(*CU)
    d.line([(26, 26), (92, 92)], fill=(120, 100, 86, 255), width=8)
    d.line([(18, 34), (34, 18)], fill=(80, 70, 64, 255), width=8)
    poly(d, [(88, 96), (104, 104), (96, 88)], (150, 130, 110, 255))
    d.ellipse([60, 86, 96, 110], fill=(150, 30, 40, 255), outline=(40, 10, 10, 255), width=2)  # the lips
    d.line([(66, 98), (90, 98)], fill=(40, 10, 10, 255), width=3)
    for k in range(3):
        d.ellipse([74 + k * 12, 16, 84 + k * 12, 26], fill=(200, 30, 30, 255))
    finish(img, "contract_curse_nail")

    # the Future Devil in your right eye
    img, d = icon_canvas(*FU)
    d.ellipse([22, 36, 106, 92], fill=(246, 238, 210, 255), outline=(60, 40, 30, 255), width=3)
    d.ellipse([44, 42, 84, 82], fill=(236, 196, 70, 255))
    for k in range(3):
        rr = 20 * (1 - (k + 0.5) / 3.6)
        d.ellipse([64 - rr, 62 - rr, 64 + rr, 62 + rr], outline=(150, 50, 20, 255), width=3)
    for k in range(3):
        d.arc([10 - k * 6, 10 - k * 6, 118 + k * 6, 118 + k * 6], -40, 40, fill=(255, 255, 255, 180), width=3)
    finish(img, "contract_future_sight")

    # the ghost's arm: a huge pale hand only you can see
    def ghost_hand(d, cx, cy, s, fist=False):
        col = (236, 236, 252, 230)
        line = (150, 146, 190, 255)
        d.line([(cx - 64 * s, cy + 64 * s), (cx - 6 * s, cy + 6 * s)], fill=line, width=int(24 * s))
        d.line([(cx - 64 * s, cy + 64 * s), (cx - 6 * s, cy + 6 * s)], fill=col, width=int(18 * s))
        d.ellipse([cx - 20 * s, cy - 20 * s, cx + 20 * s, cy + 20 * s], fill=col, outline=line, width=3)
        # four long fingers (curled round a throat when it grips) and a thumb
        for k in range(4):
            a = math.radians(-160 + k * 30)
            L = 26 if fist else 44
            tip = (cx + math.cos(a) * L * s, cy + math.sin(a) * L * s)
            d.line([(cx + math.cos(a) * 12 * s, cy + math.sin(a) * 12 * s), tip], fill=line, width=int(13 * s))
            d.line([(cx + math.cos(a) * 12 * s, cy + math.sin(a) * 12 * s), tip], fill=col, width=int(8 * s))
            if fist:
                d.line([tip, (tip[0] + math.cos(a + 1.9) * 10 * s, tip[1] + math.sin(a + 1.9) * 10 * s)], fill=col,
                       width=int(8 * s))
        a = math.radians(40)
        d.line([(cx, cy), (cx + math.cos(a) * 30 * s, cy + math.sin(a) * 30 * s)], fill=line, width=int(13 * s))
        d.line([(cx, cy), (cx + math.cos(a) * 30 * s, cy + math.sin(a) * 30 * s)], fill=col, width=int(8 * s))

    img, d = icon_canvas(*GH)  # the grip on a throat
    d.ellipse([70, 14, 104, 50], fill=(120, 110, 130, 255))
    d.rectangle([80, 48, 94, 66], fill=(120, 110, 130, 255))
    ghost_hand(d, 82, 64, 1.0, fist=True)
    finish(img, "contract_ghost_hand")
    img, d = icon_canvas(*GH)  # the fling
    d.arc([12, 12, 116, 116], 180, 320, fill=(255, 255, 255, 200), width=5)
    ghost_hand(d, 76, 52, 0.9)
    d.ellipse([22, 20, 46, 44], fill=(120, 110, 130, 255))
    finish(img, "contract_ghost_fling")


# ----------------------------------------------------------------------------- particles
def particles():
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "main", "resources",
                        "assets", "csm")
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([10, 2, 54, 62], outline=(70, 72, 80, 255), width=12)
    d.arc([10, 2, 54, 62], 200, 310, fill=(214, 218, 226, 255), width=5)
    d.arc([10, 2, 54, 62], 20, 90, fill=(40, 40, 46, 255), width=4)
    img = img.resize((16, 16), Image.LANCZOS)
    img.save(os.path.join(base, "textures", "particle", "chain.png"))
    with open(os.path.join(base, "particles", "chain.json"), "w") as f:
        json.dump({"textures": ["csm:chain"]}, f, indent=2)


if __name__ == "__main__":
    items()
    icons()
    icons_early()
    icons_big()
    icons_contract()
    icons_contract_moves()
    particles()
    print("devil assets generated")
