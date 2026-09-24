"""
Flamethrower Hybrid (Barem Bridge) - devil parts model, texture atlas and GeckoLib animations.

Manga reference points:
  * trigger: biting down on / pressing his molar (pressing it again restores him to peak condition)
  * head becomes three huge fuel tanks; the neck becomes a jumble of metal parts
  * both arms become giant flamethrowers that can engulf a whole floor in fire
"""
import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm, bezier, rotate_about
from csmgen.tex import paint_atlas
from csmgen import preview


def materials():
    a = Atlas(512, 64)
    a.add("tank", kind="painted", color=(142, 36, 28), color2=(74, 64, 58))
    a.add("tank_lt", kind="painted", color=(170, 54, 38), color2=(90, 70, 60))
    a.add("band", kind="metal", color=(92, 94, 100))
    a.add("steel", kind="metal", color=(162, 166, 172))
    a.add("steel_dk", kind="metal", color=(66, 68, 74), scratches=5)
    a.add("brass", kind="metal", color=(204, 160, 70), scratches=3)
    a.add("soot", kind="void", color=(30, 26, 24))
    a.add("hose", kind="rubber", color=(30, 30, 33))
    a.add("gauge", kind="gauge", color=(238, 234, 220))
    a.add("hazard", kind="stripes", color=(232, 188, 30), color2=(24, 24, 24))
    a.add("flesh", kind="flesh", color=(160, 40, 40))
    a.add("shroud", kind="chain", color=(96, 98, 104))
    a.add("rust", kind="rust", color=(150, 80, 40), color2=(70, 40, 24))
    a.add("pilot", kind="glow", color=(70, 120, 255), color2=(220, 235, 255), emissive=True)
    a.add("flame", kind="glow", color=(255, 96, 16), color2=(255, 214, 90), emissive=True)
    a.add("flame_core", kind="glow", color=(255, 220, 120), color2=(255, 255, 235), emissive=True)
    return a


TANKS = {"a": (-2.9, -0.7, 2.55, 11.0), "b": (2.9, -0.7, 2.55, 11.0), "c": (0.0, 3.0, 2.7, 12.5)}
TANK_BASE = 27.1


def build_tank(m, key):
    x, z, r, h = TANKS[key]
    b = m.bone("form_tank_" + key, parent="form_head", pivot=(x, TANK_BASE, z))
    y0 = TANK_BASE
    top = y0 + h
    b.cylinder((x, y0 + h / 2, z), (0, 1, 0), r, h - 1.4, "tank" if key != "c" else "tank_lt", segments=12)
    b.cylinder((x, y0 + 0.35, z), (0, 1, 0), r * 0.86, 0.72, "tank", segments=12)
    b.cylinder((x, top - 0.35, z), (0, 1, 0), r * 0.86, 0.72, "tank", segments=12)
    b.cylinder((x, top + 0.2, z), (0, 1, 0), r * 0.58, 0.5, "band", segments=10)
    for yy in (y0 + 1.8, top - 1.8):
        b.ring((x, yy, z), (0, 1, 0), r + 0.08, 0.3, 0.55, "band", count=12)
        for k in range(4):
            ang = np.radians(45 + 90 * k)
            b.cbox((x + np.sin(ang) * (r + 0.28), yy, z - np.cos(ang) * (r + 0.28)), (0.35, 0.35, 0.35), "brass")
    b.cylinder((x, y0 + h * 0.52, z), (0, 1, 0), r + 0.04, 1.3, "hazard", segments=12)
    # valve + hand wheel on top
    b.cylinder((x, top + 0.9, z), (0, 1, 0), 0.5, 1.0, "brass", segments=6)
    b.ring((x, top + 1.45, z), (0, 1, 0), 0.95, 0.22, 0.22, "brass", count=8)
    b.cbox((x, top + 1.45, z), (1.9, 0.2, 0.22), "brass")
    b.cbox((x, top + 1.45, z), (0.22, 0.2, 1.9), "brass")
    return (x, top + 1.0, z)


