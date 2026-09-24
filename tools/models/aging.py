"""
The Aging Devil, a Primal Devil (part 2) - entity model (entity/devil/aging), texture atlas and GeckoLib animations.

Reference points:
  * tall, with a thin and gaunt physique: a withered aggregate of flesh with holes all over it
  * a first face that is sliced in half, and a second face that is only a mouth
  * its feet are shaped like high heels
  * it ages what it touches to dust, flattened the Chainsaw Devil with one punch, and takes people to its own realm
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
    a.add("flesh", kind="skin", color=(176, 162, 136))
    a.add("flesh_dk", kind="skin", color=(128, 110, 90))
    a.add("flesh_lt", kind="skin", color=(204, 190, 164))
    a.add("crease", kind="flesh", color=(110, 84, 74))
    a.add("hole", kind="void", color=(26, 8, 10))
    a.add("hole_rim", kind="flesh", color=(120, 60, 60))
    a.add("cut", kind="flesh", color=(150, 40, 46))
    a.add("teeth", kind="teeth", color=(222, 212, 186))
    a.add("mouth", kind="void", color=(36, 6, 10))
    a.add("lip", kind="flesh", color=(150, 96, 92))
    a.add("eye", kind="ringeye", color=(60, 50, 44), color2=(20, 14, 12), rings=1, sclera=(224, 216, 196))
    a.add("nail", kind="bone", color=(80, 70, 60))
    return a


def holes_on(bone, f, pts, size=1.4):
    """Holes in the flesh: a dark pit with a raw rim, set into the surface."""
    for (u, v, k) in pts:
        p, n, du, dv = shapes.surface_frame(f, u, v)
        bone.obox(p + n * 0.05, dv, (size * k * 1.5, size * k * 1.5, 0.35), "hole_rim", up=n)
        bone.obox(p + n * 0.2, dv, (size * k, size * k, 0.4), "hole", up=n)


def lumps_on(bone, f, count, v0, v1, rng, scale=1.0):
    """The flesh is an aggregate: withered lumps and folds stuck together all over it."""
    for _ in range(count):
        u, v = rng.uniform(0, 1), rng.uniform(v0, v1)
        p, n, du, dv = shapes.surface_frame(f, u, v)
        r = rng.uniform(0.7, 1.5) * scale
        c = p + n * (r * 0.35)
        shapes.shell(bone, shapes.ellipsoid(c, (r, r * rng.uniform(0.8, 1.6), r * 0.7)), 6, 4,
                     "flesh_dk" if rng.uniform() < 0.35 else "flesh_lt", thick=0.3)


def creases_on(bone, f, n_rows, per_row, v0, v1, rng):
    for j in range(n_rows):
        v = v0 + (v1 - v0) * (j + 0.5) / n_rows
        for i in range(per_row):
            u = (i + rng.uniform(0, 1)) / per_row
            p, n, du, dv = shapes.surface_frame(f, u % 1.0, v)
            bone.obox(p + n * 0.1, du, (0.3, rng.uniform(1.5, 3.5), 0.3), "crease", up=n)


def build():
    atlas = materials()
    m = Model("csm.aging_devil", atlas, density=1.6, seed=611)
    rng = np.random.default_rng(611)
    m.bone("root", pivot=(0, 0, 0))
    waist = m.bone("waist", parent="root", pivot=(0, 40, 0))
    body = m.bone("body", parent="waist", pivot=(0, 40, 0))

    # ---- the torso: a narrow, withered column of flesh, ribs through it, holes all over
    torso = shapes.loft(shapes.polyline([(0, 38.0, 0.5), (0, 48.0, 0.2), (0, 58.0, -0.6), (0, 66.0, 0.0)]),
                        shapes.profile((0, 3.6), (0.35, 3.2), (0.75, 5.4), (1, 4.2)),
                        shapes.profile((0, 2.8), (0.35, 2.6), (0.75, 3.4), (1, 2.6)), up=(0, 0, -1))
    shapes.shell(body, torso, 14, 12, "flesh", thick=0.45,
                 mat_fn=lambda u, v: "flesh_dk" if int(v * 12) % 4 == 0 else "flesh")
    for k in range(5):  # ribs
        y = 52.0 + k * 2.4
        for s in (-1, 1):
            body.obox((s * 2.4, y, -2.6 + 0.1 * k), (s * 1.0, -0.25, 0), (0.6, 3.0, 0.5), "flesh_lt", up=(0, 0, -1))
    holes_on(body, torso, [(0.3, 0.3, 1.0), (0.65, 0.45, 0.8), (0.12, 0.6, 1.1), (0.85, 0.2, 0.9), (0.45, 0.15, 0.7),
                           (0.55, 0.85, 0.9), (0.95, 0.7, 1.0), (0.2, 0.9, 0.6)])
    creases_on(body, torso, 5, 7, 0.1, 0.95, rng)
    lumps_on(body, torso, 22, 0.05, 0.95, rng)
    for s in (-1, 1):  # hip bones jutting under the skin
        body.obox((s * 3.2, 40.5, -1.6), (0, 1, 0.2), (1.2, 2.6, 1.0), "flesh_lt", up=(s * 0.5, 0, -1))
    # the second face on its chest: nothing but a mouth
    body.box((-3.0, 55.0, -3.9), (3.0, 57.8, -3.5), "mouth")
    body.box((-3.4, 57.8, -4.1), (3.4, 58.5, -3.4), "lip")
    body.box((-3.4, 54.3, -4.1), (3.4, 55.0, -3.4), "lip")
    for k in range(9):
        x = -2.7 + k * 0.68
        body.spike((x, 57.8, -3.85), (0, -1, -0.1), 1.2, 0.5, 0.25, "teeth", steps=2, up=(0, 0, -1))
        body.spike((x + 0.3, 55.0, -3.85), (0, 1, -0.1), 1.0, 0.45, 0.25, "teeth", steps=2, up=(0, 0, -1))

    # ---- the head: long and narrow; the face is sliced in half down the middle, the halves apart
    head = m.bone("head", parent="body", pivot=(0, 66, 0))
    look = m.bone("look", parent="head", pivot=(0, 67, 0))
    look.cylinder((0, 66.8, 0.2), (0, 1, 0), 1.6, 2.4, "flesh_dk", segments=8)  # the neck
    for s in (-1, 1):
        # each half its own bone, pulled apart and slipped out of line where the face was cut
        hb = m.bone("face_%s" % ("r" if s < 0 else "l"), parent="look", pivot=(0, 68.0, 0.3),
                    rotation=(0, 0, s * 9.0))
        dy = -1.4 if s < 0 else 0.8
        half = shapes.ellipsoid((s * 1.4, 73.0 + dy, 0.3), (2.7, 6.0, 3.6), e_lat=0.8, e_lon=0.8)
        shapes.shell(hb, half, 10, 9, "flesh", thick=0.4, u0=0.5 if s < 0 else 0.0, u1=1.0 if s < 0 else 0.5,
                     mat_fn=lambda u, v: "flesh_lt" if v > 0.7 else "flesh")
        # the cut face of each half: raw, the inside of the skull showing
        hb.box((s * 0.05 - 0.2, 67.4 + dy, -3.3), (s * 0.05 + 0.2, 78.6 + dy, 3.6), "cut")
        hb.decal((s * 2.0, 73.6 + dy, -3.35), norm((s * 0.3, 0, -1)), 1.7, 1.2, "eye")
        hb.obox((s * 0.55, 71.6 + dy, -3.55), (0, 1, 0), (0.7, 1.6, 0.6), "flesh_lt", up=(0, 0, -1))  # half a nose
        hb.obox((s * 1.3, 69.6 + dy, -3.2), (1, 0, 0), (0.25, 1.6, 0.2), "lip", up=(0, 0, -1))
        holes_on(hb, half, [(0.25 if s > 0 else 0.75, 0.55, 0.6), (0.4 if s > 0 else 0.6, 0.85, 0.5)], size=1.2)
        for k in range(4):  # strings of flesh still joining the halves
            y = 69.5 + k * 2.3
            hb.seg((s * 0.1, y + dy * 0.5, -1.0 + k * 0.6), (-s * 0.9, y - 0.6, -0.6 + k * 0.6), 0.25, 0.25, "cut")

    # ---- arms: long, thin, reaching down past the knees, with long nails
    for side, name in ((-1, "right_arm"), (1, "left_arm")):
        sh = np.array([side * 5.2, 64.0, 0.0])
        arm = m.bone(name, parent="body", pivot=tuple(sh))
        el = sh + np.array([side * 1.6, -14.0, 0.8])
        wr = el + np.array([side * 0.4, -14.0, -1.2])
        up_ = shapes.loft(shapes.polyline([sh, el]), shapes.taper(1.8, 1.3), shapes.taper(1.7, 1.2))
        lo_ = shapes.loft(shapes.polyline([el, wr]), shapes.taper(1.3, 1.0), shapes.taper(1.2, 0.9))
        shapes.shell(arm, up_, 8, 7, "flesh", thick=0.35)
        shapes.shell(arm, lo_, 8, 7, "flesh", thick=0.35)
        shapes.shell(arm, shapes.ellipsoid(el, (1.5, 1.6, 1.5)), 7, 5, "flesh_dk", thick=0.3)
        holes_on(arm, up_, [(0.3, 0.5, 0.7), (0.8, 0.2, 0.5)], size=1.0)
        holes_on(arm, lo_, [(0.7, 0.4, 0.6), (0.2, 0.75, 0.5)], size=1.0)
        lumps_on(arm, up_, 5, 0.1, 0.9, rng, scale=0.6)
        lumps_on(arm, lo_, 4, 0.1, 0.9, rng, scale=0.5)
        hand = wr + np.array([0, -1.6, 0])
        shapes.shell(arm, shapes.ellipsoid(hand, (1.4, 1.8, 0.8)), 7, 5, "flesh_dk", thick=0.3)
        for k in range(4):
            base = hand + np.array([side * (-0.9 + k * 0.6) * 0.8, -1.4, -0.2])
            d = norm((side * (k - 1.5) * 0.08, -1, -0.15))
            arm.spike(base, d, 3.2, 0.4, 0.4, "flesh", steps=3)
            arm.spike(base + d * 3.1, d, 0.9, 0.35, 0.3, "nail", steps=2)

    # ---- legs: very long and thin, ending in high heels
    for side, name in ((-1, "right_leg"), (1, "left_leg")):
        hip = np.array([side * 2.2, 39.0, 0.3])
        leg = m.bone(name, parent="root", pivot=tuple(hip))
        knee = hip + np.array([side * 0.6, -18.5, -1.0])
        ankle = np.array([side * 2.8, 4.6, 1.4])
        th = shapes.loft(shapes.polyline([hip, knee]), shapes.taper(2.4, 1.6), shapes.taper(2.3, 1.5))
        sh_ = shapes.loft(shapes.polyline([knee, ankle]), shapes.taper(1.6, 1.0), shapes.taper(1.5, 0.9))
        shapes.shell(leg, th, 9, 8, "flesh", thick=0.4)
        shapes.shell(leg, sh_, 8, 8, "flesh", thick=0.4)
        shapes.shell(leg, shapes.ellipsoid(knee, (1.9, 1.9, 1.9)), 7, 5, "flesh_dk", thick=0.3)
        holes_on(leg, th, [(0.2, 0.4, 0.9), (0.7, 0.7, 0.7)])
        holes_on(leg, sh_, [(0.5, 0.3, 0.6)], size=1.0)
        creases_on(leg, th, 3, 5, 0.1, 0.9, rng)
        lumps_on(leg, th, 7, 0.05, 0.95, rng, scale=0.7)
        lumps_on(leg, sh_, 5, 0.05, 0.9, rng, scale=0.5)
        # the foot is a high heel: arched up on its toes, a long spike of a heel under the back
        toe = np.array([side * 2.9, 0.4, -4.6])
        arch = shapes.loft(shapes.polyline([ankle, ankle + np.array([0, -2.2, -2.4]), toe]),
                           shapes.taper(1.1, 0.7), shapes.taper(0.9, 0.35), up=(0, 1, 0))
        shapes.shell(leg, arch, 8, 6, "flesh_dk", thick=0.35)
        leg.obox(toe + np.array([0, -0.1, -0.2]), (0, 0, -1), (1.5, 1.6, 0.6), "flesh_dk", up=(0, 1, 0))
        shapes.horn(leg, ankle + np.array([0, -0.4, 0.4]), (0, -1, 0.06), 4.6, 0.55, mat="nail", sections=4, around=5,
                    r1=0.15)

    geo, tex, glow, anim_path = dk.devil_paths("aging")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=613)
    anims = animations()
    save_animations(anim_path, anims)
    print("aging devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    idle = Anim("idle", 4.0, loop=True)
    for i in range(9):
        t = 4.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("body", t, (1.5 * math.sin(ph), 0, 1.2 * math.cos(ph)))
        idle.rot("head", t, (-2 * math.sin(ph), 5 * math.sin(ph * 0.5), 3 * math.cos(ph)))
        idle.rot("right_arm", t, (2 * math.sin(ph), 0, 4))
        idle.rot("left_arm", t, (-2 * math.sin(ph), 0, -4))
    A.append(idle)

    mv = Anim("move", 1.6, loop=True)
    for i in range(9):
        t = 1.6 * i / 8
        ph = 2 * math.pi * i / 8
        s = math.sin(ph)
        mv.rot("right_leg", t, (22 * s, 0, 0))
        mv.rot("left_leg", t, (-22 * s, 0, 0))
        mv.rot("right_arm", t, (-10 * s, 0, 4))
        mv.rot("left_arm", t, (10 * s, 0, -4))
        mv.rot("waist", t, (5, 4 * s, 0))
        mv.pos("root", t, (0, -1.2 * abs(math.cos(ph)), 0))
    A.append(mv)

    # Age (20 ticks): a long finger points; the prey ages on tick 10
    ag = Anim("age", 1.0)
    ag.rot("right_arm", 0, (0, 0, 4)).rot("right_arm", 0.4, (-90, 5, 0), "easeOutQuad").rot("right_arm", 0.8, (-90, 5, 0))
    ag.rot("right_arm", 1.0, (0, 0, 4))
    ag.rot("head", 0.4, (8, -10, 12)).rot("head", 1.0, (0, 0, 0))
    A.append(ag)

    # The Punch (22 ticks): wound far back, it lands on tick 12
    pu = Anim("punch", 1.1)
    pu.rot("right_arm", 0, (0, 0, 4)).rot("right_arm", 0.45, (40, 30, 20), "easeOutQuad")
    pu.rot("right_arm", 0.6, (-95, -10, 0), "easeInQuad").rot("right_arm", 0.85, (-85, 0, 0)).rot("right_arm", 1.1, (0, 0, 4))
    pu.rot("waist", 0.45, (0, 30, 0)).rot("waist", 0.6, (10, -25, 0), "easeInQuad").rot("waist", 1.1, (0, 0, 0))
    pu.rot("right_leg", 0.6, (-20, 0, 0)).rot("left_leg", 0.6, (15, 0, 0))
    pu.rot("right_leg", 1.1, (0, 0, 0)).rot("left_leg", 1.1, (0, 0, 0))
    A.append(pu)

    # Dust to Dust (26 ticks): arms slowly spread, the world around it crumbling over ticks 8-18
    du = Anim("dust", 1.3)
    for arm, s in (("right_arm", 1), ("left_arm", -1)):
        du.rot(arm, 0, (0, 0, s * 4)).rot(arm, 0.5, (-30, 0, s * 80), "easeInOutSine").rot(arm, 1.0, (-30, 0, s * 85))
        du.rot(arm, 1.3, (0, 0, s * 4))
    du.rot("head", 0.5, (-25, 0, 0)).rot("head", 1.3, (0, 0, 0))
    A.append(du)

    # The Forest by the Lake (24 ticks): its hand closes over the prey on tick 12 and it is gone
    re = Anim("realm", 1.2)
    re.rot("left_arm", 0, (0, 0, -4)).rot("left_arm", 0.4, (-110, -20, 0), "easeOutQuad")
    re.rot("left_arm", 0.6, (-70, 30, 0), "easeInQuad").rot("left_arm", 1.2, (0, 0, -4))
    re.rot("head", 0.4, (10, 15, 0)).rot("head", 1.2, (0, 0, 0))
    A.append(re)

    dr = Anim("drink", 1.0)
    dr.rot("right_arm", 0, (0, 0, 4)).rot("right_arm", 0.3, (-60, 0, 0)).rot("right_arm", 0.8, (-60, 0, 0))
    dr.rot("right_arm", 1.0, (0, 0, 4)).rot("waist", 0.3, (12, 0, 0)).rot("waist", 1.0, (0, 0, 0))
    A.append(dr)

    death = Anim("death", 2.4, loop="hold_on_last_frame")
    death.rot("waist", 0, (0, 0, 0)).rot("waist", 1.2, (60, 0, 10), "easeInQuad")
    death.pos("root", 0, (0, 0, 0)).pos("root", 1.2, (0, -30, -14), "easeInQuad")
    death.rot("right_leg", 1.2, (-70, 0, 0)).rot("left_leg", 1.2, (-60, 0, 0))
    death.scale("root", 1.4, 1.0).scale("root", 2.4, (1.0, 0.1, 1.0), "easeInQuad")  # crumbling to dust
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.2, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    bg = (160, 170, 150)
    shots = [
        preview.render(geo, tex, preview_path("aging_front.png"), anim, "idle", 0.0, yaw=20, pitch=6, show_body=False,
                       scale=6.0, center=(0, 2.7), size=(620, 760), bg=bg),
        preview.render(geo, tex, preview_path("aging_side.png"), anim, "idle", 0.0, yaw=100, pitch=6, show_body=False,
                       scale=6.0, center=(0, 2.7), size=(620, 760), bg=bg),
        preview.render(geo, tex, preview_path("aging_face.png"), anim, "idle", 0.0, yaw=-15, pitch=2,
                       show_body=False, scale=22.0, center=(0, 4.3), size=(620, 620), bg=bg),
        preview.render(geo, tex, preview_path("aging_punch.png"), anim, "punch", 0.62, yaw=60, pitch=6,
                       show_body=True, scale=5.0, center=(0, 2.7), size=(620, 760), bg=bg),
    ]
    return preview.contact_sheet(shots, preview_path("aging_sheet.png"), cols=4)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
