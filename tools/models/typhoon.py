"""
The Typhoon Devil - entity model (entity/devil/typhoon) and animations.

Reference points (manga ch. 60s):
  * a gigantic humanoid inside a swirling storm of BRAIN MATTER and entrails - not clean wind
  * the top part of its head is gone, the brain bared, and the brain is joined to the storm around it
  * its head is a BABY'S, mouth wide open, with no upper part to the face (and it carries a severed baby's leg)
  * it levels buildings by charging through them and flings cars with its wind
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
    a.add("skin", kind="skin", color=(196, 168, 160))
    a.add("skin_dk", kind="skin", color=(150, 120, 116))
    a.add("infant", kind="skin", color=(236, 206, 192))
    a.add("eye", kind="gloss", color=(20, 18, 22))
    a.add("mouth", kind="void", color=(60, 20, 26))
    a.add("brain", kind="flesh", color=(214, 150, 160))
    a.add("brain_dk", kind="flesh", color=(170, 100, 116))
    a.add("wind", kind="flesh", color=(206, 120, 132))
    a.add("wind_dk", kind="flesh", color=(150, 66, 84))
    a.add("leg", kind="skin", color=(226, 190, 176))
    a.add("blood", kind="blood", color=(126, 8, 12))
    return a


def build():
    atlas = materials()
    m = Model("csm.typhoon_devil", atlas, density=2.0, seed=231)

    root = m.bone("root", pivot=(0, 0, 0))
    waist = m.bone("waist", parent="root", pivot=(0, 46, 0))
    body = m.bone("body", parent="waist", pivot=(0, 46, 0))
    # a hulking torso, hunched forward
    torso = shapes.loft(shapes.polyline([(0, 44.0, 1.0), (0, 62.0, -1.0), (0, 80.0, 1.5), (0, 88.0, 3.0)]),
                        shapes.profile((0, 10.0), (0.35, 12.0), (0.75, 15.5), (1, 11.0)),
                        shapes.profile((0, 7.0), (0.35, 8.0), (0.75, 9.5), (1, 7.0)), up=(0, 0, -1))
    shapes.shell(body, torso, 16, 12, "skin", thick=0.5,
                 mat_fn=lambda u, v: "skin_dk" if abs(u - 0.5) < 0.2 else "skin")
    # heaving slabs of muscle: shoulders, chest
    for s_ in (-1, 1):
        shapes.shell(body, shapes.ellipsoid((s_ * 11.0, 84.0, 1.0), (8.5, 7.0, 8.5)), 10, 6, "skin", thick=0.45)
        shapes.shell(body, shapes.ellipsoid((s_ * 6.0, 74.0, -6.5), (6.5, 6.0, 4.0)), 10, 6, "skin_dk", thick=0.4)
    # head: an infant's face under a skull whose top is gone, the brain bared like a crown
    head = m.bone("head", parent="body", pivot=(0, 88, 0))
    look = m.bone("look", parent="head", pivot=(0, 90, 0))
    face = shapes.ellipsoid((0, 96.0, -1.0), (7.5, 8.0, 7.0), e_lat=0.85, e_lon=0.85)
    shapes.shell(look, face, 14, 10, "infant", v1=0.72, thick=0.45)
    for s in (-1, 1):
        c = np.array([s * 3.0, 96.5, -7.0])
        shapes.shell(look, shapes.ellipsoid(c, (2.4, 2.9, 1.2)), 8, 6, "eye", thick=0.3)
        look.cbox(c + np.array([s * 0.4, 0.6, -0.8]), (0.5, 0.5, 0.2), "wind")
        shapes.shell(look, shapes.ellipsoid((s * 4.4, 93.0, -5.2), (2.0, 1.8, 1.6)), 6, 4, "infant", thick=0.3)
    # a baby's mouth, wide open in a wail
    shapes.shell(look, shapes.ellipsoid((0, 90.6, -6.0), (4.2, 3.4, 1.6)), 10, 6, "mouth", thick=0.3)
    look.curve([np.array([4.4 * math.cos(a), 90.6 + 3.6 * math.sin(a), -6.8]) for a in np.linspace(0, 2 * math.pi, 13)],
               0.9, 0.9, 0.8, 0.8, "skin_dk")
    brain = m.bone("brain", parent="look", pivot=(0, 100, 0))
    rng = np.random.default_rng(51)
    for k in range(20):
        u = rng.uniform(-1, 1)
        a = rng.uniform(0, 2 * math.pi)
        p = np.array([math.cos(a) * 6.5 * math.sqrt(1 - u * u), 101.0 + abs(u) * 4.0, -1.0 + math.sin(a) * 6.0 *
                      math.sqrt(1 - u * u)])
        d = norm([rng.uniform(-1, 1), rng.uniform(-0.3, 0.3), rng.uniform(-1, 1)])
        frame = __import__("csmgen.geo", fromlist=["frame_from"]).frame_from(d, (0, 1, 0))
        shapes.shell(brain, shapes.ellipsoid(p, (1.8, 3.0, 1.6), frame=frame), 6, 4, "brain" if k % 2 else "brain_dk",
                     thick=0.35)
    shapes.shell(brain, shapes.ellipsoid((0, 101.0, -1.0), (7.0, 4.5, 6.5)), 12, 6, "brain_dk", v0=0.35, thick=0.4)
    # enormous arms
    for side, name in ((-1, "right_arm"), (1, "left_arm")):
        sh = np.array([side * 15.0, 84.0, 1.0])
        arm = m.bone(name, parent="body", pivot=tuple(sh))
        el = sh + np.array([side * 6.0, -24.0, -2.0])
        wr = el + np.array([side * 1.0, -26.0, -6.0])
        shapes.shell(arm, shapes.loft(shapes.polyline([sh, el, wr]), shapes.profile((0, 6.0), (0.45, 4.6), (1, 4.0)),
                                      shapes.profile((0, 5.5), (0.45, 4.4), (1, 3.8))), 10, 12, "skin", thick=0.45)
        shapes.shell(arm, shapes.ellipsoid(wr + np.array([0, -3.0, -1.0]), (4.4, 4.0, 3.8)), 10, 6, "skin_dk",
                     thick=0.4)

    # the severed baby's leg it carries in its left hand
    lg = m.bone("baby_leg", parent="left_arm", pivot=(22.0, 28.0, -8.0))
    shapes.shell(lg, shapes.loft(shapes.polyline([(22.0, 30.0, -11.0), (22.0, 22.0, -12.0), (22.0, 16.0, -11.0)]),
                                 shapes.profile((0, 1.6), (0.5, 2.0), (1, 1.3)), 1.6), 8, 8, "leg", thick=0.3)
    shapes.shell(lg, shapes.ellipsoid((22.0, 15.0, -12.4), (1.4, 1.0, 2.2)), 6, 4, "leg", thick=0.3)
    lg.cbox((22.0, 30.6, -11.0), (2.6, 0.6, 2.6), "blood")
    # legs like pillars
    for side, name in ((-1, "right_leg"), (1, "left_leg")):
        hip = np.array([side * 6.0, 46.0, 1.0])
        leg = m.bone(name, parent="root", pivot=tuple(hip))
        knee = hip + np.array([side * 1.0, -22.0, -2.0])
        foot = np.array([side * 7.5, 3.0, 0.0])
        shapes.shell(leg, shapes.loft(shapes.polyline([hip, knee, foot]), shapes.profile((0, 7.0), (0.5, 5.2), (1, 4.6)),
                                      shapes.profile((0, 6.5), (0.5, 5.0), (1, 4.4))), 10, 12, "skin", thick=0.45)
        shapes.shell(leg, shapes.ellipsoid(foot + np.array([0, -0.5, -2.5]), (5.0, 2.6, 6.5)), 10, 6, "skin_dk",
                     thick=0.4)
    # the gale: rings of wind with chunks of brain tissue caught in them
    gales = []
    for k in range(5):
        name = "gale%d" % k
        y = 12.0 + k * 20.0
        g = m.bone(name, parent="root", pivot=(0, y, 0))
        r = 28.0 - abs(k - 2) * 3.0
        for layer in range(2):
            rr = r + layer * 3.5
            for j in range(28):
                a0 = j / 28 * 2 * math.pi + layer * 0.4
                if (j + layer * 3) % 7 == 6:
                    continue
                p = np.array([math.cos(a0) * rr, y + 3.0 * math.sin(a0 * 2 + k), math.sin(a0) * rr])
                tan = np.array([-math.sin(a0), 0.15, math.cos(a0)])
                # ropes of brain matter and gut, not clean air
                g.obox(p, tan, (1.8 - layer * 0.4, rr * 0.25, 1.9 - layer * 0.4), "wind" if (j + layer) % 2 else
                       "wind_dk", up=(0, 1, 0))
        for j in range(6):
            a0 = j / 6 * 2 * math.pi + k
            p = np.array([math.cos(a0) * (r + 2.0), y + 1.5 * math.sin(j), math.sin(a0) * (r + 2.0)])
            shapes.shell(g, shapes.ellipsoid(p, (2.0, 1.6, 1.8)), 6, 4, "brain" if j % 2 else "brain_dk", thick=0.3)
        gales.append(name)
    # cords of brain running from the bared brain out into the storm
    for j in range(6):
        a0 = j / 6 * 2 * math.pi + 0.3
        top = np.array([math.cos(a0) * 4.0, 103.0, -1.0 + math.sin(a0) * 4.0])
        mid = np.array([math.cos(a0) * 14.0, 108.0, math.sin(a0) * 14.0])
        end = np.array([math.cos(a0) * 26.0, 94.0, math.sin(a0) * 26.0])
        shapes.shell(brain, shapes.loft(shapes.polyline([top, mid, end]), shapes.profile((0, 1.4), (1, 0.6)),
                                        shapes.profile((0, 1.2), (1, 0.5))), 5, 8, "brain" if j % 2 else "brain_dk",
                     thick=0.3)
    geo, tex, glow, anim_path = dk.devil_paths("typhoon")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=233)
    anims = animations(gales)
    save_animations(anim_path, anims)
    print("typhoon devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def spin(a, gales, t0, t1, speed):
    steps = max(2, int((t1 - t0) * 8))
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        for k, g in enumerate(gales):
            a.rot(g, t, (0, speed * t * (1 if k % 2 == 0 else -1) * (1 + 0.3 * k), 0))


def animations(gales):
    A = []
    idle = Anim("idle", 2.0, loop=True)
    spin(idle, gales, 0, 2.0, 180)
    for i in range(9):
        t = 2.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("body", t, (4 + 2 * math.sin(ph), 0, 0))
        idle.rot("head", t, (-3 * math.sin(ph), 3 * math.cos(ph), 0))
    A.append(idle)
    mv = Anim("move", 1.6, loop=True)
    spin(mv, gales, 0, 1.6, 360)
    for i in range(9):
        t = 1.6 * i / 8
        ph = 2 * math.pi * i / 8
        s = math.sin(ph)
        mv.rot("right_leg", t, (24 * s, 0, 0))
        mv.rot("left_leg", t, (-24 * s, 0, 0))
        mv.rot("right_arm", t, (-18 * s, 0, 4))
        mv.rot("left_arm", t, (18 * s, 0, -4))
        mv.rot("waist", t, (10, 4 * s, 0))
        mv.pos("root", t, (0, -1.5 * abs(math.cos(ph)), 0))
    A.append(mv)
    ch = Anim("charge", 1.5)
    ch.rot("waist", 0, (0, 0, 0)).rot("waist", 0.3, (35, 0, 0), "easeOutQuad").rot("waist", 1.3, (35, 0, 0))
    ch.rot("waist", 1.5, (0, 0, 0))
    for side, s in (("right_arm", 1), ("left_arm", -1)):
        ch.rot(side, 0.3, (40, 0, s * 20)).rot(side, 1.3, (40, 0, s * 20)).rot(side, 1.5, (0, 0, 0))
    for i in range(13):
        t = 0.3 + i * 0.08
        sgn = 1 if i % 2 else -1
        ch.rot("right_leg", t, (40 * sgn, 0, 0)).rot("left_leg", t, (-40 * sgn, 0, 0))
    spin(ch, gales, 0, 1.5, 720)
    A.append(ch)
    gl = Anim("gale", 1.2)
    for side, s in (("right_arm", 1), ("left_arm", -1)):
        gl.rot(side, 0, (0, 0, 0)).rot(side, 0.4, (-40, s * -60, s * 30), "easeInQuad")
        gl.rot(side, 0.6, (-80, s * 30, s * 10), "easeOutQuad").rot(side, 1.2, (0, 0, 0))
    spin(gl, gales, 0, 1.2, 900)
    for g in gales:
        gl.scale(g, 0, 1.0).scale(g, 0.6, 1.4).scale(g, 1.2, 1.0)
    A.append(gl)
    tn = Anim("tornado", 4.0)
    spin(tn, gales, 0, 4.0, 1080)
    for g in gales:
        tn.scale(g, 0, 1.0).scale(g, 0.5, (1.6, 1.3, 1.6), "easeOutQuad").scale(g, 3.5, (1.6, 1.3, 1.6))
        tn.scale(g, 4.0, 1.0)
    for side, s in (("right_arm", 1), ("left_arm", -1)):
        tn.rot(side, 0.5, (0, 0, s * 80)).rot(side, 3.5, (0, 0, s * 80)).rot(side, 4.0, (0, 0, 0))
    tn.rot("body", 0, (0, 0, 0)).rot("body", 3.5, (0, 720, 0)).rot("body", 4.0, (0, 720, 0))
    A.append(tn)
    hu = Anim("hurl", 1.3)
    hu.rot("right_arm", 0, (0, 0, 0)).rot("right_arm", 0.5, (-170, 0, 20), "easeInOutSine")
    hu.rot("right_arm", 0.75, (-50, 0, 10), "easeOutQuad").rot("right_arm", 1.3, (0, 0, 0))
    hu.rot("waist", 0.5, (-12, 20, 0)).rot("waist", 0.75, (15, -25, 0)).rot("waist", 1.3, (0, 0, 0))
    spin(hu, gales, 0, 1.3, 360)
    A.append(hu)
    A.append(Anim("drink", 1.0))
    death = Anim("death", 2.0, loop="hold_on_last_frame")
    death.rot("waist", 0, (0, 0, 0)).rot("waist", 1.2, (80, 0, 0), "easeInQuad")
    death.pos("root", 0, (0, 0, 0)).pos("root", 1.2, (0, -24, -16), "easeInQuad")
    for g in gales:
        death.scale(g, 0, 1.0).scale(g, 1.0, 0.1)
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.1))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("typhoon_front.png"), anim, "idle", 0.0, yaw=20, pitch=6,
                       show_body=False, scale=2.8, center=(0, 3.4), size=(620, 760), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("typhoon_side.png"), anim, "idle", 0.0, yaw=90, pitch=6,
                       show_body=False, scale=2.8, center=(0, 3.4), size=(620, 760), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("typhoon_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
