"""
Spear Hybrid - devil parts model, texture atlas and GeckoLib animations, plus the spear entity.

Manga reference points:
  * trigger: he reaches over his shoulder and pulls a spear out of the nape of his neck
  * head: a huge dark reddish-brown, leaf-shaped spearhead jutting forward out of a socket,
    with a mouth of huge sharp teeth underneath
  * arms: covered in the same dark metallic armour as the head
  * powers: makes spears out of his body for melee and throwing, with inhuman accuracy
    (impaled Pochita from behind; spears erupting out of the ground)

Bone naming contract with HybridPartRenderer: form_* / human_nape_spear (the butt of the spear sticking out of the
nape while human) / trig_right_spear (the spear drawn out during the trigger, oriented by IK in poses.py).
"""
import math

import numpy as np

from common import out, preview_path, arc_point
from csmgen.geo import Atlas, Model, Anim, save_animations, norm, rotate_about, frame_from, euler_for
from csmgen.tex import paint_atlas
from csmgen import preview
import poses


def materials():
    a = Atlas(512, 64)
    a.add("metal", kind="metal", color=(112, 54, 42), scratches=6)
    a.add("metal_dk", kind="metal", color=(64, 32, 28), scratches=4)
    a.add("metal_lt", kind="metal", color=(146, 78, 60), scratches=5)
    a.add("edge", kind="metal", color=(196, 150, 128), scratches=10)
    a.add("rust", kind="rust", color=(120, 56, 34), color2=(64, 30, 20))
    a.add("teeth", kind="teeth", color=(236, 228, 206))
    a.add("mouth", kind="void", color=(30, 8, 10))
    a.add("gum", kind="flesh", color=(130, 30, 36))
    a.add("shaft", kind="metal", color=(78, 40, 32), scratches=3)
    a.add("wrap", kind="fiber", color=(52, 30, 26))
    a.add("blood", kind="blood", color=(126, 8, 12))
    a.add("flesh", kind="flesh", color=(150, 40, 40))
    return a


def leaf_w(t, wmax):
    """Width of a leaf-shaped spearhead at t in [0, 1] (0 = socket, 1 = point); widest a third of the way up."""
    if t < 0.32:
        return wmax * (0.42 + 0.58 * math.sin(t / 0.32 * math.pi / 2))
    u = (t - 0.32) / 0.68
    return wmax * math.cos(u * math.pi / 2) ** 0.85


def spearhead(bone, base, direction, length, wmax, thick, up, mats=("metal", "edge", "metal_dk"), steps=14,
              socket=True):
    """Leaf blade: a thin wide plate, a thick central ridge, bright honed edges."""
    D = norm(direction)
    N = norm(np.asarray(up, dtype=float) - np.dot(up, D) * D)
    W = np.cross(D, N)
    base = np.asarray(base, dtype=float)
    step = length / steps
    for i in range(steps):
        t = (i + 0.5) / steps
        w = leaf_w(t, wmax)
        c = base + D * (step * (i + 0.5))
        bone.obox(c, D, (max(w, 0.15), step * 1.05, max(thick * 0.45 * (1 - 0.6 * t), 0.12)), mats[0], up=N)
        bone.obox(c, D, (max(w * 0.28, 0.14), step * 1.05, max(thick * (1 - 0.65 * t), 0.14)), mats[2], up=N)
    for s in (-1, 1):
        pts = [base + D * (length * t) + W * s * (leaf_w(t, wmax) / 2 - 0.05) for t in np.linspace(0.02, 0.985, 12)]
        bone.curve(pts, 0.35, 0.16, max(thick * 0.3, 0.12), 0.1, mats[1], up=N)
    bone.spike(base + D * (length * 0.97), D, length * 0.08, 0.4, 0.3, mats[1], steps=2, up=N)
    if socket:
        bone.taper(base - D * 1.6, D, 1.8, wmax * 0.2, wmax * 0.14, mats[2], steps=2, segments=8, up=N)
        bone.ring(base - D * 0.4, D, wmax * 0.2 + 0.1, 0.25, 0.4, mats[1], count=8, up=N)


# ------------------------------------------------------------------------------------------ head
BLADE_BASE = np.array([0.0, 28.6, -0.6])
BLADE_DIR = norm([0.0, 0.72, -1.0])
BLADE_UP = norm(np.cross(BLADE_DIR, [1.0, 0, 0]))  # blade plane is horizontal-ish, width along x


