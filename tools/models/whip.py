"""
Whip Hybrid - devil parts model, texture atlas and GeckoLib animations.

Manga reference points:
  * trigger: she snaps her fingers, mimicking the crack of a whip
  * coral-red devil head with a long, elongated chin and a lipless grin of long sharp teeth (like Chainsaw Man's)
  * whips grow out of the nape and hang down the back like hair
  * her hands are replaced by bundles of long whips, strong enough to cut a person in half

The whips are bone chains (one bone per segment) so animations can send a travelling wave down them:
windup lag -> straighten -> supersonic snap at the tip.  Rest shapes are baked into the geometry; animation
rotations are composed as matrices and converted to GeckoLib euler keys (see chain_keys).
"""
import math

import numpy as np

from common import out, preview_path, arc_point, arc_normal
from csmgen.geo import Atlas, Model, Anim, save_animations, norm, euler_for, rotate_about
from csmgen.tex import paint_atlas
from csmgen import preview, shapes


def materials():
    a = Atlas(512, 64)
    a.add("skin", kind="skin", color=(224, 96, 74))
    a.add("skin_dk", kind="skin", color=(184, 66, 54))
    a.add("skin_lt", kind="skin", color=(238, 128, 104))
    a.add("gum", kind="flesh", color=(150, 34, 44))
    a.add("mouth", kind="void", color=(46, 10, 16))
    a.add("teeth", kind="teeth", color=(244, 240, 228))
    a.add("eye", kind="void", color=(22, 10, 12))
    a.add("whip", kind="braid", color=(212, 84, 66), color2=(140, 42, 36))
    a.add("whip_dk", kind="braid", color=(176, 60, 50), color2=(110, 30, 28))
    a.add("cracker", kind="fiber", color=(246, 214, 196))
    a.add("flesh", kind="flesh", color=(160, 40, 40))
    a.add("blood", kind="blood", color=(126, 8, 12))
    return a


# ------------------------------------------------------------------------------------------ maths
def axis_rot(axis, deg):
    """3x3 rotation about `axis` (bedrock space)."""
    k = norm(axis)
    t = math.radians(deg)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * (K @ K)


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def bump(x, c, w):
    return math.exp(-((x - c) / w) ** 2)


# ------------------------------------------------------------------------------------------ head
# (y, half-width x, half-depth z, centre z): a narrow skull that runs down into a long pointed chin
PROFILE = [(19.9, 0.35, 0.45, -4.6), (20.5, 0.8, 0.8, -4.35), (21.1, 1.3, 1.15, -4.0), (21.7, 1.8, 1.5, -3.6),
           (22.3, 2.25, 1.9, -3.15), (22.9, 2.65, 2.3, -2.7), (23.5, 3.0, 2.7, -2.2), (24.1, 3.3, 3.05, -1.75),
           (24.7, 3.55, 3.4, -1.3), (25.3, 3.78, 3.7, -0.9), (25.9, 3.95, 3.95, -0.55), (26.6, 4.1, 4.15, -0.25),
           (27.4, 4.2, 4.3, 0.0), (28.2, 4.25, 4.4, 0.1), (29.0, 4.22, 4.42, 0.2), (29.8, 4.1, 4.35, 0.3),
           (30.6, 3.85, 4.15, 0.35), (31.4, 3.45, 3.8, 0.4), (32.1, 2.95, 3.3, 0.45), (32.7, 2.3, 2.65, 0.5),
           (33.2, 1.5, 1.8, 0.5), (33.6, 0.7, 0.9, 0.5)]
MOUTH = (23.9, 25.9)  # grin, y range
MOUTH_PHI = 78


def prof(y):
    ys = [p[0] for p in PROFILE]
    return tuple(float(np.interp(y, ys, [p[i] for p in PROFILE])) for i in (1, 2, 3))


def surf(y, phi, inset=0.0):
    ax, az, cz = prof(y)
    return arc_point(ax - inset, az - inset, phi, y, cz), arc_normal(ax, az, phi)


