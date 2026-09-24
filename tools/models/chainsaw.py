"""
Chainsaw Hybrid (Denji) - devil parts model, texture atlas and GeckoLib animations.

Modelled from the manga side profile and the anime model sheet. The head IS a chainsaw:
  * the back and sides of the skull are the dark engine block (cooling fins, recoil-starter disc, muffler)
  * a tubular front handle hoops over the top of the head, a rear handle loops off the back
  * the upper face is the orange-red clutch cover: a sloped beak with three glowing curved vent slits
    on each side (read as the eyes in the anime)
  * the guide bar juts straight out of the front of the cover, huge cutters on top and bottom, blood on it
  * a comb of long thin white fangs hangs from the cover down to a separate notched orange lower jaw
  * dark fibrous sinew for a neck
  * forearms stay human: a bar bursts out of the outside of each forearm near the elbow and runs past the hand
  * the starter cord (Pochita's tail) hangs out of the chest; the leg saws are used by Leg Saw Spin

Bone naming contract with HybridPartRenderer (Java):
  form_*   visible while the hybrid form is out (plus emerge/retract)
  fx_X_*   only visible while the matching ability effect "X" is active
  cord / cord_handle   the starter cord (handle position is driven at runtime while pulling)
"""
import math

import numpy as np

from common import out, preview_path, arc_point, arc_normal
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview


def materials():
    a = Atlas(512, 64)
    a.add("shell", kind="painted", color=(222, 76, 34), color2=(150, 42, 20))
    a.add("shell_dk", kind="painted", color=(168, 50, 24), color2=(100, 28, 12))
    a.add("engine", kind="painted", color=(56, 54, 64), color2=(104, 104, 112))
    a.add("engine_lt", kind="metal", color=(98, 98, 108), scratches=4)
    a.add("fin", kind="metal", color=(74, 74, 84), scratches=3)
    a.add("handle", kind="rubber", color=(30, 30, 35))
    a.add("bar", kind="metal", color=(206, 208, 214), scratches=12)
    a.add("bar_rim", kind="metal", color=(122, 124, 132), scratches=4)
    a.add("cutter", kind="metal", color=(78, 80, 90), scratches=2)
    a.add("chain", kind="chain", color=(58, 60, 68))
    a.add("teeth", kind="teeth", color=(246, 242, 230))
    a.add("mouth", kind="void", color=(26, 6, 8))
    a.add("gum", kind="flesh", color=(120, 24, 28))
    a.add("sinew", kind="flesh", color=(84, 54, 50))
    a.add("sinew_dk", kind="flesh", color=(52, 34, 34))
    a.add("blood", kind="blood", color=(158, 12, 16))
    a.add("flesh", kind="flesh", color=(166, 30, 34))
    a.add("glow", kind="glow", color=(255, 150, 30), color2=(255, 238, 150), emissive=True)
    a.add("rivet", kind="metal", color=(170, 172, 178), scratches=1)
    a.add("skin_h", kind="skin", color=(228, 180, 146))
    a.add("cord", kind="rubber", color=(22, 22, 24))
    a.add("grille", kind="chain", color=(40, 40, 46))
    return a


# ---------------------------------------------------------------------------------------- head
Y0, Y1 = 27.4, 33.6   # clutch-cover (shell) vertical span


def shell_ring(y):
    """Ellipse of the clutch cover at height y: (ax, az, cz)."""
    t = (y - Y0) / (Y1 - Y0)
    ax = 4.15 - 1.5 * t ** 2
    front = -5.25 + 3.3 * t ** 1.4
    back = 3.9 - 1.3 * t ** 2
    return ax, (back - front) / 2, (back + front) / 2


def ring_band(bone, ax, az, cz, y, h, phi0, phi1, thick, mat, steps=18, out_off=0.0):
    for i in range(steps):
        pa = phi0 + (phi1 - phi0) * i / steps
        pb = phi0 + (phi1 - phi0) * (i + 1) / steps
        a = arc_point(ax + out_off, az + out_off, pa, y, cz)
        b = arc_point(ax + out_off, az + out_off, pb, y, cz)
        bone.seg(a, b, thick, h, mat, up=(0, 1, 0), overlap=0.3)


