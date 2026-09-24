"""
The Curse Devil - the mob (entity/devil/curse) and the Curse its contractor calls down (entity/contract/curse).

Reference points (manga ch. 29 / anime ep. 8):
  * a huge, gaunt SKELETON with horns and TWO HEADS side by side: its right skull looks human, its left skull has three
    eye slits and long, mandible-like teeth
  * bones and nails: rusty nails are driven through it everywhere
  * long arms ending in clawed hands, and a distended ribcage that splays open like a second set of jaws
  * a contractor stabs the same thing three times with a nail; the Curse appears behind it in full, takes it by both
    arms like a crucifixion and bites into its neck and shoulders
"""
import math

import numpy as np

from common import preview_path, out
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk


def materials():
    a = Atlas(512, 64)
    a.add("bone", kind="bone", color=(226, 220, 200))
    a.add("bone_dk", kind="bone", color=(172, 162, 138))
    a.add("hollow", kind="void", color=(14, 10, 12))
    a.add("teeth", kind="teeth", color=(238, 232, 214))
    a.add("eye", kind="glow", color=(255, 236, 200), emissive=True)
    a.add("slit", kind="glow", color=(230, 40, 30), color2=(255, 150, 90), emissive=True)
    a.add("nail", kind="rust", color=(104, 88, 78))
    a.add("horn", kind="bone", color=(74, 66, 60))
    a.add("sinew", kind="flesh", color=(96, 40, 40))
    return a


def bony_limb(bone, pts, r0, r1, mat="bone", knobs=True):
    """A thin bone along pts with knobbly joints."""
    pts = [np.asarray(p, dtype=float) for p in pts]
    f = shapes.loft(shapes.polyline(pts), shapes.taper(r0, r1), shapes.taper(r0 * 0.9, r1 * 0.9))
    shapes.shell(bone, f, 6, 3 * len(pts), mat, thick=0.3)
    if knobs:
        for p in pts[1:-1]:
            shapes.shell(bone, shapes.ellipsoid(p, (r0 * 1.25, r0 * 1.25, r0 * 1.25)), 5, 3, "bone_dk", thick=0.3)
    return f


def claw_hand(bone, wrist, forward, side, size=1.0, curl=35, detail=1.0):
    """A huge bony hand: a palm plate and five long jointed fingers ending in hooked claws."""
    wrist = np.asarray(wrist, dtype=float)
    fw = norm(forward)
    sd = norm(side)
    palm_c = wrist + fw * 3.0 * size
    shapes.shell(bone, shapes.ellipsoid(palm_c, (3.0 * size, 1.0 * size, 3.2 * size),
                                        frame=np.column_stack([sd, np.cross(fw, sd), fw])), 8, 5, "bone", thick=0.3)
    bend_axis = norm(np.cross(fw, sd))
    for k in range(5):
        thumb = k == 0
        off = (-2.4 + k * 1.2) * size
        base = palm_c + sd * off + fw * (1.8 if not thumb else -0.5) * size
        d = norm(fw + sd * (-0.8 if thumb else 0.08 * (k - 2)))
        length = (5.5 if thumb else 8.5 - abs(k - 2.5) * 0.8) * size
        shapes.horn(bone, base, d, length, 0.55 * size, mat="bone", tip_mat="horn", tip_from=0.7,
                    sections=max(3, int(5 * detail)), around=4, r1=0.12, bend_axis=bend_axis,
                    bend=curl * (0.7 if thumb else 1.0))


def nail(bone, p, d, length=4.0):
    """A rusty nail driven through the bone at p, pointing along d."""
    d = norm(d)
    p = np.asarray(p, dtype=float)
    bone.cylinder(tuple(p - d * length * 0.4), tuple(d), 0.32, length, "nail", segments=6)
    bone.cylinder(tuple(p - d * (length * 0.4 + 0.1)), tuple(d), 0.9, 0.35, "nail", segments=6)


