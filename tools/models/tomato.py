"""
The Tomato Devil - entity model (entity/devil/tomato), texture atlas and GeckoLib animations.

Reference points (anime ep. 1):
  * a huge, round, shiny red tomato covered in protruding eyeballs - and the eyeballs look like little tomatoes,
    each with its green leaves on top; a calyx and stem on the big one too
  * a large VERTICAL mouth down the middle of its front, full of human-looking teeth
  * it stands on eight pale human arms coming out of its base, hands flat on the ground
  * it comes back from its seeds unless they are burned
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
    a.add("tomato", kind="gloss", color=(214, 44, 32))
    a.add("tomato_dk", kind="gloss", color=(170, 28, 22))
    a.add("tomato_lt", kind="gloss", color=(236, 84, 60))
    a.add("calyx", kind="skin", color=(64, 132, 54))
    a.add("calyx_dk", kind="skin", color=(40, 92, 36))
    a.add("eye", kind="bone", color=(238, 234, 220))
    a.add("iris", kind="skin", color=(200, 150, 40))
    a.add("pupil", kind="void", color=(12, 10, 10))
    a.add("mouth", kind="void", color=(60, 8, 14))
    a.add("lip", kind="flesh", color=(150, 20, 30))
    a.add("teeth", kind="teeth", color=(240, 234, 214))
    a.add("skin", kind="skin", color=(214, 176, 150))
    a.add("skin_dk", kind="skin", color=(180, 140, 116))
    a.add("seed", kind="skin", color=(236, 214, 150))
    return a


C = np.array([0.0, 22.5, 0.0])
R = (13.0, 11.5, 13.0)


def tomato_surface():
    """A slightly ribbed, squashed sphere: eight lobes like a real tomato."""
    base = shapes.ellipsoid(C, R)

    def f(u, v):
        p = np.asarray(base(u, v), dtype=float)
        k = 1.0 + 0.045 * math.cos(8 * 2 * math.pi * u) * math.sin(math.pi * v)
        d = p - C
        return C + np.array([d[0] * k, d[1], d[2] * k])
    return f


ARMS = [(-100 + k * 25 if k < 4 else 80 + (k - 4) * 25) for k in range(8)]   # around the sides, none at front/back


def build():
    atlas = materials()
    m = Model("csm.tomato_devil", atlas, density=2.0, seed=181)
    root = m.bone("root", pivot=(0, 0, 0))
    body = m.bone("body", parent="root", pivot=(0, 18, 0))
    look = m.bone("look", parent="body", pivot=(0, 22, 0))
    f = tomato_surface()
    mouth_skip = lambda u, v: (u < 0.05 or u > 0.95) and 0.22 < v < 0.74
    shapes.shell(body, f, 24, 14, "tomato", skip=mouth_skip, thick=0.5,
                 mat_fn=lambda u, v: "tomato_dk" if ((u * 8) % 1.0) < 0.2 else ("tomato_lt" if v > 0.75 else "tomato"))
    # calyx and stem
    top = C + np.array([0, R[1] - 0.6, 0])
    for k in range(6):
        a = math.radians(k * 60 + 15)
        d = np.array([math.cos(a), 0.25, math.sin(a)])
        shapes.horn(body, top, d, 6.5, 1.8, mat="calyx" if k % 2 else "calyx_dk", flat=0.2, up=(0, 1, 0), sections=5,
                    around=6, r1=0.1, bend_axis=np.cross(d, (0, 1, 0)), bend=-30)
    shapes.horn(body, top, (0.1, 1, 0.05), 4.5, 0.9, mat="calyx_dk", sections=4, around=6, r1=0.5,
                bend_axis=(0, 0, 1), bend=-35)
    # the vertical mouth down its front, lips and teeth
    zf = C[2] - R[2]
    look.box((-2.4, 15.2, zf + 1.8), (2.4, 29.4, zf + 3.6), "mouth")  # the throat, behind the teeth
    for s in (-1, 1):
        look.curve([np.array([s * 2.8, y, zf + 0.6 + 0.02 * (y - 22) ** 2]) for y in np.linspace(14.8, 29.8, 7)], 1.3,
                   1.3, 1.2, 1.2, "lip")
        # human teeth: flat, square, packed side by side along each lip
        for k in range(9):
            y = 16.0 + k * 1.5
            look.obox((s * 1.6, y, zf + 1.0 + 0.02 * (y - 22) ** 2), (-s * 1.0, 0, 0), (1.35, 1.8, 0.6), "teeth",
                      up=(0, 0, -1))
    # bulging eyes all over it
    rng = np.random.default_rng(7)
    eyes = m.bone("eyes", parent="look", pivot=tuple(C))
    placed = []
    while len(placed) < 16:
        u = rng.uniform(0.0, 1.0)
        v = rng.uniform(0.3, 0.85)
        if (u < 0.06 or u > 0.94) and v < 0.75:
            continue
        p, n, du, dv = shapes.surface_frame(f, u, v)
        if any(np.linalg.norm(p - q) < 4.0 for q in placed):
            continue
        placed.append(p)
        r = rng.uniform(1.2, 2.2)
        c = p + n * (r * 0.5)
        shapes.shell(eyes, shapes.ellipsoid(c, (r, r, r)), 10, 6, "eye", thick=0.3)
        eyes.cylinder(c + n * (r * 0.92), n, r * 0.55, 0.25, "iris", segments=10)
        eyes.cylinder(c + n * (r * 1.02), n, r * 0.28, 0.2, "pupil", segments=8)
        # each eyeball is a little tomato: its leaves on top
        top = c + norm(np.array([0, 1.0, 0]) - n * 0.4) * r * 0.9
        for j in range(5):
            a = j * 2 * math.pi / 5 + rng.uniform(0, 1)
            d = norm(np.array([math.cos(a), 0.15, math.sin(a)]))
            shapes.horn(eyes, top, d, r * 1.1, r * 0.35, mat="calyx", flat=0.2, up=(0, 1, 0), sections=2, around=4,
                        r1=0.05)
        eyes.cylinder(top + np.array([0, 0.3, 0]), (0, 1, 0), r * 0.15, 0.8, "calyx_dk", segments=6)
    # eight human arms propping it up, hands flat on the ground
    names = []
    for k, ang in enumerate(ARMS):
        a = math.radians(ang)
        out = np.array([math.sin(a), 0, -math.cos(a)])
        sh = C + out * (R[0] - 1.5) + np.array([0, -4.0, 0])
        elbow = sh + out * 6.0 + np.array([0, 2.0, 0])
        wrist = sh + out * 9.0 + np.array([0, -sh[1] + 1.6, 0])
        name = "arm%d" % k
        b = m.bone(name, parent="body", pivot=tuple(sh))
        path = shapes.polyline([sh, elbow, wrist])
        shapes.shell(b, shapes.loft(path, shapes.profile((0, 1.9), (0.45, 1.5), (1, 1.2)), 1.5), 8, 10, "skin",
                     thick=0.35)
        hand = wrist + out * 1.2 + np.array([0, -0.8, 0])
        shapes.shell(b, shapes.ellipsoid(hand, (1.8, 0.8, 1.8)), 8, 5, "skin_dk", thick=0.3)
        for j in range(4):
            fa = a + math.radians(-30 + j * 20)
            fd = np.array([math.sin(fa), -0.1, -math.cos(fa)])
            shapes.horn(b, hand + fd * 1.2, fd, 2.0, 0.42, mat="skin", sections=2, around=5, r1=0.3)
        names.append(name)
    geo, tex, glow, anim_path = dk.devil_paths("tomato")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=183)
    anims = animations(names)
    save_animations(anim_path, anims)
    print("tomato devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations(arms):
    A = []
    idle = Anim("idle", 2.4, loop=True)
    for i in range(9):
        t = 2.4 * i / 8
        ph = 2 * math.pi * i / 8
        idle.scale("body", t, (1 + 0.02 * math.sin(ph), 1 - 0.02 * math.sin(ph), 1 + 0.02 * math.sin(ph)))
        idle.scale("eyes", t, 1 + 0.04 * math.sin(ph * 2))
    A.append(idle)
    mv = Anim("move", 0.8, loop=True)
    for i in range(9):
        t = 0.8 * i / 8
        ph = 2 * math.pi * i / 8
        for k, b in enumerate(arms):
            grp = 1 if k % 2 == 0 else -1
            mv.rot(b, t, (grp * 22 * math.sin(ph), 0, grp * 8 * max(0, math.cos(ph))))
        mv.pos("root", t, (0, 0.8 * abs(math.sin(ph)), 0))
    A.append(mv)
    sl = Anim("slam", 0.9)
    front = [b for k, b in enumerate(arms) if k in (0, 1, 7, 6)]
    for b in front:
        sl.rot(b, 0, (0, 0, 0)).rot(b, 0.35, (-70, 0, 0), "easeOutQuad").rot(b, 0.5, (25, 0, 0), "easeInQuad")
        sl.rot(b, 0.9, (0, 0, 0))
    sl.rot("body", 0.35, (-12, 0, 0)).rot("body", 0.5, (15, 0, 0)).rot("body", 0.9, (0, 0, 0))
    A.append(sl)
    sd = Anim("seeds", 1.0)
    sd.scale("body", 0, 1.0).scale("body", 0.35, (1.12, 0.92, 1.12), "easeOutQuad")
    sd.scale("body", 0.45, (0.94, 1.08, 0.94), "easeOutQuad").scale("body", 1.0, 1.0)
    sd.rot("body", 0.35, (-8, 0, 0)).rot("body", 0.45, (10, 0, 0)).rot("body", 1.0, (0, 0, 0))
    A.append(sd)
    bu = Anim("burst", 1.1)
    bu.scale("body", 0, 1.0).scale("body", 0.5, 1.25, "easeInQuad").scale("body", 0.58, 0.9, "easeOutQuad")
    bu.scale("body", 1.1, 1.0)
    bu.scale("eyes", 0.5, 1.4).scale("eyes", 0.6, 1.0)
    A.append(bu)
    gr = Anim("grab", 1.2)
    for k, b in enumerate(arms):
        if k in (0, 7):
            for i, t in enumerate((0.3, 0.45, 0.6, 0.75, 0.9)):
                gr.rot(b, t, (-80 if i % 2 == 0 else -40, 0, 0))
            gr.rot(b, 0, (0, 0, 0)).rot(b, 1.2, (0, 0, 0))
    A.append(gr)
    A.append(Anim("drink", 1.0))
    death = Anim("death", 1.2, loop="hold_on_last_frame")
    death.scale("body", 0, 1.0).scale("body", 0.4, (1.2, 0.7, 1.2), "easeInQuad").scale("body", 1.0, (1.4, 0.35, 1.4))
    for b in arms:
        death.rot(b, 0.6, (0, 0, 60))
    death.pos("root", 1.0, (0, -4, 0))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 0.8, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("tomato_front.png"), anim, "idle", 0.0, yaw=20, pitch=10,
                       show_body=False, scale=8, center=(0, 1.3), size=(620, 620)),
        preview.render(geo, tex, preview_path("tomato_side.png"), anim, "move", 0.2, yaw=100, pitch=10,
                       show_body=False, scale=8, center=(0, 1.3), size=(620, 620)),
    ]
    return preview.contact_sheet(shots, preview_path("tomato_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