def ring_slice(bone, y0, y1, phi0, phi1, mat, inset=0.0, thick=1.0, steps=20):
    ym = (y0 + y1) / 2
    ax, az, cz = prof(ym)
    for i in range(steps):
        pa = phi0 + (phi1 - phi0) * i / steps
        pb = phi0 + (phi1 - phi0) * (i + 1) / steps
        a = arc_point(ax - inset - thick / 2, az - inset - thick / 2, pa, ym, cz)
        b = arc_point(ax - inset - thick / 2, az - inset - thick / 2, pb, ym, cz)
        n = arc_normal(ax, az, (pa + pb) / 2)
        bone.seg(a, b, thick, (y1 - y0) + 0.08, mat, up=(0, 1, 0), roll=0, overlap=0.3)
        _ = n


def build_head(m):
    m.bone("head", pivot=(0, 24, 0))
    f = m.bone("form_head", parent="head", pivot=(0, 24, 0))
    ys = [p[0] for p in PROFILE]
    y_lo, y_hi = ys[0], ys[-1]

    def head_surface(u, v):
        return surf(y_lo + (y_hi - y_lo) * v, u * 360.0)[0]

    def y_of(v):
        return y_lo + (y_hi - y_lo) * v

    def in_mouth(u, v):
        phi = u * 360.0 if u < 0.5 else u * 360.0 - 360.0
        return MOUTH[0] < y_of(v) < MOUTH[1] and abs(phi) < MOUTH_PHI

    # one smooth skin over the whole profile (a narrow skull running down into the long pointed chin)
    shapes.shell(f, head_surface, 24, 26, "skin", skip=in_mouth, thick=0.45,
                 mat_fn=lambda u, v: "skin_lt" if y_of(v) > 31.5 else "skin")
    ym = sum(MOUTH) / 2
    ring_slice(f, MOUTH[0], MOUTH[1], -MOUTH_PHI, MOUTH_PHI, "mouth", inset=0.9, thick=0.6, steps=12)
    ax, az, cz = prof(ym)
    f.cylinder((0, ym, cz), (0, 1, 0), max(min(ax, az) - 1.0, 0.3), MOUTH[1] - MOUTH[0], "skin_dk", segments=10)
    # neck: sinewy coral flesh
    f.cylinder((0, 24.2, 0.6), (0, 1, 0), 2.3, 2.2, "skin_dk", segments=10)
    for k in range(6):
        a = math.radians(k * 60 + 15)
        p0 = np.array([math.sin(a) * 2.2, 23.3, 0.6 - math.cos(a) * 2.2])
        f.seg(p0, p0 + np.array([0, 2.4, 0]) - np.array([math.sin(a), 0, -math.cos(a)]) * 0.5, 0.6, 0.6, "skin")

    # the grin: gum ridges, then long thin fangs top and bottom
    for yy, h in ((MOUTH[1] + 0.05, 0.45), (MOUTH[0] - 0.05, 0.45)):
        ring_slice(f, yy - h / 2, yy + h / 2, -MOUTH_PHI - 4, MOUTH_PHI + 4, "gum", inset=-0.12, thick=0.55,
                   steps=14)
    step = 9.0
    for k, phi in enumerate(np.arange(-MOUTH_PHI + 5, MOUTH_PHI - 4, step)):
        p, n = surf(MOUTH[1] - 0.1, phi, inset=0.35)
        L = 1.75 - 0.35 * abs(phi) / MOUTH_PHI
        f.spike(p, norm(np.array([0, -1, 0]) + n * 0.12), L, 0.5, 0.32, "teeth", steps=3, up=n)
        p2, n2 = surf(MOUTH[0] + 0.1, phi + step / 2, inset=0.35)
        if abs(phi + step / 2) < MOUTH_PHI - 4:
            f.spike(p2, norm(np.array([0, 1, 0]) + n2 * 0.12), L * 0.8, 0.45, 0.3, "teeth", steps=3, up=n2)
    # a few longer fangs at the corners, like Chainsaw Man's comb of teeth
    for s in (-1, 1):
        p, n = surf(MOUTH[1] - 0.1, s * (MOUTH_PHI - 14), inset=0.3)
        f.spike(p, norm(np.array([0, -1, 0]) + n * 0.2), 2.4, 0.6, 0.36, "teeth", steps=4, up=n)

    # narrow slanted eyes set deep in the skull
    for s in (-1, 1):
        pts = [surf(28.4 + 0.3 * i, s * (19 + 7 * i), inset=-0.32) for i in range(4)]
        for (p, n), (q, _) in zip(pts, pts[1:]):
            f.seg(p, q, 0.55, 0.6, "eye", up=n, overlap=0.2)
        p, n = pts[1]
        f.obox(p + n * 0.05, n, (0.22, 0.12, 0.22), "teeth")
    # brow ridge + cheek creases for some shape
    for s in (-1, 1):
        pts = [surf(29.7 + 0.12 * i, s * (8 + 11 * i), inset=-0.35)[0] for i in range(4)]
        f.curve(pts, 0.45, 0.3, 0.4, 0.3, "skin_dk")
        pts = [surf(26.6 - 1.1 * i, s * (50 + 4 * i), inset=-0.3)[0] for i in range(4)]
        f.curve(pts, 0.3, 0.2, 0.3, 0.2, "skin_dk")

    build_hair(m)


