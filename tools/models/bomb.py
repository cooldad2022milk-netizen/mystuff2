"""
Bomb Hybrid (Reze) - devil parts model, texture atlas and GeckoLib animations, plus the thrown bomb-head entity.

Manga / figure reference points:
  * trigger: she hooks a finger through the grenade pin hidden under her choker and pulls it -
    she goes off on the spot and walks out of the fireball as the Bomb Devil
  * head: a "Fat Man" style bomb casing - a glossy black egg lying front-to-back with a bolted seam band,
    a spiky box-fin tail sticking out of the back of the head and a grille of square, angular teeth low on the front
  * a thin, ribbed neck
  * forearms wrapped in bomb fuses whose wicks burn at the wrists
  * dynamite belt and a fuse-and-dynamite apron round the waist
  * abilities: explosive punches / kicks, a flicked spark, blast propulsion, torpedo arm, throwing her own head
  * weakness: she cannot detonate while soaked

Bone naming contract with HybridPartRenderer: form_ / fx_torpedo_ / prop_ (choker, worn while human) /
human_pin (on the choker) / trig_pin (carried in the right fist once pulled, see computeHandleTarget).
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm, rotate_about
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import poses


def materials():
    a = Atlas(512, 64)
    a.add("casing", kind="gloss", color=(40, 40, 48))
    a.add("casing_lt", kind="gloss", color=(62, 62, 72))
    a.add("band", kind="metal", color=(70, 70, 78), scratches=4)
    a.add("bolt", kind="metal", color=(150, 150, 158), scratches=2)
    a.add("fin", kind="gloss", color=(40, 40, 46))
    a.add("teeth", kind="teeth", color=(232, 228, 214))
    a.add("mouth", kind="void", color=(26, 8, 10))
    a.add("neck", kind="rubber", color=(34, 32, 36))
    a.add("neck_flesh", kind="flesh", color=(120, 40, 44))
    a.add("fuse", kind="fuse", color=(150, 116, 70), color2=(82, 60, 36))
    a.add("fuse_dk", kind="fuse", color=(80, 70, 56), color2=(44, 38, 30))
    a.add("cord", kind="rubber", color=(146, 112, 68))
    a.add("cord_lt", kind="rubber", color=(170, 136, 86))
    a.add("cord_dk", kind="rubber", color=(98, 74, 46))
    a.add("wick", kind="glow", color=(255, 120, 20), color2=(255, 238, 170), emissive=True)
    a.add("dynamite", kind="painted", color=(178, 34, 28), color2=(120, 20, 18))
    a.add("dyn_cap", kind="painted", color=(214, 196, 150), color2=(160, 140, 100))
    a.add("strap", kind="rubber", color=(30, 28, 30))
    a.add("buckle", kind="metal", color=(186, 170, 110), scratches=2)
    a.add("choker", kind="rubber", color=(18, 18, 20))
    a.add("pin", kind="metal", color=(206, 208, 214), scratches=3)
    a.add("torpedo", kind="painted", color=(88, 94, 86), color2=(54, 58, 52))
    a.add("torpedo_band", kind="stripes", color=(200, 36, 30), color2=(230, 220, 200))
    a.add("prop", kind="metal", color=(190, 150, 70), scratches=3)
    a.add("blood", kind="blood", color=(126, 8, 12))
    return a


# ------------------------------------------------------------------------------------------ bomb casing
EGG_C = np.array([0.0, 29.6, 0.2])   # egg centre (bedrock px); the egg lies along z, nose at -z
EGG_R = (4.7, 4.5)                     # radius x, y at the widest point
EGG_ZF, EGG_ZB = -5.4, 6.2              # front / back of the casing (z)
EGG_ZW = -0.6                           # widest slice (fat front, tapering back like Fat Man)


def egg_scale(z):
    """Relative radius of the casing at depth z (1.0 at the widest slice)."""
    if z <= EGG_ZW:
        u = (z - EGG_ZW) / (EGG_ZF - EGG_ZW)
    else:
        u = (z - EGG_ZW) / (EGG_ZB - EGG_ZW)
        u = u ** 1.35
    return math.sqrt(max(0.0, 1 - min(1.0, u) ** 2))


def egg_point(z, phi, c, grow=0.0):
    s = egg_scale(z)
    return np.array([c[0] + (EGG_R[0] * s + grow) * math.sin(math.radians(phi)),
                     c[1] + (EGG_R[1] * s + grow) * math.cos(math.radians(phi)), c[2] + z])


def zring(bone, c, z0, z1, mat, thick=0.9, steps=22, grow=0.0, phi0=0.0, phi1=360.0):
    zm = (z0 + z1) / 2
    s = egg_scale(zm)
    if s < 0.05:
        return
    for i in range(steps):
        pa = phi0 + (phi1 - phi0) * i / steps
        pb = phi0 + (phi1 - phi0) * (i + 1) / steps
        a = egg_point(zm, pa, c, grow - thick / 2)
        b = egg_point(zm, pb, c, grow - thick / 2)
        radial = norm(np.array([math.sin(math.radians((pa + pb) / 2)), math.cos(math.radians((pa + pb) / 2)), 0]))
        bone.seg(a, b, abs(z1 - z0) + 0.1, thick, mat, up=radial, overlap=0.3)


MOUTH_PHI = (118, 242)   # the teeth grille sits low on the front (phi measured from the top, clockwise)


def build_casing(bone, c, detail=True):
    """The Fat Man casing + box tail, centred on egg centre c (a bone may be the hybrid head or the entity)."""
    zs = np.linspace(EGG_ZF + 0.12, EGG_ZB - 0.1, 23)
    for z0, z1 in zip(zs, zs[1:]):
        zm = (z0 + z1) / 2
        mat = "casing_lt" if zm < -3.5 else "casing"
        if zm < -3.2 and zm > -5.0:
            # leave the mouth opening on the lower front
            zring(bone, c, z0, z1, mat, steps=24, phi0=MOUTH_PHI[1] - 360, phi1=MOUTH_PHI[0])
        else:
            zring(bone, c, z0, z1, mat, steps=24)
        s = egg_scale(zm)
        if s > 0.2:
            bone.cylinder(c + np.array([0, 0, zm]), (0, 0, 1), min(EGG_R) * s - 1.0, abs(z1 - z0) + 0.1, "casing",
                          segments=8)
    # nose cap
    bone.cylinder(c + np.array([0, 0, EGG_ZF + 0.1]), (0, 0, 1), 1.3, 0.35, "casing_lt", segments=10)
    # bolted seam band round the widest point + a thinner band near the back
    for zb, w, gz in ((EGG_ZW - 0.3, 0.9, 0.25), (3.4, 0.5, 0.18)):
        zring(bone, c, zb - w / 2, zb + w / 2, "band", thick=0.5, steps=26, grow=gz)
        if detail:
            for k in range(16 if w > 0.6 else 0):
                phi = k * 22.5 + 11.25
                p = egg_point(zb, phi, c, 0.45)
                bone.obox(p, (0, 0, 1), (0.42, 0.45, 0.42), "bolt",
                          up=norm(np.array([math.sin(math.radians(phi)), math.cos(math.radians(phi)), 0])))
    # the teeth: a row of square blocks top and bottom inside the opening
    zt = -4.15
    mouth_back = c + np.array([0, -2.15, -3.15])
    bone.box(mouth_back + np.array([-3.4, -1.3, 0.0]), mouth_back + np.array([3.4, 1.3, 0.5]), "mouth")
    bone.box(c + np.array([-3.5, -3.55, -4.4]), c + np.array([3.5, -3.15, -2.9]), "mouth")
    for row, (y0, y1) in enumerate(((-1.05, -2.1), (-3.3, -2.25))):
        n = 7
        for k in range(n):
            x = -3.0 + 6.0 * (k + 0.5) / n
            s = egg_scale(zt)
            # follow the curve of the casing so the grille wraps round the front
            half_w = EGG_R[0] * s * 0.95
            z_off = 0.9 * (x / half_w) ** 2
            top = max(y0, y1)
            bot = min(y0, y1)
            bone.box(c + np.array([x - 0.36, bot, zt - 0.35 + z_off]), c + np.array([x + 0.36, top, zt + 0.55 + z_off]),
                     "teeth")
        _ = row
    # tail: cone out of the back, box fin shroud with cross braces and spikes on the corners
    tb = c + np.array([0, 0, EGG_ZB - 0.3])
    bone.taper(tb, (0, 0, 1), 3.2, 2.3, 1.1, "fin", steps=3, segments=10)
    zf0, zf1 = EGG_ZB + 0.9, EGG_ZB + 5.0
    S = 4.3
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if sx:
            bone.box(c + np.array([sx * S - 0.2, -S, zf0]), c + np.array([sx * S + 0.2, S, zf1]), "fin")
        else:
            bone.box(c + np.array([-S, sy * S - 0.2, zf0]), c + np.array([S, sy * S + 0.2, zf1]), "fin")
    for k in range(4):
        a = math.radians(45 + 90 * k)
        corner = c + np.array([math.cos(a) * S * 1.414, math.sin(a) * S * 1.414, 0])
        mid = c + np.array([0, 0, 0])
        for zz in (zf0 + 0.6, zf1 - 0.6):
            p0 = mid + np.array([0, 0, zz])
            p1 = corner + np.array([0, 0, zz])
            bone.seg(p0 + (p1 - p0) * 0.28, p1 - (p1 - p0) * 0.06, 0.3, 0.3, "band", up=(0, 0, 1))
        # vertical fin plates inside the box (the angled "California parachute" vanes)
        dirv = np.array([math.cos(a), math.sin(a), 0])
        bone.obox(c + dirv * S * 0.72 + np.array([0, 0, (zf0 + zf1) / 2]), dirv, (0.18, S * 0.9, zf1 - zf0 - 0.4),
                  "fin", up=(0, 0, 1))
        # spikes on the rear corners
        tip = corner + np.array([0, 0, zf1])
        bone.spike(tip - np.array([0, 0, 0.4]), norm(dirv + np.array([0, 0, 1.3])), 2.2, 0.8, 0.8, "band", steps=3,
                   up=(0, 0, 1))
    for zz in (zf0, zf1):
        for sx in (-1, 1):
            for sy in (-1, 1):
                bone.cbox(c + np.array([sx * S, sy * S, zz]), (0.7, 0.7, 0.7), "bolt")


def build_head(m):
    m.bone("head", pivot=(0, 24, 0))
    f = m.bone("form_head", parent="head", pivot=(0, 24, 0))
    # thin, ribbed neck
    n = m.bone("form_neck", parent="form_head", pivot=(0, 24, 0.4))
    n.cylinder((0, 24.6, 0.4), (0, 1, 0), 1.35, 2.4, "neck_flesh", segments=8)
    for k in range(5):
        n.cylinder((0, 23.9 + 0.5 * k, 0.4), (0, 1, 0), 1.72 - 0.05 * k, 0.26, "neck", segments=10)
    s = m.bone("bomb_skull", parent="form_head", pivot=(0, 25.4, 0.4))
    build_casing(s, EGG_C)

    # human form: black choker; the grenade pin ring dangles from the front of it
    ch = m.bone("prop_choker", parent="head", pivot=(0, 24.4, 0))
    ch.box((-4.24, 24.0, -4.24), (4.24, 24.9, -3.98), "choker")
    ch.box((-4.24, 24.0, 3.98), (4.24, 24.9, 4.24), "choker")
    ch.box((-4.24, 24.0, -3.98), (-3.98, 24.9, 3.98), "choker")
    ch.box((3.98, 24.0, -3.98), (4.24, 24.9, 3.98), "choker")
    ch.box((-0.5, 23.95, -4.36), (0.5, 24.95, -4.18), "buckle")
    for nm in ("human_pin", "trig_pin"):
        pin_ring(m, nm)


PIN_C = np.array([0.0, 23.3, -4.42])


def pin_ring(m, name):
    b = m.bone(name, parent="head", pivot=tuple(PIN_C))
    b.ring(PIN_C, (0, 0, 1), 0.78, 0.2, 0.2, "pin", count=10)
    b.seg(PIN_C + np.array([0, 0.78, 0]), PIN_C + np.array([0, 1.35, 0.1]), 0.2, 0.2, "pin")
    b.seg(PIN_C + np.array([0, 1.35, 0.1]), PIN_C + np.array([0.25, 1.6, 0.35]), 0.16, 0.16, "pin")


# ------------------------------------------------------------------------------------------ body
def dynamite(bone, base, direction, length=2.9, r=0.55, up=(0, 0, 1)):
    d = norm(direction)
    bone.cylinder(np.asarray(base) + d * length / 2, d, r, length, "dynamite", segments=6, up=up)
    bone.cylinder(np.asarray(base) + d * (length + 0.08), d, r * 0.92, 0.16, "dyn_cap", segments=6, up=up)
    bone.tube(np.asarray(base) + d * length, np.asarray(base) + d * (length + 0.7), 0.1, "fuse_dk", segments=4, up=up)


def build_body(m):
    m.bone("body", pivot=(0, 24, 0))
    b = m.bone("form_body", parent="body", pivot=(0, 13, 0))
    # dynamite belt: sticks standing round the waist, held by a strap
    sticks = []
    for x in np.arange(-3.4, 3.5, 1.13):
        sticks.append(((x, 12.2, -2.62), (0, 0, -1)))
        sticks.append(((x, 12.2, 2.62), (0, 0, 1)))
    for z in np.arange(-1.4, 1.5, 1.13):
        sticks.append(((-4.62, 12.2, z), (-1, 0, 0)))
        sticks.append(((4.62, 12.2, z), (1, 0, 0)))
    for (x, y, z), nrm in sticks:
        dynamite(b, (x, y, z), (0, 1, 0), length=2.6, r=0.56, up=nrm)
    for yy in (13.0, 14.2):
        hx, hz, t = 5.22, 3.22, 0.22
        b.box((-hx, yy - 0.3, -hz), (hx, yy + 0.3, -hz + t), "strap")
        b.box((-hx, yy - 0.3, hz - t), (hx, yy + 0.3, hz), "strap")
        b.box((-hx, yy - 0.3, -hz), (-hx + t, yy + 0.3, hz), "strap")
        b.box((hx - t, yy - 0.3, -hz), (hx, yy + 0.3, hz), "strap")
    b.box((-0.7, 12.9, -3.38), (0.7, 14.4, -3.18), "buckle")
    # apron: a bundle of dynamite and loose fuses hanging over the front of the hips
    for k, x in enumerate(np.arange(-2.2, 2.3, 1.1)):
        dynamite(b, (x, 11.1 - 0.25 * (k % 2), -3.2), (0, -1, -0.08), length=2.3, r=0.5, up=(0, 0, -1))
    b.box((-2.9, 10.3, -3.85), (2.9, 10.9, -2.6), "strap")
    for k, (x0, ex) in enumerate(((-3.2, -3.9), (-1.2, -1.5), (1.4, 1.9), (3.1, 3.6))):
        P = [np.array([x0, 12.6, -3.35]), np.array([(x0 + ex) / 2, 11.0, -3.7]), np.array([ex, 9.7 - 0.3 * k, -3.4])]
        for p, q in zip(P, P[1:]):
            b.tube(p, q, 0.16, "fuse", segments=4)
    # bandolier fuse across the chest (left shoulder -> right hip) with charges clipped to it
    band = [np.array([3.4, 23.8, -2.3]), np.array([1.2, 20.4, -2.45]), np.array([-1.4, 17.2, -2.45]),
            np.array([-3.6, 14.6, -2.3])]
    for p, q in zip(band, band[1:]):
        b.seg(p, q, 0.9, 0.35, "fuse", up=(0, 0, -1), overlap=0.2)
    for t in (0.35, 0.65):
        p = band[1] * (1 - t) + band[2] * t + np.array([0, 0, -0.55])
        dynamite(b, p + np.array([0, -1.0, 0]), (0, 1, 0), length=2.0, r=0.45, up=(0, 0, -1))
    back = [np.array([3.4, 23.8, 2.3]), np.array([0.4, 19.0, 2.45]), np.array([-3.6, 14.6, 2.3])]
    for p, q in zip(back, back[1:]):
        b.seg(p, q, 0.9, 0.35, "fuse", up=(0, 0, 1), overlap=0.2)


# ------------------------------------------------------------------------------------------ arms
def build_arm(m, side):
    sgn = -1 if side == "right" else 1

    def X(o):
        return sgn * o

    name = side + "_arm"
    m.bone(name, pivot=(X(5), 22, 0))
    f = m.bone("form_" + name, parent=name, pivot=(X(6), 16, 0))
    # "bomb fuses sheathe her arms like sleeves": cords wound tightly round the whole arm, from the wrist to the
    # shoulder, standing clear of the arm so they are what you see (first person included); the hand stays bare
    cx = X(6)
    half = 2.3                       # the arm is 4 x 4; the sleeve hugs it just outside

    def ring_pts(y, grow=0.0, n=16):
        pts = []
        for i in range(n + 1):
            a = 2 * math.pi * i / n
            ca, sa = math.cos(a), math.sin(a)
            # rounded square (superellipse) round the arm's square cross-section
            e = 0.45
            x = math.copysign(abs(sa) ** e, sa) * (half + grow)
            z = math.copysign(abs(ca) ** e, ca) * (half + grow)
            pts.append(np.array([cx + x, y, -z]))
        return pts

    y0, y1 = 14.3, 24.2
    rows = int((y1 - y0) / 0.62)
    for k in range(rows + 1):
        y = y0 + (y1 - y0) * k / rows
        pts = ring_pts(y, grow=0.05 * (k % 2))
        mat = ("cord", "cord_lt", "cord", "cord_dk")[k % 4]
        for p, q in zip(pts, pts[1:]):
            f.seg(p, q, 0.62, 0.62, mat, up=norm(np.array([p[0] - cx, 0, p[2]])), overlap=0.2)
    # the shoulder cap: the cords coil over the top of the arm
    for k in range(3):
        pts = ring_pts(24.35 + 0.35 * k, grow=-0.55 * (k + 1))
        for p, q in zip(pts, pts[1:]):
            f.seg(p, q, 0.55, 0.55, "cord_dk" if k % 2 else "cord", up=(0, 1, 0), overlap=0.2)
    # a few loose cords spiralling over the wraps
    for j in range(2):
        pts = []
        for i in range(41):
            t = i / 40
            a = 2 * math.pi * 1.6 * t + j * math.pi
            e = 0.45
            sa, ca = math.sin(a), math.cos(a)
            x = math.copysign(abs(sa) ** e, sa) * (half + 0.55)
            z = math.copysign(abs(ca) ** e, ca) * (half + 0.55)
            pts.append(np.array([cx + x, y0 + 0.4 + (y1 - y0 - 1.0) * t, -z]))
        for p, q in zip(pts, pts[1:]):
            f.seg(p, q, 0.42, 0.42, "cord_dk", up=norm(np.array([p[0] - cx, 0, p[2]])), overlap=0.15)
    for yy in (14.1, 21.6):
        pts = ring_pts(yy, grow=0.5)
        for p, q in zip(pts, pts[1:]):
            f.seg(p, q, 0.8, 0.45, "strap", up=norm(np.array([p[0] - cx, 0, p[2]])), overlap=0.2)
    # dynamite strapped to the outside of the upper arm
    for zz in (-0.8, 0.8):
        dynamite(f, (X(9.3), 19.4, zz), (0, 1, 0), length=2.5, r=0.5, up=(sgn * 1.0, 0, 0))
    # loose fuse ends at the cuff, their wicks burning
    for k, (zz, ang) in enumerate(((-1.6, -30), (0.2, 10), (1.5, 35))):
        base = np.array([X(8.6), 14.4 + 0.35 * k, zz])
        d = norm(np.array([sgn * 0.9, -0.5 + 0.3 * math.sin(math.radians(ang)), zz * 0.15]))
        tip = base + d * 1.6
        f.tube(base, tip, 0.17, "fuse", segments=4)
        wk = m.bone("%s_wick_%d" % (side, k), parent="form_" + name, pivot=tuple(tip))
        wk.cbox(tip + d * 0.2, (0.36, 0.36, 0.36), "wick")
        wk.spike(tip + d * 0.3, d, 0.7, 0.3, 0.3, "wick", steps=2)
    if side == "right":
        build_torpedo(m)


def build_torpedo(m):
    """Torpedo that swallows the right forearm (only drawn while Torpedo runs). Axis = the arm, nose past the fist."""
    t = m.bone("fx_torpedo_right", parent="right_arm", pivot=(-6, 16, 0))
    ax = np.array([-6.0, 0, 0])
    body = [(19.0, 2.4), (17.5, 2.9), (15.0, 3.05), (12.0, 3.05), (9.0, 3.0), (7.0, 2.8), (5.5, 2.35),
            (4.3, 1.75), (3.4, 1.05), (2.9, 0.45)]
    for (y0, r0), (y1, r1) in zip(body, body[1:]):
        mat = "torpedo_band" if abs((y0 + y1) / 2 - 7.9) < 0.9 else "torpedo"
        t.cylinder(ax + np.array([0, (y0 + y1) / 2, 0]), (0, 1, 0), (r0 + r1) / 2, abs(y0 - y1) + 0.08, mat,
                   segments=12)
    for yy in (16.0, 10.5):
        t.ring(ax + np.array([0, yy, 0]), (0, 1, 0), 3.1, 0.25, 0.35, "band", count=12)
    # tail fins
    for k in range(4):
        a = math.radians(45 + 90 * k)
        d = np.array([math.sin(a), 0, math.cos(a)])
        t.obox(ax + np.array([0, 20.2, 0]) + d * 3.0, (0, 1, 0), (0.25, 2.6, 2.4), "torpedo", up=d)
    t.cylinder(ax + np.array([0, 20.0, 0]), (0, 1, 0), 1.2, 1.4, "band", segments=8)
    pr = m.bone("torpedo_prop", parent="fx_torpedo_right", pivot=(-6, 21.4, 0))
    pr.cylinder(ax + np.array([0, 21.4, 0]), (0, 1, 0), 0.6, 1.0, "prop", segments=6)
    for k in range(3):
        a = math.radians(120 * k)
        d = np.array([math.sin(a), 0, math.cos(a)])
        pr.obox(ax + np.array([0, 21.5, 0]) + d * 1.3, d, (0.18, 2.2, 0.9), "prop", up=(0, 1, 0), roll=25)


# ------------------------------------------------------------------------------------------ build
def build():
    atlas = materials()
    m = Model("csm.bomb_hybrid", atlas, density=2.0, seed=51)
    build_head(m)
    build_body(m)
    build_arm(m, "right")
    build_arm(m, "left")
    geo = out("geo", "hybrid", "bomb.geo.json")
    tex = out("textures", "hybrid", "bomb.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "bomb_glowmask.png"), seed=23)
    anims = animations()
    anim_path = out("animations", "hybrid", "bomb.animation.json")
    save_animations(anim_path, anims)
    print("bomb: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))

    # the head she throws: same atlas, centred on the entity origin, with a lit fuse on top
    e = Model("csm.bomb_head", atlas, density=2.0, seed=52)
    hb = e.bone("bomb", pivot=(0, 4.6, 0))
    c = np.array([0.0, 4.8, -2.4])
    build_casing(hb, c, detail=True)
    top = c + np.array([0, EGG_R[1] - 0.2, -0.6])
    hb.tube(top, top + np.array([0.4, 1.6, 0.3]), 0.2, "fuse", segments=4)
    w = e.bone("bomb_wick", parent="bomb", pivot=tuple(top + np.array([0.4, 1.6, 0.3])))
    w.cbox(top + np.array([0.45, 1.85, 0.32]), (0.5, 0.5, 0.5), "wick")
    w.spike(top + np.array([0.45, 1.95, 0.32]), (0, 1, 0), 0.9, 0.4, 0.4, "wick", steps=2)
    ehead = out("geo", "entity", "bomb_head.geo.json")
    e.save(ehead)
    ea = Anim("idle", 0.3, loop=True)
    for t, s in ((0, 1.0), (0.1, 1.35), (0.2, 0.85), (0.3, 1.0)):
        ea.scale("bomb_wick", t, s)
    save_animations(out("animations", "entity", "bomb_head.animation.json"), [ea])
    print("bomb head entity: %d cubes" % e.cube_count())
    return geo, tex, anim_path


def animations():
    A = []
    WICKS = ["%s_wick_%d" % (s, k) for s in ("right", "left") for k in range(3)]

    # emerge: she walks out of her own explosion - the casing inflates out of the smoke
    e = Anim("emerge", 0.8)
    e.scale("bomb_skull", 0, 0.25).scale("bomb_skull", 0.16, 1.14, "easeOutBack").scale("bomb_skull", 0.3, 0.96)
    e.scale("bomb_skull", 0.42, 1.0, "easeInOutSine")
    for t, r in ((0, (0, 0, 0)), (0.1, (-6, 8, 4)), (0.2, (4, -5, -3)), (0.32, (-2, 2, 1)), (0.45, (0, 0, 0))):
        e.rot("bomb_skull", t, r)
    e.scale("form_neck", 0, (1, 0.2, 1)).scale("form_neck", 0.12, (1, 1.15, 1), "easeOutBack")
    e.scale("form_neck", 0.22, 1)
    e.scale("form_body", 0, 0.7).scale("form_body", 0.14, 1.08, "easeOutBack").scale("form_body", 0.26, 1.0)
    for i, s in enumerate(("right", "left")):
        o = 0.04 * i
        fa = "form_%s_arm" % s
        e.scale(fa, 0, 0.6).scale(fa, 0.12 + o, 1.1, "easeOutBack").scale(fa, 0.24 + o, 1.0)
    for k, w in enumerate(WICKS):
        t0 = 0.3 + 0.05 * k
        e.scale(w, 0, 0).scale(w, t0, 0).scale(w, t0 + 0.1, 1.6, "easeOutBack").scale(w, t0 + 0.2, 1.0)
    A.append(e)

    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    r.scale("bomb_skull", 0, 1).scale("bomb_skull", 0.35, 0.25, "easeInBack")
    r.scale("form_body", 0.05, 1).scale("form_body", 0.35, 0.7, "easeInQuad")
    for s in ("right", "left"):
        r.scale("form_%s_arm" % s, 0.05, 1).scale("form_%s_arm" % s, 0.35, 0.6, "easeInQuad")
    for w in WICKS:
        r.scale(w, 0, 1).scale(w, 0.1, 0)
    A.append(r)

    idle = Anim("idle", 1.6, loop=True)
    for k, w in enumerate(WICKS):
        for i in range(17):
            t = i * 0.1
            idle.scale(w, t, 1.0 + 0.3 * math.sin(t * 23 + k * 1.7) * math.sin(t * 7 + k))
    idle.rot("bomb_skull", 0, (0, 0, 0)).rot("bomb_skull", 0.8, (-1.2, 0.8, 0), "easeInOutSine")
    idle.rot("bomb_skull", 1.6, (0, 0, 0), "easeInOutSine")
    A.append(idle)

    def jolt(anim, t0, amp=5.0):
        anim.rot("bomb_skull", t0, (0, 0, 0)).rot("bomb_skull", t0 + 0.04, (-amp, amp * 0.6, amp * 0.4))
        anim.rot("bomb_skull", t0 + 0.12, (amp * 0.4, -amp * 0.3, 0), "easeOutQuad")
        anim.rot("bomb_skull", t0 + 0.2, (0, 0, 0), "easeInOutSine")

    def flare(anim, side, t0):
        for k in range(3):
            w = "%s_wick_%d" % (side, k)
            anim.scale(w, t0 - 0.02, 1).scale(w, t0 + 0.02, 2.6).scale(w, t0 + 0.2, 1.0, "easeOutQuad")

    co = Anim("combo", 0.8)
    jolt(co, 0.2)
    flare(co, "right", 0.2)
    jolt(co, 0.45)
    flare(co, "left", 0.45)
    jolt(co, 0.65, 7)
    A.append(co)

    fl = Anim("flick", 0.5)
    flare(fl, "right", 0.2)
    A.append(fl)

    pr = Anim("propulsion", 1.5)
    for k in range(6):
        t0 = 0.15 + 0.2 * k
        flare(pr, "right", t0)
        flare(pr, "left", t0)
    pr.rot("bomb_skull", 0, (0, 0, 0)).rot("bomb_skull", 0.2, (12, 0, 0), "easeOutQuad")
    pr.rot("bomb_skull", 1.25, (12, 0, 0)).rot("bomb_skull", 1.5, (0, 0, 0), "easeInOutSine")
    A.append(pr)

    tp = Anim("torpedo", 1.0)
    tp.scale("fx_torpedo_right", 0, (0.6, 0.2, 0.6)).scale("fx_torpedo_right", 0.22, (1.08, 1.1, 1.08), "easeOutBack")
    tp.scale("fx_torpedo_right", 0.32, 1.0).scale("fx_torpedo_right", 0.85, 1.0)
    tp.scale("fx_torpedo_right", 1.0, (0.7, 0.3, 0.7), "easeInQuad")
    for i in range(11):
        tp.rot("torpedo_prop", i * 0.1, (0, -i * 160 * (1 if i < 3 else 2), 0))
    A.append(tp)

    # Reze pulls the pin, tears her head off (thrown at 0.45 s = tick 9) and a new one grows back
    hl = Anim("headless", 1.3)
    hl.scale("bomb_skull", 0, 1).scale("bomb_skull", 0.3, 1).scale("bomb_skull", 0.38, 1.08, "easeOutQuad")
    hl.scale("bomb_skull", 0.44, 1.0).scale("bomb_skull", 0.46, 0.0).scale("bomb_skull", 0.98, 0.0)
    hl.scale("bomb_skull", 1.18, 1.12, "easeOutBack").scale("bomb_skull", 1.3, 1.0, "easeInOutSine")
    hl.scale("form_neck", 0.44, 1).scale("form_neck", 0.5, (1.3, 0.7, 1.3), "easeOutQuad")
    hl.scale("form_neck", 1.0, (1.3, 0.7, 1.3)).scale("form_neck", 1.2, 1.0, "easeOutBack")
    A.append(hl)

    dr = Anim("drink", 1.0)
    dr.rot("bomb_skull", 0, (0, 0, 0)).rot("bomb_skull", 0.35, (-14, 0, 0), "easeOutQuad")
    dr.rot("bomb_skull", 0.75, (-14, 0, 0)).rot("bomb_skull", 1.0, (0, 0, 0), "easeInOutSine")
    A.append(dr)

    # trigger prop: the pulled pin stays in her fist through the blast, then is dropped
    pp = Anim("pull_pin", 1.2)
    pp.scale("trig_pin", 0, 1).scale("trig_pin", 0.9, 1).scale("trig_pin", 1.0, 0, "easeInQuad")
    A.append(pp)
    return A


def render_previews(geo, tex, anim):
    r = poses.reze_pull()
    hide_fx = ("fx_torpedo_right", "prop_choker", "human_pin", "trig_pin")
    arms = {"right_arm": {"rot": (0, 0, 0.1)}, "left_arm": {"rot": (0, 0, -0.1)}}
    human = ("form_head", "form_body", "form_right_arm", "form_left_arm", "fx_torpedo_right", "trig_pin")
    shots = [
        preview.render(geo, tex, preview_path("bomb_front.png"), anim, "idle", 0.0, yaw=25, pitch=6, pose=arms,
                       hidden=hide_fx, scale=10.5, center=(0, 1.25)),
        preview.render(geo, tex, preview_path("bomb_head.png"), anim, "idle", 0.0, yaw=55, pitch=10,
                       show_body=False, scale=20, center=(0, 1.85), size=(640, 520),
                       hidden=hide_fx + ("body", "right_arm", "left_arm")),
        preview.render(geo, tex, preview_path("bomb_torpedo.png"), anim, "torpedo", 0.5, yaw=-60, pitch=10,
                       pose={"right_arm": {"rot": (-1.57, 0, 0)}, "left_arm": {"rot": (0.3, 0, -0.1)}},
                       hidden=("prop_choker", "human_pin", "trig_pin"), scale=9, center=(0, 1.2)),
        preview.render(geo, tex, preview_path("bomb_trigger.png"), None, None, 0, yaw=30, pitch=4,
                       pose={"right_arm": {"rot": tuple(r["grab"]["rot"])}, "head": {"rot": poses.REZE_HEAD}},
                       hidden=human, show_head=True, scale=24, center=(0, 1.5), size=(640, 520)),
    ]
    return preview.contact_sheet(shots, preview_path("bomb_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
