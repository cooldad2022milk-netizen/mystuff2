"""
The Octopus Devil (Hirofumi Yoshida's contract) - what the contract calls up (entity/contract/octopus).

Reference points (manga, the International Assassins arc and part 2):
  * Yoshida crosses his index and middle fingers and the Octopus Devil's huge tentacles, covered in suckers, come out
    of clouds of ink
  * several at once, to seize or bind a small group; strong enough to lift people and tear the Eternity Devil's hand
    off; it can also spray ink to blind and confuse
Bones: four grabbing tentacles (t0..t3, each a chain of segments so they can coil) round the target, one lifter (l)
under the contractor for Tentacle Lift, and the ink they come out of.
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes


def materials():
    a = Atlas(256, 64)
    a.add("tent", kind="skin", color=(164, 72, 124))
    a.add("tent_dk", kind="skin", color=(110, 40, 84))
    a.add("sucker", kind="skin", color=(238, 200, 216))
    a.add("sucker_rim", kind="skin", color=(196, 140, 170))
    a.add("ink", kind="void", color=(12, 8, 18))
    a.add("ink_lt", kind="skin", color=(34, 26, 44))
    return a


SEGS = 4
SEG_LEN = 15.0
# where each grabbing tentacle comes up, and the axis/sign that curls it in towards the target (see geo.py for the
# bedrock rotation convention: +z rotation bends +y towards +x, +x rotation bends +y towards -z)
TENTACLES = [((18.0, 0.0), "z", -1.0), ((-18.0, 0.0), "z", 1.0), ((0.0, 18.0), "x", 1.0), ((0.0, -18.0), "x", -1.0)]


def radius_at(t):
    return 4.6 * (1 - t) + 0.7 * t


def tentacle(m, name, parent, base, inward, segs=SEGS, seg_len=SEG_LEN, rscale=1.0):
    """A chain of bones name_0..name_{segs-1} rising from `base`; suckers on the side facing `inward`."""
    base = np.asarray(base, dtype=float)
    inward = norm(np.asarray(inward, dtype=float))
    par = parent
    names = []
    for k in range(segs):
        y0 = base[1] + k * seg_len
        b = m.bone("%s_%d" % (name, k), parent=par, pivot=(base[0], y0, base[2]))
        t0, t1 = k / segs, (k + 1) / segs
        p0 = np.array([base[0], y0, base[2]])
        p1 = p0 + np.array([0, seg_len, 0])
        f = shapes.loft(shapes.polyline([p0 - np.array([0, 0.6, 0]), p1 + np.array([0, 0.6, 0])]),
                        shapes.taper(radius_at(t0) * rscale, radius_at(t1) * rscale),
                        shapes.taper(radius_at(t0) * rscale, radius_at(t1) * rscale), up=(0, 0, 1))
        shapes.shell(b, f, 10, 4, "tent", thick=0.45)
        if k > 0:  # a round joint, so the bends don't open gaps
            r = radius_at(t0) * rscale
            shapes.shell(b, shapes.ellipsoid(p0, (r * 1.02, r * 0.9, r * 1.02)), 10, 5, "tent", thick=0.4)
        # the suckers, two rows up the inner side
        for j in range(4):
            y = y0 + (j + 0.5) * seg_len / 4
            r = radius_at(t0 + (t1 - t0) * (j + 0.5) / 4) * rscale
            side = norm(np.cross(inward, [0, 1, 0]))
            for s in (-1, 1):
                c = np.array([base[0], y, base[2]]) + inward * (r * 0.92) + side * s * r * 0.38
                d = max(0.5, r * 0.42)
                b.obox(c, (0, 1, 0), (d * 1.4, d * 1.4, 0.5), "sucker_rim", up=inward)
                b.obox(c + inward * 0.2, (0, 1, 0), (d * 0.8, d * 0.8, 0.4), "sucker", up=inward)
        # a darker stripe down the outer side
        for j in range(3):
            y = y0 + (j + 0.5) * seg_len / 3
            r = radius_at(t0 + (t1 - t0) * (j + 0.5) / 3) * rscale
            b.obox(np.array([base[0], y, base[2]]) - inward * (r * 0.95), (0, 1, 0), (r * 0.9, seg_len / 3, 0.4),
                   "tent_dk", up=-inward)
        names.append(b.name)
        par = b.name
    # the tip curls a little on its own
    return names


def ink_pool(bone, center, radius, rng):
    c = np.asarray(center, dtype=float)
    shapes.shell(bone, shapes.ellipsoid(c, (radius, 0.7, radius)), 14, 3, "ink", thick=0.3)
    for i in range(10):
        a = i / 10 * 2 * math.pi + rng.uniform(-0.2, 0.2)
        r = radius * rng.uniform(0.4, 0.95)
        p = c + np.array([math.cos(a) * r, rng.uniform(1.0, 3.0), math.sin(a) * r])
        rr = rng.uniform(2.5, 4.5)
        shapes.shell(bone, shapes.ellipsoid(p, (rr, rr * 0.8, rr)), 6, 4, "ink" if i % 3 else "ink_lt", thick=0.3)


def build():
    atlas = materials()
    m = Model("csm.octopus", atlas, density=1.4, seed=421)
    rng = np.random.default_rng(421)
    root = m.bone("root", pivot=(0, 0, 0))
    ink = m.bone("ink", parent="root", pivot=(0, 0, 0))
    ink_pool(ink, (0, 0.2, 0), 26.0, rng)
    grab = m.bone("grab", parent="root", pivot=(0, 0, 0))
    for i, ((x, z), axis, sign) in enumerate(TENTACLES):
        tentacle(m, "t%d" % i, "grab", (x, -2.0, z), (-x, 0, -z))
    lift = m.bone("lift", parent="root", pivot=(0, 0, 0))
    ink_pool(lift, (0, 0.25, 0), 12.0, rng)
    tentacle(m, "l", "lift", (0, -3.0, 2.0), (0, 0, -1), rscale=1.25)

    geo = out("geo", "entity", "contract", "octopus.geo.json")
    tex = out("textures", "entity", "contract", "octopus.png")
    glow = out("textures", "entity", "contract", "octopus_glowmask.png")
    anim_path = out("animations", "entity", "contract", "octopus.animation.json")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=423)
    save_animations(anim_path, animations())
    print("octopus: %d cubes, %d bones" % (m.cube_count(), len(m.bones)))
    return geo, tex, anim_path


GRIP = (0.6, 1.0, 1.25, 1.45)
HOIST = (0.12, 0.3, 1.9, 2.2)   # lower half straight, the coil high up: what it holds is lifted off its feet


def curl(a, name, axis, sign, t, deg, per=GRIP, easing=None):
    """Curl a tentacle by `deg` spread over its segments (more towards the tip)."""
    for k in range(SEGS):
        d = deg * per[k] * sign
        a.rot("%s_%d" % (name, k), t, (d, 0, 0) if axis == "x" else (0, 0, d), easing)


def animations():
    # grab (52 ticks): up out of the ink, coil in round the target on tick 6 (ContractSummonEntity#octopusGrab), lift and
    # squeeze, smash it down on tick 38-40, then sink back into the ink
    g = Anim("grab", 2.6, loop="hold_on_last_frame")
    g.scale("lift", 0, 0.0).scale("lift", 2.6, 0.0)
    g.scale("ink", 0, 0.2).scale("ink", 0.15, 1.0, "easeOutBack").scale("ink", 2.4, 1.0).scale("ink", 2.6, 0.01)
    g.pos("grab", 0, (0, -60, 0)).pos("grab", 0.25, (0, 0, 0), "easeOutQuad")
    g.pos("grab", 2.2, (0, 0, 0)).pos("grab", 2.6, (0, -64, 0), "easeInQuad")
    for i, ((x, z), axis, sign) in enumerate(TENTACLES):
        n = "t%d" % i
        curl(g, n, axis, sign, 0.0, -8)
        curl(g, n, axis, sign, 0.22, -12, easing="easeOutQuad")  # rearing back, open
        curl(g, n, axis, sign, 0.32, 30, easing="easeInQuad")     # snapping shut round it
        curl(g, n, axis, sign, 0.5, 30)
        for j in range(7):                                        # hoisting it up, squeezing
            curl(g, n, axis, sign, 0.7 + j * 0.16, 30 + (3 if j % 2 == 0 else -2), per=HOIST,
                 easing="easeInOutSine" if j == 0 else None)
        curl(g, n, axis, sign, 1.95, 34, easing="easeInQuad")    # and smashing it down
        curl(g, n, axis, sign, 2.2, 22)
        curl(g, n, axis, sign, 2.6, 0, easing="easeInQuad")
    # lift (22 ticks): one thick tentacle shoots up under the contractor and flings them forward on tick 6
    li = Anim("lift", 1.1, loop="hold_on_last_frame")
    li.scale("grab", 0, 0.0).scale("grab", 1.1, 0.0)
    li.scale("lift", 0, 0.3).scale("lift", 0.1, 1.0, "easeOutBack")
    li.pos("l_0", 0, (0, -50, 0)).pos("l_0", 0.3, (0, 6, 0), "easeOutQuad").pos("l_0", 0.55, (0, 4, 0))
    li.pos("l_0", 1.05, (0, -60, 0), "easeInQuad")
    for k in range(SEGS):
        n = "l_%d" % k
        li.rot(n, 0, (0, 0, 0)).rot(n, 0.2, (-8 * (k + 1) * 0.5, 0, 0)).rot(n, 0.32, (14 * (k + 1) * 0.5, 0, 0),
                                                                              "easeOutQuad")
        li.rot(n, 0.6, (8, 0, 0)).rot(n, 1.1, (0, 0, 0))
    li.scale("lift", 0.9, 1.0).scale("lift", 1.1, 0.02)
    return [g, li]


def render_previews():
    g, t, a = (out("geo", "entity", "contract", "octopus.geo.json"), out("textures", "entity", "contract", "octopus.png"),
               out("animations", "entity", "contract", "octopus.animation.json"))
    bg = (180, 170, 190)
    shots = [
        preview.render(g, t, preview_path("octopus_rise.png"), a, "grab", 0.22, yaw=150, pitch=10, show_body=True,
                       scale=5.0, center=(0, 1.8), size=(620, 700), bg=bg),
        preview.render(g, t, preview_path("octopus_coil.png"), a, "grab", 0.6, yaw=150, pitch=10, show_body=True,
                       scale=5.0, center=(0, 1.8), size=(620, 700), bg=bg),
        preview.render(g, t, preview_path("octopus_lifted.png"), a, "grab", 1.7, yaw=150, pitch=10, show_body=False,
                       scale=4.2, center=(0, 2.6), size=(620, 700), bg=bg),
        preview.render(g, t, preview_path("octopus_lift.png"), a, "lift", 0.35, yaw=110, pitch=10, show_body=True,
                       scale=5.0, center=(0, 1.8), size=(620, 700), bg=bg),
    ]
    return preview.contact_sheet(shots, preview_path("octopus_sheet.png"), cols=2)


if __name__ == "__main__":
    build()
    print(render_previews())
