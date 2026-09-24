"""
The Darkness Devil - entity model (entity/devil/darkness), texture atlas and GeckoLib animations.

Reference points:
  * a tall column of withered human bodies: two form its legs, four more stacked into its torso, each with a ruined face
  * a pteranodon-like head with curved horns, long withered arms, a mantle of darkness
  * with a gesture it shears off the arms of everyone around it; it drowns an area in darkness; its wounds won't heal
  * a Primal Fear, but weak to light and fire
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
    a.add("body", kind="skin", color=(74, 70, 78))
    a.add("body_dk", kind="skin", color=(44, 40, 48))
    a.add("rib", kind="bone", color=(120, 112, 116))
    a.add("face", kind="skin", color=(150, 140, 142))
    a.add("hollow", kind="void", color=(6, 4, 8))
    a.add("mouth", kind="void", color=(20, 6, 10))
    a.add("skull", kind="bone", color=(56, 52, 60))
    a.add("horn", kind="bone", color=(34, 30, 36))
    a.add("mantle", kind="void", color=(10, 8, 16))
    a.add("mantle_edge", kind="skin", color=(30, 22, 44))
    a.add("claw", kind="bone", color=(26, 22, 28))
    a.add("eye", kind="glow", color=(150, 120, 255), color2=(230, 220, 255), emissive=True)
    return a


def withered_body(bone, top, bottom, width, face_side=-1, rng=None, curl=0.0):
    """A shrivelled human body lying along top->bottom: bony torso, knees pulled up, a ruined face at the head end."""
    top = np.asarray(top, dtype=float)
    bottom = np.asarray(bottom, dtype=float)
    axis = bottom - top
    L = np.linalg.norm(axis)
    mid = top + axis * 0.5 + np.array([0, 0, curl])
    f = shapes.loft(shapes.polyline([top, mid, bottom]),
                    shapes.profile((0, width * 0.55), (0.12, width * 0.5), (0.3, width), (0.7, width * 0.85),
                                   (1, width * 0.55)),
                    shapes.profile((0, width * 0.5), (0.3, width * 0.7), (1, width * 0.5)), up=(0, 0, -1))
    shapes.shell(bone, f, 10, 8, "body", thick=0.45,
                 mat_fn=lambda u, v: "body_dk" if abs(u - 0.5) < 0.18 else "body")
    # ribs showing through the skin
    for k in range(3):
        p, n, du, dv = shapes.surface_frame(f, 0.0, 0.32 + k * 0.08)
        bone.obox(p + n * 0.1, du, (0.4, width * 1.2, 0.35), "rib", up=n)
    # the ruined face at the head end
    p, n, du, dv = shapes.surface_frame(f, 0.0, 0.08)
    c = p + n * 0.2
    bone.decal(c, n, width * 0.9, width * 0.9, "face", up=norm(axis) * -1)
    for s in (-1, 1):
        bone.cbox(c + n * 0.15 + du * s * width * 0.2 + norm(-axis) * width * 0.12, (0.6, 0.6, 0.2), "hollow")
    bone.cbox(c + n * 0.15 - norm(-axis) * width * 0.2, (width * 0.35, 0.4, 0.2), "mouth")
    return f


def build():
    atlas = materials()
    m = Model("csm.darkness_devil", atlas, density=2.0, seed=211)

    root = m.bone("root", pivot=(0, 0, 0))
    # legs: two withered bodies standing on their heads
    for side, name in ((-1, "right_leg"), (1, "left_leg")):
        leg = m.bone(name, parent="root", pivot=(side * 4.0, 42, 0))
        withered_body(leg, (side * 4.2, 1.5, -0.5), (side * 3.8, 45.0, 0.5), 4.6, curl=-1.5 * side)
        shapes.shell(leg, shapes.ellipsoid((side * 4.2, 1.5, -1.5), (3.0, 1.6, 4.0)), 8, 5, "body_dk", thick=0.4)
    waist = m.bone("waist", parent="root", pivot=(0, 42, 0))
    body = m.bone("body", parent="waist", pivot=(0, 42, 0))
    # torso: four more stacked, curled over one another
    for k in range(4):
        y0 = 42.0 + k * 8.0
        side = -1 if k % 2 else 1
        withered_body(body, (side * 8.5, y0 + 3.0, -1.0 + 0.3 * k), (-side * 8.5, y0 + 7.5, 0.5), 6.0, curl=-2.5)
    # sinew binding the stacked bodies into one column
    shapes.shell(body, shapes.loft(shapes.polyline([(0, 42.0, 1.0), (0, 60.0, 1.5), (0, 76.0, 1.0)]),
                                   shapes.profile((0, 4.5), (0.5, 6.0), (1, 5.5)), 3.5, up=(0, 0, -1)), 12, 8,
                 "body_dk", thick=0.4)
    # the mantle of darkness hanging from the shoulders
    mantle = m.bone("mantle", parent="body", pivot=(0, 78, 3))
    cloak = shapes.loft(shapes.polyline([(0, 80.0, 3.5), (0, 55.0, 7.0), (0, 30.0, 10.0), (0, 8.0, 12.0)]),
                        shapes.profile((0, 9.0), (0.4, 14.0), (1, 18.0)),
                        shapes.profile((0, 5.0), (0.4, 7.0), (1, 9.0)), up=(0, 0, -1))
    shapes.shell(mantle, cloak, 14, 14, "mantle", u0=0.3, u1=0.7, thick=0.4,
                 mat_fn=lambda u, v: "mantle_edge" if v > 0.92 else "mantle")
    for k in range(9):
        x = -16 + k * 4.0
        shapes.horn(mantle, (x, 9.0, 11.5 + abs(x) * 0.1), (0, -1, 0.2), 5.0 + (k % 3) * 2.5, 1.6, mat="mantle",
                    flat=0.25, up=(0, 0, 1), sections=3, around=6, r1=0.1)
    # long withered arms with clawed fingers
    for side, name in ((-1, "right_arm"), (1, "left_arm")):
        sh = np.array([side * 10.0, 76.0, 0.0])
        arm = m.bone(name, parent="body", pivot=tuple(sh))
        el = sh + np.array([side * 4.0, -18.0, 1.0])
        wr = el + np.array([side * 1.0, -18.0, -3.0])
        shapes.shell(arm, shapes.loft(shapes.polyline([sh, el, wr]), shapes.profile((0, 2.4), (0.5, 1.6), (1, 1.3)),
                                      shapes.profile((0, 2.2), (0.5, 1.5), (1, 1.2))), 8, 12, "body", thick=0.35)
        hand = wr + np.array([0, -1.5, -0.5])
        shapes.shell(arm, shapes.ellipsoid(hand, (1.6, 2.0, 1.4)), 8, 5, "body_dk", thick=0.3)
        for j in range(4):
            d = norm(np.array([side * (0.3 * (j - 1.5)), -1, -0.3]))
            shapes.horn(arm, hand + d * 1.5, d, 6.0, 0.5, mat="claw", sections=4, around=5, r1=0.08,
                        bend_axis=(1, 0, 0), bend=-35)
    # the pteranodon-like head: long beak forward, crest back, curved horns
    head = m.bone("head", parent="body", pivot=(0, 79, 0))
    look = m.bone("look", parent="head", pivot=(0, 80, 0))
    skull = shapes.loft(shapes.polyline([(0, 83.0, 9.0), (0, 84.0, 2.0), (0, 83.0, -6.0), (0, 81.0, -18.0)]),
                        shapes.profile((0, 0.5), (0.2, 3.2), (0.45, 3.8), (0.7, 2.2), (1, 0.2)),
                        shapes.profile((0, 0.5), (0.2, 3.4), (0.45, 3.6), (0.7, 1.8), (1, 0.2)), up=(0, 1, 0))
    shapes.shell(look, skull, 10, 14, "skull", thick=0.4)
    # the crest sweeping back
    shapes.horn(look, (0, 85.0, 2.0), (0, 0.3, 1), 12.0, 3.0, mat="skull", flat=0.2, up=(1, 0, 0), sections=6,
                around=6, r1=0.2, bend_axis=(1, 0, 0), bend=12)
    # curved horns
    for s in (-1, 1):
        shapes.horn(look, (s * 2.4, 85.0, 0.0), (s * 1.0, 0.6, 0.3), 9.0, 1.2, mat="horn", sections=6, around=6,
                    r1=0.1, bend_axis=(0, 0, s * 1.0), bend=70 * s)
        look.cbox((s * 2.8, 83.8, -4.0), (0.9, 0.6, 1.2), "eye")
    jaw = m.bone("jaw", parent="look", pivot=(0, 81.5, 1.0))
    lj = shapes.loft(shapes.polyline([(0, 81.0, 1.0), (0, 80.4, -8.0), (0, 80.6, -16.0)]),
                     shapes.profile((0, 2.6), (0.5, 1.6), (1, 0.2)), shapes.profile((0, 1.2), (1, 0.2)), up=(0, 1, 0))
    shapes.shell(jaw, lj, 8, 10, "skull", thick=0.35)
    for name in ("look", "jaw"):
        m.by_name[name].scale_about((0, 79.0, 0), 1.9)
    geo, tex, glow, anim_path = dk.devil_paths("darkness")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=213)
    anims = animations()
    save_animations(anim_path, anims)
    print("darkness devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))

    return geo, tex, anim_path


def animations():
    A = []
    idle = Anim("idle", 4.0, loop=True)
    for i in range(9):
        t = 4.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("body", t, (2 * math.sin(ph), 0, 1.5 * math.cos(ph)))
        idle.rot("head", t, (-3 * math.sin(ph), 4 * math.cos(ph * 0.5), 0))
        idle.rot("mantle", t, (4 + 3 * math.sin(ph), 0, 2 * math.cos(ph)))
        idle.rot("right_arm", t, (3 * math.sin(ph), 0, 4))
        idle.rot("left_arm", t, (-3 * math.sin(ph), 0, -4))
    A.append(idle)
    mv = Anim("move", 2.0, loop=True)
    for i in range(9):
        t = 2.0 * i / 8
        ph = 2 * math.pi * i / 8
        s = math.sin(ph)
        mv.rot("right_leg", t, (18 * s, 0, 0))
        mv.rot("left_leg", t, (-18 * s, 0, 0))
        mv.rot("right_arm", t, (-12 * s, 0, 5))
        mv.rot("left_arm", t, (12 * s, 0, -5))
        mv.rot("waist", t, (6, 3 * s, 0))
        mv.rot("mantle", t, (12 + 4 * math.sin(ph * 2), 0, 0))
        mv.pos("root", t, (0, -1.0 * abs(math.cos(ph)), 0))
    A.append(mv)
    # Severance: a slow sweep of the hand - and everyone's arms come off
    sv = Anim("sever", 1.5)
    sv.rot("right_arm", 0, (0, 0, 0)).rot("right_arm", 0.5, (-150, -30, 30), "easeInOutSine")
    sv.rot("right_arm", 0.75, (-90, 40, 10), "easeOutQuad").rot("right_arm", 1.5, (0, 0, 0))
    sv.rot("head", 0.5, (-15, 0, 0)).rot("head", 0.75, (10, 0, 0)).rot("head", 1.5, (0, 0, 0))
    sv.rot("mantle", 0.75, (30, 0, 0)).rot("mantle", 1.5, (0, 0, 0))
    A.append(sv)
    # Hell's darkness: arms spread, the mantle swelling out
    hl = Anim("hell", 2.0)
    for side, s in (("right_arm", 1), ("left_arm", -1)):
        hl.rot(side, 0, (0, 0, 0)).rot(side, 0.6, (-60, 0, s * 70), "easeOutQuad").rot(side, 1.6, (-60, 0, s * 70))
        hl.rot(side, 2.0, (0, 0, 0))
    hl.scale("mantle", 0, 1.0).scale("mantle", 0.8, (1.6, 1.1, 1.8), "easeOutQuad").scale("mantle", 1.6, (1.6, 1.1, 1.8))
    hl.scale("mantle", 2.0, 1.0)
    hl.rot("head", 0.6, (-30, 0, 0)).rot("jaw", 0.6, (30, 0, 0)).rot("head", 2.0, (0, 0, 0)).rot("jaw", 2.0, (0, 0, 0))
    A.append(hl)
    # Unseen cut: a flick of two claws
    ct = Anim("cut", 1.0)
    ct.rot("left_arm", 0, (0, 0, 0)).rot("left_arm", 0.35, (-100, 40, 0), "easeInQuad")
    ct.rot("left_arm", 0.5, (-70, -50, 0), "easeOutQuad").rot("left_arm", 1.0, (0, 0, 0))
    A.append(ct)
    # Rake: both claws tear down
    rk = Anim("rake", 1.0)
    for side, s in (("right_arm", 1), ("left_arm", -1)):
        rk.rot(side, 0, (0, 0, 0)).rot(side, 0.35, (-140, 0, s * 20), "easeInQuad").rot(side, 0.55, (-30, 0, s * 10),
                                                                                     "easeOutQuad")
        rk.rot(side, 1.0, (0, 0, 0))
    rk.rot("waist", 0.35, (-8, 0, 0)).rot("waist", 0.55, (18, 0, 0)).rot("waist", 1.0, (0, 0, 0))
    A.append(rk)
    A.append(Anim("drink", 1.0))
    death = Anim("death", 2.0, loop="hold_on_last_frame")
    death.rot("waist", 0, (0, 0, 0)).rot("waist", 1.2, (70, 0, 0), "easeInQuad")
    death.pos("root", 0, (0, 0, 0)).pos("root", 1.2, (0, -20, -12), "easeInQuad")
    death.scale("mantle", 1.6, 0.2)
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.15))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("darkness_front.png"), anim, "idle", 0.0, yaw=15, pitch=6,
                       show_body=False, scale=3.6, center=(0, 2.8), size=(620, 700)),
        preview.render(geo, tex, preview_path("darkness_side.png"), anim, "idle", 0.0, yaw=80, pitch=6,
                       show_body=False, scale=3.6, center=(0, 2.8), size=(620, 700)),
        preview.render(geo, tex, preview_path("darkness_back.png"), anim, "hell", 1.0, yaw=190, pitch=6,
                       show_body=False, scale=3.6, center=(0, 2.8), size=(620, 700)),
    ]
    return preview.contact_sheet(shots, preview_path("darkness_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
