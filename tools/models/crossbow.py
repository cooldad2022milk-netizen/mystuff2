"""
Crossbow Hybrid (Quanxi) - devil parts model, texture atlas and GeckoLib animations.

Manga reference points:
  * trigger: she pulls an arrow out of her RIGHT eye socket (normally hidden under an eyepatch)
  * pointy, featureless metallic head; her teeth harden into arrows running along the head
  * wide curved horns shaped like a bow sweep out from the sides of the head
  * arrowheads jut out of the neck
  * metallic arms, glove-like flesh on the forearms, each bearing a spike-adorned crossbow
    whose bolts punch perfectly round holes through whatever they hit
"""
import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm, bezier
from csmgen.tex import paint_atlas
from csmgen import preview
import poses


def materials():
    a = Atlas(512, 64)
    a.add("metal", kind="metal", color=(122, 126, 136))
    a.add("metal_dk", kind="metal", color=(54, 56, 64), scratches=5)
    a.add("metal_lt", kind="metal", color=(200, 204, 212))
    a.add("edge", kind="metal", color=(232, 234, 238), scratches=3)
    a.add("glove", kind="skin", color=(214, 176, 168))
    a.add("glove_dk", kind="flesh", color=(150, 96, 96))
    a.add("string", kind="fiber", color=(236, 232, 222))
    a.add("shaft", kind="metal", color=(70, 64, 60), scratches=2)
    a.add("fletch", kind="feather", color=(240, 238, 232), color2=(150, 18, 22))
    a.add("blood", kind="blood", color=(126, 8, 12))
    a.add("patch", kind="rubber", color=(20, 20, 22))
    a.add("glow", kind="glow", color=(255, 70, 40), color2=(255, 230, 190), emissive=True)
    return a


HEAD_PROFILE = [(25.0, 3.3), (26.0, 3.8), (27.0, 4.05), (28.0, 4.1), (29.0, 4.0), (30.0, 3.75), (31.0, 3.4),
                (32.0, 3.0), (33.0, 2.6), (34.0, 2.2), (35.0, 1.8), (36.0, 1.4), (37.0, 1.0), (37.8, 0.65),
                (38.4, 0.35)]
HCZ = 0.2


def head_r(y):
    ys = [p[0] for p in HEAD_PROFILE]
    rs = [p[1] for p in HEAD_PROFILE]
    return float(np.interp(y, ys, rs))


def arrow(bone, tail, tip, mats=("shaft", "edge", "fletch"), r=0.22, head_len=1.3, head_w=0.95, fletch=True,
          up=(0, 1, 0)):
    tail = np.asarray(tail, dtype=float)
    tip = np.asarray(tip, dtype=float)
    d = norm(tip - tail)
    shaft_end = tip - d * head_len
    bone.tube(tail, shaft_end, r, mats[0], segments=4, up=up)
    bone.spike(shaft_end - d * 0.1, d, head_len + 0.1, head_w, 0.3, mats[1], steps=3, up=up)
    bone.spike(shaft_end - d * 0.1, d, head_len * 0.8, head_w * 0.8, 0.3, mats[1], steps=2, up=np.cross(d, up))
    if fletch:
        for k in range(3):
            side = np.cross(d, up) if k == 0 else (np.asarray(up) if k == 1 else -np.asarray(up))
            side = norm(side - np.dot(side, d) * d) if np.linalg.norm(side) > 1e-6 else norm(np.cross(d, [1, 0, 0]))
            bone.obox(tail + d * 1.0 + side * 0.4, d, (0.1, 1.8, 0.7), mats[2], up=side)