def human_skull(m, parent, c, name):
    """The right head: a human skull, horned."""
    hb = m.bone(name, parent=parent, pivot=tuple(np.asarray(c) + np.array([0, -4.0, 1.0])))
    cran = shapes.ellipsoid(c, (4.2, 4.8, 5.0), e_lat=0.95)
    shapes.shell(hb, cran, 14, 10, "bone", thick=0.35)
    shapes.shell(hb, shapes.ellipsoid(np.asarray(c) + np.array([0, -3.4, -2.2]), (3.5, 1.8, 2.8)), 10, 5, "bone",
                 thick=0.3, v0=0.35)
    for s in (-1, 1):
        shapes.shell(hb, shapes.ellipsoid(np.asarray(c) + np.array([s * 3.2, -2.2, -3.0]), (1.2, 1.0, 1.6)), 6, 4,
                     "bone_dk", thick=0.3)
        p, n, du, dv = shapes.surface_frame(cran, 0.08 if s > 0 else 0.92, 0.52)
        hb.decal(p + n * 0.1, n, 2.8, 2.4, "hollow", up=(0, 1, 0))
        hb.cbox(tuple(p + n * 0.2), (0.5, 0.5, 0.3), "eye")
    p, n, du, dv = shapes.surface_frame(cran, 0.0, 0.34)
    hb.decal(p + n * 0.1, n, 1.2, 1.6, "hollow", up=(0, 1, 0))
    c = np.asarray(c, dtype=float)
    upper = [c + v for v in ([-3.2, -4.4, -0.6], [-2.6, -4.6, -3.6], [0, -4.6, -5.0], [2.6, -4.6, -3.6],
                             [3.2, -4.4, -0.6])]
    for i in range(12):
        hb.spike(shapes.polyline(upper)(i / 11), (0, -1, 0), 1.2, 0.55, 0.3, "teeth", steps=2, up=(0, 0, -1))
    jaw = m.bone(name + "_jaw", parent=name, pivot=tuple(c + np.array([0, -4.2, 0.8])))
    lower = [c + v for v in ([-3.3, -4.6, 0.8], [-3.0, -6.6, -2.4], [0, -7.0, -4.6], [3.0, -6.6, -2.4],
                             [3.3, -4.6, 0.8])]
    shapes.shell(jaw, shapes.loft(shapes.polyline(lower), 0.8, 0.9, up=(0, 1, 0)), 6, 14, "bone", thick=0.3)
    for i in range(10):
        p = shapes.polyline(lower)(0.1 + i * 0.08)
        jaw.spike(p + np.array([0, 0.5, 0]), (0, 1, 0), 1.2, 0.5, 0.3, "teeth", steps=2, up=(0, 0, -1))
    for s in (-1, 1):
        shapes.horn(hb, c + np.array([s * 2.8, 3.4, 0.5]), (s * 0.7, 0.6, 0.4), 9.0, 1.3, mat="horn", tip_mat="bone_dk",
                    sections=6, around=6, r1=0.12, bend_axis=(0, 0, s), bend=-55 * s)
    nail(hb, c + np.array([-1.0, 4.4, -1.0]), (0.15, -1, -0.2))
    return hb, jaw


