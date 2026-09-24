"""
The Snake Devil (Akane Sawatari's contract) - what the contract calls up (entity/contract/snake_head, snake_tail).

Reference points (manga / anime, the Katana Man arc):
  * an enormous snake, green-scaled
  * its mouth is made of interlocking human arms and hands instead of teeth
  * a red eye in black sclera
  * it swallows devils whole and later spits them back out, healed, to fight for Sawatari; its thick tail swats
The head comes up out of the ground under its prey, jaws opening upwards; the tail bursts up beside the contractor.
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes


def materials():
    a = Atlas(512, 64)
    a.add("scale", kind="skin", color=(70, 132, 52))
    a.add("scale_dk", kind="skin", color=(40, 86, 32))
    a.add("scale_lt", kind="skin", color=(112, 168, 76))
    a.add("belly", kind="skin", color=(170, 190, 110))
    a.add("hand", kind="skin", color=(206, 182, 164))
    a.add("hand_dk", kind="skin", color=(160, 130, 116))
    a.add("nail", kind="bone", color=(230, 220, 204))
    a.add("mouth", kind="void", color=(40, 6, 10))
    a.add("gum", kind="flesh", color=(150, 36, 44))
    a.add("hole", kind="void", color=(18, 12, 8))
    a.add("dirt", kind="skin", color=(86, 62, 40))
    a.add("eye", kind="ringeye", color=(214, 28, 28), color2=(120, 8, 8), sclera=(10, 8, 8), rings=1)
    return a


def hand(bone, wrist, direction, spread_dir, length=7.0, mat="hand", reach=1.0):
    """A human forearm and hand reaching along `direction` (the fingers point that way, spread along spread_dir)."""
    d = norm(direction)
    sd = norm(np.asarray(spread_dir, dtype=float) - np.dot(spread_dir, d) * d)
    up = norm(np.cross(d, sd))
    w = np.asarray(wrist, dtype=float)
    bone.seg(w - d * length * 0.55, w, 1.5, 1.2, mat, up=up)  # the forearm the hand grows on
    palm = w + d * 1.1
    bone.obox(palm, d, (2.2, 2.0, 0.8), mat, up=up)
    for k in range(4):
        base = palm + d * 0.9 + sd * (-0.8 + k * 0.53)
        fd = norm(d + sd * (k - 1.5) * 0.12)
        L = (1.9, 2.2, 2.1, 1.6)[k] * reach
        bone.spike(base, fd, L, 0.5, 0.45, mat, steps=2, up=up)
        bone.obox(base + fd * L * 0.92, fd, (0.36, 0.3, 0.2), "nail", up=up)
    bone.spike(palm - sd * 1.0, norm(d * 0.6 - sd), 1.4 * reach, 0.5, 0.45, mat, steps=2, up=up)  # thumb


def scales_on(bone, f, rows, per_row, v0, v1, mat_a="scale_dk", mat_b="scale_lt", size=2.2, belly=None):
    for j in range(rows):
        v = v0 + (v1 - v0) * (j + 0.5) / rows
        for i in range(per_row):
            u = ((i + 0.5 * (j % 2)) / per_row) % 1.0
            if belly is not None and belly(u):
                continue
            p, n, du, dv = shapes.surface_frame(f, u, v)
            bone.obox(p + n * 0.12, dv, (size, size * 0.8, 0.3), mat_a if (i + j) % 3 else mat_b, up=n)


def hole(bone, center, radius, rng):
    """The ground torn open where it comes up."""
    c = np.asarray(center, dtype=float)
    shapes.shell(bone, shapes.ellipsoid(c, (radius, 0.6, radius)), 14, 3, "hole", thick=0.3)
    for i in range(14):
        a = i / 14 * 2 * math.pi + rng.uniform(-0.1, 0.1)
        r = radius * rng.uniform(0.95, 1.2)
        p = c + np.array([math.cos(a) * r, 0.6, math.sin(a) * r])
        bone.obox(p, (math.cos(a), 0.5, math.sin(a)), (rng.uniform(2.0, 4.0), rng.uniform(2.0, 3.5), 1.4), "dirt",
                  up=(0, 1, 0))


HEAD_PIVOT = np.array([0.0, 48.0, 8.0])   # where the neck meets the back of the skull
SNOUT = -30.0                             # z of the snout tip (the head is built level, facing the contractor)
LIP_Y = 45.5                              # the line of the lips


def build_head():
    """entity/contract/snake_head: origin = where the prey stands. The neck comes up out of the ground behind the prey
    and rears; the head (built level, looking at the contractor, -z) then strikes down over the prey, jaws wide."""
    atlas = materials()
    m = Model("csm.snake_head", atlas, density=1.4, seed=411)
    rng = np.random.default_rng(411)
    root = m.bone("root", pivot=(0, 0, 0))
    ground = m.bone("ground", parent="root", pivot=(0, 0, 26))
    hole(ground, (0, 0.3, 26), 13.0, rng)
    rise = m.bone("rise", parent="root", pivot=(0, 0, 26))
    # the neck: up out of the ground behind the prey, arching forward, belly plates towards the contractor
    neck = shapes.loft(shapes.polyline([(0, -40.0, 28.0), (0, -4.0, 29.0), (0, 22.0, 27.0), (0, 38.0, 20.0),
                                        (0, 46.0, 11.0)]),
                       shapes.profile((0, 10.5), (0.7, 10.0), (1, 10.5)), shapes.profile((0, 9.5), (1, 9.0)),
                       up=(0, 0, -1))
    shapes.shell(rise, neck, 16, 12, "scale", thick=0.5,
                 mat_fn=lambda u, v: "belly" if (u < 0.13 or u > 0.87) else "scale")
    scales_on(rise, neck, 10, 12, 0.25, 0.98, belly=lambda u: u < 0.15 or u > 0.85)
    for k in range(9):  # belly bands
        t = 0.3 + k * 0.075
        p, n, du, dv = shapes.surface_frame(neck, 0.0, t)
        rise.obox(p + n * 0.2, du, (0.8, 12.0, 1.4), "scale_lt", up=n)

    head = m.bone("head", parent="rise", pivot=tuple(HEAD_PIVOT))
    # the upper head: a broad, flat wedge (the cranium and upper jaw in one), lips along LIP_Y
    upper = shapes.loft(shapes.polyline([(0, LIP_Y, 10.0), (0, LIP_Y, -6.0), (0, LIP_Y, -22.0), (0, LIP_Y, SNOUT)]),
                        shapes.profile((0, 11.0), (0.35, 13.0), (0.75, 10.0), (1, 5.0)),
                        shapes.profile((0, 8.0), (0.35, 8.5), (0.75, 5.5), (1, 2.6)), up=(0, 1, 0))
    shapes.shell(head, upper, 18, 12, "scale", thick=0.5, u0=-0.25, u1=0.25,
                 mat_fn=lambda u, v: "scale_lt" if abs(u) < 0.04 else "scale")
    scales_on(head, lambda u, v: upper(u * 0.5 - 0.25, v), 7, 9, 0.1, 0.95, size=2.4)
    # the roof of the mouth, following the taper of the head
    for k in range(8):
        z0, z1 = 8.0 + (SNOUT + 2.0 - 8.0) * k / 8, 8.0 + (SNOUT + 2.0 - 8.0) * (k + 1) / 8
        t = (k + 0.5) / 8
        half = float(np.interp(t, (0, 0.35, 0.75, 1), (11.0, 13.0, 10.0, 5.0))) - 1.6
        head.box((-half, LIP_Y - 0.2, z1), (half, LIP_Y + 0.6, z0), "gum")
        head.box((-half * 0.55, LIP_Y + 0.4, z1), (half * 0.55, LIP_Y + 1.6, z0), "mouth")
    # the eyes on either side of the head: red in black, under a heavy brow
    for s in (-1, 1):
        head.decal((s * 11.4, LIP_Y + 5.0, -9.0), norm((s * 1.0, 0.35, -0.35)), 6.5, 4.4, "eye")
        shapes.horn(head, (s * 8.0, LIP_Y + 8.6, -4.0), (s * 0.35, 0.05, -1), 9.0, 2.2, mat="scale_dk", flat=0.45,
                    up=(0, 1, 0), sections=3, around=6, r1=0.4)
        head.cbox((s * 2.2, LIP_Y + 3.0, SNOUT + 1.2), (1.3, 1.0, 1.4), "mouth")  # nostrils
    # the "teeth": human hands along the lips, fingers reaching down across the gap
    for k in range(10):
        z = 5.0 - k * 3.3
        t = (z - 10.0) / (SNOUT - 10.0)
        half = float(np.interp(t, (0, 0.35, 0.75, 1), (11.0, 13.0, 10.0, 5.0))) - 1.2
        for s in (-1, 1):
            hand(head, (s * half, LIP_Y - 0.2, z), norm((-s * 0.25, -1.0, -0.1)), (0, 0, 1), length=5.0,
                 reach=0.95 + 0.2 * (k % 2), mat="hand" if (k + (s > 0)) % 2 else "hand_dk")
    for x in (-3.0, 0.0, 3.0):
        hand(head, (x, LIP_Y - 0.2, SNOUT + 2.5), norm((x * 0.05, -1.0, 0.25)), (1, 0, 0), length=4.5)

    # the lower jaw, hinged at the back of the head
    jaw = m.bone("lower_jaw", parent="head", pivot=(0, LIP_Y - 1.0, 6.0))
    lower = shapes.loft(shapes.polyline([(0, LIP_Y - 1.5, 8.0), (0, LIP_Y - 2.0, -10.0), (0, LIP_Y - 1.5, SNOUT + 1.0)]),
                        shapes.profile((0, 10.5), (0.5, 11.0), (1, 4.6)),
                        shapes.profile((0, 4.2), (0.5, 3.8), (1, 1.8)), up=(0, 1, 0))
    shapes.shell(jaw, lower, 16, 10, "belly", thick=0.5, u0=0.25, u1=0.75,
                 mat_fn=lambda u, v: "belly" if abs(u - 0.5) < 0.14 else "scale")
    for k in range(8):
        z0, z1 = 7.0 + (SNOUT + 3.0 - 7.0) * k / 8, 7.0 + (SNOUT + 3.0 - 7.0) * (k + 1) / 8
        t = (k + 0.5) / 8
        half = float(np.interp(t, (0, 0.5, 1), (10.5, 11.0, 4.6))) - 2.0
        jaw.box((-half, LIP_Y - 1.8, z1), (half, LIP_Y - 1.0, z0), "gum")
        jaw.box((-half * 0.55, LIP_Y - 2.6, z1), (half * 0.55, LIP_Y - 1.6, z0), "mouth")
    for k in range(9):
        z = 3.5 - k * 3.3
        t = (z - 8.0) / (SNOUT + 1.0 - 8.0)
        half = float(np.interp(t, (0, 0.5, 1), (10.5, 11.0, 4.6))) - 1.6
        for s in (-1, 1):
            # between the upper hands, so that the two rows interlock when it bites
            hand(jaw, (s * half, LIP_Y - 1.2, z), norm((-s * 0.25, 1.0, -0.1)), (0, 0, 1), length=5.0,
                 reach=0.9 + 0.2 * ((k + 1) % 2), mat="hand_dk" if (k + (s > 0)) % 2 else "hand")

    geo = out("geo", "entity", "contract", "snake_head.geo.json")
    tex = out("textures", "entity", "contract", "snake_head.png")
    glow = out("textures", "entity", "contract", "snake_head_glowmask.png")
    anim_path = out("animations", "entity", "contract", "snake_head.animation.json")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=413)
    save_animations(anim_path, head_animations())
    print("snake head: %d cubes, %d bones" % (m.cube_count(), len(m.bones)))
    return geo, tex, anim_path


def head_animations():
    # swallow (36 ticks): up out of the ground behind the prey, rears, strikes down with the jaws gaping and they shut
    # round the prey on tick 11 (ContractSummonEntity#snakeSwallow); it lifts its head, gulps, and sinks back
    s = Anim("swallow", 1.8, loop="hold_on_last_frame")
    s.scale("ground", 0, 0.2).scale("ground", 0.12, 1.0, "easeOutBack").scale("ground", 1.6, 1.0)
    s.scale("ground", 1.8, 0.01)
    s.pos("rise", 0, (0, -70, 0)).pos("rise", 0.25, (0, 0, 0), "easeOutQuad").pos("rise", 1.2, (0, 0, 0))
    s.pos("rise", 1.75, (0, -74, 0), "easeInQuad")
    s.rot("head", 0, (-25, 0, 0)).rot("head", 0.3, (-30, 0, 0)).rot("head", 0.5, (62, 0, 0), "easeInQuad")
    s.rot("head", 0.6, (66, 0, 0)).rot("head", 0.9, (10, 0, 0), "easeInOutQuad").rot("head", 1.8, (0, 0, 0))
    s.rot("lower_jaw", 0, (0, 0, 0)).rot("lower_jaw", 0.3, (60, 0, 0), "easeOutQuad").rot("lower_jaw", 0.48, (62, 0, 0))
    s.rot("lower_jaw", 0.56, (0, 0, 0), "easeInQuad").rot("lower_jaw", 1.8, (0, 0, 0))
    for i in range(5):  # the gulp running down the neck
        t = 0.9 + i * 0.08
        s.scale("rise", t, (1.07 if i % 2 == 0 else 1.0, 1.0, 1.07 if i % 2 == 0 else 1.0))
    s.scale("rise", 1.35, 1.0)
    # release (34 ticks): it rears where the contractor points, leans in and opens wide: what it swallowed comes out
    # on tick 14
    r = Anim("release", 1.7, loop="hold_on_last_frame")
    r.scale("ground", 0, 0.2).scale("ground", 0.12, 1.0, "easeOutBack").scale("ground", 1.5, 1.0)
    r.scale("ground", 1.7, 0.01)
    r.pos("rise", 0, (0, -70, 0)).pos("rise", 0.3, (0, 0, 0), "easeOutQuad").pos("rise", 1.15, (0, 0, 0))
    r.pos("rise", 1.65, (0, -74, 0), "easeInQuad")
    r.rot("head", 0, (-25, 0, 0)).rot("head", 0.45, (-15, 0, 0)).rot("head", 0.7, (25, 0, 0), "easeInOutQuad")
    r.rot("head", 1.1, (25, 0, 0)).rot("head", 1.4, (0, 0, 0))
    r.rot("lower_jaw", 0.5, (0, 0, 0)).rot("lower_jaw", 0.7, (55, 0, 0), "easeOutQuad").rot("lower_jaw", 1.05, (55, 0, 0))
    r.rot("lower_jaw", 1.25, (0, 0, 0))
    return [s, r]


# ---------------------------------------------------------------------------------------- the tail
def build_tail():
    """entity/contract/snake_tail: origin = beside the contractor, on their right. The tail comes up out of the ground
    and reaches forward (-z); the sweep turns it round the origin from the right to the left."""
    atlas = materials()
    m = Model("csm.snake_tail", atlas, density=1.4, seed=415)
    rng = np.random.default_rng(415)
    root = m.bone("root", pivot=(0, 0, 0))
    ground = m.bone("ground", parent="root", pivot=(0, 0, 0))
    hole(ground, (0, 0.3, 0), 9.0, rng)
    tail = m.bone("tail", parent="root", pivot=(0, 0, 0))
    pts = [(0, -12.0, 2.0), (0, 8.0, -1.0), (0, 20.0, -12.0), (0, 20.0, -30.0), (0, 14.0, -48.0), (0, 10.0, -62.0)]
    f = shapes.loft(shapes.polyline(pts), shapes.profile((0, 8.0), (0.3, 7.4), (0.7, 4.6), (1, 0.8)),
                    shapes.profile((0, 7.0), (0.3, 6.6), (0.7, 4.0), (1, 0.7)), up=(0, 1, 0))
    shapes.shell(tail, f, 14, 18, "scale", thick=0.5,
                 mat_fn=lambda u, v: "belly" if abs(u - 0.5) < 0.14 else "scale")
    scales_on(tail, f, 12, 10, 0.1, 0.9, belly=lambda u: abs(u - 0.5) < 0.18, size=1.9)
    geo = out("geo", "entity", "contract", "snake_tail.geo.json")
    tex = out("textures", "entity", "contract", "snake_tail.png")
    glow = out("textures", "entity", "contract", "snake_tail_glowmask.png")
    anim_path = out("animations", "entity", "contract", "snake_tail.animation.json")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=413)
    save_animations(anim_path, [tail_animation()])
    print("snake tail: %d cubes, %d bones" % (m.cube_count(), len(m.bones)))
    return geo, tex, anim_path


def tail_animation():
    """26 ticks: up out of the ground aimed off to the right, then one sweep right-to-left that lands on tick 10."""
    a = Anim("tail", 1.3, loop="hold_on_last_frame")
    a.scale("ground", 0, 0.2).scale("ground", 0.12, 1.0, "easeOutBack").scale("ground", 1.1, 1.0)
    a.scale("ground", 1.3, 0.01)
    a.pos("tail", 0, (0, -40, 0)).pos("tail", 0.2, (0, 0, 0), "easeOutQuad").pos("tail", 0.9, (0, 0, 0))
    a.pos("tail", 1.25, (0, -50, 0), "easeInQuad")
    a.rot("tail", 0, (0, -70, 0)).rot("tail", 0.25, (0, -75, 0)).rot("tail", 0.5, (0, 70, 0), "easeInOutQuad")
    a.rot("tail", 0.8, (0, 80, 0)).rot("tail", 1.3, (0, 80, 0))
    return a


def render_previews():
    hg, ht, ha = (out("geo", "entity", "contract", "snake_head.geo.json"),
                  out("textures", "entity", "contract", "snake_head.png"),
                  out("animations", "entity", "contract", "snake_head.animation.json"))
    tg, tt, ta = (out("geo", "entity", "contract", "snake_tail.geo.json"),
                  out("textures", "entity", "contract", "snake_tail.png"),
                  out("animations", "entity", "contract", "snake_tail.animation.json"))
    bg = (160, 180, 150)
    shots = [
        preview.render(hg, ht, preview_path("snake_reared.png"), ha, "swallow", 0.28, yaw=150, pitch=6,
                       show_body=True, scale=5.0, center=(0, 2.2), size=(620, 700), bg=bg),
        preview.render(hg, ht, preview_path("snake_strike.png"), ha, "swallow", 0.48, yaw=120, pitch=6,
                       show_body=True, scale=5.0, center=(0, 2.2), size=(620, 700), bg=bg),
        preview.render(hg, ht, preview_path("snake_face.png"), ha, "release", 0.9, yaw=160, pitch=10,
                       show_body=False, scale=8.0, center=(0, 3.0), size=(620, 700), bg=bg),
        preview.render(hg, ht, preview_path("snake_side.png"), ha, "release", 0.9, yaw=90, pitch=4,
                       show_body=False, scale=5.0, center=(0, 2.2), size=(620, 700), bg=bg),
        preview.render(tg, tt, preview_path("snake_tail.png"), ta, "tail", 0.45, yaw=160, pitch=20,
                       show_body=True, scale=5.0, center=(0, 1.2), size=(620, 700), bg=bg),
    ]
    return preview.contact_sheet(shots, preview_path("snake_sheet.png"), cols=3)


if __name__ == "__main__":
    build_head()
    build_tail()
    print(render_previews())