def build_head(m):
    m.bone("head", pivot=(0, 24, 0))
    f = m.bone("form_head", parent="head", pivot=(0, 24, 0))
    # socket skull: a ferrule that swells into the upper jaw
    for y0, y1, r, mat in ((24.0, 25.0, 2.5, "metal_dk"), (25.0, 26.2, 3.3, "metal"), (26.2, 27.6, 3.7, "metal"),
                           (27.6, 28.6, 3.4, "metal_lt"), (28.6, 29.4, 2.7, "metal"), (29.4, 30.0, 2.1, "metal_dk")):
        # open at the front below y 26.2 for the maw
        if y1 <= 26.2:
            for i in range(14):
                pa = 70 + 220 * i / 14
                pb = 70 + 220 * (i + 1) / 14
                a = arc_point(r - 0.45, r - 0.45, pa, (y0 + y1) / 2, 0.4)
                b = arc_point(r - 0.45, r - 0.45, pb, (y0 + y1) / 2, 0.4)
                f.seg(a, b, 0.9, y1 - y0 + 0.06, mat, overlap=0.25)
        else:
            f.cylinder((0, (y0 + y1) / 2, 0.4), (0, 1, 0), r, y1 - y0 + 0.05, mat, segments=14)
    for yy in (27.6, 29.4):
        f.ring((0, yy, 0.4), (0, 1, 0), 3.55 if yy < 28 else 2.8, 0.3, 0.3, "edge", count=14)
    # rivets round the socket
    for k in range(10):
        a = math.radians(k * 36 + 18)
        f.cbox((math.sin(a) * 3.72, 26.9, 0.4 - math.cos(a) * 3.72), (0.4, 0.4, 0.4), "edge")
    # palate / throat inside the maw
    f.box((-2.6, 25.9, -2.4), (2.6, 26.25, 1.8), "mouth")
    f.box((-2.4, 24.0, 1.0), (2.4, 26.2, 1.6), "mouth")
    # huge sharp upper teeth hanging from the front rim of the socket
    for k in range(9):
        phi = -72 + 18 * k
        p = arc_point(3.1, 3.1, phi, 26.2, 0.4)
        L = 2.5 - 0.5 * abs(phi) / 72
        f.spike(p, norm([0, -1.0, 0.1]), L, 0.95, 0.55, "teeth", steps=4, up=norm(p - np.array([0, 26.2, 0.4])))
    # the blade, jutting up and forward (own bone so it can shiver / grow)
    bl = m.bone("spear_blade", parent="form_head", pivot=tuple(BLADE_BASE))
    spearhead(bl, BLADE_BASE, BLADE_DIR, 14.0, 7.2, 1.9, BLADE_UP, steps=16)
    # collar where the blade seats into the skull
    bl.ring(BLADE_BASE + BLADE_DIR * 0.2, BLADE_DIR, 1.8, 0.4, 0.8, "metal_dk", count=10, up=BLADE_UP)
    # lower jaw with its own row of huge teeth
    j = m.bone("jaw", parent="form_head", pivot=(0, 25.6, 1.2))
    for i in range(14):
        pa = -80 + 160 * i / 14
        pb = -80 + 160 * (i + 1) / 14
        a = arc_point(2.95, 2.95, pa, 24.7, 0.4)
        b = arc_point(2.95, 2.95, pb, 24.7, 0.4)
        j.seg(a, b, 0.9, 1.3, "metal", overlap=0.25)
    j.box((-2.4, 24.1, -2.3), (2.4, 24.45, 1.3), "gum")
    for k in range(8):
        phi = -63 + 18 * k
        p = arc_point(2.75, 2.75, phi, 25.3, 0.4)
        j.spike(p, norm([0, 1.0, 0.12]), 1.8 - 0.4 * abs(phi) / 63, 0.85, 0.5, "teeth", steps=3,
                up=norm(p - np.array([0, 25.3, 0.4])))
    j.spike((0, 24.1, -2.6), norm([0, -0.7, -1]), 1.6, 1.4, 0.9, "metal_dk", steps=3)