def build_head(m):
    m.bone("head", pivot=(0, 24, 0))
    f = m.bone("form_head", parent="head", pivot=(0, 24, 0))

    # ---- neck: dark fibrous sinew strands
    rng = np.random.default_rng(3)
    for k in range(22):
        a = k / 22 * 2 * math.pi
        r = 2.25 + rng.uniform(-0.2, 0.25)
        twist = math.radians(rng.uniform(12, 28))
        p0 = np.array([math.sin(a) * r, 21.9, 0.6 - math.cos(a) * r])
        p1 = np.array([math.sin(a + twist) * (r - 0.2), 25.8, 0.6 - math.cos(a + twist) * (r - 0.2)])
        f.seg(p0, p1, rng.uniform(0.45, 0.75), rng.uniform(0.35, 0.55), "sinew" if k % 3 else "sinew_dk",
              up=norm([math.sin(a), 0, -math.cos(a)]), overlap=0.1)
    f.cylinder((0, 23.9, 0.6), (0, 1, 0), 1.8, 4.0, "sinew_dk", segments=8)

    # ---- engine block: back and sides of the skull
    e = m.bone("form_engine", parent="form_head", pivot=(0, 28, 1.5))
    e.box((-3.7, 25.3, -1.6), (3.7, 32.4, 4.3), "engine")
    e.box((-3.2, 24.8, -0.6), (3.2, 25.4, 3.8), "engine")
    e.box((-3.1, 32.3, -0.8), (3.1, 32.9, 3.6), "engine")
    e.box((-3.3, 25.6, 4.2), (3.3, 32.0, 4.7), "engine_lt")
    for y in np.arange(25.9, 31.9, 0.75):
        for s in (-1, 1):
            e.box((s * 3.7, y, 0.1), (s * 4.15, y + 0.32, 3.9), "fin")
    # recoil starter housing (right side) and muffler (left side)
    e.cylinder((-4.2, 28.4, 1.9), (1, 0, 0), 2.05, 0.55, "engine_lt", segments=12)
    e.cylinder((-4.55, 28.4, 1.9), (1, 0, 0), 0.8, 0.35, "rivet", segments=8)
    for k in range(6):
        ang = k / 6 * 2 * math.pi
        e.cbox((-4.5, 28.4 + math.sin(ang) * 1.45, 1.9 + math.cos(ang) * 1.45), (0.25, 0.35, 0.35), "rivet")
    e.box((4.1, 26.2, 0.3), (4.9, 30.2, 3.6), "grille")
    e.box((4.0, 25.9, 0.0), (4.3, 30.5, 3.9), "engine_lt")
    e.cylinder((0.0, 33.3, 2.6), (0, 1, 0), 0.5, 0.9, "handle", segments=6)  # spark plug boot

    # ---- orange clutch cover (upper face, sloped beak)
    s = m.bone("form_shell", parent="form_head", pivot=(0, 30, -2))
    n = 12
    for i in range(n):
        y = Y0 + (Y1 - Y0) * (i + 0.5) / n
        ax, az, cz = shell_ring(y)
        t = (y - Y0) / (Y1 - Y0)
        phimax = 62 + 58 * min(1, t / 0.25) if t < 0.72 else 180
        ring_band(s, ax, az, cz, y, (Y1 - Y0) / n + 0.08, -phimax, phimax, 0.9, "shell", steps=16)
    for y, sc in ((33.7, 1.0), (34.05, 0.72)):  # top cap
        ax, az, cz = shell_ring(Y1)
        s.cylinder((0, y, cz), (0, 1, 0), min(ax, az) * sc, 0.45, "shell", segments=10)
    # darker rim along the bottom edge (upper lip) and a centre crest where the bar is mounted
    ax, az, cz = shell_ring(Y0 + 0.2)
    ring_band(s, ax + 0.08, az + 0.08, cz, Y0 + 0.1, 0.4, -64, 64, 0.5, "shell_dk", steps=14)
    crest = []
    for i in range(10):
        y = Y0 + 0.6 + (Y1 - Y0 - 0.2) * i / 9
        ax, az, cz = shell_ring(y)
        crest.append(np.array([0, y + 0.1, cz - az - 0.25]))
    s.curve(crest, 1.5, 1.2, 0.5, 0.4, "shell_dk")
    # three glowing curved vent slits on each side (the "eyes")
    for side in (-1, 1):
        for k in range(3):
            base_phi = 22 + k * 10.5
            pts = []
            for j in range(7):
                y = 28.6 + k * 0.35 + j * 0.42
                phi = side * (base_phi + 7.5 * math.sin(math.pi * j / 6))
                ax, az, cz = shell_ring(y)
                pts.append((arc_point(ax + 0.45, az + 0.45, phi, y, cz), arc_normal(ax, az, phi)))
            for (p, nrm), (q, _) in zip(pts, pts[1:]):
                s.seg(p + nrm * 0.02, q + nrm * 0.02, 0.8, 0.22, "mouth", up=nrm, overlap=0.15)
                s.seg(p + nrm * 0.1, q + nrm * 0.1, 0.46, 0.16, "glow", up=nrm, overlap=0.1)
    for side in (-1, 1):  # bolts on the cover
        for y, phi in ((32.3, 50), (29.1, 64)):
            ax, az, cz = shell_ring(y)
            s.obox(arc_point(ax + 0.35, az + 0.35, side * phi, y, cz), (0, 1, 0), (0.45, 0.45, 0.45), "rivet",
                   up=arc_normal(ax, az, side * phi))

    # ---- guide bar out of the front of the cover (own bone: it shoots out when transforming)
    b = m.bone("saw_bar", parent="form_head", pivot=(0, 31.9, -3.2), rotation=(-7, 0, 0))
    BAR_Y, BAR_H, Z0, Z1 = 31.9, 4.2, -2.2, -22.5
    b.box((-0.4, BAR_Y - BAR_H / 2, Z1), (0.4, BAR_Y + BAR_H / 2, Z0), "bar")
    for sy in (-1, 1):  # rails along both edges
        yc = BAR_Y + sy * (BAR_H / 2 - 0.3)
        b.box((-0.45, yc - 0.3, Z1 + 0.6), (0.45, yc + 0.3, Z0), "bar_rim")
    for r, dz in ((1.6, 0.0), (1.2, 0.55), (0.7, 0.95)):  # rounded nose
        b.box((-0.4, BAR_Y - r, Z1 - dz - 0.5), (0.4, BAR_Y + r, Z1 - dz), "bar")
    for z in (-5.0, -20.8):
        b.cbox((0, BAR_Y, z), (0.9, 0.6, 0.6), "rivet")
    rng = np.random.default_rng(9)
    for k in range(7):  # blood splatter on both faces: a blot, droplets and a smear trailing back
        zc_ = rng.uniform(Z1 + 1.5, Z0 - 3)
        yc_ = BAR_Y + rng.uniform(-1.3, 1.1)
        for sx in (-1, 1):
            b.box((sx * 0.4, yc_ - 0.35, zc_ - 0.45), (sx * 0.45, yc_ + 0.35, zc_ + 0.45), "blood")
            b.box((sx * 0.4, yc_ - 0.12, zc_ + 0.4), (sx * 0.44, yc_ + 0.12, zc_ + 0.4 + rng.uniform(0.8, 2.4)), "blood")
            for _ in range(3):
                dz, dy = rng.uniform(-1.2, 1.2), rng.uniform(-0.9, 0.9)
                r_ = rng.uniform(0.1, 0.22)
                b.box((sx * 0.4, yc_ + dy - r_, zc_ + dz - r_), (sx * 0.45, yc_ + dy + r_, zc_ + dz + r_), "blood")
    # cutters - big and raked, riding a chain on each edge (animated bones)
    for name, sy in (("saw_chain_t", 1), ("saw_chain_b", -1)):
        c = m.bone(name, parent="saw_bar", pivot=(0, BAR_Y + sy * BAR_H / 2, -8))
        edge = BAR_Y + sy * (BAR_H / 2)
        for i in range(15):
            z = -3.2 - i * 1.25
            c.box((-0.46, edge - 0.25 if sy > 0 else edge - 0.1, z - 0.55),
                  (0.46, edge + 0.1 if sy > 0 else edge + 0.25, z + 0.55), "chain")
            rake = norm([0.0, sy * 1.0, -0.45 * sy])
            c.spike((0.14 if i % 2 else -0.14, edge + sy * 0.05, z), rake, 1.35, 1.0, 0.36, "cutter", steps=3,
                    up=(0, 0, -1))
    nose = m.bone("saw_chain_n", parent="saw_bar", pivot=(0, BAR_Y, Z1))
    for ang in (25, 60, 95, 130, 160):
        d = np.array([0, math.cos(math.radians(ang)), -math.sin(math.radians(ang))])
        c0 = np.array([0, BAR_Y, Z1 - 0.2]) + d * 1.75
        nose.spike(c0, d, 1.2, 0.95, 0.34, "cutter", steps=3, up=np.cross(d, [1, 0, 0]))

    # ---- handles: front hoop over the head and rear grip loop off the back
    hf = m.bone("form_handle_front", parent="form_head", pivot=(0, 32.6, 0.6), rotation=(24, 0, 0))
    loop = [(-2.9, 32.4), (-2.9, 35.2), (-2.3, 36.0), (2.3, 36.0), (2.9, 35.2), (2.9, 32.4)]
    for (x0, y0), (x1, y1) in zip(loop, loop[1:]):
        hf.tube((x0, y0, 0.6), (x1, y1, 0.6), 0.55, "handle", segments=8)
    hr = m.bone("form_handle_rear", parent="form_head", pivot=(0, 29, 4.4))
    rear = [(31.0, 4.2), (31.2, 6.4), (30.4, 7.4), (27.6, 7.4), (26.8, 6.4), (26.9, 4.2)]
    for (y0, z0), (y1, z1) in zip(rear, rear[1:]):
        hr.tube((0, y0, z0), (0, y1, z1), 0.6, "handle", segments=8)
    hr.box((-0.35, 27.5, 5.0), (0.35, 28.6, 5.6), "engine_lt")  # throttle trigger

    # ---- mouth: cavity + comb of long fangs hanging from the cover
    ax, az, cz = shell_ring(Y0)
    ring_band(f, ax - 0.9, az - 0.9, cz + 0.2, 25.9, 3.2, -80, 80, 0.5, "mouth", steps=14)
    n = 17
    for i in range(n):
        phi = -66 + 132 * i / (n - 1)
        length = 2.5 - 0.9 * (abs(phi) / 66) ** 2
        base = arc_point(ax - 0.45, az - 0.45, phi, Y0 - 0.05, cz)
        nrm = arc_normal(ax, az, phi)
        f.spike(base, norm(np.array([0, -1, 0]) - nrm * 0.08), length, 0.6, 0.34, "teeth", steps=4, up=nrm)

    # ---- lower jaw: separate notched orange plate with its own comb of teeth
    j = m.bone("jaw", parent="form_head", pivot=(0, 25.4, 1.2))
    jax, jaz, jcz = 3.3, 4.6, -0.5
    for (p0, p1) in ((-72, -9), (9, 72)):  # V notch in the middle
        ring_band(j, jax, jaz, jcz, 24.2, 1.3, p0, p1, 0.8, "shell", steps=7)
    j.spike((0, 23.9, jcz - jaz + 0.1), norm([0, -0.8, -1]), 1.5, 1.6, 0.8, "shell_dk", steps=3, up=(0, 1, 0))
    for s_ in (-1, 1):
        j.seg(arc_point(jax, jaz, s_ * 9, 24.55, jcz), (s_ * 0.2, 23.75, jcz - jaz + 0.15), 0.75, 0.55, "shell",
              up=(0, 0, -1))
    j.box((-2.6, 23.7, -3.6), (2.6, 24.4, 1.5), "mouth")
    n = 15
    for i in range(n):
        phi = -62 + 124 * i / (n - 1)
        if abs(phi) < 5:
            continue
        base = arc_point(jax - 0.3, jaz - 0.3, phi, 24.8, jcz)
        nrm = arc_normal(jax, jaz, phi)
        j.spike(base, norm(np.array([0, 1, 0]) - nrm * 0.1), 1.9 - 0.5 * abs(phi) / 62, 0.55, 0.32, "teeth",
                steps=3, up=nrm)