def slit_skull(m, parent, c, name):
    """The left head: a longer skull with three eye slits and long, mandible-like teeth."""
    c = np.asarray(c, dtype=float)
    hb = m.bone(name, parent=parent, pivot=tuple(c + np.array([0, -4.0, 1.0])))
    cran = shapes.loft(shapes.polyline([c + [0, 0.4, 4.0], c + [0, 1.0, 0.0], c + [0, 0.0, -4.0], c + [0, -1.6, -7.0]]),
                       shapes.profile((0, 3.0), (0.3, 4.2), (0.7, 3.8), (1, 2.6)),
                       shapes.profile((0, 3.4), (0.3, 4.8), (0.7, 3.8), (1, 2.0)), up=(0, 1, 0))
    shapes.shell(hb, cran, 14, 10, "bone", thick=0.35)
    shapes.shell(hb, shapes.ellipsoid(c + [0, 0.4, 4.0], (3.0, 3.4, 1.4)), 8, 5, "bone", thick=0.3)
    # three vertical eye slits in a row across the brow
    for i, u in enumerate((0.92, 0.0, 0.08)):
        p, n, du, dv = shapes.surface_frame(cran, u, 0.62)
        hb.decal(p + n * 0.1, n, 0.9, 3.4, "hollow", up=(0, 1, 0))
        hb.decal(p + n * 0.16, n, 0.4, 2.8, "slit", up=(0, 1, 0))
    # long mandible teeth: tusks down out of the upper jaw, up out of the lower
    tip = c + np.array([0, -2.4, -6.8])
    for s in (-1, 1):
        for i in range(3):
            b = c + np.array([s * (2.6 - i * 0.6), -2.6, -2.5 - i * 1.6])
            hb.spike(b, norm((s * 0.25, -1, -0.35)), 5.2 - i * 0.9, 1.0, 0.5, "teeth", steps=4, up=(0, 0, -1))
    jaw = m.bone(name + "_jaw", parent=name, pivot=tuple(c + np.array([0, -3.2, 1.5])))
    lower = [c + v for v in ([-3.0, -4.0, 1.5], [-2.6, -5.2, -3.0], [0, -5.6, -6.2], [2.6, -5.2, -3.0],
                             [3.0, -4.0, 1.5])]
    shapes.shell(jaw, shapes.loft(shapes.polyline(lower), 0.9, 0.9, up=(0, 1, 0)), 6, 14, "bone", thick=0.3)
    for s in (-1, 1):
        for i in range(2):
            b = c + np.array([s * (2.2 - i * 0.8), -5.0, -2.0 - i * 2.0])
            jaw.spike(b, norm((s * 0.3, 1, -0.5)), 4.6 - i * 0.8, 0.9, 0.45, "teeth", steps=4, up=(0, 0, -1))
    for s in (-1, 1):
        shapes.horn(hb, c + np.array([s * 2.4, 3.6, 1.5]), (s * 0.5, 0.8, 0.5), 10.0, 1.3, mat="horn",
                    tip_mat="bone_dk", sections=6, around=6, r1=0.12, bend_axis=(1, 0, 0), bend=40)
    nail(hb, c + np.array([2.8, 2.0, -1.0]), (-0.9, -0.3, 0.2))
    _ = tip
    return hb, jaw