# ------------------------------------------------------------------------------------------ arms
def build_arm(m, side):
    sgn = -1 if side == "right" else 1

    def X(o):
        return sgn * o

    name = side + "_arm"
    m.bone(name, pivot=(X(5), 22, 0))
    f = m.bone("form_" + name, parent=name, pivot=(X(6), 18, 0))
    cx = np.array([X(6), 0, 0])
    # pauldron: three overlapping curved lames over the shoulder
    for k, (y, r, h) in enumerate(((24.6, 3.25, 1.1), (23.5, 3.45, 1.1), (22.4, 3.6, 1.0))):
        for i in range(10):
            pa = -95 + 190 * i / 10
            pb = -95 + 190 * (i + 1) / 10
            a = np.array([X(6) + sgn * r * math.sin(math.radians(pa + 90)), y, -r * math.cos(math.radians(pa + 90))])
            b = np.array([X(6) + sgn * r * math.sin(math.radians(pb + 90)), y, -r * math.cos(math.radians(pb + 90))])
            f.seg(a, b, 0.55, h, "metal" if k != 1 else "metal_lt", overlap=0.3)
    f.box((X(3.7), 24.9, -2.6), (X(8.4), 25.5, 2.6), "metal_dk")
    f.spike((X(7.8), 25.2, 0), norm([sgn * 0.7, 1, 0]), 2.2, 1.2, 1.2, "edge", steps=3)
    # upper arm plates
    f.cylinder(cx + np.array([0, 19.7, 0]), (0, 1, 0), 2.95, 4.6, "metal", segments=12)
    for y in (21.2, 19.4):
        f.ring(cx + np.array([0, y, 0]), (0, 1, 0), 3.05, 0.3, 0.4, "metal_dk", count=12)
    # elbow cop with a back spike
    f.cylinder(cx + np.array([0, 16.9, 0]), (0, 1, 0), 3.15, 1.3, "metal_lt", segments=12)
    f.spike(cx + np.array([0, 16.9, 2.9]), norm([0, -0.25, 1]), 1.9, 1.1, 0.9, "edge", steps=3)
    # vambrace: overlapping plates flaring toward the wrist
    for k, (y0, y1, r) in enumerate(((15.9, 16.3, 2.95), (14.6, 16.0, 3.0), (13.3, 14.7, 3.08))):
        f.cylinder(cx + np.array([0, (y0 + y1) / 2, 0]), (0, 1, 0), r, y1 - y0 + 0.08,
                   "metal" if k % 2 else "metal_dk", segments=12)
    for zz in (-2.6, 2.6):
        f.obox(cx + np.array([0, 14.8, zz * 1.2]), (0, 1, 0), (1.1, 3.0, 0.3), "edge", up=(0, 0, np.sign(zz)))
    # gauntlet: armoured fist with knuckle plates and finger lames
    f.box((X(3.7), 11.0, -2.35), (X(8.3), 13.4, 2.35), "metal_dk")
    for k in range(4):
        zz = -1.65 + 1.1 * k
        f.box((X(3.55), 11.3, zz - 0.45), (X(4.3), 12.9, zz + 0.45), "metal")
        f.cbox((X(4.0), 13.1, zz), (0.9, 0.5, 0.9), "edge")
    f.box((X(7.6), 11.2, -1.8), (X(8.5), 12.8, 0.4), "metal")
    if side == "right":
        # a spear grows straight out of the fist, along the arm
        s = m.bone("form_right_spear", parent="form_right_arm", pivot=(-6, 11.0, 0))
        s.tube((-6, 11.2, 0), (-6, 7.6, 0), 0.5, "shaft", segments=6)
        for y in (10.4, 9.0):
            s.ring((-6, y, 0), (0, 1, 0), 0.62, 0.2, 0.3, "edge", count=6)
        spearhead(s, (-6, 7.8, 0), (0, -1, 0), 8.6, 3.4, 1.0, (0, 0, -1), steps=10)


