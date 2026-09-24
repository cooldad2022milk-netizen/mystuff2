"""
Gun Fiend (the Gun Devil wearing Aki's body) - fiend parts model, texture atlas and GeckoLib animations.

Reference points:
  * loosed hair, dark veins spreading over the brow and eyes
  * the barrel of an M1911 jutting out between the eyes, its hammer poking out of the back of the skull
  * an M4 carbine where the left forearm used to be
  * letting more of the Gun Devil out: barrels burst out of the body
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview


def materials():
    a = Atlas(512, 64)
    a.add("slide", kind="metal", color=(56, 58, 64), scratches=6)
    a.add("steel", kind="metal", color=(96, 98, 106), scratches=5)
    a.add("black", kind="metal", color=(30, 30, 34), scratches=3)
    a.add("polymer", kind="rubber", color=(38, 38, 40))
    a.add("tan", kind="rubber", color=(150, 128, 92))
    a.add("bore", kind="void", color=(4, 4, 6))
    a.add("vein", kind="blood", color=(40, 10, 16))
    a.add("flesh", kind="flesh", color=(150, 44, 44))
    a.add("blood", kind="blood", color=(126, 8, 12))
    a.add("flash", kind="glow", color=(255, 170, 40), color2=(255, 250, 200), emissive=True)
    return a


def barrel(bone, base, direction, length, r, mats=("steel", "bore"), up=(0, 1, 0)):
    d = norm(direction)
    b = np.asarray(base, dtype=float)
    bone.cylinder(b + d * length / 2, d, r, length, mats[0], segments=8, up=up)
    bone.cylinder(b + d * (length + 0.02), d, r * 0.55, 0.1, mats[1], segments=6, up=up)
    bone.ring(b + d * (length - 0.4), d, r + 0.08, 0.15, 0.4, "black", count=8, up=up)


def build_head(m):
    m.bone("head", pivot=(0, 24, 0))
    h = m.bone("base_pistol", parent="head", pivot=(0, 28.8, -4))
    # M1911 slide and barrel jutting from between the eyes
    h.box((-0.75, 28.0, -11.0), (0.75, 29.6, -3.9), "slide")
    for k in range(6):
        h.box((-0.8, 28.3, -5.2 + k * 0.28), (0.8, 29.4, -5.1 + k * 0.28), "black")   # rear serrations
    h.box((-0.25, 29.6, -10.4), (0.25, 29.9, -9.9), "black")                      # front sight
    h.box((-0.45, 27.5, -11.1), (0.45, 28.1, -8.6), "steel")                      # recoil spring plug / barrel
    h.cylinder((0, 28.45, -11.05), (0, 0, -1), 0.32, 0.12, "bore", segments=6)
    h.box((-0.55, 29.0, -4.1), (0.55, 29.8, -3.9), "blood")
    # the hammer poking out of the back of the skull
    h.box((-0.4, 29.4, 4.0), (0.4, 30.6, 5.6), "steel")
    h.box((-0.5, 30.2, 5.2), (0.5, 30.9, 6.0), "black")
    # dark veins spreading over the brow and round the eyes
    rng = np.random.default_rng(9)
    for k in range(12):
        a = math.radians(-160 + k * 28)
        p = np.array([0.0, 28.8, -4.02])
        for i in range(3):
            q = p + np.array([math.cos(a) * 1.1, math.sin(a) * 0.9, 0]) + np.array([rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), 0])
            q[1] = min(q[1], 31.8)
            h.seg(p, q, 0.22, 0.12, "vein", up=(0, 0, -1), overlap=0.1)
            p = q
            a += rng.uniform(-0.5, 0.5)


def build_left_carbine(m):
    m.bone("left_arm", pivot=(5, 22, 0))
    g = m.bone("base_left_m4", parent="left_arm", pivot=(6, 16, 0))
    # the torn elbow where flesh becomes receiver
    g.cylinder((6, 17.2, 0), (0, 1, 0), 2.5, 1.2, "flesh", segments=8)
    g.box((3.9, 16.6, -2.1), (8.1, 17.0, 2.1), "blood")
    # lower + upper receiver swallowing the forearm
    g.box((3.6, 11.2, -2.6), (8.4, 16.8, 2.6), "polymer")
    g.box((3.9, 12.0, -2.9), (8.1, 16.4, -2.5), "black")
    # magazine sticking out in front, curved
    for i in range(4):
        g.box((4.6, 13.8 - i * 0.2, -2.9 - i * 1.1), (7.4, 15.8 - i * 0.2, -1.8 - i * 1.1), "tan")
    # carry rail / charging handle along the back
    g.box((5.3, 11.0, 2.6), (6.7, 16.8, 3.2), "black")
    for k in range(8):
        g.box((5.2, 11.2 + k * 0.7, 3.2), (6.8, 11.5 + k * 0.7, 3.5), "steel")
    # quad-rail handguard over where the hand was, then the barrel and front sight post
    g.box((4.3, 4.6, -1.9), (7.7, 11.2, 1.9), "black")
    for k in range(9):
        g.box((4.1, 4.9 + k * 0.7, -2.1), (7.9, 5.2 + k * 0.7, 2.1), "steel")
    barrel(g, (6, 4.7, 0), (0, -1, 0), 5.2, 0.45, up=(0, 0, -1))
    g.box((5.6, 3.2, 1.2), (6.4, 5.4, 2.4), "black")
    g.cylinder((6, -0.8, 0), (0, 1, 0), 0.7, 1.2, "black", segments=6)       # flash hider
    # muzzle flash (only while firing)
    fl = m.bone("fx_storm_carbine", parent="base_left_m4", pivot=(6, -1.5, 0))
    fl.spike((6, -1.4, 0), (0, -1, 0), 2.6, 1.8, 1.8, "flash", steps=3, up=(0, 0, -1))


def build_barrels(m):
    m.bone("body", pivot=(0, 24, 0))
    b = m.bone("form_barrels", parent="body", pivot=(0, 20, 0))
    rng = np.random.default_rng(13)
    sprouts = [((-3.4, 23.2, 1.8), (-0.6, 1, 0.7), 7.0, 0.55), ((3.4, 23.4, 1.6), (0.7, 1, 0.6), 7.5, 0.6),
               ((-1.6, 21.0, 2.3), (-0.3, 0.6, 1), 6.0, 0.5), ((1.8, 19.5, 2.3), (0.4, 0.4, 1), 6.5, 0.55),
               ((0.0, 16.5, 2.3), (0, 0.2, 1), 5.5, 0.5), ((-3.9, 18.0, -1.0), (-1, 0.3, -0.4), 5.0, 0.45),
               ((3.9, 17.5, -0.8), (1, 0.4, -0.3), 5.2, 0.45), ((-2.5, 15.0, -2.2), (-0.4, -0.2, -1), 4.5, 0.4),
               ((2.4, 22.0, -2.2), (0.5, 0.5, -1), 4.2, 0.4)]
    for i, (base, d, L, r) in enumerate(sprouts):
        base = np.array(base)
        d = norm(d)
        b.cylinder(base, d, r + 0.6, 0.8, "flesh", segments=8)
        barrel(b, base + d * 0.3, d, L, r)
        if i % 2 == 0:
            b.box(base + d * 1.2 - np.array([0.6, 0.6, 0.6]), base + d * 1.2 + np.array([0.6, 0.6, 0.6]), "black")
        fl = m.bone("fx_storm_flash_%d" % i, parent="form_barrels", pivot=tuple(base + d * (L + 0.3)))
        fl.spike(base + d * (L + 0.3), d, 2.2, 1.6, 1.6, "flash", steps=3)
    _ = rng


def build():
    atlas = materials()
    m = Model("csm.gun_fiend", atlas, density=2.0, seed=101)
    build_head(m)
    build_barrels(m)
    m.bone("right_arm", pivot=(-5, 22, 0))
    build_left_carbine(m)
    geo = out("geo", "hybrid", "gun.geo.json")
    tex = out("textures", "hybrid", "gun.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "gun_glowmask.png"), seed=61)
    anims = animations()
    anim_path = out("animations", "hybrid", "gun.animation.json")
    save_animations(anim_path, anims)
    print("gun: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


FLASHES = ["fx_storm_flash_%d" % i for i in range(9)]


def animations():
    A = []
    e = Anim("emerge", 0.8)
    e.scale("form_barrels", 0, 0.1).scale("form_barrels", 0.25, 1.15, "easeOutBack").scale("form_barrels", 0.4, 1.0)
    A.append(e)
    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    r.scale("form_barrels", 0, 1).scale("form_barrels", 0.3, 0.1, "easeInBack")
    A.append(r)
    A.append(Anim("idle", 2.0, loop=True))

    def flash(anim, bone, t):
        anim.scale(bone, t - 0.01, 0.2).scale(bone, t + 0.02, 1.3).scale(bone, t + 0.07, 0.2)

    bu = Anim("burst", 1.2)
    for t in (0.2, 0.25, 0.3, 0.6, 0.65, 0.7, 1.0, 1.05, 1.1):
        flash(bu, "fx_storm_carbine", t)
        bu.pos("base_left_m4", t, (0, 0.6, 0)).pos("base_left_m4", t + 0.04, (0, 0, 0))
    A.append(bu)
    hs = Anim("headshot", 1.0)
    hs.pos("base_pistol", 0.58, (0, 0, 0)).pos("base_pistol", 0.6, (0, 0, 2.2)).pos("base_pistol", 0.75, (0, 0, 0), "easeOutQuad")
    A.append(hs)
    st = Anim("storm", 2.0)
    for k in range(14):
        t = 0.3 + k * 0.1
        flash(st, FLASHES[k % len(FLASHES)], t)
        flash(st, FLASHES[(k * 4 + 2) % len(FLASHES)], t + 0.05)
    A.append(st)
    ma = Anim("massacre", 2.0)
    for k in range(18):
        t = 0.6 + k * 0.05
        flash(ma, FLASHES[(k * 5) % len(FLASHES)], t)
        flash(ma, "fx_storm_carbine", t + 0.02)
    A.append(ma)
    A.append(Anim("drink", 1.0))
    return A


def render_previews(geo, tex, anim):
    arms = {"right_arm": {"rot": (0, 0, 0.1)}, "left_arm": {"rot": (0, 0, -0.1)}}
    shots = [
        preview.render(geo, tex, preview_path("gun_base.png"), anim, "burst", 0.0, yaw=30, pitch=6, pose=arms,
                       hidden=("form_barrels", "fx_storm_carbine"), show_head=True, scale=10, center=(0, 1.2)),
        preview.render(geo, tex, preview_path("gun_face.png"), anim, "burst", 0.0, yaw=50, pitch=8,
                       hidden=("form_barrels", "fx_storm_carbine", "body", "left_arm"), show_head=True, scale=20,
                       center=(0, 1.8), size=(640, 520)),
        preview.render(geo, tex, preview_path("gun_devil.png"), anim, "storm", 0.32, yaw=150, pitch=10,
                       pose={"left_arm": {"rot": (-1.5, 0, 0)}}, show_head=True, scale=9, center=(0, 1.2)),
    ]
    return preview.contact_sheet(shots, preview_path("gun_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
