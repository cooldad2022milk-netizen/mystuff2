"""
Galgali (Violence Fiend) - fiend parts model, texture atlas and GeckoLib animations.

Reference points:
  * masked: a rather slight man in a hooded suit, his face hidden behind a plague-doctor style gas mask
    (parrot-like greens, reds and oranges in the coloured manga) that leaks poison to hold his strength in check
  * unmasked: much taller and heavily muscled, spiky black hair, four hollow eyes
  * he swells a limb with muscle to fight; once grew an arm out of his mouth after both of his were cut off
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm, bezier
from csmgen.tex import paint_atlas
from csmgen import preview, shapes


def materials():
    a = Atlas(512, 64)
    a.add("mask", kind="painted", color=(74, 176, 70), color2=(40, 110, 44))
    a.add("mask_dk", kind="painted", color=(46, 122, 50), color2=(24, 70, 30))
    a.add("mask_red", kind="painted", color=(206, 46, 40), color2=(130, 24, 22))
    a.add("mask_yel", kind="painted", color=(238, 196, 56), color2=(170, 120, 30))
    a.add("hood_dk", kind="rubber", color=(26, 27, 34))
    a.add("lens_shine", kind="glow", color=(190, 200, 210), color2=(250, 250, 255), emissive=True)
    a.add("beak", kind="painted", color=(214, 52, 38), color2=(140, 28, 24))
    a.add("beak_tip", kind="painted", color=(240, 150, 40), color2=(170, 90, 20))
    a.add("lens", kind="gloss", color=(20, 22, 30))
    a.add("brass", kind="metal", color=(206, 166, 72), scratches=2)
    a.add("strap", kind="rubber", color=(46, 34, 28))
    a.add("hood", kind="rubber", color=(34, 36, 44))
    a.add("canister", kind="metal", color=(170, 176, 170), scratches=4)
    a.add("hose", kind="rubber", color=(40, 40, 44))
    a.add("gas", kind="glow", color=(150, 220, 60), color2=(230, 255, 160), emissive=True)
    a.add("skin", kind="skin", color=(204, 176, 156))
    a.add("skin_dk", kind="skin", color=(170, 140, 122))
    a.add("muscle", kind="flesh", color=(196, 150, 130))
    a.add("hair", kind="fiber", color=(20, 20, 24))
    a.add("hollow", kind="void", color=(4, 4, 6))
    a.add("teeth", kind="teeth", color=(236, 230, 214))
    a.add("mouth", kind="void", color=(40, 10, 12))
    a.add("blood", kind="blood", color=(126, 8, 12))
    return a


# ------------------------------------------------------------------------------------------ mask + hood
def _u_for_x(f, x, v, front=True):
    """Longitude u on surface f whose point at latitude v has the given x (front half)."""
    best, bu = 1e9, 0.0
    for k in range(-60, 61):
        u = k / 240.0 if front else 0.5 + k / 240.0
        d = abs(f(u, v)[0] - x)
        if d < best:
            best, bu = d, u
    return bu


def _v_for_y(f, y, u=0.0):
    best, bv = 1e9, 0.5
    for k in range(0, 201):
        v = k / 200.0
        d = abs(f(u, v)[1] - y)
        if d < best:
            best, bv = d, v
    return bv


def plague_mask(b, offset=(0, 0, 0)):
    """Plague-doctor gas mask in parrot colours: domed green face plate, round brass-rimmed goggles, a long curved
    red beak going orange at the tip, and the poison canister feeding it through a hose."""
    o = np.asarray(offset, dtype=float)
    face = shapes.ellipsoid(o + (0, 28.0, -0.6), (4.45, 4.25, 3.95), e_lat=0.8, e_lon=0.8)

    def face_mat(u, v):
        uu = u if u < 0.5 else u - 1.0
        if v > 0.78:
            return "mask_dk"
        if 0.55 < v < 0.72 and abs(uu) > 0.05:
            return "mask_red"          # red band across the goggles
        if v < 0.36 and abs(uu) < 0.12:
            return "mask_yel"          # yellow cheeks round the beak base
        return "mask"
    shapes.shell(b, face, 12, 10, "mask", u0=-0.25, u1=0.25, v0=0.12, v1=0.93, mat_fn=face_mat, thick=0.4)
    # rim where the plate meets the hood
    for side in (-1, 1):
        u = 0.25 * side
        pts = [np.asarray(face(u, 0.12 + 0.8 * k / 8)) for k in range(9)]
        for p, q in zip(pts, pts[1:]):
            b.seg(p, q, 0.5, 0.5, "strap", overlap=0.2)
    # goggles
    for s in (-1, 1):
        v = _v_for_y(face, o[1] + 29.5)
        u = _u_for_x(face, o[0] + s * 1.95, v)
        p, n, du, dv = shapes.surface_frame(face, u, v)
        n = norm(n + np.array([0, 0.05, 0]))
        b.cylinder(p + n * 0.25, n, 1.55, 0.9, "brass", segments=12)
        b.cylinder(p + n * 0.55, n, 1.3, 0.5, "lens", segments=12)
        b.cbox(p + n * 0.82 + np.array([s * 0.35, 0.45, 0]), (0.35, 0.35, 0.2), "lens_shine")
    # the long curved beak
    P = [o + (0, 27.1, -3.6), o + (0, 26.9, -8.2), o + (0, 25.4, -11.4), o + (0, 22.8, -12.6)]
    path = lambda t: bezier(*P, t)
    beak = shapes.loft(path, shapes.profile((0, 2.3), (0.3, 1.9), (0.7, 1.0), (1, 0.15)),
                       shapes.profile((0, 2.1), (0.3, 1.8), (0.7, 0.9), (1, 0.15)), up=(0, 1, 0))
    shapes.shell(b, beak, 10, 12, "beak", mat_fn=lambda u, v: "beak_tip" if v > 0.68 else "beak", thick=0.4)
    for t in (0.2, 0.42):
        p = path(t)
        q = path(t + 0.02)
        b.ring(p, q - p, 1.95 - 0.5 * t, 0.2, 0.35, "brass", count=10)
    # breathing holes along the top of the beak
    for t in (0.3, 0.38):
        p, n, du, dv = shapes.surface_frame(beak, 0.0, t)
        b.cylinder(p, n, 0.3, 0.2, "lens", segments=6)
    # the poison canister clipped to the side, feeding the mask through a hose
    c = o + (-5.0, 26.6, 1.0)
    b.cylinder(c, (0, 1, 0), 1.1, 3.6, "canister", segments=12)
    b.cylinder(c + (0, 1.95, 0), (0, 1, 0), 0.7, 0.4, "brass", segments=10)
    b.cylinder(c + (0, -1.9, 0), (0, 1, 0), 0.9, 0.3, "brass", segments=10)
    b.cbox(c + (-0.9, 0, -0.2), (0.3, 1.8, 0.8), "gas")
    hose = shapes.polyline([c + (0, 2.1, 0), c + (-0.9, 2.2, -2.0), c + (0.2, 1.0, -4.0), o + (-2.6, 26.2, -4.4)])
    shapes.shell(b, shapes.loft(hose, 0.32, 0.32), 6, 8, "hose", thick=0.25)


def hood(b):
    """The hood of his suit: a rounded cowl over the head, open at the face."""
    h = shapes.ellipsoid((0, 28.3, 0.4), (4.95, 4.85, 5.0), e_lat=0.75, e_lon=0.8)
    shapes.shell(b, h, 16, 10, "hood", v0=0.18, skip=lambda u, v: (u < 0.2 or u > 0.8) and v < 0.86, thick=0.45)
    # the hood's face opening: a thick rolled rim
    for side in (-1, 1):
        pts = [np.asarray(h(0.5 + side * 0.3, 0.18 + 0.68 * k / 8)) for k in range(9)]
        for p, q in zip(pts, pts[1:]):
            b.seg(p, q, 0.9, 0.9, "hood_dk", overlap=0.3)
    top = [np.asarray(h(0.8 + 0.4 * k / 10, 0.86)) for k in range(11)]
    for p, q in zip(top, top[1:]):
        b.seg(p, q, 0.9, 0.9, "hood_dk", overlap=0.3)
    # the collar draping onto the shoulders
    collar = shapes.loft(shapes.polyline([(0, 25.2, 0.6), (0, 23.6, 0.8)]), shapes.profile((0, 4.8), (1, 5.6)),
                         shapes.profile((0, 4.6), (1, 5.2)), up=(0, 0, -1))
    shapes.shell(b, collar, 14, 2, "hood", u0=0.14, u1=0.86, thick=0.45)


# ------------------------------------------------------------------------------------------ unmasked head
def unmasked_head(f, rng):
    skull = shapes.ellipsoid((0, 28.4, 0.2), (4.35, 4.6, 4.5), e_lat=0.72, e_lon=0.72)
    shapes.shell(f, skull, 14, 12, "skin", v0=0.16, thick=0.45)
    jaw = shapes.ellipsoid((0, 25.4, -0.9), (3.9, 2.0, 3.4), e_lat=0.7, e_lon=0.7)
    shapes.shell(f, jaw, 12, 6, "skin", thick=0.4)
    # heavy brow ridge
    for s in (-1, 1):
        f.obox((s * 1.8, 30.9, -4.25), (s * 1.0, 0.05, 0), (0.9, 3.2, 1.0), "skin_dk", up=(0, 0.3, -1))
    # four hollow eyes: two pairs of sunken black sockets
    for row, y in enumerate((29.9, 28.0)):
        v = _v_for_y(skull, y)
        for s in (-1, 1):
            u = _u_for_x(skull, s * (1.85 - 0.15 * row), v)
            p, n, du, dv = shapes.surface_frame(skull, u, v)
            f.obox(p + n * 0.22, du, (1.25, 1.7, 0.5), "hollow", up=n)
            f.obox(p + n * 0.08, du, (1.7, 2.2, 0.4), "skin_dk", up=n)
    # a wide mouth full of teeth
    mp, mn, mdu, mdv = shapes.surface_frame(jaw, 0.0, 0.62)
    f.obox(mp + mn * 0.2, (1, 0, 0), (1.1, 5.2, 0.5), "mouth", up=mn)
    for k in range(8):
        x = -2.3 + k * 0.66
        f.spike((x, mp[1] + 0.55, mp[2] - 0.5), (0, -1, -0.1), 0.6, 0.5, 0.2, "teeth", steps=2)
        f.spike((x + 0.33, mp[1] - 0.55, mp[2] - 0.45), (0, 1, -0.1), 0.5, 0.45, 0.2, "teeth", steps=2)
    # spiky black hair
    # a cropped black mat over the scalp with long spikes bristling out of it
    shapes.shell(f, lambda u, v: np.asarray(skull(u, v)) + 0.35 * shapes.surface_frame(skull, u, v)[1], 14, 5,
                 "hair", v0=0.66, v1=1.0, thick=0.5,
                 skip=lambda u, v: abs(u if u < 0.5 else u - 1.0) < 0.16 and v < 0.76)
    placed = 0
    while placed < 46:
        u = rng.random()
        v = rng.uniform(0.6, 0.98)
        uu = u if u < 0.5 else u - 1.0
        if abs(uu) < 0.16 and v < 0.78:
            continue  # keep the forehead clear
        p, n, du, dv = shapes.surface_frame(skull, u, v)
        d = norm(n * 1.2 + np.array([0, 0.75, 0.3]) + np.array([rng.uniform(-0.3, 0.3), 0, rng.uniform(-0.3, 0.3)]))
        shapes.horn(f, p - n * 0.2, d, rng.uniform(3.2, 6.4), rng.uniform(1.0, 1.5), mat="hair", sections=4,
                    around=5, r1=0.05, thick=0.3)
        placed += 1


def muscle_limb(bone, top, bottom, radii, mat="skin", around=12, sections=12, flat=1.0, bulges=True):
    """A smooth muscular limb from top to bottom with a bulging radius profile [(t, r), ...], plus separate muscle
    bellies (deltoid cap, biceps, triceps, forearm) so it reads as muscle rather than a padded tube."""
    r = shapes.profile(*radii)
    top = np.asarray(top, dtype=float)
    bottom = np.asarray(bottom, dtype=float)
    f = shapes.loft(shapes.polyline([top, bottom]), r, lambda t: r(t) * flat, up=(0, 0, -1))
    shapes.shell(bone, f, around, sections, mat, thick=0.45)
    if bulges:
        L = np.linalg.norm(bottom - top)
        axis = norm(bottom - top)
        out_x = 1.0 if top[0] >= 0 else -1.0
        k = r(0.3)
        for t, dirv, size, m in ((0.12, (out_x * 0.8, 0.3, 0), (0.85, 0.46, 0.9), mat),       # deltoid cap
                                 (0.34, (0, 0, -1), (0.72, 0.56, 0.62), mat),                  # biceps
                                 (0.67, (out_x * 0.4, 0, -1), (0.7, 0.42, 0.62), mat)):         # forearm
            c = top + axis * (L * t) + norm(dirv) * (r(t) * 0.36)
            e = shapes.ellipsoid(c, (k * size[0], L * size[1] * 0.45, k * size[2]), e_lat=0.9, e_lon=0.9)
            shapes.shell(bone, e, 10, 6, m, thick=0.4)
    return f


def fist(bone, center, size, knuckle_dir=(0, -1, -0.35), mat="skin"):
    c = np.asarray(center, dtype=float)
    sx, sy, sz = size
    f = shapes.ellipsoid(c, (sx, sy, sz), e_lat=0.5, e_lon=0.5)
    shapes.shell(bone, f, 12, 8, mat, thick=0.4)
    d = norm(knuckle_dir)
    for k in range(4):
        x = -sx * 0.66 + k * sx * 0.44
        bone.cbox(c + np.array([x, 0, 0]) + d * (sy * 0.92), (sx * 0.36, sy * 0.4, sz * 0.36), "skin_dk")


def build_head(m):
    rng = __import__("random").Random(11)
    m.bone("head", pivot=(0, 24, 0))
    hood(m.bone("prop_hood", parent="head", pivot=(0, 24, 0)))
    plague_mask(m.bone("prop_mask", parent="head", pivot=(0, 28, -4)))

    # unmasked: taller (the whole player renders bigger), four hollow eyes, spiky black hair
    f = m.bone("form_head", parent="head", pivot=(0, 24, 0))
    unmasked_head(f, rng)
    # the arm that grows out of his mouth
    ma = m.bone("fx_moutharm_head", parent="form_head", pivot=(0, 25.6, -4.4))
    P = [np.array([0, 25.6, -4.0]), np.array([0, 24.8, -8.0]), np.array([0, 25.6, -11.5]), np.array([0, 25.8, -14.2])]
    arm = shapes.loft(lambda t: bezier(*P, t), shapes.profile((0, 1.3), (0.3, 1.95), (0.55, 1.5), (0.8, 1.75), (1, 1.4)),
                      shapes.profile((0, 1.2), (0.3, 1.8), (0.55, 1.4), (0.8, 1.6), (1, 1.3)), up=(0, 1, 0))
    shapes.shell(ma, arm, 10, 12, "skin", thick=0.4)
    fist(ma, (0, 25.8, -16.0), (2.0, 1.8, 1.9), knuckle_dir=(0, 0, -1))
    ma.obox((0, 25.4, -4.3), (1, 0, 0), (1.4, 4.6, 0.6), "blood", up=(0, 0, -1))


def build_trigger(m):
    """The mask pulled off and held in his right hand."""
    t = m.bone("trig_mask", parent="right_arm", pivot=(-6, 11, -1))
    plague_mask(t, offset=(-6.0, -16.0, 3.4))


# ------------------------------------------------------------------------------------------ body / limbs
ARM_PROFILE = ((0, 2.6), (0.1, 3.35), (0.28, 3.25), (0.47, 2.95), (0.62, 3.2), (0.86, 2.95), (1, 2.9))


def muscle_arm(m, side):
    sgn = -1 if side == "right" else 1

    def X(o):
        return sgn * o

    # the arms swell with muscle (the sleeves are gone)
    f = m.bone("form_%s_arm" % side, parent=side + "_arm", pivot=(X(6), 22, 0))
    muscle_limb(f, (X(6), 24.6, 0), (X(6), 12.2, 0), ARM_PROFILE)
    fist(f, (X(6), 11.0, -0.1), (2.75, 1.85, 2.6))
    # swollen arm and fist for the haymaker
    p = m.bone("fx_punch_" + side, parent=side + "_arm", pivot=(X(6), 12, 0))
    muscle_limb(p, (X(6), 25.0, 0), (X(6), 10.4, 0), tuple((t, r * 1.42) for t, r in ARM_PROFILE), sections=14)
    fist(p, (X(6), 8.4, -0.2), (3.9, 2.7, 3.7))


def build_limbs(m):
    m.bone("body", pivot=(0, 24, 0))
    for side in ("right", "left"):
        m.bone(side + "_arm", pivot=((-5 if side == "right" else 5), 22, 0))
        muscle_arm(m, side)
    m.bone("right_leg", pivot=(-1.9, 12, 0))
    k = m.bone("fx_kick_right", parent="right_leg", pivot=(-1.9, 12, 0))
    muscle_limb(k, (-1.9, 12.6, 0), (-1.9, 1.6, 0), ((0, 3.5), (0.25, 3.95), (0.5, 3.15), (0.72, 3.45), (1, 2.7)),
                bulges=False)
    foot = shapes.ellipsoid((-1.9, 1.1, -1.4), (2.7, 1.25, 4.0), e_lat=0.55, e_lon=0.6)
    shapes.shell(k, foot, 12, 6, "strap", thick=0.4)
    m.bone("left_leg", pivot=(1.9, 12, 0))


def build():
    atlas = materials()
    m = Model("csm.violence_fiend", atlas, density=2.0, seed=89)
    build_head(m)
    build_limbs(m)
    build_trigger(m)
    geo = out("geo", "hybrid", "violence.geo.json")
    tex = out("textures", "hybrid", "violence.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "violence_glowmask.png"), seed=53)
    anims = animations()
    anim_path = out("animations", "hybrid", "violence.animation.json")
    save_animations(anim_path, anims)
    print("violence: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    e = Anim("emerge", 0.8)
    e.scale("form_head", 0, 0.8).scale("form_head", 0.2, 1.1, "easeOutBack").scale("form_head", 0.35, 1.0)
    for i, side in enumerate(("right", "left")):
        fa = "form_%s_arm" % side
        e.scale(fa, 0, 0.7).scale(fa, 0.2 + 0.05 * i, 1.15, "easeOutBack").scale(fa, 0.4, 1.0)
    A.append(e)
    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    r.scale("form_head", 0, 1).scale("form_head", 0.3, 0.85)
    for side in ("right", "left"):
        r.scale("form_%s_arm" % side, 0, 1).scale("form_%s_arm" % side, 0.35, 0.75, "easeInQuad")
    A.append(r)
    idle = Anim("idle", 2.0, loop=True)
    for side in ("right", "left"):
        fa = "form_%s_arm" % side
        idle.scale(fa, 0, 1).scale(fa, 1.0, 1.03, "easeInOutSine").scale(fa, 2.0, 1, "easeInOutSine")
    A.append(idle)

    def swell(anim, bone, t0, t1, t2):
        anim.scale(bone, 0, 0.6).scale(bone, t0, 0.6).scale(bone, t1, 1.1, "easeOutBack").scale(bone, t2, 1.0)
        anim.scale(bone, t2 + 0.1, 0.6, "easeInQuad")

    pu = Anim("punch", 0.8)
    swell(pu, "fx_punch_right", 0.05, 0.3, 0.55)
    A.append(pu)
    ki = Anim("kick", 0.9)
    swell(ki, "fx_kick_right", 0.1, 0.4, 0.65)
    A.append(ki)
    ma = Anim("mouth_arm", 1.1)
    ma.scale("fx_moutharm_head", 0, (1, 1, 0.05)).scale("fx_moutharm_head", 0.2, (1, 1, 0.05))
    ma.scale("fx_moutharm_head", 0.4, (1.05, 1.05, 1.15), "easeOutBack").scale("fx_moutharm_head", 0.62, (1.1, 1.1, 1.0))
    ma.scale("fx_moutharm_head", 0.68, (1.2, 1.2, 1.25)).scale("fx_moutharm_head", 0.9, 1.0)
    ma.scale("fx_moutharm_head", 1.1, (1, 1, 0.05), "easeInQuad")
    A.append(ma)
    ra = Anim("rampage", 1.6)
    for side, t0 in (("right", 0.1), ("left", 0.25)):
        bn = "fx_punch_" + side
        ra.scale(bn, 0, 0.6).scale(bn, t0, 1.0, "easeOutBack")
        for k in range(8):
            t = t0 + 0.05 + k * 0.17
            ra.scale(bn, t, 1.15).scale(bn, t + 0.08, 0.95)
        ra.scale(bn, 1.5, 1.0).scale(bn, 1.6, 0.6)
    A.append(ra)
    A.append(Anim("drink", 1.0))
    # trigger: the mask comes away in his hand at 0.4 s and is dropped once he has grown
    um = Anim("unmask", 1.2)
    um.scale("trig_mask", 0, 0).scale("trig_mask", 0.39, 0).scale("trig_mask", 0.4, 1).scale("trig_mask", 1.0, 1)
    um.pos("trig_mask", 0.8, (0, 0, 0)).pos("trig_mask", 1.05, (0, -8, 0), "easeInQuad")
    um.scale("trig_mask", 1.1, 0)
    A.append(um)
    return A


def render_previews(geo, tex, anim):
    fx = ("fx_punch_right", "fx_punch_left", "fx_kick_right", "fx_moutharm_head", "trig_mask")
    arms = {"right_arm": {"rot": (0, 0, 0.1)}, "left_arm": {"rot": (0, 0, -0.1)}}
    shots = [
        preview.render(geo, tex, preview_path("violence_masked.png"), anim, "idle", 0, yaw=40, pitch=6, pose=arms,
                       hidden=fx + ("form_head", "form_right_arm", "form_left_arm"), scale=16, center=(0, 1.6),
                       size=(640, 520)),
        preview.render(geo, tex, preview_path("violence_unmasked.png"), anim, "idle", 0, yaw=25, pitch=6, pose=arms,
                       hidden=fx + ("prop_hood", "prop_mask"), scale=10, center=(0, 1.2)),
        preview.render(geo, tex, preview_path("violence_moutharm.png"), anim, "idle", 0, yaw=60, pitch=8,
                       pose={"right_arm": {"rot": (-1.5, 0, 0)}},
                       hidden=("prop_hood", "prop_mask", "fx_punch_left", "fx_kick_right", "trig_mask"), scale=9,
                       center=(0, 1.3)),
        preview.render(geo, tex, preview_path("violence_kick.png"), anim, "idle", 0, yaw=-40, pitch=8,
                       pose={"right_leg": {"rot": (-1.2, 0, 0)}},
                       hidden=("prop_hood", "prop_mask", "fx_punch_left", "fx_punch_right", "fx_moutharm_head", "trig_mask"),
                       scale=9, center=(0, 1.1)),
    ]
    return preview.contact_sheet(shots, preview_path("violence_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