# ------------------------------------------------------------------------------------------ human / trigger
def build_trigger(m):
    sp = poses.spear_pull()
    nape = np.array([0.0, 24.0 - poses.NAPE[1], poses.NAPE[2]])
    out_b = poses.model_to_bedrock_vec(poses.SPEAR_OUT)
    # human form: the butt of a spear sticks out of the back of his neck
    h = m.bone("human_nape_spear", parent="body", pivot=tuple(nape))
    h.tube(nape - out_b * 0.3, nape + out_b * (sp["embed"] - 0.2), 0.42, "shaft", segments=6)
    h.cylinder(nape + out_b * (sp["embed"] - 0.1), out_b, 0.6, 0.6, "metal_dk", segments=6)
    h.ring(nape + out_b * 1.2, out_b, 0.5, 0.16, 0.25, "wrap", count=6)
    h.cbox(nape - out_b * 0.15, (1.3, 1.3, 0.3), "blood")
    # the spear being drawn out, in the right fist. The bone is rotated so its local -y runs from the fist to the
    # nape (IK); modelled straight down, it can then be scaled along its length only, so just the part that has
    # already left the neck is ever visible.
    grip = np.array([-6.0, 12.6, 0.0])
    t = m.bone("trig_right_spear", parent="right_arm", pivot=tuple(grip), rotation=trig_rest_euler())
    down = np.array([0, -1.0, 0])
    butt = grip - down * 3.5
    blade0 = grip + down * SPEAR_SHAFT
    t.tube(butt, blade0 + down * 0.3, 0.45, "shaft", segments=6, up=(0, 0, 1))
    t.cylinder(butt, down, 0.62, 0.7, "metal_dk", segments=6, up=(0, 0, 1))
    for k in range(3):
        t.ring(grip + down * (1.6 + 3.2 * k), down, 0.52, 0.14, 0.3, "wrap", count=6, up=(0, 0, 1))
    spearhead(t, blade0, down, SPEAR_BLADE, 3.2, 1.0, (0, 0, -1), steps=10)
    t.tube(grip + down * 8.0, blade0 + down * 2.5, 0.5, "blood", segments=4, up=(0, 0, 1))


SPEAR_SHAFT = 13.0
SPEAR_BLADE = 8.0


def trig_R():
    d = np.asarray(poses.spear_pull()["spear_dir"])
    return frame_from(-d, (0, 0, 1))  # maps local -y onto the fist->nape direction


def trig_rest_euler():
    return euler_for(trig_R())


def twirl_keys(angles):
    """Animation rotation offsets (added to the rest euler) that spin the spear about its own local x."""
    from whip import axis_rot
    R0 = trig_R()
    e0 = np.array(euler_for(R0))
    prev = np.zeros(3)
    keys = []
    for a in angles:
        e = np.array(euler_for(R0 @ axis_rot([1, 0, 0], a))) - e0
        e = prev + (e - prev + 180) % 360 - 180  # unwrap so the interpolation takes the short way
        keys.append(tuple(e))
        prev = e
    return keys


# ------------------------------------------------------------------------------------------ spear entity
def build_entity():
    atlas = Atlas(256, 32)
    atlas.add("metal", kind="metal", color=(112, 54, 42), scratches=6)
    atlas.add("metal_dk", kind="metal", color=(64, 32, 28), scratches=4)
    atlas.add("edge", kind="metal", color=(196, 150, 128), scratches=10)
    atlas.add("shaft", kind="metal", color=(78, 40, 32), scratches=3)
    atlas.add("wrap", kind="fiber", color=(52, 30, 26))
    atlas.add("blood", kind="blood", color=(126, 8, 12))
    m = Model("csm.spear", atlas, density=2.0, seed=61)
    b = m.bone("spear", pivot=(0, 0, 0))
    b.tube((0, 0, 16.0), (0, 0, -6.2), 0.5, "shaft", segments=6)
    b.cylinder((0, 0, 16.0), (0, 0, 1), 0.7, 0.8, "metal_dk", segments=6)
    b.spike((0, 0, 16.3), (0, 0, 1), 1.0, 0.8, 0.8, "metal_dk", steps=2)
    for z in (10.0, 7.5, 5.0):
        b.ring((0, 0, z), (0, 0, 1), 0.58, 0.16, 0.5, "wrap", count=6)
    spearhead(b, (0, 0, -6.4), (0, 0, -1), 9.6, 3.8, 1.2, (0, 1, 0), steps=12)
    b.tube((0, 0, -3.0), (0, 0, -8.0), 0.55, "blood", segments=4)
    m.save(out("geo", "entity", "spear.geo.json"))
    paint_atlas(atlas, out("textures", "entity", "spear.png"), None, seed=33)
    rise = Anim("rise", 2.0, loop="hold_on_last_frame")
    rise.pos("spear", 0, (0, 0, 16.5)).pos("spear", 0.12, (0, 0, -3.5), "easeOutBack")
    rise.pos("spear", 0.2, (0, 0, -2.5)).pos("spear", 1.55, (0, 0, -2.5)).pos("spear", 2.0, (0, 0, 16.5), "easeInQuad")
    for t, r in ((0.12, (0, 0, 0)), (0.16, (3, 2, 0)), (0.22, (-2, -1, 0)), (0.3, (0, 0, 0))):
        rise.rot("spear", t, r)
    save_animations(out("animations", "entity", "spear.animation.json"), [rise])
    print("spear entity: %d cubes" % m.cube_count())