HAIR_ROOTS = [(145, 31.0), (180, 31.4), (215, 31.0), (160, 29.0), (200, 29.0), (172, 27.2), (188, 27.2)]
HAIR_SEGS = 6


def build_hair(m):
    """Whips growing out of the nape, hanging down her back like hair."""
    chains = []
    for k, (phi, y) in enumerate(HAIR_ROOTS):
        p, n = surf(y, phi, inset=0.35)
        d = norm(np.array([n[0] * 0.25, -1.0, n[2] * 0.45]))
        side = norm(np.cross(d, [0, 1, 0])) if abs(n[0]) > 0.05 else np.array([1.0, 0, 0])
        inward = np.cross(side, d)
        parent = "form_head"
        bones = []
        L = 2.5 - 0.1 * (k % 3)
        for i in range(HAIR_SEGS):
            name = "hair_%d_%d" % (k, i)
            b = m.bone(name, parent=parent, pivot=tuple(p))
            r = 0.46 - 0.05 * i
            q = p + d * L
            b.tube(p, q + d * 0.15, max(r, 0.16), "whip" if i % 2 == 0 else "whip_dk", segments=6)
            if i == HAIR_SEGS - 1:
                b.spike(q, d, 1.2, 0.6, 0.25, "cracker", steps=2, up=side)
            bones.append(name)
            p = q
            # hang down against the back, then flick outward at the ends
            d = norm(rotate_about(d, side, 7 if i < 3 else -11))
            L *= 0.93
            _ = inward
        chains.append(bones)
    return chains


# ------------------------------------------------------------------------------------------ arms
N_WHIPS = 4
WHIP_SEGS = 7


def arm_whips(side):
    """Rest geometry of every whip in one hand bundle: [(bones, curl_axis, curl_angles)]"""
    sgn = -1 if side == "right" else 1
    spec = []
    offs = [(-0.75, -0.75), (0.8, -0.7), (-0.7, 0.8), (0.75, 0.75)]
    for k, (dx, dz) in enumerate(offs):
        root = np.array([sgn * (6 + dx), 10.6, dz])
        h = norm(np.array([sgn * dx, 0, dz]))
        spread = norm(np.array([0, -1.0, 0]) + h * 0.16)
        axis = norm(np.cross(np.array([0, -1.0, 0]), h))
        lens = [2.25 - 0.06 * i + 0.08 * ((k * 3 + i) % 2) for i in range(WHIP_SEGS)]
        curls = [3, 4, 4, 6, 16, 22, 26] if k % 2 == 0 else [2, 3, 5, 8, 14, 24, 30]
        spec.append((k, root, spread, axis, lens, curls))
    return spec