# ---------------------------------------------------------------------------------------- body
def build_body(m):
    m.bone("body", pivot=(0, 24, 0))
    c = m.bone("cord", parent="body", pivot=(0, 20.5, -2))
    c.ring((0, 20.5, -2.08), (0, 0, -1), 0.6, 0.3, 0.35, "engine_lt", count=8)
    c.box((-0.95, 19.55, -2.14), (0.95, 21.45, -2.02), "flesh")
    c.box((-0.3, 18.6, -2.12), (0.1, 19.6, -2.03), "blood")
    h = m.bone("cord_handle", parent="cord", pivot=(0, 20.5, -3.6))
    h.box((-0.32, 20.18, -3.95), (0.32, 20.82, -3.5), "handle")
    h.cylinder((0, 20.5, -4.35), (1, 0, 0), 0.46, 3.0, "handle", segments=8)
    for sx in (-1, 1):
        h.cylinder((sx * 1.62, 20.5, -4.35), (1, 0, 0), 0.56, 0.35, "shell", segments=8)


# ---------------------------------------------------------------------------------------- arms
def build_arm(m, side):
    sgn = -1 if side == "right" else 1

    def X(o):
        return sgn * o

    name = side + "_arm"
    m.bone(name, pivot=(X(5), 22, 0))
    f = m.bone("form_" + name, parent=name, pivot=(X(8), 18.5, 0))
    # torn wound on the outside of the forearm just below the elbow
    f.box((X(7.9), 16.6, -1.9), (X(8.18), 19.3, 1.9), "flesh")
    for zz, d in ((-2.0, -1), (2.0, 1)):
        hinge = np.array([X(8.1), 18.0, zz])
        f.obox(hinge + np.array([sgn * 0.6, 0.3, d * 0.3]), norm([sgn * 1.0, 0.4, d * 0.5]), (1.8, 1.4, 0.24),
               "skin_h", up=(0, 0, d))
        f.obox(hinge + np.array([sgn * 0.5, 0.2, d * 0.1]), norm([sgn * 1.0, 0.4, d * 0.5]), (1.5, 1.1, 0.2),
               "flesh", up=(0, 0, d))
    f.box((X(8.1), 16.9, -1.3), (X(9.3), 19.0, 1.3), "engine")  # drive sprocket bursting out
    f.cylinder((X(9.35), 18.0, 0), (1, 0, 0), 0.9, 0.3, "engine_lt", segments=8)
    # blood running down the forearm and over the hand
    rng = np.random.default_rng(5 if side == "right" else 6)
    for k in range(5):
        z = rng.uniform(-1.7, 1.7)
        y1 = rng.uniform(16.2, 17.2)
        y0 = rng.uniform(11.6, 14.8)
        f.box((X(8.0), y0, z - 0.14), (X(8.08), y1, z + 0.14), "blood")
    for k in range(3):
        x = rng.uniform(4.6, 7.4)
        f.box((X(x - 0.14), rng.uniform(12.2, 14.5), -2.07), (X(x + 0.14), 17.0, -2.0), "blood")

    # the bar: flat faces front/back, cutting edges point outward and inward, splayed slightly outward
    sname = side + "_saw"
    s = m.bone(sname, parent="form_" + name, pivot=(X(8.3), 18.6, 0.45), rotation=(0, 0, sgn * -5))
    XC, W, T, TOP, BOT = 8.3, 3.4, 0.7, 19.2, 3.2
    zc = 0.45
    s.box((X(XC - W / 2), BOT, zc - T / 2), (X(XC + W / 2), TOP, zc + T / 2), "bar")
    for e in (-1, 1):
        s.box((X(XC + e * (W / 2 - 0.3) - 0.28), BOT + 0.6, zc - T / 2 - 0.04),
              (X(XC + e * (W / 2 - 0.3) + 0.28), TOP, zc + T / 2 + 0.04), "bar_rim")
    for r, dy in ((1.5, 0.0), (1.15, 0.5), (0.7, 0.9)):
        s.box((X(XC - r), BOT - dy - 0.5, zc - T / 2), (X(XC + r), BOT - dy, zc + T / 2), "bar")
    s.cbox((X(XC), BOT + 1.4, zc), (0.6, 0.6, T + 0.2), "rivet")
    for k in range(5):
        y = rng.uniform(BOT + 1.5, 15.5)
        xo = rng.uniform(-1.0, 1.0)
        for sz in (-1, 1):
            s.box((X(XC + xo - 0.35), y - 0.35, zc + sz * T / 2), (X(XC + xo + 0.35), y + 0.35, zc + sz * (T / 2 + 0.05)),
                  "blood")
            s.box((X(XC + xo - 0.12), y - rng.uniform(1.0, 3.0), zc + sz * T / 2),
                  (X(XC + xo + 0.12), y, zc + sz * (T / 2 + 0.04)), "blood")
            for _ in range(2):
                dx, dy = rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8)
                s.box((X(XC + xo + dx - 0.15), y + dy - 0.15, zc + sz * T / 2),
                      (X(XC + xo + dx + 0.15), y + dy + 0.15, zc + sz * (T / 2 + 0.05)), "blood")
    for cname, e in ((sname + "_chain_o", 1), (sname + "_chain_i", -1)):
        c = m.bone(cname, parent=sname, pivot=(X(XC + e * W / 2), 12, zc))
        ex = X(XC + e * W / 2)
        out_dir = np.array([sgn * e, 0, 0])
        for i in range(13):
            y = TOP - 0.8 - i * 1.25
            c.box((min(ex, ex + out_dir[0] * 0.3) - 0.12, y - 0.55, zc - 0.42),
                  (max(ex, ex + out_dir[0] * 0.3) + 0.12, y + 0.55, zc + 0.42), "chain")
            rake = norm(out_dir + np.array([0, -0.45 * e, 0]))
            c.spike((ex, y, zc + (0.13 if i % 2 else -0.13)), rake, 1.1, 0.85, 0.32, "cutter", steps=3,
                    up=(0, 1, 0))
    cn = m.bone(sname + "_chain_n", parent=sname, pivot=(X(XC), BOT, zc))
    for ang in (25, 60, 95, 130, 160):
        d = np.array([sgn * math.cos(math.radians(ang)), -math.sin(math.radians(ang)), 0])
        c0 = np.array([X(XC), BOT - 0.2, zc]) + d * 1.6
        cn.spike(c0, d, 1.05, 0.8, 0.3, "cutter", steps=3, up=(0, 0, 1))