def build():
    atlas = materials()
    m = Model("csm.spear_hybrid", atlas, density=2.0, seed=57)
    build_head(m)
    m.bone("body", pivot=(0, 24, 0))
    build_arm(m, "right")
    build_arm(m, "left")
    build_trigger(m)
    geo = out("geo", "hybrid", "spear.geo.json")
    tex = out("textures", "hybrid", "spear.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "spear_glowmask.png"), seed=29)
    anims = animations()
    anim_path = out("animations", "hybrid", "spear.animation.json")
    save_animations(anim_path, anims)
    print("spear: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    build_entity()
    return geo, tex, anim_path


def animations():
    A = []
    SP = "form_right_spear"

    e = Anim("emerge", 0.8)
    e.scale("form_head", 0, (0.8, 0.5, 0.8)).scale("form_head", 0.12, (1.06, 1.1, 1.06), "easeOutBack")
    e.scale("form_head", 0.24, 1.0)
    e.scale("spear_blade", 0, (0.4, 0.05, 0.4)).scale("spear_blade", 0.06, (0.4, 0.05, 0.4))
    e.scale("spear_blade", 0.24, (1.05, 1.18, 1.05), "easeOutBack").scale("spear_blade", 0.36, 1.0, "easeInOutSine")
    e.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.18, (30, 0, 0), "easeOutQuad").rot("jaw", 0.5, (24, 0, 0))
    e.rot("jaw", 0.8, (0, 0, 0), "easeInOutSine")
    for i, s in enumerate(("right", "left")):
        o = 0.05 * i
        fa = "form_%s_arm" % s
        e.scale(fa, 0, 0.7).scale(fa, 0.12 + o, 1.1, "easeOutBack").scale(fa, 0.26 + o, 1.0)
    e.scale(SP, 0, (1, 0.02, 1)).scale(SP, 0.1, (1, 0.02, 1)).scale(SP, 0.3, (1, 1.15, 1), "easeOutBack")
    e.scale(SP, 0.42, 1.0)
    A.append(e)

    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    r.scale("spear_blade", 0, 1).scale("spear_blade", 0.25, (0.4, 0.05, 0.4), "easeInBack")
    r.scale(SP, 0, 1).scale(SP, 0.2, (1, 0.02, 1), "easeInBack")
    r.scale("form_head", 0.1, 1).scale("form_head", 0.4, (0.8, 0.5, 0.8), "easeInQuad")
    for s in ("right", "left"):
        r.scale("form_%s_arm" % s, 0.1, 1).scale("form_%s_arm" % s, 0.4, 0.7, "easeInQuad")
    A.append(r)

    idle = Anim("idle", 3.0, loop=True)
    for t, a in ((0, 0), (0.12, 5), (0.24, 0), (0.36, 3), (0.5, 0), (1.9, 0), (2.0, 6), (2.15, 0), (3.0, 0)):
        idle.rot("jaw", t, (a, 0, 0))
    idle.rot("spear_blade", 0, (0, 0, 0)).rot("spear_blade", 1.5, (-1.0, 0, 0.6), "easeInOutSine")
    idle.rot("spear_blade", 3.0, (0, 0, 0), "easeInOutSine")
    A.append(idle)

    def extend(anim, t0, dist=3.0, hold=0.06):
        anim.pos(SP, t0 - 0.06, (0, 0, 0)).pos(SP, t0, (0, -dist, 0), "easeOutQuad")
        anim.pos(SP, t0 + hold, (0, -dist, 0)).pos(SP, t0 + hold + 0.1, (0, 0, 0), "easeInOutSine")

    th = Anim("thrust", 0.7)
    for t0 in (0.15, 0.35, 0.55):
        extend(th, t0, 3.2, 0.04)
    A.append(th)

    tw = Anim("throw", 0.7)
    tw.scale(SP, 0, 1).scale(SP, 0.2, (1.1, 1.3, 1.1), "easeInQuad").scale(SP, 0.3, (1.1, 1.3, 1.1))
    tw.scale(SP, 0.31, 0).scale(SP, 0.45, 0).scale(SP, 0.62, (1, 1.12, 1), "easeOutBack").scale(SP, 0.7, 1)
    A.append(tw)

    vo = Anim("volley", 1.2)
    vo.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.15, (34, 0, 0), "easeOutQuad").rot("jaw", 0.65, (30, 0, 0))
    vo.rot("jaw", 0.72, (8, 0, 0)).rot("jaw", 1.2, (0, 0, 0))
    for k in range(12):
        t = 0.15 + k * 0.045
        vo.rot("spear_blade", t, ((-1) ** k * 1.5, 0, (-1) ** (k + 1) * 1.2))
    vo.rot("spear_blade", 0.7, (-8, 0, 0), "easeOutQuad").rot("spear_blade", 1.0, (0, 0, 0), "easeInOutSine")
    A.append(vo)

    im = Anim("impale", 0.8)
    extend(im, 0.25, 5.0, 0.25)
    im.rot("jaw", 0.2, (0, 0, 0)).rot("jaw", 0.3, (32, 0, 0), "easeOutQuad").rot("jaw", 0.6, (26, 0, 0))
    im.rot("jaw", 0.8, (0, 0, 0))
    A.append(im)

    er = Anim("eruption", 1.1)
    extend(er, 0.25, 4.0, 0.45)
    er.rot("jaw", 0.2, (0, 0, 0)).rot("jaw", 0.3, (36, 0, 0), "easeOutQuad").rot("jaw", 0.85, (30, 0, 0))
    er.rot("jaw", 1.1, (0, 0, 0))
    er.scale("spear_blade", 0.2, 1).scale("spear_blade", 0.28, (1.08, 1.12, 1.08)).scale("spear_blade", 0.5, 1)
    A.append(er)

    dr = Anim("drink", 1.0)
    dr.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.35, (30, 0, 0), "easeOutQuad").rot("jaw", 0.5, (6, 0, 0))
    dr.rot("jaw", 0.6, (26, 0, 0)).rot("jaw", 1.0, (0, 0, 0))
    A.append(dr)

    # trigger prop: only the part already pulled out of the nape shows (tip side = hand-to-nape distance + a bit),
    # then it is twirled tip-forward, grows to full size, and melts into the arm spear when the devil bursts out
    ps = Anim("pull_spear", 1.3)
    T = "trig_right_spear"
    tip_len = SPEAR_SHAFT + SPEAR_BLADE
    ps.scale(T, 0, 0).scale(T, 0.29, 0)
    for t, d in ((0.3, 4.0), (0.5, 6.0), (0.7, 8.0)):
        ps.scale(T, t, (1, (d + 1.6) / tip_len, 1))
    ps.scale(T, 0.8, (1, 1.05, 1), "easeOutBack").scale(T, 0.86, 1.0).scale(T, 0.9, 0)
    ps.rot(T, 0, (0, 0, 0)).rot(T, 0.7, (0, 0, 0))
    for t, k in zip((0.73, 0.76, 0.79, 0.82), twirl_keys((60, 120, 180, 200))):
        ps.rot(T, t, k)
    A.append(ps)
    return A