def skeleton(m, name_prefix=""):
    """The whole Curse, standing (feet at y = 0, about 4.4 blocks tall, facing -z)."""
    root = m.bone("root", pivot=(0, 0, 0))
    body = m.bone("body", parent="root", pivot=(0, 30, 2))
    # pelvis, legs bent like a crouching animal's, clawed feet
    shapes.shell(body, shapes.ellipsoid((0, 31.0, 2.0), (6.0, 2.6, 3.4)), 10, 5, "bone_dk", thick=0.3)
    for s, name in ((-1, "right_leg"), (1, "left_leg")):
        hip = np.array([s * 5.0, 30.0, 2.0])
        leg = m.bone(name, parent="root", pivot=tuple(hip))
        knee = hip + np.array([s * 2.0, -13.0, -6.0])
        ankle = knee + np.array([0, -12.0, 7.0])
        bony_limb(leg, [hip, knee, ankle], 1.5, 1.0)
        for off in (-0.6, 0.6):
            bony_limb(leg, [knee + [off, 0, 0], ankle + [off * 0.6, 0, 0]], 0.7, 0.55, knobs=False)
        for i in range(4):
            d = norm((s * 0.15 * (i - 1.5), -0.35, -1))
            shapes.horn(leg, ankle + np.array([(i - 1.5) * 1.1, -1.6, -1.0]), d, 5.0, 0.6, mat="bone", tip_mat="horn",
                        sections=3, around=5, r1=0.1, bend_axis=(1, 0, 0), bend=40)
    # the spine, bent forward at the top
    spine = shapes.polyline([(0, 31.0, 3.5), (0, 42.0, 4.5), (0, 54.0, 4.0), (0, 62.0, 1.5)])
    for i in range(16):
        p = spine(i / 15)
        shapes.shell(body, shapes.ellipsoid(p, (1.3, 0.9, 1.3)), 5, 3, "bone_dk", thick=0.3)
    # a distended ribcage: the ribs sweep out wide and forward and never meet - the front hangs open like jaws
    for i in range(7):
        y = 59.0 - i * 2.8
        w = 9.0 + min(i, 3) * 1.6 - max(0, i - 3) * 0.8
        for s in (-1, 1):
            pts = [(s * 1.2, y, 3.8), (s * w * 0.8, y + 0.4, 2.4), (s * w, y - 1.2, -2.0), (s * w * 0.8, y - 2.6, -6.0),
                   (s * (3.0 + i * 0.2), y - 3.2 - i * 0.3, -8.4)]
            shapes.shell(body, shapes.loft(shapes.polyline(pts), 0.7, 0.5), 4, 8, "bone", thick=0.25)
            body.spike(np.array(pts[-1]), norm((-s * 0.5, -0.2, -0.4)), 2.4, 0.7, 0.4, "teeth", steps=2,
                       up=(0, 1, 0))
    # something withered inside it
    shapes.shell(body, shapes.loft(shapes.polyline([(0, 36.0, 2.0), (0, 46.0, 1.0), (0, 56.0, 1.5)]),
                                   shapes.profile((0, 2.4), (0.5, 3.8), (1, 2.4)),
                                   shapes.profile((0, 2.0), (0.5, 3.0), (1, 2.0)), up=(0, 0, -1)), 10, 8, "sinew",
                 thick=0.3)
    # shoulders
    for s in (-1, 1):
        bony_limb(body, [(s * 1.2, 61.5, 2.5), (s * 7.0, 63.0, 1.5), (s * 12.0, 62.5, 1.0)], 1.0, 0.8, knobs=False)
        bony_limb(body, [(s * 1.2, 60.0, -3.5), (s * 7.0, 62.0, -2.0), (s * 12.0, 62.5, 1.0)], 0.8, 0.7, knobs=False)
    nail(body, (-7.5, 55.5, -4.0), (0.3, 0.2, 1))
    nail(body, (8.8, 50.0, -3.0), (-0.4, 0.1, 1))
    nail(body, (0.0, 44.0, 5.0), (0.2, 0.3, -1))
    # the neck forks into two
    head = m.bone("head", parent="body", pivot=(0, 62, 1.5))
    bony_limb(head, [(0, 61.0, 1.5), (0, 64.0, 1.0)], 1.6, 1.4, mat="bone_dk")
    for s in (-1, 1):
        bony_limb(head, [(0, 64.0, 1.0), (s * 3.0, 67.0, 1.0), (s * 5.5, 69.5, 1.0)], 1.3, 1.0, mat="bone_dk")
    human_skull(m, "head", (-6.0, 74.5, -0.5), "skull_r")
    slit_skull(m, "head", (6.0, 74.0, -0.5), "skull_l")
    # arms long enough to reach the ground
    for side, name in ((-1, "right_arm"), (1, "left_arm")):
        sh = np.array([side * 12.5, 62.5, 1.0])
        arm = m.bone(name, parent="body", pivot=tuple(sh))
        shapes.shell(arm, shapes.ellipsoid(sh, (2.4, 2.4, 2.4)), 7, 5, "bone_dk", thick=0.3)
        el = sh + np.array([side * 3.0, -17.0, 3.0])
        wr = el + np.array([side * 0.5, -17.0, -3.0])
        bony_limb(arm, [sh, el], 1.4, 1.1)
        for off in (-0.8, 0.8):
            bony_limb(arm, [el + np.array([off, 0, 0]), wr + np.array([off * 0.6, 0, 0])], 0.85, 0.65, knobs=False)
        shapes.shell(arm, shapes.ellipsoid(el, (1.7, 1.7, 1.7)), 6, 4, "bone_dk", thick=0.3)
        nail(arm, el + np.array([0, -6.0, 0]), (side * -1, 0.2, 0.3), 5.0)
        claw_hand(arm, wr, (0, -1, -0.25), (side, 0, 0), size=1.35, curl=40)
    return root, body