# ---------------------------------------------------------------------------------------- legs
def build_leg(m, side):
    sgn = -1 if side == "right" else 1

    def X(o):
        return sgn * o

    name = side + "_leg"
    m.bone(name, pivot=(X(1.9), 12, 0))
    ls = m.bone("fx_legsaw_" + side, parent=name, pivot=(X(3.9), 6, 0))
    ls.box((X(3.9), 4.0, -1.3), (X(4.14), 8.0, 1.3), "flesh")
    base = np.array([X(4.1), 6.2, 0.0])
    d = norm([sgn * 1.0, -0.28, 0.25])
    up = np.array([0, 0, 1.0])
    ez = norm(up - np.dot(up, d) * d)
    ls.obox(base + d * 0.8, d, (1.8, 1.9, 3.0), "engine", up=up)
    ls.obox(base + d * 6.4, d, (0.6, 10.0, 3.0), "bar", up=up)
    ls.obox(base + d * 11.6, d, (0.6, 1.0, 1.9), "bar", up=up)
    for i in range(8):
        p = base + d * (2.2 + i * 1.2)
        for e in (1, -1):
            ls.obox(p + ez * e * 1.5, d, (0.7, 1.0, 0.3), "chain", up=ez * e)
            ls.spike(p + ez * e * 1.55, norm(ez * e - d * 0.4 * e), 1.0, 0.8, 0.32, "cutter", steps=2, up=d)


