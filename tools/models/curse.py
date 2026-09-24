"""
The Curse Devil - entity model (entity/devil/curse) and animations.

Reference points:
  * a gaunt, towering skeleton of a devil wrapped in grave cloth, rising out of the ground behind whoever called it
  * a long horned skull with deep sockets, pin-prick eyes and a lipless grin of teeth
  * arms long enough to reach the ground and hands big enough to close round a man
  * called with a nail: stab the same thing three times and the Curse takes it
"""
import math

import numpy as np

from common import preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk


def materials():
    a = Atlas(512, 64)
    a.add("bone", kind="bone", color=(222, 214, 190))
    a.add("bone_dk", kind="bone", color=(170, 160, 136))
    a.add("cloth", kind="fiber", color=(206, 200, 184))
    a.add("cloth_dk", kind="fiber", color=(120, 112, 100))
    a.add("hollow", kind="void", color=(16, 12, 14))
    a.add("teeth", kind="teeth", color=(236, 230, 212))
    a.add("eye", kind="glow", color=(255, 244, 220), emissive=True)
    a.add("nail", kind="rust", color=(96, 84, 76))
    a.add("horn", kind="bone", color=(90, 80, 70))
    return a


def bony_limb(bone, pts, r0, r1, mat="bone", knobs=True):
    """A thin bone along pts with knobbly joints."""
    pts = [np.asarray(p, dtype=float) for p in pts]
    f = shapes.loft(shapes.polyline(pts), shapes.taper(r0, r1), shapes.taper(r0 * 0.9, r1 * 0.9))
    shapes.shell(bone, f, 7, 4 * len(pts), mat, thick=0.3)
    if knobs:
        for p in pts[1:-1]:
            shapes.shell(bone, shapes.ellipsoid(p, (r0 * 1.2, r0 * 1.2, r0 * 1.2)), 6, 4, "bone_dk", thick=0.3)
    return f


def hand(bone, wrist, forward, side, size=1.0, curl=35):
    """A huge bony hand: palm plate and five long jointed fingers curling round."""
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
        length = (5.5 if thumb else 8.0 - abs(k - 2.5) * 0.8) * size
        shapes.horn(bone, base, d, length, 0.55 * size, mat="bone", tip_mat="bone_dk", sections=6, around=5, r1=0.18,
                    bend_axis=bend_axis, bend=curl * (0.7 if thumb else 1.0))


