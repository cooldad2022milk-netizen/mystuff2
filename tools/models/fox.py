"""
The Fox Devil - entity model (entity/devil/fox) and animations.

Reference points:
  * a monstrous fox: long snout full of fangs, huge pointed ears, a big bushy tail
  * many eyes ringed like a Devil's, some even on its clawed forelimbs
  * orange / pale brown in the manga (white with red-orange eyes in the anime)
  * summoned by the "Kon!" hand sign, it bites people clean in half
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
    a.add("fur", kind="fiber", color=(226, 152, 88))
    a.add("fur_lt", kind="fiber", color=(244, 222, 190))
    a.add("fur_dk", kind="fiber", color=(176, 104, 56))
    a.add("eye", kind="ringeye", color=(236, 170, 60), color2=(150, 30, 20), rings=2, sclera=(250, 236, 214))
    a.add("teeth", kind="teeth", color=(242, 238, 224))
    a.add("mouth", kind="void", color=(70, 14, 20))
    a.add("gum", kind="flesh", color=(190, 80, 90))
    a.add("nose", kind="gloss", color=(30, 22, 22))
    a.add("claw", kind="bone", color=(40, 30, 28))
    a.add("ear_in", kind="skin", color=(90, 50, 40))
    return a


def body_and_head(m):
    root = m.bone("root", pivot=(0, 0, 0))
    body = m.bone("body", parent="root", pivot=(0, 22, 4))
    # a long body: deep chest in front, narrow waist, rounded haunches
    torso = shapes.loft(shapes.polyline([(0, 25.0, -13.0), (0, 23.0, -6.0), (0, 23.5, 4.0), (0, 24.5, 12.0),
                                         (0, 25.5, 17.0)]),
                        shapes.profile((0, 4.5), (0.15, 6.8), (0.5, 5.4), (0.8, 6.4), (1, 3.5)),
                        shapes.profile((0, 5.0), (0.15, 8.2), (0.5, 5.8), (0.8, 6.6), (1, 3.5)), up=(0, 1, 0))
    shapes.shell(body, torso, 18, 14, "fur", thick=0.5,
                 mat_fn=lambda u, v: "fur_lt" if abs(u - 0.5) < 0.13 and v < 0.6 else "fur")
    # eyes scattered along its flanks
    for (u, v, w) in ((0.2, 0.3, 2.6), (0.28, 0.55, 2.0), (0.16, 0.75, 2.2), (0.8, 0.28, 2.4), (0.73, 0.5, 2.2),
                      (0.84, 0.7, 2.0)):
        p, n, du, dv = shapes.surface_frame(torso, u, v)
        body.decal(p + n * 0.15, n, w * 1.5, w * 0.95, "eye", up=(0, 1, 0))
    # the bushy tail: a thick brush that thins to a pale tip
    tail = m.bone("tail", parent="body", pivot=(0, 25, 17))
    tf = shapes.loft(shapes.polyline([(0, 25.5, 16.0), (0, 27.0, 22.0), (0, 31.0, 28.0), (0, 36.0, 32.0),
                                      (0, 41.0, 34.0)]),
                     shapes.profile((0, 2.6), (0.25, 5.2), (0.55, 6.6), (0.82, 5.2), (1, 0.8)),
                     shapes.profile((0, 2.6), (0.25, 4.8), (0.55, 6.0), (0.82, 4.8), (1, 0.8)))
    shapes.shell(tail, tf, 14, 14, "fur", thick=0.45, mat_fn=lambda u, v: "fur_lt" if v > 0.8 else "fur")
    # neck
    shapes.shell(body, shapes.loft(shapes.polyline([(0, 25.0, -10.0), (0, 29.0, -14.0), (0, 32.5, -16.0)]),
                                   shapes.profile((0, 5.5), (1, 4.2)), shapes.profile((0, 6.0), (1, 4.5)),
                                   up=(0, 0.4, -1)), 12, 6, "fur", thick=0.45,
                 mat_fn=lambda u, v: "fur_lt" if abs(u - 0.5) < 0.2 else "fur")
    # the head: one wedge from the back of the skull to the nose, a jaw cut out of its front half
    head = m.bone("head", parent="body", pivot=(0, 31, -14))
    look = m.bone("look", parent="head", pivot=(0, 33, -16))
    skull = shapes.loft(shapes.polyline([(0, 35.5, -12.5), (0, 36.0, -17.0), (0, 34.6, -23.0), (0, 33.0, -29.0),
                                         (0, 32.2, -34.0)]),
                        shapes.profile((0, 3.0), (0.15, 6.0), (0.35, 5.8), (0.55, 3.2), (0.8, 2.2), (1, 1.0)),
                        shapes.profile((0, 3.0), (0.15, 5.2), (0.35, 4.6), (0.55, 3.0), (0.8, 2.1), (1, 1.1)),
                        up=(0, 1, 0))
    mouth = shapes.Mouth(skull, 0.5, 0.25, 0.42, 0.97)
    shapes.shell(look, skull, 16, 14, "fur", skip=mouth.skip, thick=0.4,
                 mat_fn=lambda u, v: "fur_lt" if abs(u - 0.5) < 0.3 and v > 0.2 else "fur")
    jaw = m.bone("jaw", parent="look", pivot=(0, 33.0, -20.0))
    mouth.build(look, jaw, "fur_lt", upper=11, lower=9, tooth_len=1.5, tooth_w=0.6, nu=6, nv=9, gum_mat="gum")
    look.cbox((0, 33.7, -34.2), (1.9, 1.5, 1.2), "nose")
    # its many eyes: the main pair, then more crowding up the brow
    for (u, v, w) in ((0.12, 0.46, 3.2), (0.88, 0.46, 3.2), (0.2, 0.3, 2.4), (0.8, 0.3, 2.4), (0.04, 0.33, 2.0),
                      (0.96, 0.33, 2.0), (0.0, 0.2, 2.2), (0.24, 0.62, 1.6), (0.76, 0.62, 1.6)):
        p, n, du, dv = shapes.surface_frame(skull, u, v)
        look.decal(p + n * 0.18, n, w * 1.4, w * 0.9, "eye", up=(0, 1, 0))
    # huge ears, dark inside
    for s in (-1, 1):
        root_p = np.array([s * 3.4, 39.0, -14.5])
        d = (s * 0.3, 1, 0.15)
        shapes.horn(look, root_p, d, 9.0, 3.0, mat="fur", tip_mat="fur_dk", flat=0.3, up=(0, 0, 1), sections=5,
                    around=8, r1=0.2)
        shapes.horn(look, root_p + np.array([0, 0.5, -0.8]), d, 7.0, 2.0, mat="ear_in", flat=0.15, up=(0, 0, 1),
                    sections=4, around=8, r1=0.2)
    # cheek ruff
    for s in (-1, 1):
        for k in range(5):
            p = np.array([s * 5.2, 33.0 - k * 0.8, -16.0 + k * 1.2])
            shapes.horn(look, p, norm([s * 1.0, -0.4, 0.5]), 3.0 - k * 0.3, 1.1, mat="fur_lt", sections=2, around=5,
                        r1=0.1)
    # chest ruff
    for k in range(9):
        a = math.radians(-70 + k * 140 / 8)
        p = np.array([math.sin(a) * 5.5, 25.0 - abs(math.sin(a)) * 1.5, -13.5])
        shapes.horn(body, p, norm([math.sin(a) * 0.5, -1.0, -0.6]), 4.0, 1.6, mat="fur_lt", sections=3, around=5,
                    r1=0.1)
    return root, body


def leg(m, name, pts, radii, eyes=0):
    """A leg through hip -> joints -> wrist, tapering by `radii`; a padded clawed paw at the end."""
    pts = [np.array(p, dtype=float) for p in pts]
    b = m.bone(name, parent="body", pivot=tuple(pts[0]))
    f = shapes.loft(shapes.polyline(pts), shapes.profile(*radii), shapes.profile(*[(t, r * 0.9) for t, r in radii]),
                    up=(0, 0, -1))
    shapes.shell(b, f, 10, 12, "fur", thick=0.4, mat_fn=lambda u, v: "fur_dk" if v > 0.75 else "fur")
    foot = pts[-1]
    paw = foot + np.array([0, -0.6, -1.4])
    shapes.shell(b, shapes.ellipsoid(paw, (1.9, 1.1, 2.4)), 8, 5, "fur_dk", thick=0.35)
    for k in range(4):
        x = -1.2 + k * 0.8
        shapes.horn(b, paw + np.array([x, 0.1, -2.0]), (0, -0.3, -1), 1.6, 0.35, mat="claw", sections=2, around=5,
                    r1=0.05, bend_axis=(1, 0, 0), bend=40)
    for k in range(eyes):
        p, n, du, dv = shapes.surface_frame(f, 0.5 + (0.1 if k % 2 else -0.1), 0.2 + k * 0.2)
        b.decal(p + n * 0.15, n, 2.6, 1.6, "eye", up=norm(dv))


def build():
    atlas = materials()
    m = Model("csm.fox_devil", atlas, density=2.0, seed=241)
    body_and_head(m)
    for side, s in (("right", -1), ("left", 1)):
        leg(m, side + "_front_leg", [(s * 4.8, 23.0, -8.5), (s * 5.2, 13.0, -7.0), (s * 5.2, 5.0, -8.5),
                                     (s * 5.2, 1.8, -9.5)], [(0, 3.4), (0.4, 2.2), (0.8, 1.6), (1, 1.5)], eyes=3)
        leg(m, side + "_back_leg", [(s * 5.2, 24.0, 12.0), (s * 5.8, 15.0, 8.0), (s * 5.8, 8.0, 14.5),
                                    (s * 5.8, 1.8, 13.5)], [(0, 4.4), (0.35, 2.8), (0.65, 1.7), (1, 1.5)])
    geo, tex, glow, anim_path = dk.devil_paths("fox")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=243)
    anims = animations()
    save_animations(anim_path, anims)
    print("fox devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    legs = ["right_front_leg", "left_front_leg", "right_back_leg", "left_back_leg"]
    idle = Anim("idle", 3.0, loop=True)
    for i in range(9):
        t = 3.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("tail", t, (6 * math.sin(ph), 14 * math.sin(ph * 0.5), 0))
        idle.rot("head", t, (3 * math.sin(ph), 5 * math.cos(ph * 0.5), 0))
        idle.scale("body", t, (1 + 0.015 * math.sin(ph), 1 + 0.02 * math.sin(ph), 1))
    A.append(idle)
    mv = Anim("move", 0.7, loop=True)
    for i in range(9):
        t = 0.7 * i / 8
        ph = 2 * math.pi * i / 8
        s = math.sin(ph)
        mv.rot("right_front_leg", t, (35 * s, 0, 0))
        mv.rot("left_front_leg", t, (35 * math.sin(ph + 0.6), 0, 0))
        mv.rot("right_back_leg", t, (-35 * math.sin(ph + 0.3), 0, 0))
        mv.rot("left_back_leg", t, (-35 * math.sin(ph + 0.9), 0, 0))
        mv.rot("body", t, (4 * math.sin(2 * ph), 0, 0))
        mv.rot("tail", t, (-15 + 8 * math.sin(2 * ph), 0, 0))
        mv.pos("root", t, (0, 1.5 * abs(math.sin(ph)), 0))
    A.append(mv)
    # "Kon!": the head lunges, the jaws gape and snap shut
    kn = Anim("kon", 1.0)
    kn.rot("head", 0, (0, 0, 0)).rot("head", 0.3, (-20, 0, 0), "easeInQuad").rot("head", 0.45, (18, 0, 0), "easeOutQuad")
    kn.rot("head", 1.0, (0, 0, 0))
    kn.pos("head", 0.3, (0, 1, 2)).pos("head", 0.45, (0, -1, -8), "easeOutQuad").pos("head", 1.0, (0, 0, 0))
    kn.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.3, (50, 0, 0), "easeOutQuad").rot("jaw", 0.45, (-4, 0, 0), "easeInQuad")
    kn.rot("jaw", 1.0, (0, 0, 0))
    A.append(kn)
    cl = Anim("claw", 0.9)
    cl.rot("right_front_leg", 0, (0, 0, 0)).rot("right_front_leg", 0.3, (-80, 0, -20), "easeOutQuad")
    cl.rot("right_front_leg", 0.45, (20, 0, 10), "easeInQuad").rot("right_front_leg", 0.9, (0, 0, 0))
    cl.rot("body", 0.3, (-10, 0, 5)).rot("body", 0.45, (8, 0, -5)).rot("body", 0.9, (0, 0, 0))
    A.append(cl)
    po = Anim("pounce", 1.2)
    po.rot("body", 0, (0, 0, 0)).rot("body", 0.25, (15, 0, 0)).rot("body", 0.45, (-25, 0, 0), "easeOutQuad")
    po.rot("body", 0.85, (20, 0, 0), "easeInQuad").rot("body", 1.2, (0, 0, 0))
    for l in legs:
        front = "front" in l
        po.rot(l, 0.25, (30 if front else -30, 0, 0)).rot(l, 0.45, (-70 if front else 60, 0, 0))
        po.rot(l, 0.85, (-20 if front else 20, 0, 0)).rot(l, 1.2, (0, 0, 0))
    po.rot("jaw", 0.7, (40, 0, 0)).rot("jaw", 0.9, (0, 0, 0))
    A.append(po)
    dv = Anim("devour", 1.2)
    for i in range(7):
        t = 0.2 + i * 0.12
        dv.rot("jaw", t, (40 if i % 2 == 0 else 5, 0, 0))
        dv.rot("head", t, (15 + (6 if i % 2 else -6), (10 if i % 2 else -10), 0))
    dv.rot("jaw", 0, (0, 0, 0)).rot("jaw", 1.2, (0, 0, 0)).rot("head", 0, (0, 0, 0)).rot("head", 1.2, (0, 0, 0))
    A.append(dv)
    dr = Anim("drink", 1.0)
    dr.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.3, (30, 0, 0)).rot("jaw", 1.0, (0, 0, 0))
    A.append(dr)
    death = Anim("death", 1.4, loop="hold_on_last_frame")
    death.rot("root", 0, (0, 0, 0)).rot("root", 0.9, (0, 0, 85), "easeInQuad")
    death.pos("root", 0.9, (0, -2, 0))
    for l in legs:
        death.rot(l, 0.9, (0, 0, 30))
    death.rot("jaw", 0.9, (30, 0, 0))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 0.8, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("fox_front.png"), anim, "idle", 0.0, yaw=35, pitch=8, show_body=False,
                       scale=6.5, center=(0, 1.3), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("fox_side.png"), anim, "kon", 0.3, yaw=100, pitch=8, show_body=False,
                       scale=6.5, center=(0, 1.3), size=(620, 620), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("fox_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
