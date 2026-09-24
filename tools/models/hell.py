"""
The Hell Devil's hand (Santa Claus's contract) - what the contract calls up (entity/contract/hell_hand).

Reference points (manga, the International Assassins arc):
  * the Hell Devil itself is a centaur with a featureless head but for a huge grimacing mouth, its taut flesh burning
  * when called it manifests as a giant six-fingered hand, which drags its targets down to Hell
Here the hand comes up out of a burning crack in the ground round the area: five fingers on the far side, the thumb on
the contractor's side, closing over everything inside and pulling it down. Origin = the centre of the area.
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes


def materials():
    a = Atlas(256, 64)
    a.add("flesh", kind="flesh", color=(150, 40, 30))
    a.add("flesh_dk", kind="flesh", color=(96, 22, 18))
    a.add("burn", kind="glow", color=(255, 120, 30), color2=(255, 220, 120), emissive=True)
    a.add("nail", kind="bone", color=(40, 22, 20))
    a.add("pit", kind="void", color=(20, 6, 4))
    a.add("rock", kind="skin", color=(60, 40, 34))
    return a


R = 60.0        # the burning crack runs round the area this far out (px)
SEG = 26.0      # each digit is three segments of this length
# (yaw, distance from the centre of the palm, thickness, length): five fingers side by side along the far edge of the
# palm and the thumb out to one side - six digits in all
DIGITS = [(146.0, 44.0, 1.0, 0.9), (163.0, 46.0, 1.05, 1.02), (180.0, 47.0, 1.08, 1.1), (197.0, 46.0, 1.05, 1.04),
          (214.0, 44.0, 1.0, 0.92), (282.0, 36.0, 1.35, 0.78)]


def digit(m, i, yaw, dist, rscale, lscale):
    """A chain of bones hell_i (turned to its place round the palm) > hell_i_0 > _1 > _2, built along +y at +z."""
    top = m.bone("hell_%d" % i, parent="hand", pivot=(0, 0, 0), rotation=(0, yaw, 0))
    par = top.name
    base = np.array([0.0, -2.0, dist])
    for k in range(3):
        b = m.bone("hell_%d_%d" % (i, k), parent=par, pivot=tuple(base))
        L = SEG * lscale
        r0 = (9.4 - 1.8 * k) * rscale
        r1 = (8.2 - 1.8 * k) * rscale
        f = shapes.loft(shapes.polyline([base - np.array([0, 1.0, 0]), base + np.array([0, L + 0.5, 0])]),
                        shapes.taper(r0, r1), shapes.taper(r0 * 0.9, r1 * 0.9), up=(0, 0, 1))
        # taut flesh, split by burning cracks
        shapes.shell(b, f, 10, 6, "flesh", thick=0.5,
                     mat_fn=lambda u, v, k=k: "burn" if (int(u * 10 + v * 3 + k) % 5 == 0) else
                     ("flesh_dk" if int(v * 6) % 3 == 0 else "flesh"))
        shapes.shell(b, shapes.ellipsoid(base, (r0 * 1.02, r0 * 0.8, r0 * 1.02)), 10, 5, "flesh_dk", thick=0.4)
        # the knuckle creases, glowing
        for j in range(3):
            y = base[1] + L * (0.2 + 0.3 * j)
            b.obox(np.array([0, y, dist + r0 * 0.95]), (1, 0, 0), (0.5, r0 * 1.2, 0.5), "burn", up=(0, 0, 1))
        if k == 2:
            tip = base + np.array([0, L, 0])
            # the nail, on the outer side, the fingertip curling in
            b.obox(tip + np.array([0, -2.0, r1 * 0.9]), (0, 1, 0), (r1 * 1.4, 4.0, 0.8), "nail", up=(0, 0, 1))
            shapes.shell(b, shapes.ellipsoid(tip, (r1, r1 * 0.9, r1)), 8, 4, "flesh", thick=0.4)
        par = b.name
        base = base + np.array([0, L, 0])


def build():
    atlas = materials()
    m = Model("csm.hell_hand", atlas, density=1.0, seed=711)
    rng = np.random.default_rng(711)
    root = m.bone("root", pivot=(0, 0, 0))
    ground = m.bone("ground", parent="root", pivot=(0, 0, 0))
    # the burning crack in the ground round the whole area
    for i in range(36):
        a = i / 36 * 2 * math.pi
        r = R + rng.uniform(-6, 6)
        p = np.array([math.sin(a) * r, 0.3, math.cos(a) * r])
        tangent = np.array([math.cos(a), 0, -math.sin(a)])
        ground.obox(p, tangent, (rng.uniform(5, 9), 12.0, 0.6), "pit", up=(0, 1, 0))
        ground.obox(p + np.array([0, 0.35, 0]), tangent, (rng.uniform(1.5, 3.0), 11.0, 0.4), "burn", up=(0, 1, 0))
        if i % 3 == 0:
            ground.obox(p + tangent * 3 + np.array([0, 1.0, 0]), (math.sin(a), 0.6, math.cos(a)),
                        (rng.uniform(3, 6), rng.uniform(2, 4), 2.0), "rock", up=(0, 1, 0))
    hand = m.bone("hand", parent="root", pivot=(0, 0, 0))
    # the palm, level with the ground under everything it closes on, its lines burning; the wrist goes down into the
    # pit on the contractor's side
    palm = shapes.ellipsoid((0, -3.0, -4.0), (40.0, 5.0, 46.0), e_lat=0.7, e_lon=0.8)
    shapes.shell(hand, palm, 20, 6, "flesh", thick=0.6,
                 mat_fn=lambda u, v: "flesh_dk" if v < 0.5 else "flesh")
    for pts in (((-30, -20), (-8, -6), (22, -12)), ((-26, 6), (0, 10), (28, 2)), ((-4, -36), (-10, -4), (-18, 30))):
        for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
            hand.seg((x0, 2.1, z0), (x1, 2.1, z1), 1.4, 0.5, "burn", up=(0, 1, 0))
    wrist = shapes.loft(shapes.polyline([(0, -2.0, 30.0), (0, -30.0, 50.0), (0, -70.0, 66.0)]),
                        shapes.profile((0, 30.0), (1, 22.0)), shapes.profile((0, 6.0), (0.4, 14.0), (1, 18.0)),
                        up=(0, 1, 0))
    shapes.shell(hand, wrist, 16, 8, "flesh", thick=0.6,
                 mat_fn=lambda u, v: "burn" if int(u * 16 + v * 8) % 7 == 0 else "flesh_dk")
    for i, (yaw, dist, rs, ls) in enumerate(DIGITS):
        digit(m, i, yaw, dist, rs, ls)
    geo = out("geo", "entity", "contract", "hell_hand.geo.json")
    tex = out("textures", "entity", "contract", "hell_hand.png")
    glow = out("textures", "entity", "contract", "hell_hand_glowmask.png")
    anim_path = out("animations", "entity", "contract", "hell_hand.animation.json")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=713)
    save_animations(anim_path, [animation()])
    print("hell hand: %d cubes, %d bones" % (m.cube_count(), len(m.bones)))
    return geo, tex, anim_path


def animation():
    """58 ticks: the digits come up out of the crack (to tick 14), close over the area on tick 16, hold everything
    while the whole hand sinks, and drag it down under on tick 46."""
    a = Anim("drag", 2.9, loop="hold_on_last_frame")
    a.scale("ground", 0, 0.3).scale("ground", 0.2, 1.0, "easeOutBack").scale("ground", 2.6, 1.0)
    a.scale("ground", 2.9, 0.01)
    a.pos("hand", 0, (0, -100, 0)).pos("hand", 0.6, (0, 0, 0), "easeOutQuad").pos("hand", 0.8, (0, 2, 0))
    a.pos("hand", 2.2, (0, -12, 0), "easeInSine").pos("hand", 2.4, (0, -40, 0), "easeInQuad")
    a.pos("hand", 2.9, (0, -100, 0), "easeInQuad")
    for i in range(len(DIGITS)):
        for k in range(3):
            n = "hell_%d_%d" % (i, k)
            thumb = i == len(DIGITS) - 1
            open_ = (-18, 4, 8)[k]
            shut = (30, 40, 42)[k] + (10 if thumb else 0)
            a.rot(n, 0, (open_, 0, 0)).rot(n, 0.65, (open_ - 6, 0, 0), "easeOutQuad")
            a.rot(n, 0.8, (shut, 0, 0), "easeInQuad")
            for j in range(6):  # squeezing
                a.rot(n, 1.0 + j * 0.2, (shut + (3 if j % 2 == 0 else -2), 0, 0))
            a.rot(n, 2.9, (shut, 0, 0))
    return a


def render_previews():
    g, t, a = (out("geo", "entity", "contract", "hell_hand.geo.json"),
               out("textures", "entity", "contract", "hell_hand.png"),
               out("animations", "entity", "contract", "hell_hand.animation.json"))
    bg = (60, 40, 40)
    shots = [
        preview.render(g, t, preview_path("hell_open.png"), a, "drag", 0.62, yaw=160, pitch=18, show_body=True,
                       scale=2.0, center=(0, 2.4), size=(620, 620), bg=bg),
        preview.render(g, t, preview_path("hell_shut.png"), a, "drag", 1.2, yaw=160, pitch=18, show_body=True,
                       scale=2.2, center=(0, 2.0), size=(620, 620), bg=bg),
        preview.render(g, t, preview_path("hell_side.png"), a, "drag", 1.2, yaw=80, pitch=8, show_body=True,
                       scale=2.2, center=(0, 2.0), size=(620, 620), bg=bg),
    ]
    return preview.contact_sheet(shots, preview_path("hell_sheet.png"), cols=3)


if __name__ == "__main__":
    build()
    print(render_previews())