def build_head(m):
    m.bone("head", pivot=(0, 24, 0))
    f = m.bone("form_head", parent="head", pivot=(0, 24, 0))
    # neck: a jumble of metal parts
    n = m.bone("form_neck", parent="form_head", pivot=(0, 24, 0.4))
    n.cylinder((0, 23.7, 0.4), (0, 1, 0), 2.55, 0.9, "flesh", segments=10)
    n.cylinder((0, 25.0, 0.4), (0, 1, 0), 2.3, 2.4, "steel_dk", segments=10)
    n.cylinder((0, 26.75, 0.6), (0, 1, 0), 4.3, 0.6, "steel_dk", segments=12)
    n.ring((0, 26.4, 0.6), (0, 1, 0), 3.6, 0.3, 0.3, "band", count=12)
    pipes = [((-2.6, 23.9, -1.6), (-1.1, 25.2, -3.0), (-1.4, 26.4, -2.6), "steel", 0.45),
             ((2.5, 23.7, -1.8), (3.6, 25.0, -1.4), (3.2, 26.5, -0.6), "hose", 0.5),
             ((-3.0, 24.2, 1.9), (-3.9, 25.3, 2.4), (-2.6, 26.5, 3.0), "brass", 0.42),
             ((2.0, 24.0, 2.4), (3.4, 25.0, 3.3), (2.9, 26.4, 2.3), "steel", 0.4),
             ((-0.6, 23.9, 2.9), (0.4, 25.2, 3.6), (1.0, 26.4, 3.2), "hose", 0.48)]
    for a, b_, c, mat, r in pipes:
        pts = [bezier(a, b_, b_, c, t) for t in np.linspace(0, 1, 5)]
        for p, q in zip(pts, pts[1:]):
            n.tube(p, q, r, mat, segments=6)
    # pressure gauge + valve wheel on the throat
    n.cylinder((0.8, 25.2, -2.55), (0, 0, -1), 1.15, 0.6, "steel", segments=10)
    n.cylinder((0.8, 25.2, -2.9), (0, 0, -1), 0.98, 0.12, "gauge", segments=10)
    n.tube((0.8, 25.2, -2.2), (0.8, 25.2, -1.6), 0.3, "brass", segments=6)
    n.ring((-1.9, 24.6, -2.4), (0.3, 0, -1), 0.7, 0.18, 0.2, "brass", count=8)
    n.tube((-1.9, 24.6, -2.3), (-1.9, 24.6, -1.4), 0.2, "brass", segments=4)
    for k in range(6):
        ang = np.radians(k * 60)
        n.cbox((np.sin(ang) * 3.9, 27.1, 0.6 - np.cos(ang) * 3.9), (0.45, 0.3, 0.45), "brass")

    valves = {k: build_tank(m, k) for k in TANKS}
    # feed lines between the tank valves and down the back
    p = m.bone("form_pipes", parent="form_head", pivot=(0, 38, 1))
    for a, b_ in (("a", "c"), ("b", "c"), ("a", "b")):
        A = np.array(valves[a])
        B = np.array(valves[b_])
        mid = (A + B) / 2 + np.array([0, 2.2, 0])
        pts = [bezier(A, mid, mid, B, t) for t in np.linspace(0, 1, 7)]
        for u, v in zip(pts, pts[1:]):
            p.tube(u, v, 0.32, "hose" if a != "a" or b_ != "b" else "steel", segments=6)
    C = np.array(valves["c"])
    back = [C, C + np.array([0, 1.5, 2.2]), np.array([0.5, 30.0, 6.4]), np.array([0.8, 26.9, 4.2])]
    pts = [bezier(*back, t) for t in np.linspace(0, 1, 9)]
    for u, v in zip(pts, pts[1:]):
        p.tube(u, v, 0.45, "hose", segments=6)


