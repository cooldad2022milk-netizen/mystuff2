"""
Cosmo (Cosmos Fiend) - fiend parts model, texture atlas and GeckoLib animations.

Reference points:
  * spiky pink hair gathered into pigtails held by red bands
  * heart-shaped pupils, orange to yellow-red; the right eye tends to dangle from its socket
  * much of her upper-right skull is gone, baring the brain; a length of it spills past her face and is knotted
    into a small bow
  * she only ever says "Halloween"; her power forces a mind to understand the whole universe at once
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm, bezier
from csmgen.tex import paint_atlas
from csmgen import preview, shapes


def materials():
    a = Atlas(512, 64)
    a.add("brain", kind="flesh", color=(236, 150, 170))
    a.add("brain_dk", kind="flesh", color=(196, 104, 128))
    a.add("skull", kind="bone", color=(232, 222, 206))
    a.add("wound", kind="blood", color=(140, 18, 30))
    a.add("hair", kind="fiber", color=(246, 128, 188))
    a.add("hair_dk", kind="fiber", color=(210, 86, 150))
    a.add("band", kind="rubber", color=(214, 30, 40))
    a.add("eye", kind="bone", color=(246, 244, 238))
    a.add("iris", kind="glow", color=(250, 150, 40), color2=(255, 220, 110), emissive=True)
    a.add("nerve", kind="flesh", color=(200, 110, 110))
    a.add("cosmos", kind="glow", color=(120, 60, 200), color2=(255, 170, 230), emissive=True)
    a.add("star", kind="glow", color=(255, 230, 170), color2=(255, 255, 255), emissive=True)
    a.add("planet", kind="glow", color=(110, 170, 255), color2=(230, 180, 255), emissive=True)
    return a


def brain_lumps(b, center, rx, ry, rz, n, rng, mats=("brain", "brain_dk")):
    """A mass of rounded gyri."""
    c = np.asarray(center, dtype=float)
    for k in range(n):
        u = rng.uniform(-1, 1)
        a = rng.uniform(0, 2 * math.pi)
        p = c + np.array([math.cos(a) * rx * math.sqrt(1 - u * u), abs(u) * ry, math.sin(a) * rz * math.sqrt(1 - u * u)])
        r = rng.uniform(0.6, 1.0)
        # a rounded fold (gyrus): an elongated blob lying along the surface
        d = norm([rng.uniform(-1, 1), rng.uniform(-0.3, 0.3), rng.uniform(-1, 1)])
        frame = __import__("csmgen.geo", fromlist=["frame_from"]).frame_from(d, (0, 1, 0))
        shapes.shell(b, shapes.ellipsoid(p, (r, rng.uniform(1.0, 1.5), r * 0.9), frame=frame), 6, 4, mats[k % 2],
                     thick=0.3)


def build_head(m):
    rng = np.random.default_rng(5)
    m.bone("head", pivot=(0, 24, 0))
    # the missing upper-right of the skull and the brain bared in it (her right = -x)
    br = m.bone("base_brain", parent="head", pivot=(-2.2, 32, 0))
    br.box((-4.35, 29.4, -3.6), (-0.4, 32.35, 3.6), "wound")
    brain_lumps(br, (-2.4, 31.6, 0.0), 2.0, 1.6, 3.0, 26, rng)
    for k in range(10):
        a = k / 10 * math.pi * 2
        br.obox((-2.4 + math.cos(a) * 2.3, 32.2, math.sin(a) * 3.6), (0, 1, 0), (0.7, 0.8, 0.9), "skull",
                up=(math.cos(a), 0, math.sin(a)))
    # a length of brain spilling down past her face, knotted into a small bow
    P = [np.array([-3.2, 31.4, -3.4]), np.array([-4.6, 29.6, -4.9]), np.array([-3.4, 27.2, -5.0]),
         np.array([-2.6, 25.4, -4.8])]
    pts = [bezier(*P, t) for t in np.linspace(0, 1, 9)]
    for p, q in zip(pts, pts[1:]):
        br.tube(p, q, 0.45, "brain", segments=6)
    knot = pts[-1]
    br.cylinder(knot, (0, 0, 1), 0.55, 0.7, "brain_dk", segments=6)
    for s in (-1, 1):
        for i in range(5):
            a = math.radians(i * 72)
            p = knot + np.array([s * (0.9 + 0.7 * math.cos(a)), 0.6 * math.sin(a), -0.1])
            br.cbox(p, (0.55, 0.55, 0.5), "brain")
        br.obox(knot + np.array([s * 0.5, -0.9, 0]), (s * 0.4, -1, 0), (0.45, 1.3, 0.4), "brain_dk", up=(0, 0, -1))

    # the right eye, dangling out of its socket on the optic nerve; heart-shaped pupil
    ey = m.bone("base_eye", parent="head", pivot=(-2.0, 28.2, -4.1))
    ey.box((-2.9, 27.6, -4.15), (-1.1, 28.8, -4.02), "wound")
    nerve = [np.array([-2.0, 28.0, -4.2]), np.array([-2.3, 27.0, -4.9]), np.array([-2.2, 25.8, -4.9])]
    for p, q in zip(nerve, nerve[1:]):
        ey.tube(p, q, 0.22, "nerve", segments=4)
    c = np.array([-2.2, 25.0, -4.95])
    shapes.shell(ey, shapes.ellipsoid(c, (1.0, 1.0, 0.95)), 10, 6, "eye", thick=0.3)
    for dx, dy in ((-0.25, 0.15), (0.25, 0.15), (0, -0.2), (-0.12, -0.02), (0.12, -0.02)):
        ey.cbox(c + np.array([dx, dy, -1.12]), (0.4, 0.4, 0.14), "iris")

    # spiky pink pigtails held by red bands
    for s in (-1, 1):
        pt = m.bone("base_pigtail_" + ("right" if s < 0 else "left"), parent="head", pivot=(s * 4.2, 30.4, 1.6))
        # the gathered hair under the band, then a burst of stiff spikes
        shapes.shell(pt, shapes.ellipsoid((s * 4.7, 30.4, 1.6), (1.0, 1.25, 1.25)), 8, 5, "hair", thick=0.3)
        pt.ring((s * 4.75, 30.4, 1.6), (s * 1, 0, 0), 1.42, 0.4, 0.7, "band", count=12)
        tuft = __import__("random").Random(31 if s < 0 else 37)
        for k in range(13):
            a = math.radians(-80 + k * 13.3)
            spread = 0.55 + 0.35 * tuft.random()
            d = norm([s * 1.0, math.sin(a) * spread - 0.35, math.cos(a) * spread * 0.9 + 0.25])
            root = np.array([s * 5.2, 30.4, 1.6]) + d * 0.3
            shapes.horn(pt, root, d, 2.4 + tuft.random() * 1.9, 0.6 + 0.25 * tuft.random(),
                        mat="hair" if k % 3 else "hair_dk", sections=4, around=5, r1=0.05, thick=0.3,
                        bend_axis=(0, 0, 1), bend=-s * 18)

    # opened cosmos: the brain lit from within and a halo of stars and planets orbiting her head
    g = m.bone("form_brain_glow", parent="base_brain", pivot=(-2.4, 32, 0))
    brain_lumps(g, (-2.4, 31.9, 0.0), 1.8, 1.4, 2.7, 10, rng, mats=("cosmos", "cosmos"))
    halo = m.bone("form_halo", parent="head", pivot=(0, 34.5, 0))
    for k in range(12):
        a = k / 12 * math.pi * 2
        p = np.array([math.cos(a) * 7.5, 34.5 + math.sin(a * 2) * 0.8, math.sin(a) * 7.5])
        if k % 4 == 0:
            halo.cylinder(p, (0, 1, 0), 0.9, 1.6, "planet", segments=8)
        else:
            halo.cbox(p, (0.6, 0.6, 0.6), "star")
    halo.ring((0, 34.5, 0), (0, 1, 0), 7.5, 0.1, 0.15, "cosmos", count=24)


def build():
    atlas = materials()
    m = Model("csm.cosmos_fiend", atlas, density=2.0, seed=97)
    build_head(m)
    m.bone("body", pivot=(0, 24, 0))
    m.bone("right_arm", pivot=(-5, 22, 0))
    m.bone("left_arm", pivot=(5, 22, 0))
    geo = out("geo", "hybrid", "cosmos.geo.json")
    tex = out("textures", "hybrid", "cosmos.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "cosmos_glowmask.png"), seed=59)
    anims = animations()
    anim_path = out("animations", "hybrid", "cosmos.animation.json")
    save_animations(anim_path, anims)
    print("cosmos: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    e = Anim("emerge", 0.8)
    e.scale("form_halo", 0, 0.1).scale("form_halo", 0.3, 1.15, "easeOutBack").scale("form_halo", 0.45, 1.0)
    e.scale("form_brain_glow", 0, 0.5).scale("form_brain_glow", 0.2, 1.2, "easeOutBack").scale("form_brain_glow", 0.35, 1)
    A.append(e)
    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    r.scale("form_halo", 0, 1).scale("form_halo", 0.3, 0.1, "easeInBack")
    A.append(r)
    idle = Anim("idle", 4.0, loop=True)
    for i in range(9):
        t = i * 0.5
        idle.rot("form_halo", t, (0, -i * 45, 0))
    for t, a in ((0, 0), (1.0, 8), (2.0, 0), (3.0, -8), (4.0, 0)):
        idle.rot("base_eye", t, (a, 0, a * 0.6))
    for side in ("right", "left"):
        for t, a in ((0, 0), (2.0, 4 if side == "left" else -4), (4.0, 0)):
            idle.rot("base_pigtail_" + side, t, (0, 0, a))
    idle.scale("form_brain_glow", 0, 1).scale("form_brain_glow", 2.0, 1.08, "easeInOutSine")
    idle.scale("form_brain_glow", 4.0, 1, "easeInOutSine")
    A.append(idle)

    def pulse(anim, t0, amount=1.25):
        anim.scale("form_brain_glow", t0, 1).scale("form_brain_glow", t0 + 0.1, amount).scale("form_brain_glow", t0 + 0.4, 1)
        for t, a in ((t0, 0), (t0 + 0.08, 18), (t0 + 0.3, -6), (t0 + 0.5, 0)):
            anim.rot("base_eye", t, (a, 0, 0))

    hw = Anim("halloween", 0.7)
    pulse(hw, 0.25)
    A.append(hw)
    ao = Anim("all_out", 1.6)
    ao.scale("form_halo", 0, 1).scale("form_halo", 0.6, 0.4, "easeInQuad").scale("form_halo", 0.72, 1.8, "easeOutBack")
    ao.scale("form_halo", 1.4, 1.0)
    for i in range(9):
        ao.rot("form_halo", i * 0.2, (0, -i * 80, 0))
    pulse(ao, 0.65, 1.5)
    A.append(ao)
    kn = Anim("knowledge", 1.0)
    pulse(kn, 0.35)
    A.append(kn)
    co = Anim("collapse", 0.8)
    pulse(co, 0.35, 1.4)
    A.append(co)
    A.append(Anim("drink", 1.0))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("cosmos_front.png"), anim, "idle", 0, yaw=20, pitch=6,
                       hidden=("form_halo", "form_brain_glow"), show_head=True, scale=20, center=(0, 1.7), size=(640, 520)),
        preview.render(geo, tex, preview_path("cosmos_side.png"), anim, "idle", 0, yaw=70, pitch=10,
                       hidden=("form_halo", "form_brain_glow"), show_head=True, scale=20, center=(0, 1.8), size=(640, 520)),
        preview.render(geo, tex, preview_path("cosmos_open.png"), anim, "idle", 1.0, yaw=30, pitch=14, show_head=True,
                       scale=12, center=(0, 1.6)),
    ]
    return preview.contact_sheet(shots, preview_path("cosmos_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