# ---------------------------------------------------------------------------------------- head
def build_head(m):
    m.bone("head", pivot=(0, 24, 0))
    f = m.bone("form_head", parent="head", pivot=(0, 24, 0))
    f.cylinder((0, 24.3, 0.3), (0, 1, 0), 2.25, 1.8, "metal_dk", segments=8)
    for i, (y, r) in enumerate(HEAD_PROFILE):
        h = 1.06 if i < len(HEAD_PROFILE) - 3 else 0.7
        f.cylinder((0, y, HCZ), (0, 1, 0), r, h, "metal", segments=10)
    # blade ridge down the face and the back of the skull
    for zs in (-1, 1):
        pts = [np.array([0, y, HCZ + zs * (head_r(y) + 0.05)]) for y in np.linspace(25.6, 38.2, 9)]
        f.curve(pts, 0.45, 0.25, 0.5, 0.3, "edge")
    f.spike((0, 38.1, HCZ), (0, 1, 0), 2.4, 0.75, 0.75, "edge", steps=4)
    # teeth turned into arrowheads, running up both edges of the head like serrations
    for s in (-1, 1):
        for k, y in enumerate(np.arange(25.6, 36.2, 1.25)):
            r = head_r(y)
            base = np.array([s * (r - 0.2), y, HCZ - 0.2])
            d = norm([s * 1.0, 0.55 + 0.04 * k, -0.15])
            f.spike(base, d, 1.35 - 0.05 * k, 0.95, 0.28, "edge", steps=3, up=(0, 0, -1))
    # arrowheads bursting out of the neck
    ns = m.bone("form_neck_spikes", parent="form_head", pivot=(0, 24.5, 0.3))
    for k in range(9):
        a = np.radians(k * 40 + 20)
        radial = np.array([np.sin(a), 0, -np.cos(a)])
        base = np.array([0, 24.6, 0.3]) + radial * 2.1
        ns.spike(base, norm(radial + np.array([0, -0.35, 0])), 1.6, 0.8, 0.28, "edge", steps=3, up=(0, 1, 0))

    # bow-shaped horns (their own bones so they can unfold)
    for side, s in (("right", -1), ("left", 1)):
        hb = m.bone("form_horn_" + side, parent="form_head", pivot=(s * 3.8, 28.2, 0.3))
        P = [(s * 3.6, 28.2, 0.3), (s * 8.8, 28.4, -2.4), (s * 12.8, 31.0, -1.2), (s * 14.4, 33.8, 3.4)]
        pts = [bezier(*P, t) for t in np.linspace(0, 1, 11)]
        hb.curve(pts, 1.3, 0.55, 1.9, 0.7, "metal_dk")
        edge_pts = [p + np.array([0, 0.75 - 0.4 * i / 10, 0]) for i, p in enumerate(pts)]
        hb.curve(edge_pts, 0.6, 0.3, 0.35, 0.2, "edge")
        for t in (0.3, 0.5, 0.7):
            p = bezier(*P, t)
            tan = norm(bezier(*P, t + 0.01) - p)
            fwd = norm(np.cross(tan, [0, 1, 0]) * -s)
            hb.spike(p, norm(fwd + np.array([0, 0.3, 0])), 1.2, 0.7, 0.3, "edge", steps=2, up=tan)
        tip = np.array(P[3])
        hb.obox(tip + np.array([0, 0.3, 0]), (0, 1, 0), (0.8, 1.2, 0.8), "edge")
    bs = m.bone("form_bowstring", parent="form_head", pivot=(0, 33.8, 3.4))
    bs.seg((-14.4, 33.8, 3.4), (14.4, 33.8, 3.4), 0.24, 0.24, "string")

    # human form: eyepatch over the right eye (the arrow is hidden underneath)
    p = m.bone("human_eyepatch", parent="head", pivot=(0, 28, -4))
    p.box((-3.3, 26.9, -4.28), (-0.7, 29.3, -4.0), "patch")
    p.box((-0.7, 28.9, -4.2), (4.2, 29.5, -4.0), "patch")
    p.box((-4.25, 28.9, -4.2), (-3.3, 29.5, -4.0), "patch")
    for s in (-1, 1):
        p.box((s * 4.0, 28.9, -4.2), (s * 4.22, 29.5, 4.2), "patch")
    p.box((-4.2, 28.9, 4.0), (4.2, 29.5, 4.22), "patch")