def build_arm(m, side):
    sgn = -1 if side == "right" else 1

    def X(o):
        return sgn * o

    name = side + "_arm"
    m.bone(name, pivot=(X(5), 22, 0))
    f = m.bone("form_" + name, parent=name, pivot=(X(6), 22, 0))
    # shoulder mount
    f.box((X(3.5), 20.8, -2.9), (X(8.7), 24.8, 2.9), "steel_dk")
    f.box((X(4.1), 24.8, -2.4), (X(8.1), 25.4, 2.4), "band")
    for zz in (-2.0, 0, 2.0):
        f.cbox((X(8.75), 23.8, zz), (0.3, 0.5, 0.5), "brass")
    # fuel canister (upper arm)
    f.cylinder((X(6.1), 17.4, 0), (0, 1, 0), 3.0, 7.0, "tank", segments=12)
    f.cylinder((X(6.1), 20.9, 0), (0, 1, 0), 2.6, 0.5, "band", segments=12)
    for yy in (19.8, 15.0):
        f.ring((X(6.1), yy, 0), (0, 1, 0), 3.06, 0.3, 0.55, "band", count=12)
    f.cylinder((X(6.1), 17.4, 0), (0, 1, 0), 3.04, 1.1, "hazard", segments=12)
    f.cylinder((X(9.2), 17.4, 0), (1, 0, 0), 0.6, 0.8, "brass", segments=6)
    f.ring((X(9.7), 17.4, 0), (1, 0, 0), 0.8, 0.18, 0.2, "brass", count=8)
    # grip / regulator housing where the hand was
    f.box((X(4.3), 11.2, -2.3), (X(7.9), 14.0, 2.3), "steel_dk")
    f.box((X(4.1), 12.0, -2.45), (X(8.1), 12.6, 2.45), "band")
    f.cylinder((X(6.1), 12.6, -2.55), (0, 0, -1), 0.8, 0.5, "steel", segments=8)
    f.cylinder((X(6.1), 12.6, -2.82), (0, 0, -1), 0.66, 0.08, "gauge", segments=8)
    # hoses from the canister down to the barrel
    for zz, mat in ((2.2, "hose"), (-1.9, "hose")):
        P = [(X(8.3), 15.0, zz), (X(9.4), 12.5, zz * 1.1), (X(8.4), 9.6, zz * 0.7), (X(7.3), 8.0, zz * 0.4)]
        pts = [bezier(*P, t) for t in np.linspace(0, 1, 7)]
        for u, v in zip(pts, pts[1:]):
            f.tube(u, v, 0.42, mat, segments=6)

    # barrel (own bone so it can telescope out / recoil)
    b = m.bone(side + "_barrel", parent="form_" + name, pivot=(X(6.1), 11.2, 0))
    b.cylinder((X(6.1), 6.9, 0), (0, 1, 0), 1.3, 8.6, "steel", segments=8)
    b.cylinder((X(6.1), 7.4, 0), (0, 1, 0), 2.05, 6.4, "shroud", segments=10)
    for yy in (10.6, 4.2):
        b.cylinder((X(6.1), yy, 0), (0, 1, 0), 2.2, 0.45, "band", segments=10)
    b.taper((X(6.1), 2.6, 0), (0, -1, 0), 1.9, 1.75, 1.15, "soot", steps=3, segments=10)
    b.cylinder((X(6.1), 0.55, 0), (0, 1, 0), 1.3, 0.45, "steel_dk", segments=10)
    b.cylinder((X(6.1), 0.3, 0), (0, 1, 0), 0.8, 0.12, "flame_core", segments=8)
    # pilot light under the nozzle
    b.box((X(5.6), 1.2, -2.3), (X(6.6), 2.2, -1.5), "steel_dk")
    b.tube((X(6.1), 4.0, -1.7), (X(6.1), 2.0, -1.95), 0.18, "brass", segments=4)
    pl = m.bone(side + "_pilot", parent=side + "_barrel", pivot=(X(6.1), 1.0, -1.9))
    pl.cbox((X(6.1), 0.95, -1.9), (0.5, 0.6, 0.5), "pilot")
    pl.cbox((X(6.1), 0.45, -1.9), (0.3, 0.5, 0.3), "flame_core")

    # flame jet (only drawn while a flame ability is running)
    fx = m.bone("fx_flame_" + side, parent=side + "_barrel", pivot=(X(6.1), 0.2, 0))
    base = np.array([X(6.1), 0.2, 0.0])
    down = np.array([0, -1.0, 0])
    for k in range(3):
        up = rotate_about(np.array([1.0, 0, 0]), down, 60 * k)
        for i, (L, w0, w1, mat) in enumerate(((3.0, 1.2, 3.2, "flame_core"), (4.0, 3.2, 5.8, "flame"),
                                              (5.0, 5.8, 7.8, "flame"), (5.0, 7.8, 6.0, "flame"))):
            off = sum(x[0] for x in ((3.0,), (4.0,), (5.0,), (5.0,))[:i])
            c = base + down * (off + L / 2)
            fx.obox(c, down, (0.0, L, (w0 + w1) / 2), mat, up=up)
    fx.cylinder(base + down * 3.5, down, 0.7, 7.0, "flame_core", segments=6)