def build_mob():
    atlas = materials()
    m = Model("csm.curse_devil", atlas, density=2.0, seed=251)
    skeleton(m)
    # grave hands that claw up out of the ground (Grave Hands)
    for k in range(8):
        a = k * 2 * math.pi / 8 + 0.3
        rr = 34.0 + (k % 3) * 8.0
        base = np.array([math.cos(a) * rr, 0.0, math.sin(a) * rr])
        fx = m.bone("fx_rise_hand%d" % k, parent="root", pivot=tuple(base))
        up = norm(np.array([-math.cos(a) * 0.2, 1, -math.sin(a) * 0.2]))
        bony_limb(fx, [base - up * 2.0, base + up * 6.0, base + up * 12.0 + np.array([math.cos(a), 0, math.sin(a)])],
                  1.4, 1.0)
        claw_hand(fx, base + up * 12.0, up, (math.sin(a), 0, -math.cos(a)), size=1.5, curl=55, detail=0.6)
    geo, tex, glow, anim_path = dk.devil_paths("curse")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=253)
    anims = mob_animations()
    save_animations(anim_path, anims)
    print("curse devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def jaws(a, t, open_deg):
    a.rot("skull_r_jaw", t, (open_deg, 0, 0))
    a.rot("skull_l_jaw", t, (open_deg * 1.1, 0, 0))


def mob_animations():
    A = []
    arms = ("right_arm", "left_arm")
    idle = Anim("idle", 4.0, loop=True)
    for i in range(9):
        t = 4.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("body", t, (6 + 2 * math.sin(ph), 3 * math.sin(ph * 0.5), 0))
        idle.rot("skull_r", t, (-4 + 4 * math.sin(ph + 1), 6 * math.sin(ph * 0.5), 5 * math.sin(ph)))
        idle.rot("skull_l", t, (-4 + 4 * math.sin(ph + 2), -6 * math.sin(ph * 0.5), -5 * math.sin(ph + 1)))
        idle.rot("right_arm", t, (-4 + 4 * math.sin(ph), 0, 4 + 2 * math.sin(ph)))
        idle.rot("left_arm", t, (-4 + 4 * math.sin(ph + 1.5), 0, -4 - 2 * math.sin(ph + 1.5)))
        jaws(idle, t, 4 + 3 * math.sin(ph * 2))
    A.append(idle)
    mv = Anim("move", 1.6, loop=True)
    for i in range(9):
        t = 1.6 * i / 8
        ph = 2 * math.pi * i / 8
        mv.rot("body", t, (14 + 3 * math.sin(ph), 6 * math.sin(ph), 0))
        mv.rot("right_arm", t, (-20 + 25 * math.sin(ph), 0, 6))
        mv.rot("left_arm", t, (-20 - 25 * math.sin(ph), 0, -6))
        mv.rot("right_leg", t, (28 * math.sin(ph), 0, 0))
        mv.rot("left_leg", t, (-28 * math.sin(ph), 0, 0))
        mv.pos("root", t, (0, 1.0 * math.sin(2 * ph), 0))
    A.append(mv)
    nl = Anim("nail", 0.7)
    nl.rot("right_arm", 0, (0, 0, 0)).rot("right_arm", 0.2, (-150, 0, 15), "easeOutQuad")
    nl.rot("right_arm", 0.3, (-60, 0, 5), "easeInQuad").rot("right_arm", 0.7, (0, 0, 0))
    nl.rot("body", 0.2, (-6, 0, 0)).rot("body", 0.3, (16, 0, 0)).rot("body", 0.7, (4, 0, 0))
    jaws(nl, 0.2, 25)
    jaws(nl, 0.35, 0)
    A.append(nl)
    gp = Anim("grip", 2.2)
    gp.rot("left_arm", 0, (0, 0, 0)).rot("left_arm", 0.4, (-95, 0, -10), "easeOutQuad")
    gp.rot("left_arm", 1.0, (-120, 0, -5)).rot("left_arm", 1.5, (-130, 20, -5)).rot("left_arm", 1.8, (-50, 0, 0),
                                                                                     "easeInQuad")
    gp.rot("left_arm", 2.2, (0, 0, 0))
    gp.pos("left_arm", 0.4, (0, 2, -6)).pos("left_arm", 1.8, (0, 0, -2)).pos("left_arm", 2.2, (0, 0, 0))
    gp.rot("body", 0.4, (20, -10, 0)).rot("body", 1.5, (10, 10, 0)).rot("body", 1.8, (28, 0, 0)).rot("body", 2.2,
                                                                                                    (4, 0, 0))
    jaws(gp, 0.9, 30)
    jaws(gp, 1.8, 10)
    jaws(gp, 2.2, 0)
    A.append(gp)
    hx = Anim("hex", 1.5)
    for a_, s in zip(arms, (1, -1)):
        hx.rot(a_, 0, (0, 0, 0)).rot(a_, 0.4, (-100, 0, s * 40), "easeOutQuad").rot(a_, 1.0, (-95, 0, s * 45))
        hx.rot(a_, 1.5, (0, 0, 0))
    for sk in ("skull_r", "skull_l"):
        hx.rot(sk, 0.4, (-20, 0, 0)).rot(sk, 1.0, (-25, 0, 0)).rot(sk, 1.5, (0, 0, 0))
    jaws(hx, 0.3, 45)
    jaws(hx, 1.0, 40)
    jaws(hx, 1.5, 0)
    hx.rot("body", 0.4, (-10, 0, 0)).rot("body", 1.5, (4, 0, 0))
    A.append(hx)
    rs = Anim("rise", 2.0)
    for a_, s in zip(arms, (1, -1)):
        rs.rot(a_, 0, (0, 0, 0)).rot(a_, 0.35, (-170, 0, s * 10), "easeOutQuad").rot(a_, 0.5, (-40, 0, s * 5),
                                                                                    "easeInQuad")
        rs.rot(a_, 1.6, (-40, 0, s * 5)).rot(a_, 2.0, (0, 0, 0))
    rs.rot("body", 0.35, (-12, 0, 0)).rot("body", 0.5, (35, 0, 0)).rot("body", 1.6, (30, 0, 0)).rot("body", 2.0,
                                                                                                   (4, 0, 0))
    for k in range(8):
        b = "fx_rise_hand%d" % k
        t0 = 0.5 + (k % 4) * 0.08
        rs.pos(b, 0, (0, -24, 0)).pos(b, t0, (0, -24, 0)).pos(b, t0 + 0.2, (0, 1, 0), "easeOutBack")
        rs.pos(b, 1.7, (0, 0, 0)).pos(b, 2.0, (0, -24, 0), "easeInQuad")
        rs.rot(b, t0 + 0.2, (0, 0, 0)).rot(b, 1.2, (0, 0, 10 if k % 2 else -10)).rot(b, 1.7, (0, 0, 0))
    A.append(rs)
    dr = Anim("drink", 1.0)
    jaws(dr, 0, 0)
    jaws(dr, 0.3, 30)
    jaws(dr, 1.0, 0)
    A.append(dr)
    death = Anim("death", 2.0, loop="hold_on_last_frame")
    death.rot("body", 0, (0, 0, 0)).rot("body", 0.8, (40, 0, 10), "easeInQuad").rot("body", 1.4, (85, 0, 15), "easeInQuad")
    death.pos("root", 1.4, (0, -8, 0))
    death.rot("right_leg", 1.0, (-80, 0, 10)).rot("left_leg", 1.0, (-80, 0, -10))
    death.rot("right_arm", 1.2, (-40, 0, 40)).rot("left_arm", 1.2, (-20, 0, -50))
    death.rot("skull_r", 1.4, (30, 30, 0)).rot("skull_l", 1.4, (20, -30, 0))
    jaws(death, 1.4, 40)
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.5, from_scale=1.0, loop="hold_on_last_frame"))
    return A