def build():
    atlas = materials()
    m = Model("csm.chainsaw_hybrid", atlas, density=2.0, seed=11)
    build_head(m)
    build_body(m)
    build_arm(m, "right")
    build_arm(m, "left")
    build_leg(m, "right")
    build_leg(m, "left")

    geo = out("geo", "hybrid", "chainsaw.geo.json")
    tex = out("textures", "hybrid", "chainsaw.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "chainsaw_glowmask.png"), seed=5)
    anims = animations()
    anim_path = out("animations", "hybrid", "chainsaw.animation.json")
    save_animations(anim_path, anims)
    print("chainsaw: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


# ---------------------------------------------------------------------------------------- animations
SAWS = ("right_saw", "left_saw")


def animations():
    A = []

    # the chainsaw rips out of the face and forearms; the jaw drops in a roar
    e = Anim("emerge", 0.8)
    e.scale("form_head", 0, 0.8).scale("form_head", 0.14, 1.1, "easeOutBack").scale("form_head", 0.32, 1.0,
                                                                                   "easeInOutSine")
    for t, r in [(0, (0, 0, 0)), (0.08, (8, -5, 4)), (0.16, (-6, 4, -3)), (0.26, (3, -2, 1)), (0.4, (0, 0, 0))]:
        e.rot("form_head", t, r)
    e.scale("saw_bar", 0, (1, 1, 0.03)).scale("saw_bar", 0.06, (1, 1, 0.03))
    e.scale("saw_bar", 0.2, (1, 1, 1.14), "easeOutBack").scale("saw_bar", 0.34, (1, 1, 1), "easeInOutSine")
    for bn, t0 in (("form_handle_front", 0.12), ("form_handle_rear", 0.18)):
        e.scale(bn, 0, 0.02).scale(bn, t0, 0.02).scale(bn, t0 + 0.14, 1.15, "easeOutBack").scale(bn, t0 + 0.24, 1.0)
    e.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.2, (34, 0, 0), "easeOutQuad").rot("jaw", 0.5, (26, 0, 0))
    e.rot("jaw", 0.8, (0, 0, 0), "easeInOutSine")
    for i, side in enumerate(("right", "left")):
        o = 0.06 * i
        fa = "form_%s_arm" % side
        e.scale(fa, 0, 0.5).scale(fa, 0.1 + o, 1.12, "easeOutBack").scale(fa, 0.26 + o, 1.0, "easeInOutSine")
        sw = "%s_saw" % side
        e.scale(sw, 0, (1, 0.03, 1)).scale(sw, 0.05 + o, (1, 0.03, 1))
        e.scale(sw, 0.22 + o, (1, 1.15, 1), "easeOutBack").scale(sw, 0.36 + o, (1, 1, 1), "easeInOutSine")
    A.append(e)

    r = Anim("retract", 0.35, loop="hold_on_last_frame")
    r.scale("saw_bar", 0, (1, 1, 1)).scale("saw_bar", 0.2, (1, 1, 0.03), "easeInBack")
    for bn in ("form_handle_front", "form_handle_rear"):
        r.scale(bn, 0, 1).scale(bn, 0.15, 0.02, "easeInBack")
    r.scale("form_head", 0.1, 1.0).scale("form_head", 0.35, 0.78, "easeInQuad")
    for side in ("right", "left"):
        r.scale("%s_saw" % side, 0, (1, 1, 1)).scale("%s_saw" % side, 0.2, (1, 0.03, 1), "easeInBack")
        r.scale("form_%s_arm" % side, 0.1, 1.0).scale("form_%s_arm" % side, 0.35, 0.4, "easeInQuad")
    A.append(r)

    # idle: the engine block throbs, the cover breathes, the jaw twitches
    idle = Anim("idle", 2.0, loop=True)
    for i in range(21):
        idle.rot("form_engine", i * 0.1, (0.4 * math.sin(i * 2.7), 0, 0.35 * math.cos(i * 3.1)))
    idle.rot("form_shell", 0, (0, 0, 0)).rot("form_shell", 1.0, (-1.2, 0, 0.5), "easeInOutSine")
    idle.rot("form_shell", 2.0, (0, 0, 0), "easeInOutSine")
    for t, a in [(0, 0), (0.1, 4), (0.2, 0), (0.3, 3), (0.4, 0), (1.2, 0), (1.3, 5), (1.45, 0), (2.0, 0)]:
        idle.rot("jaw", t, (a, 0, 0))
    A.append(idle)

    # chain crawls toward the nose along the top/outer edge, back along the bottom/inner edge
    for name, period in (("chain_idle", 0.7), ("chain_rev", 0.07)):
        c = Anim(name, period, loop=True)
        c.pos("saw_chain_t", 0, (0, 0, 0)).pos("saw_chain_t", period, (0, 0, -1.25))
        c.pos("saw_chain_b", 0, (0, 0, -1.25)).pos("saw_chain_b", period, (0, 0, 0))
        for s in SAWS:
            c.pos(s + "_chain_o", 0, (0, 0, 0)).pos(s + "_chain_o", period, (0, -1.25, 0))
            c.pos(s + "_chain_i", 0, (0, -1.25, 0)).pos(s + "_chain_i", period, (0, 0, 0))
        A.append(c)

    def jitter(anim, bone, t0, t1, amp, step=0.05, base=(0, 0, 0)):
        t = t0
        k = 0
        while t < t1:
            sg = 1 if k % 2 == 0 else -1
            anim.rot(bone, t, (base[0] + amp * sg, base[1] - amp * 0.6 * sg, base[2] + amp * 0.4 * sg))
            t += step
            k += 1
        anim.rot(bone, t1, base)

    ARM_BASE = {"right_saw": (0, 0, 5), "left_saw": (0, 0, -5)}
    slash = Anim("slash", 0.7)
    for s in SAWS:
        jitter(slash, s, 0.0, 0.7, 2.0, 0.04, base=ARM_BASE[s])
    slash.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.15, (22, 0, 0)).rot("jaw", 0.6, (0, 0, 0), "easeInOutSine")
    A.append(slash)

    roar = Anim("roar", 1.1)
    roar.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.18, (40, 0, 0), "easeOutBack")
    jitter(roar, "jaw", 0.2, 0.85, 2.5, 0.05, base=(38, 0, 0))
    roar.rot("jaw", 1.1, (0, 0, 0), "easeInOutSine")
    jitter(roar, "saw_bar", 0.0, 1.0, 1.3, 0.04, base=(-7, 0, 0))
    A.append(roar)

    head = Anim("headbutt", 0.85)
    jitter(head, "saw_bar", 0.0, 0.85, 1.8, 0.035, base=(-7, 0, 0))
    head.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.2, (28, 0, 0)).rot("jaw", 0.85, (0, 0, 0))
    A.append(head)

    rip = Anim("rip", 1.55)
    for s in SAWS:
        jitter(rip, s, 0.0, 1.55, 3.0, 0.035, base=ARM_BASE[s])
    rip.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.2, (34, 0, 0))
    jitter(rip, "jaw", 0.25, 1.35, 3.0, 0.07, base=(32, 0, 0))
    rip.rot("jaw", 1.55, (0, 0, 0), "easeInOutSine")
    A.append(rip)

    leg = Anim("leg_spin", 0.85)
    for side in ("right", "left"):
        bn = "fx_legsaw_" + side
        leg.scale(bn, 0, 0.05).scale(bn, 0.14, 1.15, "easeOutBack").scale(bn, 0.2, 1.0).scale(bn, 0.66, 1.0)
        leg.scale(bn, 0.85, 0.05, "easeInBack")
    A.append(leg)

    throw = Anim("throw", 0.45)
    jitter(throw, "right_saw", 0.0, 0.45, 2.0, 0.04, base=ARM_BASE["right_saw"])
    A.append(throw)

    drink = Anim("drink", 1.0)
    for t, a in [(0, 0), (0.25, 32), (0.4, 4), (0.5, 28), (0.62, 3), (0.72, 26), (0.85, 2), (1.0, 0)]:
        drink.rot("jaw", t, (a, 0, 0), "easeInOutSine")
    A.append(drink)

    # plays from the start of the trigger; the handle snaps back into the chest at 0.62s and swings
    snap = Anim("cord_snap", 1.35)
    snap.rot("cord_handle", 0, (0, 0, 0)).rot("cord_handle", 0.64, (0, 0, 0))
    for t, a in [(0.68, 55), (0.8, -35), (0.92, 20), (1.04, -10), (1.17, 4), (1.32, 0)]:
        snap.rot("cord_handle", t, (a, 0, a * 0.3), "easeInOutSine")
    A.append(snap)
    return A


def render_previews(geo, tex, anim):
    legs = ("fx_legsaw_right", "fx_legsaw_left")
    head_only = legs + ("body", "right_arm", "left_arm", "right_leg", "left_leg")
    shots = [
        preview.render(geo, tex, preview_path("chainsaw_front.png"), anim, "idle", 0.0, yaw=0, pitch=5, hidden=legs,
                       scale=12, center=(0, 1.3)),
        preview.render(geo, tex, preview_path("chainsaw_34.png"), anim, "idle", 0.0, yaw=35, pitch=8, hidden=legs,
                       scale=12, center=(0, 1.3)),
        preview.render(geo, tex, preview_path("chainsaw_head_side.png"), anim, "idle", 0.0, yaw=90, pitch=4,
                       scale=30, center=(-0.35, 1.85), size=(640, 520), show_body=False, hidden=head_only),
        preview.render(geo, tex, preview_path("chainsaw_head_34.png"), anim, "roar", 0.4, yaw=40, pitch=10,
                       scale=30, center=(-0.2, 1.85), size=(640, 520), show_body=False, hidden=head_only),
    ]
    return preview.contact_sheet(shots, preview_path("chainsaw_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
