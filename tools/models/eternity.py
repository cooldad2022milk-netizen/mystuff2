"""
The Eternity Devil - entity model (entity/devil/eternity), texture atlas and GeckoLib animations.

Reference points:
  * a figure-eight (infinity-shaped) knot of flesh - the number 8 - with an eye and a mouth on each loop and two
    more mouths where the loops cross
  * inside its trap it is a tide of arms and heads; it heaves along on a slug-like foot
  * it loops a floor of a building into infinity (the clocks stuck at 8:18) and regenerates endlessly
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
    a.add("flesh", kind="flesh", color=(196, 140, 124))
    a.add("flesh_dk", kind="flesh", color=(150, 96, 88))
    a.add("skin", kind="skin", color=(214, 170, 150))
    a.add("skin_dk", kind="skin", color=(170, 124, 110))
    a.add("eye", kind="bone", color=(238, 232, 214))
    a.add("iris", kind="skin", color=(60, 40, 30))
    a.add("pupil", kind="void", color=(8, 6, 6))
    a.add("mouth", kind="void", color=(50, 10, 16))
    a.add("teeth", kind="teeth", color=(236, 226, 200))
    a.add("hair", kind="fiber", color=(40, 30, 26))
    a.add("foot", kind="skin", color=(170, 120, 110))
    return a


def loop_surface(center, R, r, tilt=0.0):
    """One loop of the figure eight: a torus-like ring of flesh (major radius R, tube radius r) standing upright."""
    c = np.asarray(center, dtype=float)

    def f(u, v):
        a = u * 2 * math.pi          # around the tube
        b = v * 2 * math.pi          # around the ring
        rr = R + r * math.cos(a) * (1 + 0.12 * math.sin(3 * b))
        p = np.array([rr * math.cos(b), rr * math.sin(b), r * math.sin(a)])
        ct, st = math.cos(tilt), math.sin(tilt)
        p = np.array([p[0], p[1] * ct - p[2] * st, p[1] * st + p[2] * ct])
        return c + p
    return f


def build():
    atlas = materials()
    m = Model("csm.eternity_devil", atlas, density=2.0, seed=201)
    root = m.bone("root", pivot=(0, 0, 0))
    body = m.bone("body", parent="root", pivot=(0, 10, 0))
    look = m.bone("look", parent="body", pivot=(0, 34, 0))
    loops = []
    for side in (-1, 1):
        name = "loop_" + ("right" if side < 0 else "left")
        lb = m.bone(name, parent="body", pivot=(side * 11.0, 32.0, 0))
        f = loop_surface((side * 11.0, 32.0, 0), 11.5, 5.2, tilt=0.15 * side)
        shapes.shell(lb, f, 10, 26, "flesh", thick=0.55,
                     mat_fn=lambda u, v: "flesh_dk" if (0.35 < u < 0.65) else "flesh")
        # an eye and a mouth on each loop (on the outer front)

        ec = np.array([side * 18.0, 42.0, -5.0])
        shapes.shell(look, shapes.ellipsoid(ec, (3.2, 3.2, 2.4)), 12, 8, "eye", thick=0.35)
        look.cylinder(ec + np.array([0, 0, -2.3]), (0, 0, -1), 1.8, 0.3, "iris", segments=12)
        look.cylinder(ec + np.array([0, 0, -2.5]), (0, 0, -1), 0.8, 0.2, "pupil", segments=10)
        mc = np.array([side * 18.0, 22.0, -5.0])
        mb = m.bone(name + "_mouth", parent=name, pivot=tuple(mc))
        shapes.shell(mb, shapes.ellipsoid(mc, (4.2, 2.8, 2.2)), 10, 6, "mouth", thick=0.35)
        for k in range(7):
            x = mc[0] - 3.3 + k * 1.1
            mb.spike((x, mc[1] + 2.2, mc[2] - 1.5), (0, -1, -0.1), 1.6, 0.8, 0.4, "teeth", steps=3)
            mb.spike((x + 0.5, mc[1] - 2.2, mc[2] - 1.4), (0, 1, -0.1), 1.4, 0.7, 0.4, "teeth", steps=3)
        loops.append(name)

    # the knot in the middle where the loops cross - with two more mouths on it, one above the other
    shapes.shell(body, shapes.ellipsoid((0, 32.0, 0), (6.5, 8.0, 6.5)), 12, 10, "flesh_dk", thick=0.5)
    for k, y in enumerate((36.2, 27.4)):
        mc = np.array([0, y, -5.6])
        mb = m.bone("knot_mouth%d" % k, parent="body", pivot=tuple(mc))
        shapes.shell(mb, shapes.ellipsoid(mc, (3.4, 2.0, 1.8)), 10, 6, "mouth", thick=0.35)
        for j in range(6):
            x = -2.6 + j * 1.05
            mb.spike((x, y + 1.6, mc[2] - 1.2), (0, -1, -0.1), 1.3, 0.7, 0.35, "teeth", steps=3)
            mb.spike((x + 0.5, y - 1.6, mc[2] - 1.1), (0, 1, -0.1), 1.1, 0.6, 0.35, "teeth", steps=3)
    # a tide of arms and heads heaving out of the flesh
    rng = np.random.default_rng(23)
    arms = []
    for k in range(10):
        side = -1 if k % 2 else 1
        b = rng.uniform(0, 2 * math.pi)
        base = np.array([side * 11.0 + math.cos(b) * 13.5, 32.0 + math.sin(b) * 13.5, rng.uniform(-3, 3)])
        out = norm(np.array([math.cos(b), math.sin(b), rng.uniform(-0.6, 0.2)]))
        name = "arm%d" % k
        ab = m.bone(name, parent="body", pivot=tuple(base))
        elbow = base + out * 5.0 + np.array([0, 1.5, 0])
        hand = elbow + norm(out + np.array([0, -0.8, -0.3])) * 4.5
        shapes.shell(ab, shapes.loft(shapes.polyline([base, elbow, hand]), shapes.profile((0, 1.3), (1, 0.9)), 1.1),
                     6, 8, "skin", thick=0.3)
        shapes.shell(ab, shapes.ellipsoid(hand, (1.1, 1.0, 1.1)), 6, 4, "skin_dk", thick=0.3)
        arms.append(name)
    for k in range(6):
        side = -1 if k % 2 else 1
        b = rng.uniform(0.3, 2.8)
        c = np.array([side * 11.0 + math.cos(b) * 15.0, 32.0 + math.sin(b) * 15.0, rng.uniform(-2, 1)])
        shapes.shell(body, shapes.ellipsoid(c, (2.4, 2.8, 2.4)), 8, 6, "skin", thick=0.3)
        body.box(c + np.array([-1.0, 0.2, -2.5]), c + np.array([1.0, 0.7, -2.2]), "pupil")
        body.box(c + np.array([-0.6, -1.3, -2.4]), c + np.array([0.6, -0.8, -2.1]), "mouth")
        shapes.shell(body, shapes.ellipsoid(c + np.array([0, 1.2, 0.4]), (2.5, 1.8, 2.5)), 8, 5, "hair", v0=0.45,
                     thick=0.3)
    # the knot sits low on its foot
    for bone in m.bones:
        if bone.name not in ("root",):
            bone.offset((0, -7.0, 0))
    # the slug-like foot it slides along on
    foot = shapes.loft(shapes.polyline([(0, 2.0, 12.0), (0, 3.5, 2.0), (0, 3.0, -9.0)]),
                       shapes.profile((0, 5.0), (0.4, 14.0), (0.85, 13.0), (1, 6.0)),
                       shapes.profile((0, 2.0), (0.5, 3.6), (1, 2.2)), up=(0, 1, 0))
    fb = m.bone("foot", parent="root", pivot=(0, 3, 0))
    shapes.shell(fb, foot, 14, 10, "foot", thick=0.45)
    shapes.shell(fb, shapes.loft(shapes.polyline([(0, 3.0, 0), (0, 16.0, 0)]), shapes.profile((0, 12.0), (1, 7.0)),
                                 shapes.profile((0, 5.0), (1, 5.5)), up=(0, 0, -1)), 14, 5, "flesh_dk", thick=0.45)
    geo, tex, glow, anim_path = dk.devil_paths("eternity")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=203)
    anims = animations(loops, arms)
    save_animations(anim_path, anims)
    print("eternity devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def writhe(a, arms, t0, t1, amp, freq):
    steps = max(2, int((t1 - t0) * 8))
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        for k, b in enumerate(arms):
            ph = 2 * math.pi * freq * t + k * 0.9
            a.rot(b, t, (amp * math.sin(ph), amp * 0.6 * math.cos(ph * 1.3), amp * 0.5 * math.sin(ph * 0.7)))


def animations(loops, arms):
    A = []
    idle = Anim("idle", 4.0, loop=True)
    writhe(idle, arms, 0, 4.0, 14, 0.5)
    for i in range(9):
        t = 4.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot(loops[0], t, (0, 0, 4 * math.sin(ph)))
        idle.rot(loops[1], t, (0, 0, -4 * math.sin(ph)))
        idle.scale("body", t, (1 + 0.02 * math.sin(ph), 1 - 0.02 * math.sin(ph), 1))
        idle.rot(loops[0] + "_mouth", t, (6 + 6 * math.sin(ph * 2), 0, 0))
        idle.rot(loops[1] + "_mouth", t, (6 + 6 * math.cos(ph * 2), 0, 0))
    A.append(idle)
    mv = Anim("move", 2.0, loop=True)
    writhe(mv, arms, 0, 2.0, 20, 1.0)
    for i in range(9):
        t = 2.0 * i / 8
        ph = 2 * math.pi * i / 8
        mv.scale("foot", t, (1 - 0.06 * math.sin(ph), 1, 1 + 0.1 * math.sin(ph)))
        mv.rot("body", t, (6 + 3 * math.sin(ph), 0, 3 * math.cos(ph)))
    A.append(mv)
    lp = Anim("loop", 2.0)
    for i in range(17):
        t = 2.0 * i / 16
        lp.rot(loops[0], t, (0, 0, 360 * t / 2.0))
        lp.rot(loops[1], t, (0, 0, -360 * t / 2.0))
    writhe(lp, arms, 0, 2.0, 30, 2.0)
    A.append(lp)
    td = Anim("tide", 1.4)
    for k, b in enumerate(arms):
        td.rot(b, 0, (0, 0, 0)).rot(b, 0.4, (-40, 0, 0), "easeInQuad").rot(b, 0.6, (60, 0, 0), "easeOutQuad")
        td.rot(b, 1.4, (0, 0, 0))
        td.scale(b, 0, 1.0).scale(b, 0.6, 1.5).scale(b, 1.4, 1.0)
    td.rot("body", 0.4, (-10, 0, 0)).rot("body", 0.6, (18, 0, 0)).rot("body", 1.4, (0, 0, 0))
    A.append(td)
    sw = Anim("swallow", 1.2)
    for l in loops:
        sw.rot(l + "_mouth", 0, (0, 0, 0)).rot(l + "_mouth", 0.35, (45, 0, 0), "easeOutQuad")
        sw.rot(l + "_mouth", 0.55, (-5, 0, 0), "easeInQuad").rot(l + "_mouth", 1.2, (0, 0, 0))
    sw.rot("body", 0.35, (-14, 0, 0)).rot("body", 0.55, (24, 0, 0)).rot("body", 1.2, (0, 0, 0))
    A.append(sw)
    rg = Anim("regen", 2.0)
    for i in range(11):
        t = 2.0 * i / 10
        rg.scale("body", t, 1.0 + 0.07 * math.sin(i * 2.1))
    rg.scale("body", 2.0, 1.0)
    writhe(rg, arms, 0, 2.0, 25, 3.0)
    A.append(rg)
    A.append(Anim("drink", 1.0))
    death = Anim("death", 2.0, loop="hold_on_last_frame")
    death.scale("body", 0, 1.0).scale("body", 1.6, (1.2, 0.3, 1.2), "easeInQuad")
    death.pos("root", 1.6, (0, -3, 0))
    writhe(death, arms, 0, 1.4, 45, 3)
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("eternity_front.png"), anim, "idle", 0.0, yaw=10, pitch=6,
                       show_body=False, scale=5.5, center=(0, 1.9), size=(620, 620)),
        preview.render(geo, tex, preview_path("eternity_side.png"), anim, "idle", 0.0, yaw=70, pitch=6,
                       show_body=False, scale=5.5, center=(0, 1.9), size=(620, 620)),
    ]
    return preview.contact_sheet(shots, preview_path("eternity_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