# ----------------------------------------------------------------------------- the Curse a contractor calls
def build_summon():
    """entity/contract/curse: the same devil, standing behind its victim (origin = its feet, front toward the victim).
    ContractSummonEntity holds the victim in front of its chest at (0, 2.2 blocks, -1.3 blocks)."""
    atlas = materials()
    m = Model("csm.curse_summon", atlas, density=1.6, seed=255)
    skeleton(m)
    geo = out("geo", "entity", "contract", "curse.geo.json")
    tex = out("textures", "entity", "contract", "curse.png")
    glow = out("textures", "entity", "contract", "curse_glowmask.png")
    anim_path = out("animations", "entity", "contract", "curse.animation.json")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=253)
    save_animations(anim_path, [seize_animation()])
    print("curse (summon): %d cubes, %d bones" % (m.cube_count(), len(m.bones)))
    return geo, tex, anim_path


def seize_animation():
    """64 ticks (3.2 s): it stands up behind the victim, takes it by both arms, bites on ticks 22 and 32 and finishes
    it on 44 (ContractSummonEntity#curse), then sinks away."""
    a = Anim("seize", 3.2, loop="hold_on_last_frame")
    a.pos("root", 0, (0, -70, 6)).pos("root", 0.45, (0, 0, 0), "easeOutQuad").pos("root", 2.55, (0, 0, 0))
    a.pos("root", 3.2, (0, -74, 6), "easeInQuad")
    a.scale("root", 0, 0.7).scale("root", 0.45, 1.0).scale("root", 2.6, 1.0).scale("root", 3.2, 0.5)
    # lean over the victim
    a.rot("body", 0, (0, 0, 0)).rot("body", 0.5, (12, 0, 0)).rot("body", 2.5, (16, 0, 0)).rot("body", 3.2, (0, 0, 0))
    # both hands reach forward and close round the victim's arms, spreading them wide
    for arm, s in (("right_arm", -1), ("left_arm", 1)):
        a.rot(arm, 0, (0, 0, 0)).rot(arm, 0.5, (-70, s * -10, s * -10), "easeOutQuad")
        a.rot(arm, 0.75, (-62, s * -18, s * -34), "easeInOutQuad").rot(arm, 2.5, (-62, s * -18, s * -34))
        a.rot(arm, 2.8, (-20, 0, 0)).rot(arm, 3.2, (0, 0, 0))
    # the two heads bite into the neck and shoulders: 1.1 s, 1.6 s, and the last bite at 2.2 s
    for t, deep in ((1.1, 1.0), (1.6, 1.0), (2.2, 1.4)):
        for sk, s in (("skull_r", -1), ("skull_l", 1)):
            a.rot(sk, t - 0.25, (-20, 0, s * 8), "easeOutQuad").rot(sk, t, (38 * deep, s * -10, s * -6), "easeInQuad")
            a.rot(sk, t + 0.2, (26 * deep, s * -8, 0))
            a.pos(sk, t - 0.25, (0, 2, 2)).pos(sk, t, (-s * 1.5, -5 * deep, -9 * deep), "easeInQuad")
            a.pos(sk, t + 0.2, (0, -3, -6))
        jaws(a, t - 0.25, 55)
        jaws(a, t, 0)
    for sk in ("skull_r", "skull_l"):
        a.rot(sk, 2.6, (0, 0, 0)).pos(sk, 2.6, (0, 0, 0))
    jaws(a, 2.6, 20)
    jaws(a, 3.2, 0)
    return a


def render_previews():
    g, t, _, a = dk.devil_paths("curse")
    sg, st, sa = (out("geo", "entity", "contract", "curse.geo.json"), out("textures", "entity", "contract", "curse.png"),
                  out("animations", "entity", "contract", "curse.animation.json"))
    fxh = tuple("fx_rise_hand%d" % k for k in range(8))
    shots = [
        preview.render(g, t, preview_path("curse_front.png"), a, "idle", 0.0, yaw=20, pitch=6, show_body=False,
                       hidden=fxh, scale=2.9, center=(0, 2.5), size=(620, 620), bg=(150, 170, 200)),
        preview.render(g, t, preview_path("curse_face.png"), a, "idle", 0.0, yaw=10, pitch=0, show_body=False,
                       hidden=fxh, scale=9.0, center=(0, 4.4), size=(620, 620), bg=(150, 170, 200)),
        preview.render(sg, st, preview_path("curse_seize.png"), sa, "seize", 2.2, yaw=60, pitch=8, show_body=False,
                       scale=2.6, center=(0, 2.6), size=(620, 620), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("curse_sheet.png"), cols=3)


if __name__ == "__main__":
    build_mob()
    build_summon()
    print(render_previews())