def build_arm(m, side):
    sgn = -1 if side == "right" else 1

    def X(o):
        return sgn * o

    name = side + "_arm"
    m.bone(name, pivot=(X(5), 22, 0))
    f = m.bone("form_" + name, parent=name, pivot=(X(6), 13, 0))
    # the hand is gone: the forearm swells into a knot of coral flesh the whips grow out of
    for y0, y1, r, mat in ((14.6, 15.8, 3.05, "skin_dk"), (12.6, 14.7, 3.0, "skin"), (11.6, 12.7, 2.75, "skin"),
                           (10.9, 11.7, 2.2, "skin_dk"), (10.4, 11.0, 1.6, "gum")):
        f.cylinder((X(6), (y0 + y1) / 2, 0), (0, 1, 0), r, y1 - y0, mat, segments=10)
    # swollen sinew running down into the whip roots
    for k in range(6):
        a = math.radians(k * 60 + 30)
        rr = np.array([math.sin(a), 0, -math.cos(a)])
        pts = [np.array([X(6), 15.4 - 1.1 * i, 0]) + rr * (3.1 - 0.05 * i - (0.55 if i > 2 else 0) * (i - 2))
               for i in range(5)]
        f.curve(pts, 0.5, 0.3, 0.45, 0.3, "skin_lt")
    # torn skin edge where the human arm ends
    for k in range(8):
        a = k * 45 + 20
        rr = np.array([math.sin(math.radians(a)) * 2.9, 0, -math.cos(math.radians(a)) * 2.9])
        f.obox(np.array([X(6), 16.1, 0]) + rr, (0, 1, 0), (1.3, 0.7 + 0.3 * (k % 3), 0.3), "flesh",
               up=norm(rr))

    chains = []
    for k, root, d, axis, lens, curls in arm_whips(side):
        parent = "form_" + name
        bones = []
        p = root.copy()
        for i in range(WHIP_SEGS):
            bn = "%s_whip_%d_%d" % (side, k, i)
            b = m.bone(bn, parent=parent, pivot=tuple(p))
            q = p + d * lens[i]
            r = 0.52 - 0.05 * i
            b.tube(p, q + d * 0.14, max(r, 0.17), "whip" if i % 2 == 0 else "whip_dk", segments=6)
            if i % 2 == 1:
                b.ring(p + d * lens[i] * 0.5, d, max(r, 0.17) + 0.05, 0.12, 0.3, "whip_dk", count=6)
            if i == WHIP_SEGS - 1:
                b.spike(q, d, 1.5, 0.7, 0.3, "cracker", steps=3, up=axis)
                b.spike(q, norm(d + np.cross(axis, d) * 0.4), 1.1, 0.5, 0.25, "cracker", steps=2, up=axis)
            bones.append(bn)
            parent = bn
            p = q
            d = norm(rotate_about(d, axis, curls[i]))
        chains.append((bones, axis, curls))
    return chains