def render_previews(geo, tex, anim):
    sp = poses.spear_pull()
    g = sp["frames"]["grab"]
    hide = ("human_nape_spear", "trig_right_spear")
    arms = {"right_arm": {"rot": (0, 0, 0.1)}, "left_arm": {"rot": (0, 0, -0.1)}}
    shots = [
        preview.render(geo, tex, preview_path("spear_front.png"), anim, "idle", 0.0, yaw=30, pitch=6, pose=arms,
                       hidden=hide, show_arms=False, scale=10, center=(0, 1.25)),
        preview.render(geo, tex, preview_path("spear_head.png"), anim, "idle", 0.0, yaw=60, pitch=8,
                       show_body=False, scale=18, center=(0, 2.0), size=(640, 520),
                       hidden=hide + ("body", "right_arm", "left_arm")),
        preview.render(geo, tex, preview_path("spear_thrust.png"), anim, "thrust", 0.15, yaw=-70, pitch=8,
                       pose={"right_arm": {"rot": (-1.57, 0, 0)}, "left_arm": {"rot": (0, 0, -0.1)}},
                       hidden=hide, show_arms=False, scale=8, center=(0, 1.2)),
        preview.render(geo, tex, preview_path("spear_trigger.png"), anim, "pull_spear", 0.5, yaw=150, pitch=6,
                       pose={"right_arm": {"rot": tuple(g["rot"]), "pos": tuple(np.array([-5, 2, 0]) + g["shift"])},
                             "head": {"rot": poses.SPEAR_HEAD}},
                       hidden=("form_head", "form_right_arm", "form_left_arm"), show_head=True, scale=14,
                       center=(0, 1.5)),
    ]
    return preview.contact_sheet(shots, preview_path("spear_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