# ---------------------------------------------------------------------------------------- arms
def build_arm(m, side):
    sgn = -1 if side == "right" else 1

    def X(o):
        return sgn * o

    name = side + "_arm"
    m.bone(name, pivot=(X(5), 22, 0))
    f = m.bone("form_" + name, parent=name, pivot=(X(6), 22, 0))

    # metallic shoulder / upper arm / elbow
    f.box((X(3.8), 21.3, -2.45), (X(8.45), 24.55, 2.45), "metal_dk")
    f.box((X(4.3), 24.5, -1.95), (X(7.95), 25.05, 1.95), "metal")
    f.spike((X(7.4), 24.8, 0), norm([sgn * 0.6, 1, 0]), 1.8, 0.9, 0.9, "edge", steps=3)
    f.spike((X(7.6), 24.2, -1.4), norm([sgn * 0.8, 0.6, -0.3]), 1.3, 0.7, 0.7, "edge", steps=2)
    f.cylinder((X(6), 19.4, 0), (0, 1, 0), 1.98, 4.0, "metal", segments=8)
    for y in (20.4, 18.3):
        f.ring((X(6), y, 0), (0, 1, 0), 2.0, 0.3, 0.35, "metal_dk", count=8)
    f.cylinder((X(6), 17.2, 0), (1, 0, 0), 1.45, 3.9, "metal_dk", segments=8)
    # glove-like flesh forearm with armour plates
    f.cylinder((X(6), 14.3, 0), (0, 1, 0), 2.16, 5.4, "glove", segments=10)
    f.ring((X(6), 11.8, 0), (0, 1, 0), 2.18, 0.35, 0.5, "metal_dk", count=10)
    f.box((X(7.9), 12.6, -1.6), (X(8.3), 16.4, 1.6), "metal")
    f.box((X(4.1), 9.7, -1.75), (X(7.9), 11.7, 1.75), "metal_dk")
    for k in range(4):
        z0 = -1.6 + k * 0.85
        f.box((X(4.35), 8.9, z0), (X(5.2), 9.8, z0 + 0.7), "metal")
    # bow-shaped blade fin on the outside of the forearm
    P = [(X(8.2), 17.0, 0.3), (X(10.6), 15.2, 0.4), (X(10.4), 11.8, 0.4), (X(8.3), 10.2, 0.2)]
    pts = [bezier(*P, t) for t in np.linspace(0, 1, 8)]
    f.curve(pts, 0.55, 0.35, 1.2, 0.6, "metal_dk")
    for t in (0.25, 0.5, 0.75):
        p = bezier(*P, t)
        f.spike(p, norm([sgn * 1, -0.2, 0]), 1.1, 0.6, 0.3, "edge", steps=2, up=(0, 1, 0))
    # arrows jutting out of the back of the forearm
    for yy, zz, d in ((15.8, 1.5, (sgn * 0.5, 0.35, 1)), (13.6, 1.8, (sgn * 0.8, 0.1, 1)),
                      (16.4, -0.4, (sgn * 1, 0.5, 0.2))):
        base = np.array([X(6.9), yy, zz])
        arrow(f, base - norm(d) * 1.0, base + norm(d) * 4.0, fletch=False)

    # ---- the crossbow, mounted on the front of the forearm (points forward when aiming)
    xb = name.replace("arm", "xbow")
    c = m.bone(xb, parent="form_" + name, pivot=(X(6), 13, -2.6))
    c.box((X(5.3), 6.8, -3.3), (X(6.7), 16.8, -2.1), "metal_dk")
    c.box((X(5.72), 6.8, -3.46), (X(6.28), 16.4, -3.3), "metal")
    c.box((X(5.5), 15.4, -2.25), (X(6.5), 16.2, -1.9), "metal")
    c.box((X(5.5), 12.0, -2.25), (X(6.5), 12.8, -1.9), "metal")
    c.box((X(5.15), 12.8, -3.75), (X(6.85), 13.6, -3.2), "metal_lt")
    c.box((X(5.2), 6.2, -3.35), (X(6.8), 6.9, -2.05), "metal")
    for k in range(4):
        c.spike((X(6.7), 8.0 + k * 2.2, -2.7), (sgn, 0, 0), 0.9, 0.5, 0.4, "edge", steps=2, up=(0, 0, -1))
        c.spike((X(5.3), 8.0 + k * 2.2, -2.7), (-sgn, 0, 0), 0.7, 0.5, 0.4, "edge", steps=2, up=(0, 0, -1))
    # prod (limbs) - separate bones so they can flex when firing
    tips = {}
    for part, o_sign in (("out", 1), ("in", -1)):
        lb = m.bone("%s_limb_%s" % (xb, part), parent=xb, pivot=(X(6), 8.2, -2.7))
        P = [(X(6 + o_sign * 0.6), 8.0, -2.7), (X(6 + o_sign * 2.4), 8.2, -2.6),
             (X(6 + o_sign * 4.0), 9.0, -2.35), (X(6 + o_sign * 4.9), 10.4, -2.25)]
        pts = [bezier(*P, t) for t in np.linspace(0, 1, 8)]
        lb.curve(pts, 0.95, 0.5, 1.05, 0.55, "metal_dk", up=(0, 0, -1))
        edge = [p + np.array([0, -0.45, 0]) for p in pts]
        lb.curve(edge, 0.35, 0.22, 0.4, 0.25, "edge", up=(0, 0, -1))
        for t in (0.35, 0.65, 0.9):
            p = bezier(*P, t)
            lb.spike(p, norm([sgn * o_sign * 0.3, -1, 0]), 1.0, 0.55, 0.35, "edge", steps=2, up=(0, 0, -1))
        tips[part] = np.array(P[3])
        lb.obox(tips[part], (0, 1, 0), (0.7, 0.8, 0.7), "metal_lt")
    # drawn string (V to the nut); scaled flat when the bolt is loosed
    sb = m.bone(xb + "_string", parent=xb, pivot=(X(6), 10.4, -2.25))
    nut = np.array([X(6), 13.0, -3.55])
    sb.seg(tips["out"], nut, 0.22, 0.22, "string", overlap=0.1)
    sb.seg(tips["in"], nut, 0.22, 0.22, "string", overlap=0.1)
    # loaded bolt
    bb = m.bone(xb + "_bolt", parent=xb, pivot=(X(6), 13.0, -3.7))
    arrow(bb, (X(6), 13.3, -3.72), (X(6), 5.2, -3.72), r=0.26, head_len=1.5, head_w=1.1, up=(0, 0, -1))
    # glowing overcharge (Piercing Bolt)
    fx = m.bone("fx_charge_" + side, parent=xb, pivot=(X(6), 9, -3.7))
    fx.cylinder((X(6), 9.2, -3.72), (0, 1, 0), 0.55, 8.2, "glow", segments=6)
    fx.spike((X(6), 5.4, -3.72), (0, -1, 0), 2.2, 1.6, 0.6, "glow", steps=3, up=(0, 0, -1))