# ------------------------------------------------------------------------------------------ build
def build():
    atlas = materials()
    m = Model("csm.whip_hybrid", atlas, density=2.0, seed=41)
    build_head(m)
    m.bone("body", pivot=(0, 24, 0))
    chains = {s: build_arm(m, s) for s in ("right", "left")}
    geo = out("geo", "hybrid", "whip.geo.json")
    tex = out("textures", "hybrid", "whip.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "whip_glowmask.png"), seed=17)
    anims = animations(chains)
    anim_path = out("animations", "hybrid", "whip.animation.json")
    save_animations(anim_path, anims)
    print("whip: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


# ------------------------------------------------------------------------------------------ animation helpers
LAG_AXIS = np.array([1.0, 0, 0])   # bending about arm-local x: +deg bends toward -z (trails a forward swing)
TWIST_AXIS = np.array([0, 0, 1.0])


def chain_keys(anim, bones, fn, t0, t1, step=0.04):
    """fn(i, t) -> 3x3 rotation of segment i relative to its parent; sampled into euler keys."""
    ts = list(np.arange(t0, t1 + 1e-6, step))
    if abs(ts[-1] - t1) > 1e-6:
        ts.append(t1)
    for t in ts:
        for i, b in enumerate(bones):
            anim.rot(b, float(t), euler_for(fn(i, float(t))))


def hair_chains():
    return [["hair_%d_%d" % (k, i) for i in range(HAIR_SEGS)] for k in range(len(HAIR_ROOTS))]


def idle_sway(i, t, period, k, amp=3.0):
    w = 2 * math.pi / period
    return axis_rot(LAG_AXIS, amp * math.sin(w * t - 0.55 * i + k)) @ axis_rot(TWIST_AXIS, amp * 0.7 * math.sin(
        w * t * 1.0 - 0.45 * i + 2.1 * k))


def lash_rot(i, u, axis, curls, power=1.0):
    """Segment rotation for one whip crack; u = time relative to the moment the arm stops (seconds)."""
    lag = 13.0 * smoothstep(-0.16, -0.03, u) * (1 - smoothstep(-0.01, 0.05, u))
    wave = -24.0 * bump(u - 0.012 * i, 0.03, 0.04) * power
    settle = 5.0 * bump(u - 0.012 * i, 0.14, 0.06)
    straight = bump(u, 0.02, 0.07)
    return axis_rot(LAG_AXIS, lag + wave + settle) @ axis_rot(axis, -curls[i] * straight * power)


def animations(chains):
    A = []
    hair = hair_chains()
    allw = {s: chains[s] for s in ("right", "left")}

    # -- emerge: whips tear out of the hands and the nape, then uncurl
    e = Anim("emerge", 0.7)
    e.scale("form_head", 0, (0.75, 0.55, 0.75)).scale("form_head", 0.14, (1.06, 1.12, 1.06), "easeOutBack")
    e.scale("form_head", 0.3, 1.0, "easeInOutSine")
    for k, bones in enumerate(hair):
        t0 = 0.08 + 0.03 * k
        e.scale(bones[0], 0, 0.02).scale(bones[0], t0, 0.02).scale(bones[0], t0 + 0.18, 1.1, "easeOutBack")
        e.scale(bones[0], t0 + 0.3, 1.0)
        chain_keys(e, bones, lambda i, t, t0=t0: axis_rot(LAG_AXIS, -26 * (1 - smoothstep(t0, t0 + 0.4, t))),
                   0, 0.7, step=0.05)
    for s in ("right", "left"):
        fa = "form_%s_arm" % s
        e.scale(fa, 0, 0.4).scale(fa, 0.1, 1.15, "easeOutBack").scale(fa, 0.22, 1.0)
        for k, (bones, axis, curls) in enumerate(allw[s]):
            t0 = 0.02 + 0.035 * k
            e.scale(bones[0], 0, 0.02).scale(bones[0], t0, 0.02).scale(bones[0], t0 + 0.2, 1.12, "easeOutBack")
            e.scale(bones[0], t0 + 0.32, 1.0)
            chain_keys(e, bones, lambda i, t, t0=t0, axis=axis, curls=curls:
                       axis_rot(axis, curls[i] * 2.2 * (1 - smoothstep(t0, t0 + 0.45, t)) + 8 * bump(t, t0 + 0.35, 0.08)),
                       0, 0.7, step=0.05)
    A.append(e)

    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    r.scale("form_head", 0, 1.0).scale("form_head", 0.35, (0.75, 0.55, 0.75), "easeInBack")
    for bones in hair:
        r.scale(bones[0], 0, 1).scale(bones[0], 0.3, 0.02, "easeInBack")
    for s in ("right", "left"):
        for bones, axis, curls in allw[s]:
            chain_keys(r, bones, lambda i, t, axis=axis, curls=curls: axis_rot(axis, curls[i] * 2 * smoothstep(0, 0.25, t)),
                       0, 0.4, step=0.05)
            r.scale(bones[0], 0, 1).scale(bones[0], 0.32, 0.02, "easeInQuad")
    A.append(r)

    # -- idle: everything sways like hanging rope
    idle = Anim("idle", 2.4, loop=True)
    for k, bones in enumerate(hair):
        chain_keys(idle, bones, lambda i, t, k=k: idle_sway(i, t, 2.4, k, 2.6), 0, 2.4, step=0.1)
    for s in ("right", "left"):
        for k, (bones, axis, curls) in enumerate(allw[s]):
            chain_keys(idle, bones, lambda i, t, k=k: idle_sway(i, t, 2.4, k * 1.3 + (s == "left"), 2.2),
                       0, 2.4, step=0.1)
    A.append(idle)

    # -- lash: right, left, right (strikes at 0.2 / 0.4 / 0.6 s = server ticks 4 / 8 / 12)
    la = Anim("lash", 0.8)
    for s, strikes in (("right", (0.2, 0.6)), ("left", (0.4,))):
        for bones, axis, curls in allw[s]:
            def fn(i, t, axis=axis, curls=curls, strikes=strikes):
                R = np.eye(3)
                for ts in strikes:
                    R = R @ lash_rot(i, t - ts, axis, curls)
                return R
            chain_keys(la, bones, fn, 0, 0.8, step=0.02)
    A.append(la)

    # -- storm: arms flung out, whips straight out and trailing the spin
    st = Anim("storm", 1.3)
    for s in ("right", "left"):
        for k, (bones, axis, curls) in enumerate(allw[s]):
            def fn(i, t, axis=axis, curls=curls, k=k):
                on = smoothstep(0.1, 0.25, t) * (1 - smoothstep(1.05, 1.25, t))
                flutter = 5 * math.sin(t * 38 - i * 0.9 + k)
                return axis_rot(LAG_AXIS, on * (7 + flutter)) @ axis_rot(axis, -curls[i] * on * 0.9)
            chain_keys(st, bones, fn, 0, 1.3, step=0.04)
    for k, bones in enumerate(hair):
        chain_keys(st, bones, lambda i, t, k=k: axis_rot(LAG_AXIS, -14 * smoothstep(0.1, 0.3, t) *
                                                           (1 - smoothstep(1.0, 1.3, t)) + 4 * math.sin(t * 30 - i + k)),
                   0, 1.3, step=0.05)
    A.append(st)

    # -- snare: right whips shoot out straight, coil round the target, yank
    sn = Anim("snare", 0.7)
    for k, (bones, axis, curls) in enumerate(allw["right"]):
        def fn(i, t, axis=axis, curls=curls, k=k):
            straight = smoothstep(0.08, 0.18, t) * (1 - smoothstep(0.24, 0.3, t))
            coil = smoothstep(0.24, 0.34, t) * (1 - smoothstep(0.5, 0.7, t))
            lag = 10 * bump(t, 0.1, 0.05)
            return axis_rot(LAG_AXIS, lag - 8 * bump(t - 0.01 * i, 0.19, 0.04)) @ axis_rot(
                axis, -curls[i] * straight + (38 + 6 * k) * coil)
        chain_keys(sn, bones, fn, 0, 0.7, step=0.02)
    A.append(sn)

    # -- swing: one whip bundle lashes up at a ledge and holds taut
    sw = Anim("swing", 0.7)
    for bones, axis, curls in allw["right"]:
        chain_keys(sw, bones, lambda i, t, axis=axis, curls=curls:
                   axis_rot(axis, -curls[i] * smoothstep(0.06, 0.16, t) * (1 - smoothstep(0.45, 0.65, t)))
                   @ axis_rot(LAG_AXIS, -18 * bump(t - 0.012 * i, 0.15, 0.04)), 0, 0.7, step=0.025)
    A.append(sw)

    # -- sonic crack: both bundles overhead, then one massive crack at 0.5 s (server tick 10)
    cr = Anim("crack", 1.0)
    for s in ("right", "left"):
        for bones, axis, curls in allw[s]:
            def fn(i, t, axis=axis, curls=curls):
                wind = 16 * smoothstep(0.05, 0.35, t) * (1 - smoothstep(0.42, 0.48, t))
                return axis_rot(LAG_AXIS, wind) @ lash_rot(i, t - 0.5, axis, curls, power=1.4)
            chain_keys(cr, bones, fn, 0, 1.0, step=0.02)
    A.append(cr)

    dr = Anim("drink", 1.0)
    for bones in hair:
        chain_keys(dr, bones, lambda i, t: axis_rot(LAG_AXIS, 6 * bump(t, 0.5, 0.2)), 0, 1.0, step=0.1)
    A.append(dr)
    return A


def render_previews(geo, tex, anim):
    arms_down = {"right_arm": {"rot": (0, 0, 0.1)}, "left_arm": {"rot": (0, 0, -0.1)}}
    head_only = ("body", "right_arm", "left_arm")
    shots = [
        preview.render(geo, tex, preview_path("whip_front.png"), anim, "idle", 0.0, yaw=20, pitch=6, pose=arms_down,
                       scale=10.5, center=(0, 1.1)),
        preview.render(geo, tex, preview_path("whip_back.png"), anim, "idle", 0.6, yaw=160, pitch=8, pose=arms_down,
                       scale=10.5, center=(0, 1.1)),
        preview.render(geo, tex, preview_path("whip_head.png"), anim, "idle", 0.0, yaw=35, pitch=8,
                       show_body=False, scale=24, center=(0, 1.75), size=(640, 520), hidden=head_only),
        preview.render(geo, tex, preview_path("whip_lash.png"), anim, "lash", 0.215, yaw=70, pitch=8,
                       pose={"right_arm": {"rot": (-1.35, 0, 0)}, "left_arm": {"rot": (0, 0, -0.1)}},
                       scale=8, center=(0, 1.2)),
    ]
    return preview.contact_sheet(shots, preview_path("whip_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
