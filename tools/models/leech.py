"""
The Leech Devil - entity model (entity/devil/leech), texture atlas and GeckoLib animations.

Reference points (manga ch. 5 / anime ep. 3):
  * a large, wrinkled body of slimy, segmented, blackish-purple leech flesh standing on four legs
  * a LONG NECK ending in a head that is nothing but a HUMAN MOUTH: plump lips, blocky teeth - and greasy long
    black hair
  * two boneless tentacle arms tipped with round sucking orifices like a leech's
  * three pairs of udder-like glands
  * it drinks blood, and stabs with a long piercing tongue
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
    a.add("flesh", kind="gloss", color=(62, 44, 68))
    a.add("flesh_dk", kind="gloss", color=(44, 30, 50))
    a.add("crease", kind="skin", color=(26, 18, 30))
    a.add("pale", kind="gloss", color=(70, 52, 76))
    a.add("lip", kind="flesh", color=(196, 110, 120))
    a.add("spit", kind="gloss", color=(220, 220, 230))
    a.add("teeth", kind="teeth", color=(236, 228, 206))
    a.add("mouth", kind="void", color=(40, 8, 16))
    a.add("gum", kind="flesh", color=(150, 60, 76))
    a.add("tongue", kind="flesh", color=(176, 64, 84))
    a.add("hair", kind="fiber", color=(18, 16, 20))
    a.add("sucker", kind="flesh", color=(190, 120, 130))
    a.add("udder", kind="skin", color=(196, 150, 150))
    a.add("blood", kind="blood", color=(126, 8, 12))
    return a


BODY_C = np.array([0.0, 26.0, 3.0])
BODY_R = (11.0, 9.5, 13.0)


def body(m):
    root = m.bone("root", pivot=(0, 0, 0))
    b = m.bone("body", parent="root", pivot=(0, 22, 2))
    # a large, wrinkled, segmented bulk of leech flesh
    f = shapes.ellipsoid(BODY_C, BODY_R, e_lat=0.9, e_lon=0.85)
    shapes.shell(b, f, 18, 14, "flesh", thick=0.5,
                 mat_fn=lambda u, v: "flesh_dk" if v < 0.3 or int(v * 14) % 3 == 0 else "flesh")
    # segment rings and creases wrapping round it
    for k in range(7):
        v = 0.2 + k * 0.1
        pts = [np.asarray(f(u, v)) * 1.0 for u in np.linspace(0, 1, 19)]
        b.curve(pts, 0.55, 0.55, 0.4, 0.4, "crease")
    # three pairs of udder-like glands hanging under it
    for k, z in enumerate((-4.0, 2.0, 8.0)):
        for sx in (-1, 1):
            c = np.array([sx * 3.6, 16.6, z])
            shapes.shell(b, shapes.ellipsoid(c, (2.1, 2.5, 2.1)), 8, 6, "udder", thick=0.35)
            shapes.horn(b, c + np.array([0, -2.3, 0]), (0, -1, 0), 1.3, 0.6, mat="sucker", sections=2, around=5,
                        r1=0.3)
    # a long neck of the same segmented flesh, rising and reaching forward
    look = m.bone("look", parent="body", pivot=(0, 33, -6))
    neck_path = shapes.polyline([(0, 32.0, -5.0), (0, 38.0, -10.0), (0, 44.0, -14.0), (0, 46.5, -18.0)])
    neck = shapes.loft(neck_path, shapes.profile((0, 5.2), (0.5, 3.8), (1, 3.6)),
                       shapes.profile((0, 4.8), (0.5, 3.6), (1, 3.4)), up=(0, 1, 0))
    shapes.shell(look, neck, 12, 12, "flesh", thick=0.4,
                 mat_fn=lambda u, v: "crease" if int(v * 12) % 3 == 1 else "flesh")
    # the head is nothing but a human mouth: plump lips round blocky teeth, a dark throat behind
    mc = np.array([0, 46.5, -19.2])
    shapes.shell(look, shapes.ellipsoid(mc + np.array([0, 0, 1.4]), (3.4, 3.0, 1.6)), 10, 6, "mouth", thick=0.3)
    upper = shapes.loft(shapes.polyline([mc + [-4.2, 0.6, 0.6], mc + [0, 2.6, -0.6], mc + [4.2, 0.6, 0.6]]), 1.4, 1.2,
                        up=(0, 1, 0))
    shapes.shell(look, upper, 8, 10, "lip", thick=0.4)
    for k in range(6):
        x = -2.5 + k * 1.0
        look.obox((x, mc[1] + 1.0, mc[2] - 0.2), (0, -1, 0), (0.9, 1.4, 0.7), "teeth", up=(0, 0, -1))
    jaw = m.bone("jaw", parent="look", pivot=tuple(mc + np.array([0, -0.4, 2.2])))
    lower = shapes.loft(shapes.polyline([mc + [-4.2, -0.6, 0.6], mc + [0, -2.8, -0.6], mc + [4.2, -0.6, 0.6]]), 1.5,
                        1.3, up=(0, 1, 0))
    shapes.shell(jaw, lower, 8, 10, "lip", thick=0.4)
    for k in range(6):
        x = -2.5 + k * 1.0
        jaw.obox((x, mc[1] - 1.1, mc[2] - 0.1), (0, 1, 0), (0.9, 1.3, 0.7), "teeth", up=(0, 0, -1))
    # drool
    shapes.horn(jaw, mc + np.array([1.4, -2.6, -0.6]), (0, -1, 0), 3.0, 0.35, mat="spit", sections=2, around=4,
                r1=0.12)
    # greasy long black hair from the top and back of the head, hanging over the neck
    for k in range(18):
        a = math.radians(-100 + k * 200 / 17)
        top = mc + np.array([math.sin(a) * 3.2, 2.6 + math.cos(a) * 0.4, 3.0 + math.cos(a) * 2.4])
        end = top + np.array([math.sin(a) * 2.5, -16.0 - (k % 4) * 2.0, 6.0 + math.cos(a) * 1.5])
        mid = top + np.array([math.sin(a) * 2.0, 0.5, 3.0])
        shapes.shell(look, shapes.loft(shapes.polyline([top, mid, end]), shapes.profile((0, 1.1), (1, 0.3)), 0.35,
                                       up=(math.sin(a), 0, math.cos(a))), 4, 7, "hair", thick=0.3)
    # the piercing tongue, curled in the mouth until it stabs out
    t = m.bone("fx_tongue_mouth", parent="look", pivot=tuple(mc))
    tongue = shapes.loft(shapes.polyline([mc + [0, 0, 1.0], mc + [0, 0.3, -10.0], mc + [0, 0, -22.0]]),
                         shapes.profile((0, 1.4), (0.7, 0.9), (1, 0.08)), shapes.profile((0, 0.8), (1, 0.08)),
                         up=(0, 1, 0))
    shapes.shell(t, tongue, 8, 12, "tongue", thick=0.35)
    return root, b


def tentacle(m, side):
    s = -1 if side == "right" else 1
    root = np.array([s * 10.0, 30.0, -4.0])
    pts = [root, root + np.array([s * 5.0, -1.0, -3.0]), root + np.array([s * 8.0, -6.0, -6.0]),
           root + np.array([s * 8.5, -13.0, -8.0]), root + np.array([s * 7.0, -18.0, -10.0])]
    names = []
    parent = "body"
    for k in range(4):
        name = "%s_tentacle%d" % (side, k)
        b = m.bone(name, parent=parent, pivot=tuple(pts[k]))
        r0 = 2.2 * (1 - k / 4.5)
        r1 = 2.2 * (1 - (k + 1) / 4.5)
        seg = shapes.loft(shapes.polyline([pts[k], pts[k + 1]]), shapes.profile((0, r0), (1, max(r1, 0.4))),
                          shapes.profile((0, r0), (1, max(r1, 0.4))))
        shapes.shell(b, seg, 8, 4, "flesh", thick=0.35)
        # suckers down the inside of the arm
        for j in range(3):
            q = pts[k] + (pts[k + 1] - pts[k]) * ((j + 0.5) / 3)
            inward = norm(np.array([-s * 1.0, -0.3, -0.5]))
            b.cylinder(q + inward * max(r0 * 0.9, 0.5), inward, max(r0 * 0.35, 0.3), 0.3, "sucker", segments=8)
        if k == 3:
            # the tip: a round sucking orifice like a leech's
            d = norm(pts[4] - pts[3])
            b.ring(pts[4], d, 1.0, 0.45, 0.5, "sucker", count=10)
            b.cylinder(pts[4] - d * 0.1, d, 0.7, 0.3, "mouth", segments=8)
        names.append(name)
        parent = name
    return names


def leg(m, name, hip, foot):
    hip = np.array(hip, dtype=float)
    foot = np.array(foot, dtype=float)
    knee = (hip + foot) / 2 + np.array([np.sign(hip[0]) * 1.5, 0, -1.5])
    b = m.bone(name, parent="root", pivot=tuple(hip))
    f = shapes.loft(shapes.polyline([hip, knee, foot]), shapes.profile((0, 3.6), (0.5, 2.9), (1, 2.5)),
                    shapes.profile((0, 3.2), (0.5, 2.7), (1, 2.4)))
    shapes.shell(b, f, 10, 8, "pale", thick=0.4)
    shapes.shell(b, shapes.ellipsoid(foot + np.array([0, -0.4, -1.2]), (2.6, 1.2, 3.2)), 8, 5, "flesh_dk", thick=0.35)


def build():
    atlas = materials()
    m = Model("csm.leech_devil", atlas, density=2.0, seed=161)
    body(m)
    tents = tentacle(m, "right") + tentacle(m, "left")
    # squat: the whole bulk sits low on short legs
    for bone in m.bones:
        if bone.name != "root":
            bone.offset((0, -4.0, 0))
    for side, x in (("right", -6.5), ("left", 6.5)):
        leg(m, side + "_front_leg", (x, 15.0, -5.0), (x * 1.3, 1.2, -7.5))
        leg(m, side + "_back_leg", (x, 15.0, 8.0), (x * 1.3, 1.2, 10.0))
    geo, tex, glow, anim_path = dk.devil_paths("leech")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=163)
    anims = animations(tents)
    save_animations(anim_path, anims)
    print("leech devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def tentacle_wave(a, t0, t1, amp, freq, curl=0.0):
    steps = max(2, int((t1 - t0) * 10))
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        for side, s in (("right", 1), ("left", -1)):
            for k in range(4):
                ph = 2 * math.pi * freq * t - k * 0.7
                a.rot("%s_tentacle%d" % (side, k), t, (amp * math.sin(ph) + curl * k, 0, s * amp * 0.6 * math.cos(ph)))


def walk_legs(a, length, amp):
    for i in range(9):
        t = length * i / 8
        ph = 2 * math.pi * i / 8
        a.rot("right_front_leg", t, (amp * math.sin(ph), 0, 0))
        a.rot("left_back_leg", t, (amp * math.sin(ph), 0, 0))
        a.rot("left_front_leg", t, (-amp * math.sin(ph), 0, 0))
        a.rot("right_back_leg", t, (-amp * math.sin(ph), 0, 0))
        a.pos("root", t, (0, -0.6 * abs(math.cos(ph)), 0))
        a.rot("body", t, (0, 0, 3 * math.sin(ph)))


def animations(tents):
    A = []
    idle = Anim("idle", 3.0, loop=True)
    tentacle_wave(idle, 0, 3.0, 8, 1 / 3.0)
    for i in range(7):
        t = 3.0 * i / 6
        idle.scale("body", t, (1 + 0.02 * math.sin(2 * math.pi * i / 6), 1 - 0.02 * math.sin(2 * math.pi * i / 6), 1))
        idle.rot("jaw", t, (4 + 4 * math.sin(2 * math.pi * i / 6), 0, 0))
    A.append(idle)
    mv = Anim("move", 1.2, loop=True)
    walk_legs(mv, 1.2, 24)
    tentacle_wave(mv, 0, 1.2, 12, 1 / 1.2)
    A.append(mv)

    tg = Anim("tongue", 0.9)
    tg.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.25, (30, 0, 0), "easeOutQuad").rot("jaw", 0.7, (30, 0, 0))
    tg.rot("jaw", 0.9, (0, 0, 0))
    tg.scale("fx_tongue_mouth", 0, (1, 1, 0.05)).scale("fx_tongue_mouth", 0.35, (1, 1, 0.05))
    tg.scale("fx_tongue_mouth", 0.42, (1, 1, 1.1), "easeOutQuad").scale("fx_tongue_mouth", 0.6, (1, 1, 1.0))
    tg.scale("fx_tongue_mouth", 0.85, (1, 1, 0.05), "easeInQuad")
    tg.rot("body", 0.3, (-6, 0, 0)).rot("body", 0.42, (6, 0, 0)).rot("body", 0.9, (0, 0, 0))
    A.append(tg)

    gr = Anim("grab", 1.2)
    for side, s in (("right", 1), ("left", -1)):
        for k in range(4):
            b = "%s_tentacle%d" % (side, k)
            gr.rot(b, 0, (0, 0, 0)).rot(b, 0.3, (-25 - 8 * k, s * -20, s * 25), "easeInQuad")
            gr.rot(b, 0.45, (-70 + 10 * k, s * 25, s * -10), "easeOutQuad")
            gr.rot(b, 0.8, (30 + 12 * k, s * 10, s * -20), "easeInOutQuad").rot(b, 1.2, (0, 0, 0))
    A.append(gr)

    dv = Anim("devour", 0.8)
    dv.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.25, (45, 0, 0), "easeOutQuad").rot("jaw", 0.4, (-4, 0, 0), "easeInQuad")
    dv.rot("jaw", 0.8, (0, 0, 0))
    dv.rot("body", 0, (0, 0, 0)).rot("body", 0.25, (-12, 0, 0)).rot("body", 0.4, (14, 0, 0), "easeInQuad")
    dv.rot("body", 0.8, (0, 0, 0))
    A.append(dv)

    dr = Anim("drain", 2.0)
    for i in range(11):
        t = 2.0 * i / 10
        dr.rot("jaw", t, (20 + 10 * math.sin(i * 1.7), 0, 0))
        dr.scale("body", t, (1 + 0.04 * math.sin(i * 1.3), 1 + 0.03 * math.cos(i * 1.3), 1))
    tentacle_wave(dr, 0, 2.0, 18, 1.5, curl=12)
    A.append(dr)
    drink = Anim("drink", 1.0)
    drink.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.3, (25, 0, 0)).rot("jaw", 1.0, (0, 0, 0))
    A.append(drink)

    death = Anim("death", 1.3, loop="hold_on_last_frame")
    for side in ("right", "left"):
        death.rot(side + "_front_leg", 0.5, (-60, 0, 0), "easeInQuad")
        death.rot(side + "_back_leg", 0.5, (50, 0, 0), "easeInQuad")
    death.pos("root", 0, (0, 0, 0)).pos("root", 0.6, (0, -8, 0), "easeInQuad")
    death.rot("body", 0.6, (8, 0, 12)).rot("jaw", 0.6, (35, 0, 0))
    tentacle_wave(death, 0, 0.6, 30, 3)
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 0.8, from_scale=0.25))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("leech_front.png"), anim, "idle", 0.3, yaw=20, pitch=8, show_body=False,
                       scale=8, center=(0, 1.3), size=(620, 620)),
        preview.render(geo, tex, preview_path("leech_side.png"), anim, "idle", 0.3, yaw=110, pitch=8, show_body=False,
                       scale=8, center=(0, 1.3), size=(620, 620)),
        preview.render(geo, tex, preview_path("leech_tongue.png"), anim, "tongue", 0.5, yaw=50, pitch=8,
                       show_body=False, scale=6.5, center=(0, 1.3), size=(620, 620)),
        preview.render(geo, tex, preview_path("leech_back.png"), anim, "grab", 0.45, yaw=200, pitch=18,
                       show_body=False, scale=8, center=(0, 1.3), size=(620, 620)),
    ]
    return preview.contact_sheet(shots, preview_path("leech_sheet.png"), cols=4)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
