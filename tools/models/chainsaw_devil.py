"""
The Chainsaw Devil's true form - Pochita as the Hero of Hell (entity/devil/chainsaw_devil). A Chainsaw hybrid's
Hero of Hell move turns the player into this model for a while; it is also fought as a boss.

Reference points (manga, the Control Devil arc):
  * a brutish, towering, muscular devil covered all over in black armoured plates and spikes
  * the head is shaped like a chainsaw - an engine-block skull, a guide bar out of the front - with horns; it is
    featureless (no eyes) apart from a wide grin full of sharp teeth
  * each forearm is split in two at the elbow, a chainsaw coming out of each: four saws in all
  * its intestines come out of its chest and wind round its neck like a scarf, the ends trailing
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
    a.add("hide", kind="skin", color=(32, 32, 36))
    a.add("hide_dk", kind="skin", color=(18, 18, 22))
    a.add("plate", kind="metal", color=(44, 44, 50), scratches=3)
    a.add("plate_lt", kind="metal", color=(70, 70, 78), scratches=2)
    a.add("spike", kind="bone", color=(28, 28, 32))
    a.add("engine", kind="painted", color=(36, 36, 42), color2=(70, 70, 80))
    a.add("fin", kind="metal", color=(56, 56, 64), scratches=2)
    a.add("bar", kind="metal", color=(196, 198, 204), scratches=12)
    a.add("bar_rim", kind="metal", color=(110, 112, 120), scratches=4)
    a.add("cutter", kind="metal", color=(70, 72, 80), scratches=2)
    a.add("chain", kind="chain", color=(52, 54, 62))
    a.add("rivet", kind="metal", color=(150, 152, 160), scratches=1)
    a.add("teeth", kind="teeth", color=(240, 236, 224))
    a.add("mouth", kind="void", color=(22, 4, 6))
    a.add("gum", kind="flesh", color=(110, 18, 24))
    a.add("guts", kind="flesh", color=(178, 74, 84))
    a.add("guts_dk", kind="flesh", color=(122, 40, 52))
    a.add("blood", kind="blood", color=(150, 10, 14))
    a.add("claw", kind="bone", color=(20, 20, 24))
    return a


# ---------------------------------------------------------------------------------------- saws
def saw(bone, root, direction, length, height, side_up, rng, bloody=True):
    """A chainsaw guide bar from `root` along `direction`: flat faces along `side_up`, cutters round both edges."""
    d = norm(direction)
    up = norm(side_up)
    across = norm(np.cross(d, up))  # the cutting edges point along +-across
    root = np.asarray(root, dtype=float)
    mid = root + d * (length / 2)
    bone.obox(mid, d, (height, length, 0.9), "bar", up=up)
    for e in (-1, 1):
        bone.obox(mid + across * e * (height / 2 - 0.3), d, (0.55, length - 0.4, 1.0), "bar_rim", up=up)
    tip = root + d * length
    for r, k in ((height * 0.45, 0.0), (height * 0.34, 0.45), (height * 0.2, 0.8)):
        bone.obox(tip + d * k, d, (r * 2, 0.6, 0.9), "bar", up=up)
    bone.obox(root + d * 1.2, d, (0.8, 0.8, 1.1), "rivet", up=up)
    n = int(length / 1.25)
    for i in range(n):
        p = root + d * (0.8 + i * 1.25)
        for e in (-1, 1):
            edge = p + across * e * (height / 2)
            bone.obox(edge, d, (0.5, 1.1, 0.95), "chain", up=up)
            rake = norm(across * e - d * 0.45)
            bone.spike(edge + up * (0.14 if i % 2 else -0.14), rake, 1.2, 0.9, 0.34, "cutter", steps=3, up=d)
    for a in (30, 70, 110, 150):
        r = math.radians(a)
        dd = norm(across * math.cos(r) + d * math.sin(r))
        bone.spike(tip + d * 0.2 + dd * height * 0.45, dd, 1.1, 0.85, 0.32, "cutter", steps=3, up=up)
    if bloody:
        for _ in range(5):
            t = rng.uniform(0.2, 0.9)
            o = rng.uniform(-0.3, 0.3) * height
            for s in (-1, 1):
                c = root + d * (length * t) + across * o + up * s * 0.47
                bone.obox(c, d, (rng.uniform(0.6, 1.2), rng.uniform(0.8, 2.6), 0.06), "blood", up=up * s)


# ---------------------------------------------------------------------------------------- body
def limb(bone, pts, r0, r1, mat="hide", nu=10, nv=8):
    f = shapes.loft(shapes.polyline(pts), shapes.taper(r0, r1), shapes.taper(r0 * 0.92, r1 * 0.92))
    shapes.shell(bone, f, nu, nv, mat, thick=0.45)
    return f


def plates_on(bone, f, rows, per_row, v0, v1, mat="plate", size=(2.6, 2.4), lift=0.25, rng=None):
    """Overlapping armour plates scattered over a surface in rows (the black scales)."""
    for j in range(rows):
        v = v0 + (v1 - v0) * (j + 0.5) / rows
        for i in range(per_row):
            u = (i + 0.5 * (j % 2)) / per_row
            p, n, du, dv = shapes.surface_frame(f, u % 1.0, v)
            jitter = rng.uniform(0.85, 1.15) if rng is not None else 1.0
            bone.obox(p + n * lift, dv, (size[0] * jitter, size[1] * jitter, 0.5), mat, up=n)


def spikes_on(bone, f, pts_uv, length, width, mat="spike", tilt=0.35):
    for (u, v) in pts_uv:
        p, n, du, dv = shapes.surface_frame(f, u, v)
        shapes.horn(bone, p - n * 0.2, norm(n - dv * tilt), length, width, mat=mat, sections=3, around=5, r1=0.08)


def build():
    atlas = materials()
    m = Model("csm.chainsaw_devil", atlas, density=1.6, seed=331)
    rng = np.random.default_rng(331)

    root = m.bone("root", pivot=(0, 0, 0))
    waist = m.bone("waist", parent="root", pivot=(0, 24, 0))
    body = m.bone("body", parent="waist", pivot=(0, 24, 0))

    # ---- torso: a broad, muscular black chest tapering to the waist
    torso = shapes.loft(shapes.polyline([(0, 22.0, 0.5), (0, 30.0, 0.0), (0, 38.0, -0.4), (0, 44.5, 0.2)]),
                        shapes.profile((0, 5.4), (0.3, 6.2), (0.7, 9.2), (0.92, 10.0), (1, 8.4)),
                        shapes.profile((0, 4.0), (0.3, 4.2), (0.7, 5.6), (0.92, 5.4), (1, 4.2)), up=(0, 0, -1))
    shapes.shell(body, torso, 18, 10, "hide", thick=0.5)
    # pectoral and abdominal plates on the front, bigger plates over the back
    for s in (-1, 1):
        body.obox((s * 4.2, 39.0, -5.4), (0, 1, 0.1), (7.0, 5.0, 0.8), "plate", up=norm((s * 0.3, 0, -1)))
        body.obox((s * 4.4, 39.4, -5.8), (0, 1, 0.1), (5.0, 3.0, 0.5), "plate_lt", up=norm((s * 0.3, 0, -1)))
        for k in range(3):
            body.obox((s * 2.0, 33.5 - k * 3.2, -4.5 + k * 0.2), (0, 1, 0), (3.4, 2.7, 0.7), "plate",
                      up=(0, 0, -1))
    plates_on(body, torso, 4, 7, 0.25, 0.95, rng=rng, size=(3.4, 3.0))
    # the spine: a row of spikes down the back
    for k in range(6):
        y = 43.0 - k * 3.4
        shapes.horn(body, (0, y, 4.6 - 0.1 * k), (0, 0.35, 1), 3.0 - 0.25 * k, 0.9, mat="spike", sections=3,
                    around=5, r1=0.06)
    # where the guts come out of the chest
    body.obox((1.6, 36.0, -5.9), (0, 1, 0), (3.0, 3.6, 0.4), "gum", up=(0, 0, -1))

    # ---- the intestine scarf: out of the chest, round the neck, the ends trailing
    scarf = m.bone("scarf", parent="body", pivot=(0, 44, 0))

    def gut(pts, r=1.35, bulge=0.28, n=16):
        path = shapes.polyline(pts)
        rad = lambda t: r * (1 + bulge * math.sin(t * n * math.pi))
        f = shapes.loft(path, rad, rad)
        shapes.shell(scarf, f, 8, max(8, int(len(pts) * 3.2)), "guts", thick=0.4,
                     mat_fn=lambda u, v: "guts_dk" if (int(v * n) % 2 == 0 and abs(u - 0.5) < 0.18) else "guts")
        return f

    ring = [(math.sin(a) * 6.4, 45.0 + 0.6 * math.cos(a), -math.cos(a) * 5.6 + 0.4)
            for a in np.linspace(0.0, 2 * math.pi * 1.05, 14)]
    gut([(1.6, 36.2, -6.0), (2.6, 40.0, -6.8), (1.0, 43.6, -6.2)] + ring[1:], n=24)
    # one end hangs down the front, the other trails over the left shoulder and down the back
    gut([(-5.0, 44.6, -4.0), (-6.4, 40.0, -6.6), (-6.0, 34.0, -7.0), (-6.8, 28.0, -6.4), (-7.6, 23.0, -5.8)],
        r=1.25, n=12)
    gut([(5.6, 45.2, 2.0), (6.2, 42.0, 6.0), (5.0, 35.0, 7.4), (6.4, 27.0, 8.2), (5.0, 19.0, 9.6)], r=1.2, n=12)

    # ---- arms: huge shoulders, each forearm split at the elbow into two saws
    for side, name in ((-1, "right_arm"), (1, "left_arm")):
        sh = np.array([side * 11.0, 42.5, 0.0])
        arm = m.bone(name, parent="body", pivot=tuple(sh))
        el = sh + np.array([side * 2.6, -12.0, 0.8])
        shoulder = shapes.ellipsoid(sh + np.array([side * 0.6, 0.4, 0]), (4.6, 4.2, 4.4))
        shapes.shell(arm, shoulder, 10, 7, "plate", thick=0.45)
        spikes_on(arm, shoulder, [(0.25 if side > 0 else 0.75, 0.75), (0.25 if side > 0 else 0.75, 0.55),
                                  (0.15 if side > 0 else 0.85, 0.65)], 4.2, 1.1)
        upper = limb(arm, [sh, sh + (el - sh) * 0.5 + np.array([side * 0.6, 0, 0]), el], 3.8, 3.1)
        plates_on(arm, upper, 3, 5, 0.15, 0.9, rng=rng, size=(2.6, 2.6))
        shapes.shell(arm, shapes.ellipsoid(el, (3.2, 3.0, 3.2)), 8, 6, "plate_lt", thick=0.4)
        # the split: two forearms fork out of the elbow, a saw bursting out of the end of each
        for fork, (dz, dx) in enumerate(((-2.1, 0.6), (2.0, -0.4))):
            fname = "%s_%s" % (name, "front" if fork == 0 else "back")
            fb = m.bone(fname, parent=name, pivot=tuple(el))
            wrist = el + np.array([side * dx, -8.0, dz])
            fore = limb(fb, [el + np.array([0, -0.5, dz * 0.25]), el + np.array([side * dx * 0.5, -4.0, dz * 0.7]),
                             wrist], 2.5, 2.1, nu=8, nv=6)
            plates_on(fb, fore, 2, 4, 0.2, 0.9, rng=rng, size=(2.2, 2.4))
            spikes_on(fb, fore, [(0.25 if side > 0 else 0.75, 0.45)], 2.2, 0.7, tilt=0.6)
            # the saw housing at the wrist, then the bar
            fb.cbox(wrist + np.array([0, -0.4, 0]), (3.8, 2.4, 3.4), "engine")
            saw(fb, wrist + np.array([0, -1.2, 0]), norm((side * 0.12, -1.0, -0.18 if fork == 0 else 0.05)), 17.0,
                3.6, (1, 0, 0), rng)

    # ---- legs: armoured, spiked knees, clawed feet
    for side, name in ((-1, "right_leg"), (1, "left_leg")):
        hip = np.array([side * 4.8, 23.5, 0.3])
        leg = m.bone(name, parent="root", pivot=tuple(hip))
        knee = hip + np.array([side * 0.8, -11.5, -1.4])
        ankle = np.array([side * 5.8, 2.6, 0.6])
        thigh = limb(leg, [hip, (hip + knee) / 2 + np.array([side * 0.4, 0, 0]), knee], 4.4, 3.4)
        plates_on(leg, thigh, 3, 6, 0.1, 0.9, rng=rng, size=(3.0, 2.8))
        shin = limb(leg, [knee, (knee + ankle) / 2 + np.array([0, 0, -0.4]), ankle], 3.4, 2.4)
        plates_on(leg, shin, 3, 5, 0.1, 0.95, rng=rng, size=(2.8, 2.6), mat="plate_lt")
        shapes.shell(leg, shapes.ellipsoid(knee + np.array([0, 0, -1.2]), (2.8, 2.6, 2.4)), 8, 6, "plate",
                     thick=0.4)
        shapes.horn(leg, knee + np.array([0, 0.6, -2.8]), (0, 0.4, -1), 3.2, 1.0, mat="spike", sections=3, around=5,
                    r1=0.06)
        foot = shapes.ellipsoid(np.array([side * 5.9, 1.2, -1.8]), (2.7, 1.3, 4.4), e_lat=0.6, e_lon=0.7)
        shapes.shell(leg, foot, 10, 5, "plate", thick=0.4)
        for k in range(3):
            x = side * 5.9 + (k - 1) * 1.6
            shapes.horn(leg, (x, 0.9, -5.6), (0, -0.25, -1), 2.2, 0.55, mat="claw", sections=3, around=5, r1=0.05,
                        bend_axis=(1, 0, 0), bend=-40)

    # ---- the head: a chainsaw with horns, no eyes, a wide grin
    head = m.bone("head", parent="body", pivot=(0, 45, 0))
    look = m.bone("look", parent="head", pivot=(0, 46, 0))
    look.cylinder((0, 45.8, 0.4), (0, 1, 0), 3.0, 2.4, "hide_dk", segments=10)  # neck
    skull = shapes.ellipsoid((0, 51.2, 1.4), (5.0, 5.2, 5.2), e_lat=0.55, e_lon=0.6)
    shapes.shell(look, skull, 14, 9, "engine", thick=0.45)
    for y in np.arange(47.8, 55.0, 1.0):
        for s in (-1, 1):
            look.box((s * 5.0, y, -0.4), (s * 5.55, y + 0.4, 4.0), "fin")
    # the sloped front cover the bar comes out of (the upper face)
    cover = shapes.loft(shapes.polyline([(0, 55.6, -0.8), (0, 53.8, -4.0), (0, 51.6, -5.6)]),
                        shapes.profile((0, 3.6), (0.5, 4.4), (1, 4.6)), shapes.profile((0, 1.6), (0.5, 2.2), (1, 1.8)),
                        up=(0, 0.3, -1))
    shapes.shell(look, cover, 12, 6, "plate", thick=0.45)
    look.cbox((0, 53.6, -4.9), (2.8, 3.2, 1.6), "engine")
    saw(look, (0, 53.8, -5.0), norm((0, 0.08, -1)), 20.0, 4.4, (1, 0, 0), rng)
    # horns off the top of the skull, curving back
    for s in (-1, 1):
        shapes.horn(look, (s * 3.6, 55.0, 1.2), (s * 0.75, 1.0, 0.25), 9.5, 1.5, mat="spike", sections=6, around=6,
                    r1=0.08, bend_axis=(0, 0, s * 1.0), bend=-45 * s)
        shapes.horn(look, (s * 4.8, 51.0, 3.4), (s * 0.6, 0.2, 1), 3.4, 0.8, mat="spike", sections=3, around=5,
                    r1=0.06)
    for k in range(4):
        shapes.horn(look, (0, 56.0 - k * 1.8, 4.0 + k * 1.0), (0, 0.5, 1), 2.6, 0.7, mat="spike", sections=3,
                    around=5, r1=0.06)
    # the grin: a wide dark mouth right round the front, a comb of long teeth above, a jaw of teeth below
    for i in range(15):
        a = math.radians(-78 + 156 * i / 14)
        p = np.array([math.sin(a) * 5.0, 49.2, 1.0 - math.cos(a) * 5.3])
        n = norm((math.sin(a), 0, -math.cos(a)))
        look.obox(p - n * 0.2, (0, 1, 0), (1.3, 2.4, 0.4), "mouth", up=n)
        look.spike(p + np.array([0, 1.1, 0]) + n * 0.05, norm((0, -1, 0) + n * 0.08), 1.9 - 0.6 * abs(math.sin(a)),
                   0.75, 0.3, "teeth", steps=3, up=n)
    jaw = m.bone("jaw", parent="look", pivot=(0, 48.6, 2.6))
    jf = shapes.loft(shapes.polyline([(0, 47.6, 3.6), (0, 47.0, -1.0), (0, 47.3, -4.0)]),
                     shapes.profile((0, 4.4), (0.6, 4.2), (1, 2.6)), shapes.profile((0, 1.2), (1, 0.9)),
                     up=(0, 1, 0))
    shapes.shell(jaw, jf, 10, 6, "plate", thick=0.4)
    for i in range(13):
        a = math.radians(-72 + 144 * i / 12)
        p = np.array([math.sin(a) * 4.4, 48.0, 1.0 - math.cos(a) * 4.8])
        n = norm((math.sin(a), 0, -math.cos(a)))
        jaw.obox(p - n * 0.4, (0, 1, 0), (1.2, 1.0, 0.5), "gum", up=n)
        jaw.spike(p + np.array([0, -0.2, 0]), norm((0, 1, 0) + n * 0.05), 1.6 - 0.5 * abs(math.sin(a)), 0.7, 0.3,
                  "teeth", steps=3, up=n)
    # a couple of rivets and the spark-plug boot on top
    look.cylinder((0, 56.6, 2.4), (0, 1, 0), 0.6, 1.0, "hide_dk", segments=6)
    for s in (-1, 1):
        look.cbox((s * 4.4, 53.4, -2.2), (0.6, 0.6, 0.6), "rivet")

    geo, tex, glow, anim_path = dk.devil_paths("chainsaw_devil")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=333)
    anims = animations()
    save_animations(anim_path, anims)
    print("chainsaw devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


# ---------------------------------------------------------------------------------------- animations
FORKS = ("right_arm_front", "right_arm_back", "left_arm_front", "left_arm_back")


def animations():
    A = []
    idle = Anim("idle", 3.0, loop=True)
    for i in range(9):
        t = 3.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("body", t, (2.0 * math.sin(ph), 0, 0))
        idle.rot("head", t, (-2.5 * math.sin(ph), 3 * math.sin(ph * 0.5), 0))
        idle.rot("jaw", t, (4 + 3 * math.sin(ph * 2), 0, 0))
        idle.rot("right_arm", t, (-6 + 3 * math.sin(ph), 0, 10))
        idle.rot("left_arm", t, (-6 - 3 * math.sin(ph), 0, -10))
        idle.rot("scarf", t, (2 * math.sin(ph), 0, 1.5 * math.cos(ph)))
        for k, f in enumerate(FORKS):
            idle.rot(f, t, (-12 if "front" in f else 8, 0, (2 if k % 2 else -2) * math.sin(ph * 2 + k)))
    A.append(idle)

    mv = Anim("move", 1.1, loop=True)
    for i in range(9):
        t = 1.1 * i / 8
        ph = 2 * math.pi * i / 8
        s = math.sin(ph)
        mv.rot("right_leg", t, (26 * s, 0, 0))
        mv.rot("left_leg", t, (-26 * s, 0, 0))
        mv.rot("right_arm", t, (-20 * s - 8, 0, 10))
        mv.rot("left_arm", t, (20 * s - 8, 0, -10))
        mv.rot("waist", t, (8, 5 * s, 0))
        mv.rot("head", t, (-6, -4 * s, 0))
        mv.rot("scarf", t, (10 + 4 * math.sin(2 * ph), 0, 3 * s))
        mv.pos("root", t, (0, -1.0 * abs(math.cos(ph)), 0))
        for k, f in enumerate(FORKS):
            mv.rot(f, t, (-12 if "front" in f else 8, 0, 0))
    A.append(mv)

    # Four-Saw Rend (20 ticks): cuts land on ticks 4, 8, 12, 16 - right, left, right, left
    rd = Anim("rend", 1.0)
    for k, (t, arm) in enumerate(((0.2, "right_arm"), (0.4, "left_arm"), (0.6, "right_arm"), (0.8, "left_arm"))):
        s = 1 if arm == "right_arm" else -1
        rd.rot(arm, t - 0.12, (-150, s * -30, s * 30), "easeInQuad")
        rd.rot(arm, t, (-60, s * 40, s * -10), "easeOutQuad")
        rd.rot(arm, t + 0.12, (-40, s * 10, s * 10))
        rd.rot("waist", t, (6, s * -18, 0), "easeOutQuad")
    rd.rot("right_arm", 1.0, (0, 0, 10)).rot("left_arm", 1.0, (0, 0, -10)).rot("waist", 1.0, (0, 0, 0))
    rd.rot("jaw", 0.1, (20, 0, 0)).rot("jaw", 0.9, (20, 0, 0)).rot("jaw", 1.0, (4, 0, 0))
    for f in FORKS:
        rd.rot(f, 0.0, (-12 if "front" in f else 8, 0, 0)).rot(f, 0.5, (-30 if "front" in f else 20, 0, 0))
        rd.rot(f, 1.0, (-12 if "front" in f else 8, 0, 0))
    A.append(rd)

    # Rev Charge (22 ticks): head down, bar forward, arms swept back; runs ticks 3-18
    ch = Anim("charge", 1.1)
    ch.rot("waist", 0, (0, 0, 0)).rot("waist", 0.15, (38, 0, 0), "easeOutQuad").rot("waist", 0.9, (38, 0, 0))
    ch.rot("waist", 1.1, (0, 0, 0))
    ch.rot("head", 0.15, (-30, 0, 0)).rot("head", 0.9, (-30, 0, 0)).rot("head", 1.1, (0, 0, 0))
    for arm, s in (("right_arm", 1), ("left_arm", -1)):
        ch.rot(arm, 0.15, (50, 0, s * 25), "easeOutQuad").rot(arm, 0.9, (50, 0, s * 25)).rot(arm, 1.1, (0, 0, s * 10))
    for i in range(8):
        t = 0.15 + i * 0.1
        sg = 1 if i % 2 == 0 else -1
        ch.rot("right_leg", t, (40 * sg, 0, 0)).rot("left_leg", t, (-40 * sg, 0, 0))
    ch.rot("right_leg", 1.1, (0, 0, 0)).rot("left_leg", 1.1, (0, 0, 0))
    A.append(ch)

    # Chain Whip (26 ticks): arms flung out wide (the chains sweep round on ticks 6-13), then yanked in on tick 17
    cw = Anim("chains", 1.3)
    for arm, s in (("right_arm", 1), ("left_arm", -1)):
        cw.rot(arm, 0, (0, 0, s * 10)).rot(arm, 0.25, (-80, 0, s * 80), "easeOutQuad").rot(arm, 0.65, (-80, 0, s * 80))
        cw.rot(arm, 0.85, (-100, s * 40, s * 20), "easeInQuad").rot(arm, 1.3, (0, 0, s * 10))
    cw.rot("waist", 0.3, (0, 0, 0)).rot("waist", 0.5, (0, 180, 0), "easeInOutQuad").rot("waist", 0.65, (0, 350, 0))
    cw.rot("waist", 0.66, (0, -10, 0)).rot("waist", 0.85, (10, 0, 0)).rot("waist", 1.3, (0, 0, 0))
    cw.rot("scarf", 0.5, (20, 0, 30)).rot("scarf", 1.0, (0, 0, 0))
    A.append(cw)

    # Devour (28 ticks): the prey is seized on tick 6, held to the mouth, bitten on 12 and 17, swallowed on 22
    dv = Anim("devour", 1.4)
    dv.rot("right_arm", 0, (0, 0, 10)).rot("right_arm", 0.3, (-100, 20, 10), "easeOutQuad")
    dv.rot("right_arm", 0.5, (-130, 40, 0)).rot("right_arm", 1.2, (-130, 40, 0)).rot("right_arm", 1.4, (0, 0, 10))
    dv.rot("left_arm", 0.3, (-70, -20, -20)).rot("left_arm", 1.2, (-90, -30, -10)).rot("left_arm", 1.4, (0, 0, -10))
    for t, open_ in ((0.45, 55), (0.6, 0), (0.72, 55), (0.85, 0), (1.0, 40), (1.1, 0)):
        dv.rot("jaw", t, (open_, 0, 0), "easeInQuad" if open_ == 0 else "easeOutQuad")
    dv.rot("head", 0.45, (-20, 0, 0)).rot("head", 0.6, (8, 0, 0)).rot("head", 0.72, (-18, 0, 0))
    dv.rot("head", 0.85, (10, 0, 0)).rot("head", 1.1, (-10, 0, 0)).rot("head", 1.4, (0, 0, 0))
    dv.rot("waist", 0.6, (10, 0, 0)).rot("waist", 1.4, (0, 0, 0))
    A.append(dv)

    # the roar (30 ticks): head thrown back, jaw wide, arms spread (tick 10 is the scream)
    ro = Anim("roar", 1.5)
    ro.rot("head", 0, (0, 0, 0)).rot("head", 0.4, (-40, 0, 0), "easeOutQuad").rot("head", 1.1, (-38, 0, 0))
    ro.rot("head", 1.5, (0, 0, 0))
    ro.rot("jaw", 0.35, (60, 0, 0), "easeOutQuad").rot("jaw", 1.1, (58, 0, 0)).rot("jaw", 1.5, (4, 0, 0))
    ro.rot("waist", 0.4, (-12, 0, 0)).rot("waist", 1.1, (-10, 0, 0)).rot("waist", 1.5, (0, 0, 0))
    for arm, s in (("right_arm", 1), ("left_arm", -1)):
        ro.rot(arm, 0.4, (-40, 0, s * 70), "easeOutQuad").rot(arm, 1.1, (-45, 0, s * 72)).rot(arm, 1.5, (0, 0, s * 10))
    for i in range(10):
        t = 0.4 + i * 0.07
        ro.rot("body", t, (0, 0, 1.5 if i % 2 else -1.5))
    ro.rot("body", 1.5, (0, 0, 0))
    A.append(ro)

    dr = Anim("drink", 1.0)
    dr.rot("right_arm", 0, (0, 0, 10)).rot("right_arm", 0.3, (-120, 30, 0)).rot("right_arm", 0.8, (-120, 30, 0))
    dr.rot("right_arm", 1.0, (0, 0, 10))
    dr.rot("jaw", 0.3, (40, 0, 0)).rot("jaw", 0.5, (0, 0, 0)).rot("jaw", 0.65, (40, 0, 0)).rot("jaw", 0.8, (0, 0, 0))
    A.append(dr)

    death = Anim("death", 2.0, loop="hold_on_last_frame")
    death.rot("waist", 0, (0, 0, 0)).rot("waist", 0.5, (-15, 0, 0)).rot("waist", 1.3, (80, 0, 0), "easeInQuad")
    death.pos("root", 0, (0, 0, 0)).pos("root", 0.5, (0, -3, 0)).pos("root", 1.3, (0, -18, -10), "easeInQuad")
    death.rot("right_leg", 0.5, (-60, 0, 0)).rot("left_leg", 0.5, (-60, 0, 0))
    death.rot("right_leg", 1.3, (-5, 0, 0)).rot("left_leg", 1.3, (-10, 0, 0))
    death.rot("head", 0.5, (-40, 0, 0)).rot("jaw", 0.5, (60, 0, 0)).rot("head", 1.3, (-20, 20, 0))
    A.append(death)

    mf = dk.scale_in("manifest", "root", 1.2, from_scale=0.3)
    mf.rot("head", 0.5, (-35, 0, 0)).rot("jaw", 0.5, (55, 0, 0)).rot("head", 1.2, (0, 0, 0)).rot("jaw", 1.2, (4, 0, 0))
    for arm, s in (("right_arm", 1), ("left_arm", -1)):
        mf.rot(arm, 0.5, (-30, 0, s * 60)).rot(arm, 1.2, (0, 0, s * 10))
    A.append(mf)
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    bg = (170, 150, 140)
    shots = [
        preview.render(geo, tex, preview_path("chainsaw_devil_front.png"), anim, "idle", 0.0, yaw=20, pitch=6,
                       show_body=False, scale=3.2, center=(0, 1.8), size=(620, 700), bg=bg),
        preview.render(geo, tex, preview_path("chainsaw_devil_side.png"), anim, "idle", 0.0, yaw=95, pitch=6,
                       show_body=False, scale=3.2, center=(0, 1.8), size=(620, 700), bg=bg),
        preview.render(geo, tex, preview_path("chainsaw_devil_back.png"), anim, "idle", 0.0, yaw=200, pitch=6,
                       show_body=False, scale=3.2, center=(0, 1.8), size=(620, 700), bg=bg),
        preview.render(geo, tex, preview_path("chainsaw_devil_face.png"), anim, "roar", 0.8, yaw=-25, pitch=4,
                       show_body=False, scale=7.0, center=(0, 3.0), size=(620, 620), bg=bg),
        preview.render(geo, tex, preview_path("chainsaw_devil_rend.png"), anim, "rend", 0.2, yaw=30, pitch=8,
                       show_body=True, scale=3.0, center=(0, 1.8), size=(620, 700), bg=bg),
        preview.render(geo, tex, preview_path("chainsaw_devil_charge.png"), anim, "charge", 0.5, yaw=70, pitch=8,
                       show_body=False, scale=3.0, center=(0, 1.8), size=(620, 700), bg=bg),
    ]
    return preview.contact_sheet(shots, preview_path("chainsaw_devil_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