def build():
    atlas = materials()
    m = Model("csm.flamethrower_hybrid", atlas, density=2.0, seed=31)
    build_head(m)
    m.bone("body", pivot=(0, 24, 0))
    build_arm(m, "right")
    build_arm(m, "left")
    geo = out("geo", "hybrid", "flamethrower.geo.json")
    tex = out("textures", "hybrid", "flamethrower.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "flamethrower_glowmask.png"), seed=13)
    anims = animations()
    anim_path = out("animations", "hybrid", "flamethrower.animation.json")
    save_animations(anim_path, anims)
    print("flamethrower: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    e = Anim("emerge", 0.85)
    e.scale("form_neck", 0, 0.4).scale("form_neck", 0.14, 1.12, "easeOutBack").scale("form_neck", 0.24, 1.0)
    for i, k in enumerate(("c", "a", "b")):
        t0 = 0.06 + i * 0.07
        bn = "form_tank_" + k
        e.pos(bn, 0, (0, -9, 0)).pos(bn, t0, (0, -9, 0)).pos(bn, t0 + 0.22, (0, 0.8, 0), "easeOutBack")
        e.pos(bn, t0 + 0.34, (0, 0, 0), "easeInOutSine")
        e.scale(bn, 0, 0.2).scale(bn, t0, 0.2).scale(bn, t0 + 0.2, 1.08, "easeOutBack").scale(bn, t0 + 0.32, 1.0)
    e.scale("form_pipes", 0, 0).scale("form_pipes", 0.4, 0).scale("form_pipes", 0.55, 1.0, "easeOutBack")
    for i, side in enumerate(("right", "left")):
        o = i * 0.05
        fa = "form_%s_arm" % side
        e.scale(fa, 0, 0.5).scale(fa, 0.16 + o, 1.12, "easeOutBack").scale(fa, 0.3 + o, 1.0)
        br = side + "_barrel"
        e.scale(br, 0, (1, 0.1, 1)).scale(br, 0.2 + o, (1, 0.1, 1)).scale(br, 0.4 + o, (1, 1.12, 1), "easeOutBack")
        e.scale(br, 0.5 + o, (1, 1, 1))
        pl = side + "_pilot"
        e.scale(pl, 0, 0).scale(pl, 0.55 + o, 0).scale(pl, 0.7 + o, 1.4, "easeOutBack").scale(pl, 0.85, 1.0)
    A.append(e)

    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    for k in ("a", "b", "c"):
        r.pos("form_tank_" + k, 0, (0, 0, 0)).pos("form_tank_" + k, 0.3, (0, -9, 0), "easeInBack")
        r.scale("form_tank_" + k, 0.1, 1.0).scale("form_tank_" + k, 0.35, 0.2)
    r.scale("form_pipes", 0, 1).scale("form_pipes", 0.1, 0)
    for side in ("right", "left"):
        r.scale(side + "_barrel", 0, (1, 1, 1)).scale(side + "_barrel", 0.25, (1, 0.1, 1), "easeInBack")
        r.scale("form_%s_arm" % side, 0.1, 1.0).scale("form_%s_arm" % side, 0.4, 0.5, "easeInQuad")
    A.append(r)

    idle = Anim("idle", 1.2, loop=True)
    for k, ph in (("a", 0.0), ("b", 0.2), ("c", 0.1)):
        bn = "form_tank_" + k
        for t in np.arange(0, 1.21, 0.1):
            idle.rot(bn, t, (0.35 * np.sin(t * 31 + ph * 20), 0, 0.3 * np.cos(t * 27 + ph * 20)))
    for side in ("right", "left"):
        pl = side + "_pilot"
        for t, s in ((0, 1.0), (0.15, 1.25), (0.3, 0.9), (0.5, 1.2), (0.7, 0.95), (0.9, 1.3), (1.2, 1.0)):
            idle.scale(pl, t, (s, s * 1.2, s))
    A.append(idle)

    fl = Anim("flame", 0.3, loop=True)
    for side in ("right", "left"):
        fx = "fx_flame_" + side
        for t, s, ry in ((0, 1.0, 0), (0.05, 1.15, 25), (0.1, 0.92, 55), (0.15, 1.2, 85), (0.2, 0.95, 120),
                         (0.25, 1.1, 150), (0.3, 1.0, 180)):
            fl.scale(fx, t, (s, 1.0 + (s - 1) * 1.6, s)).rot(fx, t, (0, ry, 0))
        br = side + "_barrel"
        for t, a in ((0, 0), (0.05, 1.4), (0.1, -1.0), (0.15, 1.2), (0.2, -1.3), (0.25, 0.9), (0.3, 0)):
            fl.rot(br, t, (a, 0, -a * 0.6))
    for k in ("a", "b", "c"):
        for t, a in ((0, 0), (0.075, 1.2), (0.15, -1.0), (0.225, 0.8), (0.3, 0)):
            fl.rot("form_tank_" + k, t, (a, 0, -a))
    A.append(fl)

    nap = Anim("napalm", 0.6)
    nap.pos("right_barrel", 0, (0, 0, 0)).pos("right_barrel", 0.26, (0, 0, 0)).pos("right_barrel", 0.29, (0, 2.6, 0))
    nap.pos("right_barrel", 0.6, (0, 0, 0), "easeOutQuad")
    nap.scale("right_pilot", 0.25, 1).scale("right_pilot", 0.28, 2.2).scale("right_pilot", 0.5, 1.0)
    A.append(nap)

    burst = Anim("burst", 1.0)
    for side in ("right", "left"):
        br = side + "_barrel"
        burst.pos(br, 0, (0, 0, 0)).pos(br, 0.45, (0, 0, 0)).pos(br, 0.5, (0, 3.0, 0)).pos(br, 0.9, (0, 0, 0),
                                                                                         "easeOutQuad")
    for k in ("a", "b", "c"):
        bn = "form_tank_" + k
        burst.scale(bn, 0, 1.0).scale(bn, 0.4, 1.06, "easeInQuad").scale(bn, 0.5, 0.94).scale(bn, 0.8, 1.0,
                                                                                               "easeOutBack")
    A.append(burst)

    regen = Anim("regen", 0.8)
    for i, k in enumerate(("a", "b", "c")):
        bn = "form_tank_" + k
        t0 = 0.3 + i * 0.05
        regen.scale(bn, 0, 1.0).scale(bn, t0, 1.12, "easeOutQuad").scale(bn, t0 + 0.3, 1.0, "easeInOutSine")
    regen.scale("form_neck", 0.3, 1.0).scale("form_neck", 0.4, 1.1).scale("form_neck", 0.7, 1.0)
    A.append(regen)

    dr = Anim("drink", 1.0)
    dr.rot("form_neck", 0, (0, 0, 0)).rot("form_neck", 0.3, (8, 0, 0)).rot("form_neck", 0.7, (8, 0, 0))
    dr.rot("form_neck", 1.0, (0, 0, 0))
    A.append(dr)
    return A


def render_previews(geo, tex, anim):
    hide = ("fx_flame_right", "fx_flame_left")
    shots = [
        preview.render(geo, tex, preview_path("flame_front.png"), anim, "idle", 0.0, yaw=25, pitch=8,
                       show_arms=False, hidden=hide, scale=10.5, center=(0, 1.35)),
        preview.render(geo, tex, preview_path("flame_fire.png"), anim, "flame", 0.1, yaw=-50, pitch=12,
                       show_arms=False, pose={"right_arm": {"rot": (-1.5, 0.1, 0)},
                                              "left_arm": {"rot": (-1.45, -0.1, 0)}},
                       scale=8.5, center=(0, 1.25)),
        preview.render(geo, tex, preview_path("flame_head.png"), anim, "idle", 0.0, yaw=30, pitch=14,
                       show_body=False, scale=18, center=(0, 2.0), size=(640, 520),
                       hidden=hide + ("body", "right_arm", "left_arm")),
        preview.render(geo, tex, preview_path("flame_emerge.png"), anim, "emerge", 0.2, yaw=25, pitch=8,
                       show_arms=False, hidden=hide, scale=10.5, center=(0, 1.35)),
    ]
    return preview.contact_sheet(shots, preview_path("flame_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