def build_trigger(m):
    """Arrow held in the right fist while drawing it out of the eye (orientation solved by IK)."""
    q = poses.quanxi_pull()
    d = q["arrow_dir"]
    grip = np.array([-6.0, 12.6, 0.0])
    t = m.bone("trig_right_arrow", parent="right_arm", pivot=tuple(grip))
    tip = grip + d * q["embed"]
    tail = grip - d * 3.4
    arrow(t, tail, tip, r=0.24, head_len=1.4, head_w=1.0, up=(0, 0, 1))
    # the part that was buried in the socket comes out bloody
    t.tube(grip + d * 3.3, tip - d * 1.3, 0.3, "blood", segments=4, up=(0, 0, 1))


def build():
    atlas = materials()
    m = Model("csm.crossbow_hybrid", atlas, density=2.0, seed=21)
    build_head(m)
    m.bone("body", pivot=(0, 24, 0))
    build_arm(m, "right")
    build_arm(m, "left")
    build_trigger(m)
    geo = out("geo", "hybrid", "crossbow.geo.json")
    tex = out("textures", "hybrid", "crossbow.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "crossbow_glowmask.png"), seed=9)
    anims = animations()
    anim_path = out("animations", "hybrid", "crossbow.animation.json")
    save_animations(anim_path, anims)
    print("crossbow: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


# ---------------------------------------------------------------------------------------- animations
def animations():
    A = []
    XB = ("right_xbow", "left_xbow")

    e = Anim("emerge", 0.8)
    e.scale("form_head", 0, (0.7, 0.35, 0.7)).scale("form_head", 0.2, (1.05, 1.15, 1.05), "easeOutBack")
    e.scale("form_head", 0.34, 1.0, "easeInOutSine")
    e.scale("form_neck_spikes", 0, 0.1).scale("form_neck_spikes", 0.12, 0.1).scale("form_neck_spikes", 0.26, 1.2,
                                                                                     "easeOutBack")
    e.scale("form_neck_spikes", 0.36, 1.0)
    for side, s in (("right", -1), ("left", 1)):
        hb = "form_horn_" + side
        e.rot(hb, 0, (0, s * 80, s * -40)).rot(hb, 0.15, (0, s * 80, s * -40))
        e.rot(hb, 0.45, (0, s * -6, s * 4), "easeOutBack").rot(hb, 0.6, (0, 0, 0), "easeInOutSine")
        e.scale(hb, 0, 0.2).scale(hb, 0.3, 1.0, "easeOutQuad")
    e.scale("form_bowstring", 0, (0.02, 1, 1)).scale("form_bowstring", 0.42, (0.02, 1, 1))
    e.scale("form_bowstring", 0.6, (1, 1, 1), "easeOutQuad")
    for i, side in enumerate(("right", "left")):
        o = 0.05 * i
        fa = "form_%s_arm" % side
        e.scale(fa, 0, 0.6).scale(fa, 0.14 + o, 1.08, "easeOutBack").scale(fa, 0.3 + o, 1.0)
        xb = "%s_xbow" % side
        e.scale(xb, 0, (1, 0.05, 1)).scale(xb, 0.18 + o, (1, 0.05, 1)).scale(xb, 0.36 + o, (1, 1.1, 1),
                                                                               "easeOutBack")
        e.scale(xb, 0.46 + o, (1, 1, 1))
        for part, sg in (("out", 1), ("in", -1)):
            lb = "%s_limb_%s" % (xb, part)
            e.rot(lb, 0, (0, 0, 0)).rot(lb, 0.36 + o, (0, 0, 0))
            e.scale(lb, 0, (0.05, 1, 1)).scale(lb, 0.36 + o, (0.05, 1, 1))
            e.scale(lb, 0.55 + o, (1.1, 1, 1), "easeOutBack").scale(lb, 0.65 + o, (1, 1, 1))
        e.scale(xb + "_string", 0, 0).scale(xb + "_string", 0.55 + o, 0).scale(xb + "_string", 0.62 + o, 1)
        e.pos(xb + "_bolt", 0, (0, 6, 0)).pos(xb + "_bolt", 0.6 + o, (0, 6, 0))
        e.pos(xb + "_bolt", 0.75 + o, (0, 0, 0), "easeOutQuad")
        e.scale(xb + "_bolt", 0, 0).scale(xb + "_bolt", 0.58 + o, 0).scale(xb + "_bolt", 0.6 + o, 1)
    A.append(e)

    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    r.scale("form_head", 0, 1.0).scale("form_head", 0.4, (0.7, 0.3, 0.7), "easeInBack")
    for side, s in (("right", -1), ("left", 1)):
        r.rot("form_horn_" + side, 0, (0, 0, 0)).rot("form_horn_" + side, 0.3, (0, s * 80, s * -40), "easeInQuad")
        r.scale("form_%s_arm" % side, 0.1, 1.0).scale("form_%s_arm" % side, 0.4, 0.55, "easeInQuad")
        r.scale("%s_xbow" % side, 0, (1, 1, 1)).scale("%s_xbow" % side, 0.25, (1, 0.05, 1), "easeInBack")
    r.scale("form_bowstring", 0, 1).scale("form_bowstring", 0.15, (0.02, 1, 1))
    A.append(r)

    idle = Anim("idle", 3.0, loop=True)
    for side, s in (("right", -1), ("left", 1)):
        hb = "form_horn_" + side
        idle.rot(hb, 0, (0, 0, 0)).rot(hb, 1.5, (0, s * -2.5, s * 1.5), "easeInOutSine")
        idle.rot(hb, 3.0, (0, 0, 0), "easeInOutSine")
    idle.scale("form_bowstring", 0, 1).scale("form_bowstring", 1.5, (0.985, 1, 1), "easeInOutSine")
    idle.scale("form_bowstring", 3.0, 1, "easeInOutSine")
    A.append(idle)

    def fire(anim, xb, t0):
        for part, sg in (("out", 1), ("in", -1)):
            lb = "%s_limb_%s" % (xb, part)
            anim.rot(lb, t0, (0, 0, 0)).rot(lb, t0 + 0.04, (8, 0, sg * (-9 if xb.startswith("right") else 9)))
            anim.rot(lb, t0 + 0.12, (-3, 0, sg * (3 if xb.startswith("right") else -3)), "easeOutQuad")
            anim.rot(lb, t0 + 0.24, (0, 0, 0), "easeInOutSine")
        st = xb + "_string"
        anim.scale(st, t0, 1).scale(st, t0 + 0.03, (1, 0.05, 0.05)).scale(st, t0 + 0.22, (1, 0.05, 0.05))
        anim.scale(st, t0 + 0.32, 1, "easeOutQuad")
        bo = xb + "_bolt"
        anim.scale(bo, t0, 1).scale(bo, t0 + 0.02, 0).scale(bo, t0 + 0.24, 0).scale(bo, t0 + 0.26, 1)
        anim.pos(bo, t0, (0, 0, 0)).pos(bo, t0 + 0.25, (0, 5, 0)).pos(bo, t0 + 0.4, (0, 0, 0), "easeOutQuad")
        anim.rot(xb, t0, (0, 0, 0)).rot(xb, t0 + 0.04, (-6, 0, 0)).rot(xb, t0 + 0.18, (0, 0, 0), "easeOutQuad")

    v = Anim("volley", 0.62)
    fire(v, "right_xbow", 0.12)
    fire(v, "left_xbow", 0.32)
    A.append(v)

    ch = Anim("charge", 1.35)
    for side in ("right",):
        xb = side + "_xbow"
        for part, sg in (("out", 1), ("in", -1)):
            lb = "%s_limb_%s" % (xb, part)
            ch.rot(lb, 0, (0, 0, 0)).rot(lb, 0.85, (-10, 0, sg * 6), "easeInQuad")
        ch.pos(xb + "_string", 0, (0, 0, 0)).pos(xb + "_string", 0.85, (0, 1.4, 0), "easeInQuad")
        fx = "fx_charge_" + side
        ch.scale(fx, 0, 0.2).scale(fx, 0.85, 1.25, "easeInQuad")
        for k in range(10):
            t = 0.2 + k * 0.065
            ch.rot(xb, t, ((-1) ** k * 1.2 * (k / 10), 0, (-1) ** (k + 1) * 0.8 * (k / 10)))
        ch.rot(xb, 0.87, (0, 0, 0))
        fire(ch, xb, 0.9)
        ch.pos(xb + "_string", 0.9, (0, 0, 0))
        ch.scale(fx, 0.9, 1.3).scale(fx, 0.95, 0)
    A.append(ch)

    st = Anim("storm", 1.5)
    for k in range(4):
        fire(st, XB[k % 2], 0.2 + k * 0.2)
    A.append(st)

    fl = Anim("flash", 0.45)
    for side, s in (("right", -1), ("left", 1)):
        hb = "form_horn_" + side
        fl.rot(hb, 0, (0, 0, 0)).rot(hb, 0.08, (-10, s * 25, 0), "easeOutQuad").rot(hb, 0.3, (-10, s * 25, 0))
        fl.rot(hb, 0.45, (0, 0, 0), "easeInOutSine")
    A.append(fl)

    dr = Anim("drink", 1.0)
    dr.scale("form_neck_spikes", 0, 1).scale("form_neck_spikes", 0.3, 1.25, "easeOutBack")
    dr.scale("form_neck_spikes", 1.0, 1.0, "easeInOutSine")
    A.append(dr)

    # trigger: the drawn arrow is flicked away and dissolves once it's out
    pull = Anim("pull_arrow", 1.5)
    pull.scale("trig_right_arrow", 0, 1).scale("trig_right_arrow", 0.95, 1)
    pull.scale("trig_right_arrow", 1.1, 0, "easeInQuad")
    A.append(pull)
    return A


def render_previews(geo, tex, anim):
    q = poses.quanxi_pull()
    shots = [
        preview.render(geo, tex, preview_path("crossbow_front.png"), anim, "idle", 0.0, yaw=25, pitch=8,
                       show_arms=False, hidden=("trig_right_arrow", "human_eyepatch", "fx_charge_right",
                                                "fx_charge_left"), scale=11, center=(0, 1.25)),
        preview.render(geo, tex, preview_path("crossbow_aim.png"), anim, "volley", 0.14, yaw=-40, pitch=12,
                       show_arms=False, pose={"right_arm": {"rot": (-1.5, 0.05, 0)},
                                              "left_arm": {"rot": (-1.5, -0.05, 0)}},
                       hidden=("trig_right_arrow", "human_eyepatch", "fx_charge_right", "fx_charge_left"),
                       scale=11, center=(0, 1.25)),
    ]
    g = q["frames"]["grab"]
    shots.append(preview.render(geo, tex, preview_path("crossbow_trigger.png"), None, None, 0, yaw=35, pitch=5,
                                pose={"right_arm": {"rot": tuple(g["rot"]),
                                                    "pos": tuple(np.array([-5, 2, 0]) + g["shift"])},
                                      "head": {"rot": poses.QX_HEAD}},
                                hidden=[b for b in ("form_head", "form_right_arm", "form_left_arm",
                                                    "fx_charge_right", "fx_charge_left")],
                                show_arms=True, show_head=True, scale=26, center=(0, 1.55), size=(640, 520)))
    shots.append(preview.render(geo, tex, preview_path("crossbow_head.png"), anim, "idle", 0, yaw=20, pitch=15,
                                show_body=False, scale=20, center=(0, 1.95), size=(640, 520),
                                hidden=("trig_right_arrow", "human_eyepatch", "body", "right_arm", "left_arm")))
    return preview.contact_sheet(shots, preview_path("crossbow_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