def build():
    atlas = materials()
    m = Model("csm.curse_devil", atlas, density=2.0, seed=251)
    root = m.bone("root", pivot=(0, 0, 0))
    # the shroud it rises out of: grave cloth spreading over the ground, gathering into the waist
    shroud = m.bone("shroud", parent="root", pivot=(0, 0, 0))
    sf = shapes.loft(shapes.polyline([(0, 0.5, 2.0), (0, 10.0, 1.5), (0, 22.0, 0.5), (0, 30.0, 0.0)]),
                     shapes.profile((0, 13.0), (0.3, 8.0), (0.7, 5.5), (1, 4.0)),
                     shapes.profile((0, 11.0), (0.3, 6.5), (0.7, 4.2), (1, 3.4)), up=(0, 0, -1))
    shapes.shell(shroud, sf, 18, 12, "cloth", thick=0.4,
                 mat_fn=lambda u, v: "cloth_dk" if int(u * 18) % 4 == 0 and v < 0.85 else "cloth")
    # torn strips trailing over the ground
    for k in range(12):
        a = k * 2 * math.pi / 12 + 0.2
        p = np.array([math.cos(a) * 11.0, 1.0, math.sin(a) * 9.5 + 2.0])
        shapes.horn(shroud, p, (math.cos(a), -0.05, math.sin(a)), 6.0 + (k % 3) * 2.0, 1.8, mat="cloth_dk", flat=0.2,
                    up=(0, 1, 0), sections=3, around=6, r1=0.3)
    body = m.bone("body", parent="root", pivot=(0, 30, 0))
    # a withered core inside the ribcage
    shapes.shell(body, shapes.loft(shapes.polyline([(0, 29.0, 1.0), (0, 40.0, 1.0), (0, 52.0, 0.5),
                                                    (0, 58.0, 0.0)]),
                                   shapes.profile((0, 2.4), (0.5, 3.4), (1, 2.0)),
                                   shapes.profile((0, 2.2), (0.5, 3.0), (1, 1.8)), up=(0, 0, -1)),
                 10, 10, "hollow", thick=0.3)
    # spine
    for k in range(15):
        y = 30.0 + k * 1.9
        shapes.shell(body, shapes.ellipsoid((0, y, 3.6), (1.1, 0.8, 1.1)), 6, 3, "bone_dk", thick=0.3)
    # ribs sweeping down and round from the spine to the breastbone
    for k in range(6):
        y = 55.0 - k * 2.6
        w = 5.2 + min(k, 3) * 0.7 - max(0, k - 3) * 0.5
        for s_ in (-1, 1):
            pts = [(s_ * 1.0, y, 3.4), (s_ * w * 0.85, y - 0.6, 2.4), (s_ * w, y - 1.8, -0.8),
                   (s_ * w * 0.75, y - 3.0, -3.6), (s_ * 1.2, y - 3.6 - k * 0.2, -4.6)]
            shapes.shell(body, shapes.loft(shapes.polyline(pts), 0.6, 0.45), 5, 9, "bone", thick=0.25)
    # breastbone
    shapes.shell(body, shapes.loft(shapes.polyline([(0, 55.5, -4.4), (0, 50.0, -4.9), (0, 44.0, -4.6)]),
                                   shapes.profile((0, 1.0), (1, 0.6)), 0.5, up=(0, 0, -1)), 6, 6, "bone", thick=0.25)
    # pelvis where the shroud swallows it
    shapes.shell(body, shapes.ellipsoid((0, 31.5, 0.5), (5.5, 2.5, 3.6)), 10, 5, "bone_dk", thick=0.3)
    # shoulder girdle
    for s_ in (-1, 1):
        bony_limb(body, [(s_ * 1.0, 57.5, 2.0), (s_ * 6.0, 58.5, 1.0), (s_ * 10.0, 58.0, 0.5)], 0.9, 0.7, knobs=False)
        bony_limb(body, [(s_ * 1.0, 56.8, -4.0), (s_ * 6.0, 57.8, -2.0), (s_ * 10.0, 58.0, 0.5)], 0.7, 0.6,
                  knobs=False)
    # a strip of grave cloth over one shoulder and across the ribs
    sash = shapes.loft(shapes.polyline([(6.0, 59.5, 2.5), (5.5, 59.5, -3.5), (1.0, 52.0, -6.0), (-5.0, 43.0, -5.0),
                                        (-7.0, 38.0, -1.0)]), 1.6, 0.3, up=lambda t: (0.6, 0.3, -0.8))
    shapes.shell(body, sash, 4, 18, "cloth", thick=0.25)
    # neck
    bony_limb(body, [(0, 57.0, 1.0), (0, 61.0, 0.5), (0, 64.0, -0.5)], 1.4, 1.1, mat="bone_dk")

    # the skull
    head = m.bone("head", parent="body", pivot=(0, 63, 0))
    look = m.bone("look", parent="head", pivot=(0, 65, 0))
    # a long cranium swept back, with a jutting muzzle of teeth
    cran = shapes.ellipsoid((0, 69.0, 0.5), (5.0, 5.2, 6.8), e_lat=0.95)
    shapes.shell(look, cran, 16, 12, "bone", thick=0.4)
    shapes.shell(look, shapes.ellipsoid((0, 65.4, -3.2), (4.3, 2.0, 3.8)), 12, 6, "bone", thick=0.35, v0=0.35)
    # cheekbones
    for s_ in (-1, 1):
        shapes.shell(look, shapes.ellipsoid((s_ * 4.0, 66.6, -3.6), (1.4, 1.2, 2.0)), 6, 4, "bone_dk", thick=0.3)
    # deep sockets with pin-prick eyes, and the nose hole
    for s_ in (-1, 1):
        p, n, du, dv = shapes.surface_frame(cran, 0.07 if s_ > 0 else 0.93, 0.56)
        look.decal(p + n * 0.1, n, 3.2, 2.8, "hollow", up=(0, 1, 0))
        look.cbox(tuple(p + n * 0.2), (0.6, 0.6, 0.3), "eye")
    p, n, du, dv = shapes.surface_frame(cran, 0.0, 0.36)
    look.decal(p + n * 0.1, n, 1.4, 1.8, "hollow", up=(0, 1, 0))
    # the grin
    upper = [(-4.2, 64.2, -1.5), (-3.6, 63.8, -4.8), (0, 63.8, -6.8), (3.6, 63.8, -4.8), (4.2, 64.2, -1.5)]
    for k in range(15):
        t = k / 14
        p = shapes.polyline(upper)(t)
        look.spike(p, (0, -1, 0), 1.8, 0.6, 0.3, "teeth", steps=2, up=(0, 0, -1))
    jaw = m.bone("jaw", parent="look", pivot=(0, 64.5, 0.5))
    lower = [(-4.3, 64.0, 0.5), (-4.0, 61.8, -3.0), (0, 61.3, -6.4), (4.0, 61.8, -3.0), (4.3, 64.0, 0.5)]
    shapes.shell(jaw, shapes.loft(shapes.polyline(lower), 0.9, 1.0, up=(0, 1, 0)), 6, 16, "bone", thick=0.3)
    for k in range(13):
        t = 0.08 + k * 0.07
        p = shapes.polyline(lower)(t)
        jaw.spike(p + np.array([0, 0.6, 0]), (0, 1, 0), 1.6, 0.55, 0.3, "teeth", steps=2, up=(0, 0, -1))
    # horns sweeping back and out
    for s in (-1, 1):
        shapes.horn(look, (s * 3.6, 72.0, 1.5), (s * 0.8, 0.5, 0.6), 11.0, 1.5, mat="horn", tip_mat="bone_dk",
                    sections=7, around=6, r1=0.15, bend_axis=(0, 0, s), bend=-60 * s)
    # the nails driven through it
    for (p, d) in (((0.5, 74.2, -1.0), (0.1, -1, -0.3)), ((-3.9, 71.5, -3.8), (0.6, -0.4, 0.6)),
                   ((4.6, 68.6, -2.4), (-0.8, -0.2, 0.4))):
        d = norm(d)
        p = np.asarray(p)
        look.cylinder(tuple(p - d * 1.5), tuple(d), 0.3, 3.5, "nail", segments=6)
        look.cylinder(tuple(p - d * 1.6), tuple(d), 0.8, 0.3, "nail", segments=6)

    # arms long enough to reach the ground
    for side, name in ((-1, "right_arm"), (1, "left_arm")):
        sh = np.array([side * 10.5, 58.0, 0.5])
        arm = m.bone(name, parent="body", pivot=tuple(sh))
        shapes.shell(arm, shapes.ellipsoid(sh, (2.2, 2.2, 2.2)), 7, 5, "bone_dk", thick=0.3)
        el = sh + np.array([side * 3.5, -17.0, 2.5])
        wr = el + np.array([side * 0.5, -17.0, -3.0])
        bony_limb(arm, [sh, el], 1.3, 1.0)
        for off in (-0.7, 0.7):
            bony_limb(arm, [el + np.array([off, 0, 0]), wr + np.array([off * 0.6, 0, 0])], 0.8, 0.6, knobs=False)
        shapes.shell(arm, shapes.ellipsoid(el, (1.6, 1.6, 1.6)), 6, 4, "bone_dk", thick=0.3)
        # grave cloth trailing from the forearm
        shapes.horn(arm, el + np.array([0, -2, 1.0]), (0, -1, 0.4), 12.0, 1.8, mat="cloth", flat=0.2, up=(0, 0, 1),
                    sections=4, around=6, r1=0.4)
        hand(arm, wr, (0, -1, -0.25), (side, 0, 0), size=1.25, curl=40)

    # grave hands that claw up out of the ground (Grave Hands)
    for k in range(8):
        a = k * 2 * math.pi / 8 + 0.3
        rr = 34.0 + (k % 3) * 8.0
        base = np.array([math.cos(a) * rr, 0.0, math.sin(a) * rr])
        fx = m.bone("fx_rise_hand%d" % k, parent="root", pivot=tuple(base))
        up = norm(np.array([-math.cos(a) * 0.2, 1, -math.sin(a) * 0.2]))
        bony_limb(fx, [base - up * 2.0, base + up * 6.0, base + up * 12.0 + np.array([math.cos(a), 0, math.sin(a)])],
                  1.4, 1.0)
        hand(fx, base + up * 12.0, up, (math.sin(a), 0, -math.cos(a)), size=1.5, curl=55)

    geo, tex, glow, anim_path = dk.devil_paths("curse")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=253)
    anims = animations()
    save_animations(anim_path, anims)
    print("curse devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    arms = ("right_arm", "left_arm")
    idle = Anim("idle", 4.0, loop=True)
    for i in range(9):
        t = 4.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("body", t, (4 + 2 * math.sin(ph), 3 * math.sin(ph * 0.5), 0))
        idle.rot("head", t, (-6 + 4 * math.sin(ph + 1), 8 * math.sin(ph * 0.5), 5 * math.sin(ph)))
        idle.rot("right_arm", t, (-4 + 4 * math.sin(ph), 0, 4 + 2 * math.sin(ph)))
        idle.rot("left_arm", t, (-4 + 4 * math.sin(ph + 1.5), 0, -4 - 2 * math.sin(ph + 1.5)))
        idle.rot("jaw", t, (4 + 3 * math.sin(ph * 2), 0, 0))
        idle.scale("shroud", t, (1 + 0.02 * math.sin(ph), 1, 1 + 0.02 * math.sin(ph)))
    A.append(idle)
    mv = Anim("move", 2.0, loop=True)
    for i in range(9):
        t = 2.0 * i / 8
        ph = 2 * math.pi * i / 8
        mv.rot("body", t, (14 + 3 * math.sin(ph), 6 * math.sin(ph), 0))
        mv.rot("right_arm", t, (-20 + 25 * math.sin(ph), 0, 6))
        mv.rot("left_arm", t, (-20 - 25 * math.sin(ph), 0, -6))
        mv.pos("root", t, (0, 1.0 * math.sin(2 * ph), 0))
        mv.scale("shroud", t, (1 + 0.05 * math.sin(2 * ph), 1 - 0.03 * math.sin(2 * ph), 1))
        mv.rot("head", t, (-10, 5 * math.sin(ph), 0))
    A.append(mv)
    # the nail: a quick overhand stab with the right hand
    nl = Anim("nail", 0.7)
    nl.rot("right_arm", 0, (0, 0, 0)).rot("right_arm", 0.2, (-150, 0, 15), "easeOutQuad")
    nl.rot("right_arm", 0.3, (-60, 0, 5), "easeInQuad").rot("right_arm", 0.7, (0, 0, 0))
    nl.rot("body", 0.2, (-6, 0, 0)).rot("body", 0.3, (16, 0, 0)).rot("body", 0.7, (4, 0, 0))
    nl.rot("jaw", 0.2, (25, 0, 0)).rot("jaw", 0.35, (0, 0, 0))
    A.append(nl)
    # the grip: the left hand reaches far out, closes, lifts, wrings - and slams down
    gp = Anim("grip", 2.2)
    gp.rot("left_arm", 0, (0, 0, 0)).rot("left_arm", 0.4, (-95, 0, -10), "easeOutQuad")
    gp.rot("left_arm", 1.0, (-120, 0, -5)).rot("left_arm", 1.5, (-130, 20, -5)).rot("left_arm", 1.8, (-50, 0, 0), "easeInQuad")
    gp.rot("left_arm", 2.2, (0, 0, 0))
    gp.pos("left_arm", 0.4, (0, 2, -6)).pos("left_arm", 1.8, (0, 0, -2)).pos("left_arm", 2.2, (0, 0, 0))
    gp.rot("body", 0.4, (20, -10, 0)).rot("body", 1.5, (10, 10, 0)).rot("body", 1.8, (28, 0, 0)).rot("body", 2.2, (4, 0, 0))
    gp.rot("jaw", 0.9, (30, 0, 0)).rot("jaw", 1.8, (10, 0, 0)).rot("jaw", 2.2, (0, 0, 0))
    A.append(gp)
    hx = Anim("hex", 1.5)
    for a_, s in zip(arms, (1, -1)):
        hx.rot(a_, 0, (0, 0, 0)).rot(a_, 0.4, (-100, 0, s * 40), "easeOutQuad").rot(a_, 1.0, (-95, 0, s * 45))
        hx.rot(a_, 1.5, (0, 0, 0))
    hx.rot("head", 0.4, (-20, 0, 0)).rot("head", 1.0, (-25, 0, 0)).rot("head", 1.5, (0, 0, 0))
    hx.rot("jaw", 0.3, (45, 0, 0), "easeOutQuad").rot("jaw", 1.0, (40, 0, 0)).rot("jaw", 1.5, (0, 0, 0))
    hx.rot("body", 0.4, (-10, 0, 0)).rot("body", 1.5, (4, 0, 0))
    A.append(hx)
    rs = Anim("rise", 2.0)
    for a_, s in zip(arms, (1, -1)):
        rs.rot(a_, 0, (0, 0, 0)).rot(a_, 0.35, (-170, 0, s * 10), "easeOutQuad").rot(a_, 0.5, (-40, 0, s * 5), "easeInQuad")
        rs.rot(a_, 1.6, (-40, 0, s * 5)).rot(a_, 2.0, (0, 0, 0))
    rs.rot("body", 0.35, (-12, 0, 0)).rot("body", 0.5, (35, 0, 0)).rot("body", 1.6, (30, 0, 0)).rot("body", 2.0, (4, 0, 0))
    for k in range(8):
        b = "fx_rise_hand%d" % k
        t0 = 0.5 + (k % 4) * 0.08
        rs.pos(b, 0, (0, -24, 0)).pos(b, t0, (0, -24, 0)).pos(b, t0 + 0.2, (0, 1, 0), "easeOutBack")
        rs.pos(b, 1.7, (0, 0, 0)).pos(b, 2.0, (0, -24, 0), "easeInQuad")
        rs.rot(b, t0 + 0.2, (0, 0, 0)).rot(b, 1.2, (0, 0, 10 if k % 2 else -10)).rot(b, 1.7, (0, 0, 0))
    A.append(rs)
    dr = Anim("drink", 1.0)
    dr.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.3, (30, 0, 0)).rot("jaw", 1.0, (0, 0, 0))
    A.append(dr)
    death = Anim("death", 2.0, loop="hold_on_last_frame")
    death.rot("body", 0, (0, 0, 0)).rot("body", 0.8, (40, 0, 10), "easeInQuad").rot("body", 1.4, (85, 0, 15), "easeInQuad")
    death.pos("root", 1.4, (0, -8, 0))
    death.rot("right_arm", 1.2, (-40, 0, 40)).rot("left_arm", 1.2, (-20, 0, -50))
    death.rot("head", 1.4, (30, 30, 0)).rot("jaw", 1.4, (40, 0, 0))
    death.scale("shroud", 0, 1.0).scale("shroud", 2.0, (1.3, 0.3, 1.3))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.5, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    fxh = tuple("fx_rise_hand%d" % k for k in range(8))
    shots = [
        preview.render(geo, tex, preview_path("curse_front.png"), anim, "idle", 0.0, yaw=25, pitch=6, show_body=False, hidden=fxh,
                       scale=4.2, center=(0, 2.2), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("curse_rise.png"), anim, "rise", 1.0, yaw=60, pitch=18, show_body=False,
                       scale=3.0, center=(0, 2.0), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("curse_face.png"), anim, "idle", 0.0, yaw=15, pitch=0, show_body=False, hidden=fxh,
                       scale=12.0, center=(0, 4.1), size=(620, 620), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("curse_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
