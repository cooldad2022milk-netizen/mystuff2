"""
The Leech Devil - entity model (entity/devil/leech), texture atlas and GeckoLib animations.

Reference points:
  * a faceless giant mouth full of squarish teeth set in a creased bulk that stands on four legs
  * tentacle arms lined with suckers, long black hair, udder-like glands hanging underneath
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
    a.add("flesh", kind="skin", color=(104, 84, 92))
    a.add("flesh_dk", kind="skin", color=(72, 56, 64))
    a.add("crease", kind="skin", color=(44, 32, 40))
    a.add("pale", kind="skin", color=(170, 146, 150))
    a.add("teeth", kind="teeth", color=(236, 228, 206))
    a.add("mouth", kind="void", color=(40, 8, 16))
    a.add("gum", kind="flesh", color=(150, 60, 76))
    a.add("tongue", kind="flesh", color=(176, 64, 84))
    a.add("hair", kind="fiber", color=(18, 16, 20))
    a.add("sucker", kind="flesh", color=(190, 120, 130))
    a.add("udder", kind="skin", color=(196, 150, 150))
    a.add("blood", kind="blood", color=(126, 8, 12))
    return a


BODY_C = np.array([0.0, 27.0, 1.5])
BODY_R = (11.5, 11.0, 13.0)


def body(m):
    root = m.bone("root", pivot=(0, 0, 0))
    b = m.bone("body", parent="root", pivot=(0, 22, 2))
    look = m.bone("look", parent="body", pivot=(0, 26, -8))
    f = shapes.ellipsoid(BODY_C, BODY_R, e_lat=0.9, e_lon=0.85)
    # the front of the bulk is one enormous mouth: leave the maw open
    maw = lambda u, v: (u < 0.13 or u > 0.87) and 0.28 < v < 0.64
    shapes.shell(b, f, 18, 14, "flesh", skip=maw, thick=0.5,
                 mat_fn=lambda u, v: "flesh_dk" if v < 0.3 else "flesh")
    # deep creases wrapping round the bulk
    rng = np.random.default_rng(3)
    for k in range(11):
        u0 = rng.uniform(0.15, 0.85)
        v0 = rng.uniform(0.35, 0.95)
        pts = []
        for i in range(6):
            p, n, du, dv = shapes.surface_frame(f, (u0 + i * 0.03) % 1.0, min(0.98, v0 + 0.05 * math.sin(i + k)))
            pts.append(p + n * 0.1)
        b.curve(pts, 0.5, 0.25, 0.35, 0.2, "crease")
    # the maw: dark cavity, gums, and rows of big squarish teeth
    shapes.shell(look, shapes.ellipsoid(BODY_C + np.array([0, -0.5, -4.0]), (7.2, 5.8, 8.0)), 12, 8, "mouth",
                 u0=-0.2, u1=0.2, thick=0.4)
    cz = BODY_C[2] - BODY_R[2]
    for k in range(10):
        ph = math.radians(-66 + 132 * (k + 0.5) / 10)
        x = 7.8 * math.sin(ph)
        z = cz + 3.2 * (1 - math.cos(ph)) + 0.6
        look.obox((x, 29.4, z), (0, -1, 0), (1.35, 2.2, 1.1), "teeth", up=(math.sin(ph), 0, -math.cos(ph)))
    look.ring((0, 30.6, cz + 2.4), (0, 1, 0), 7.2, 0.9, 1.3, "gum", count=18)
    jaw = m.bone("jaw", parent="look", pivot=(0, 25.0, 6.0))
    for k in range(9):
        ph = math.radians(-60 + 120 * (k + 0.5) / 9)
        x = 7.0 * math.sin(ph)
        z = cz + 3.0 * (1 - math.cos(ph)) + 0.8
        jaw.obox((x, 23.4, z), (0, 1, 0), (1.3, 2.0, 1.05), "teeth", up=(math.sin(ph), 0, -math.cos(ph)))
    lip = shapes.loft(shapes.polyline([(-7.8, 21.8, cz + 3.6), (0, 21.2, cz + 0.4), (7.8, 21.8, cz + 3.6)]), 1.5, 1.2,
                      up=(0, 1, 0))
    shapes.shell(jaw, lip, 8, 10, "flesh_dk", thick=0.4)
    jaw.ring((0, 22.2, cz + 2.4), (0, 1, 0), 6.6, 0.8, 1.0, "gum", count=16)
    # the piercing tongue, coiled in the mouth until it stabs out
    t = m.bone("fx_tongue_mouth", parent="look", pivot=(0, 26.0, cz + 2.0))
    tongue = shapes.loft(shapes.polyline([(0, 26.0, cz + 3.0), (0, 26.4, cz - 8.0), (0, 26.0, cz - 20.0)]),
                         shapes.profile((0, 1.6), (0.7, 1.0), (1, 0.08)), shapes.profile((0, 0.9), (1, 0.08)),
                         up=(0, 1, 0))
    shapes.shell(t, tongue, 8, 12, "tongue", thick=0.35)
    # long black hair falling from the top of the bulk down its back
    for k in range(16):
        a = math.radians(-70 + k * 140 / 15)
        top = BODY_C + np.array([math.sin(a) * 6.5, BODY_R[1] - 1.2, 2.0 + math.cos(a) * 2.0])
        end = top + np.array([math.sin(a) * 6.0, -24.0 + (k % 3) * 2.0, 10.0])
        mid = top + np.array([math.sin(a) * 5.0, 1.0, 7.0])
        shapes.shell(b, shapes.loft(shapes.polyline([top, mid, end]), shapes.profile((0, 1.2), (1, 0.3)), 0.4,
                                    up=(0, 0, 1)), 4, 8, "hair", thick=0.3)
    # udder-like glands under the belly
    for k, (x, z) in enumerate(((-3.5, 2.0), (3.5, 2.0), (-2.0, 6.0), (2.0, 6.0))):
        c = np.array([x, 16.6, z])
        shapes.shell(b, shapes.ellipsoid(c, (2.2, 2.6, 2.2)), 8, 6, "udder", thick=0.35)
        shapes.horn(b, c + np.array([0, -2.4, 0]), (0, -1, 0), 1.4, 0.6, mat="sucker", sections=2, around=6, r1=0.3)
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
