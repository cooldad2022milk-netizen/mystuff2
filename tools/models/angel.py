"""
The Angel Devil - mob model (entity/devil/angel), the player's devil parts (hybrid/angel) and the moves' body
animations, authored once for both the player (PlayerAnimator) and the mob (GeckoLib).

Reference points:
  * a slight, sleepy-eyed youth with pale golden, shoulder-length hair and a halo floating over his head
  * a pair of white feathered wings on his back
  * Public Safety clothes: white shirt, black tie, dark trousers
  * whatever he touches loses years of its life; he forges the lifespan he has taken into weapons - a golden sword,
    spears that rain from the sky
"""
import math
import os
import sys

import numpy as np

from common import preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from player_anims import A, NEUTRAL_R, NEUTRAL_L, Z3  # noqa: E402

HAIR = (236, 212, 150)
HAIR_DK = (204, 176, 112)


def draw_sleepy_eye(d, n):
    """A tired, half-lidded eye: the upper lid hangs over half of an amber iris."""
    d.ellipse([1, n * 0.2, n - 2, n * 0.8], fill=(246, 242, 236, 255))
    r = n * 0.26
    cx, cy = n * 0.5, n * 0.54
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 150, 70, 255))
    d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=(60, 36, 20, 255))
    d.rectangle([0, 0, n, n * 0.46], fill=(0, 0, 0, 0))
    d.line([(1, n * 0.46), (n - 2, n * 0.46)], fill=(70, 50, 40, 255), width=max(2, n // 12))


def materials(size=512):
    a = Atlas(size, 64)
    a.add("skin", kind="skin", color=(246, 222, 206))
    a.add("hair", kind="fiber", color=HAIR)
    a.add("hair_dk", kind="fiber", color=HAIR_DK)
    a.add("shirt", kind="skin", color=(244, 244, 240))
    a.add("shirt_dk", kind="skin", color=(214, 214, 210))
    a.add("tie", kind="skin", color=(24, 24, 28))
    a.add("pants", kind="skin", color=(34, 34, 42))
    a.add("shoe", kind="gloss", color=(22, 22, 24))
    a.add("eye", kind="decal", color=(200, 150, 70), draw=draw_sleepy_eye)
    a.add("brow", kind="skin", color=(196, 166, 104))
    a.add("lip", kind="skin", color=(220, 164, 150))
    a.add("feather", kind="feather", color=(248, 248, 244), color2=(206, 206, 214))
    a.add("feather_dk", kind="feather", color=(226, 226, 232), color2=(180, 180, 194))
    a.add("halo", kind="glow", color=(255, 236, 150), emissive=True)
    a.add("gold", kind="glow", color=(255, 224, 120), color2=(255, 250, 220), emissive=True)
    return a


# ------------------------------------------------------------------------------------------ pieces
def hair(look):
    """Pale gold hair: a soft cap, bangs over the brow, and locks falling to the shoulders all round."""
    cap = shapes.ellipsoid((0, 28.5, 0.3), (4.5, 4.5, 4.55), e_lat=0.45, e_lon=0.5)
    shapes.shell(look, cap, 16, 10, "hair", v0=0.28, thick=0.45,
                 skip=lambda u, v: (u < 0.2 or u > 0.8) and v < 0.62,
                 mat_fn=lambda u, v: "hair_dk" if v < 0.4 else "hair")
    for k in range(9):
        x = -3.5 + k * 0.88
        top = np.array([x * 0.8, 32.3, -3.0])
        tip = np.array([x * 1.05 + 0.3 * math.sin(k * 2.1), 28.6 - 0.4 * (k % 3), -4.45])
        shapes.horn(look, top, tip - top, np.linalg.norm(tip - top), 1.0, mat="hair" if k % 2 else "hair_dk",
                    flat=0.35, up=(0, 0, 1), sections=4, around=6, r1=0.12, thick=0.3)
    # locks all round the back and sides, ending at the shoulders with a slight outward flick
    for k in range(15):
        a = math.radians(-105 + k * 15)
        base = np.array([math.sin(a) * 4.2, 29.5, 0.3 + math.cos(a) * 4.2])
        if math.cos(a) < -0.45:
            continue
        d = norm(np.array([math.sin(a) * 0.2, -1.0, math.cos(a) * 0.15]))
        shapes.horn(look, base, d, 7.5 + 0.6 * (k % 2), 1.3, mat="hair" if k % 2 else "hair_dk", flat=0.45,
                    up=(math.sin(a), 0, math.cos(a)), sections=5, around=6, r1=0.3, thick=0.3,
                    bend_axis=(math.cos(a), 0, -math.sin(a)), bend=-18)


def face(look):
    dk.face_eyes(look, "eye", y=27.5, spacing=1.95, size=(2.0, 1.4), z=-3.97)
    for s in (-1, 1):
        look.obox((s * 1.95, 28.75, -4.02), (s * 1.0, -0.05, 0), (0.25, 1.8, 0.2), "brow", up=(0, 0, -1))
    look.obox((0, 25.7, -4.0), (1, 0, 0), (0.25, 1.1, 0.15), "lip", up=(0, 0, -1))
    look.obox((0, 26.8, -4.02), (0, 1, 0), (0.35, 0.5, 0.15), "skin", up=(0, 0, -1))


def clothes(body):
    for s in (-1, 1):
        body.obox((s * 1.2, 23.4, -2.2), (s * 0.7, -1, 0), (1.6, 1.9, 0.25), "shirt_dk", up=(0, 0, -1))
    body.obox((0, 23.2, -2.25), (0, 1, 0), (0.95, 0.9, 0.35), "tie", up=(0, 0, -1))
    tie = shapes.loft(shapes.polyline([(0, 22.8, -2.25), (0, 18.0, -2.15), (0, 16.4, -2.2)]),
                      shapes.profile((0, 0.4), (0.8, 0.62), (1, 0.1)), 0.12, up=(0, 0, -1))
    shapes.shell(body, tie, 4, 6, "tie", thick=0.2)
    for y in (21.0, 19.3, 17.6):
        body.cbox((0.9, y, -2.18), (0.25, 0.25, 0.1), "shirt_dk")
    dk.rbox(body, (0, 12.4, 0), (3.75, 0.9, 2.0), "pants", e=0.45, nu=12, nv=4)


def wing(bone, s, root):
    """A feathered wing folded half-open behind the back: coverts along the arm, secondaries hanging from the
    forearm, long primaries fanning from the wrist."""
    root = np.asarray(root, dtype=float)
    el = root + np.array([s * 5.0, 5.0, 3.0])
    wr = root + np.array([s * 9.5, 1.8, 4.6])
    arm_pts = [root, el, wr]
    edge = shapes.polyline(arm_pts)
    shapes.shell(bone, shapes.loft(edge, shapes.profile((0, 1.1), (1, 0.6)), shapes.profile((0, 0.9), (1, 0.5))),
                 6, 10, "feather", thick=0.3)
    along = norm(wr - root)
    n = norm(np.cross(along, (0, -1, 0)))
    for k in range(9):   # coverts
        t = (k + 0.5) / 9
        p = edge(t)
        d = norm(np.array([s * 0.15, -1.0, 0.25]))
        shapes.horn(bone, p, d, 3.0 + 2.5 * t, 1.1, mat="feather_dk", flat=0.22, up=n, sections=3, around=5, r1=0.25,
                    thick=0.25)
    for k in range(8):   # secondaries
        t = 0.35 + 0.65 * (k + 0.5) / 8
        p = edge(t) + n * 0.15
        d = norm(np.array([s * 0.1, -1.0, 0.3]))
        shapes.horn(bone, p, d, 8.0 + 2.0 * t, 1.2, mat="feather", flat=0.2, up=n, sections=4, around=5, r1=0.3,
                    thick=0.25)
    for k in range(6):   # primaries
        f = k / 5
        d = norm(np.array([s * (0.75 - 0.5 * f), -1.0 + 0.45 * (1 - f), 0.25 + 0.1 * f]))
        shapes.horn(bone, wr + n * 0.3, d, 11.0 + 3.0 * math.sin(f * math.pi) + 2 * f, 1.2, mat="feather",
                    flat=0.2, up=n, sections=5, around=5, r1=0.25, thick=0.25, bend_axis=n, bend=-8 * s)


def halo(bone, center):
    bone.ring(center, (0, 1, 0.12), 3.3, 0.4, 0.55, "halo", count=24)


def lifespan_sword(bone, grip):
    """A golden sword forged out of stolen years, held forward in the right fist."""
    grip = np.asarray(grip, dtype=float)
    d = norm(np.array([0, 0.3, -1.0]))
    bone.cylinder(tuple(grip), tuple(d), 0.45, 2.4, "gold", segments=6)
    bone.obox(grip + d * 1.4, (1, 0, 0), (0.5, 3.0, 0.6), "gold", up=d)
    blade = shapes.loft(shapes.polyline([grip + d * 1.6, grip + d * 12.0, grip + d * 16.5]),
                        shapes.profile((0, 0.9), (0.75, 0.75), (1, 0.05)), 0.15, up=(1, 0, 0))
    shapes.shell(bone, blade, 4, 10, "gold", thick=0.2)


def spear_ring(bone, center, radius, count=8):
    """Lifespan spears hanging point-down in a ring over his head before they fall."""
    c = np.asarray(center, dtype=float)
    for k in range(count):
        a = k * 2 * math.pi / count
        p = c + np.array([math.cos(a) * radius, 0, math.sin(a) * radius])
        d = norm(np.array([math.cos(a) * 0.2, -1.0, math.sin(a) * 0.2]))
        bone.cylinder(tuple(p - d * 4.0), tuple(d), 0.25, 9.0, "gold", segments=5)
        bone.spike(p + d * 0.6, d, 2.4, 0.9, 0.3, "gold", steps=3, up=(math.cos(a), 0, math.sin(a)))


# ------------------------------------------------------------------------------------------ entity
def build_entity():
    atlas = materials()
    m = Model("csm.angel_devil", atlas, density=2.0, seed=281)
    bones = dk.humanoid(m, {"skin": "skin", "shirt": "shirt", "sleeve": "shirt", "cuff": "shirt_dk", "pants": "pants",
                            "shoe": "shoe"}, slim=True)
    clothes(bones["body"])
    face(bones["look"])
    hair(bones["look"])
    halo(bones["look"], (0, 34.4, 0.6))
    for s, name in ((-1, "wing_right"), (1, "wing_left")):
        root = (s * 1.4, 21.0, 2.3)
        w = m.bone(name, parent="body", pivot=root)
        wing(w, s, root)
    sw = m.bone("fx_sword_blade", parent="right_arm", pivot=(-5.5, 11.5, -0.4))
    lifespan_sword(sw, (-5.5, 11.3, -0.6))
    sp = m.bone("fx_spears_ring", parent="root", pivot=(0, 42, 0))
    spear_ring(sp, (0, 42, 0), 7.0)
    geo, tex, glow, anim_path = dk.devil_paths("angel")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=283)
    anims = entity_animations()
    save_animations(anim_path, anims)
    print("angel entity: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


# ------------------------------------------------------------------------------------------ the player's features
def build_parts():
    """A player who became the Angel Devil: a halo and wings while the devil is out, the golden weapons in use."""
    atlas = materials(256)
    m = Model("csm.angel_parts", atlas, density=2.0, seed=287)
    m.bone("head", pivot=(0, 24, 0))
    h = m.bone("form_halo", parent="head", pivot=(0, 34.4, 0.6))
    halo(h, (0, 34.4, 0.6))
    sp = m.bone("fx_spears_ring", parent="head", pivot=(0, 42, 0))
    spear_ring(sp, (0, 42, 0), 7.0)
    m.bone("body", pivot=(0, 24, 0))
    fw = m.bone("form_wings", parent="body", pivot=(0, 21, 2.3))
    for s, name in ((-1, "wing_right"), (1, "wing_left")):
        root = (s * 1.4, 21.0, 2.3)
        w = m.bone(name, parent="form_wings", pivot=root)
        wing(w, s, root)
    m.bone("right_arm", pivot=(-5, 22, 0))
    sw = m.bone("fx_sword_blade", parent="right_arm", pivot=(-6, 11.5, -0.4))
    lifespan_sword(sw, (-6.0, 11.0, -0.6))
    m.bone("left_arm", pivot=(5, 22, 0))
    geo, tex, glow, anim_path = dk.part_paths("angel")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=289)
    A_ = []
    idle = Anim("idle", 3.0, loop=True)
    for i in range(9):
        t = 3.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("wing_right", t, (0, -4 - 3 * math.sin(ph), 0))
        idle.rot("wing_left", t, (0, 4 + 3 * math.sin(ph), 0))
        idle.pos("form_halo", t, (0, 0.3 * math.sin(ph), 0))
    A_.append(idle)
    em = Anim("emerge", 0.7)
    em.scale("form_wings", 0, 0.1).scale("form_wings", 0.4, 1.12, "easeOutBack").scale("form_wings", 0.7, 1.0)
    em.scale("form_halo", 0, 0.1).scale("form_halo", 0.5, 1.2, "easeOutBack").scale("form_halo", 0.7, 1.0)
    A_.append(em)
    rt = Anim("retract", 0.4, loop="hold_on_last_frame")
    rt.scale("form_wings", 0, 1.0).scale("form_wings", 0.35, 0.1).scale("form_halo", 0, 1.0).scale("form_halo", 0.35, 0.1)
    A_.append(rt)
    un = unfurl("unleash", 1.0)
    un.scale("form_wings", 0, 0.1).scale("form_wings", 0.45, 1.1, "easeOutBack").scale("form_wings", 0.7, 1.0)
    un.scale("form_halo", 0, 0.1).scale("form_halo", 0.6, 1.2, "easeOutBack").scale("form_halo", 0.8, 1.0)
    A_.append(un)
    A_.append(unfurl("gust", 0.8, beat=True))
    for name in ("touch", "sword", "spears", "drink"):
        A_.append(Anim(name, 0.5))
    save_animations(anim_path, A_)
    print("angel parts: %d cubes" % m.cube_count())
    return geo, tex, anim_path


def unfurl(name, length, beat=False):
    """The wings open wide (and, for a wing beat, sweep hard forward and back)."""
    a = Anim(name, length)
    for b, s in (("wing_right", -1), ("wing_left", 1)):
        a.rot(b, 0, (0, 0, 0))
        if beat:
            a.rot(b, 0.2, (0, s * 55, s * -20), "easeOutQuad").rot(b, 0.4, (0, s * -30, s * 10), "easeInQuad")
            a.rot(b, length, (0, 0, 0))
        else:
            a.rot(b, length * 0.5, (0, s * 50, s * -25), "easeOutQuad").rot(b, length, (0, 0, 0))
    return a


# ------------------------------------------------------------------------------------------ moves (body)
def player_moves():
    anims = {}
    # slot 0: the wings unfold and the halo lights - a yawn, a stretch
    t = A("angel_trigger", 20)
    t.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    t.k(8, "OUTQUAD", rightArm=(-0.2, 0.1, 0.6), leftArm=(-0.2, -0.1, -0.6), head=(-0.25, 0, 0), torso=(-0.1, 0, 0))
    t.k(14, rightArm=(-0.15, 0.1, 0.5), leftArm=(-0.15, -0.1, -0.5), head=(-0.2, 0, 0.05))
    t.k(20, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    t.save()
    anims["unleash"] = t
    r = A("angel_revert", 12)
    r.k(0, head=Z3).k(5, head=(0.25, 0, 0)).k(12, head=Z3)
    r.save()

    # Lifespan drain: a lazy reach, the fingertips rest on the target
    tc = A("angel_touch", 18)
    tc.k(0, rightArm=NEUTRAL_R, head=Z3)
    tc.k(6, "OUTQUAD", rightArm=(-1.45, 0.1, 0.0), head=(0.1, -0.05, 0), torso=(0.12, 0, 0))
    tc.k(12, rightArm=(-1.4, 0.1, 0.0), head=(0.1, -0.05, 0))
    tc.k(18, rightArm=NEUTRAL_R, head=Z3, torso=Z3)
    tc.save()
    anims["touch"] = tc

    # Lifespan sword: raised over the left shoulder, then a long diagonal cut
    sw = A("angel_sword", 20)
    sw.k(0, rightArm=NEUTRAL_R, torso=Z3)
    sw.k(6, "OUTQUAD", rightArm=(-2.6, -0.6, 0.3), torso=(0, 0.35, 0), head=(0, 0.1, 0))
    sw.k(10, "INQUAD", rightArm=(-0.9, 0.7, 0.2), torso=(0.15, -0.45, 0), head=(0.05, -0.1, 0))
    sw.k(13, rightArm=(-0.7, 0.8, 0.2), torso=(0.12, -0.4, 0))
    sw.k(20, rightArm=NEUTRAL_R, torso=Z3, head=Z3)
    sw.save()
    anims["sword"] = sw

    # Spears: a hand raised to the sky, then brought down - the spears fall
    sp = A("angel_spears", 30)
    sp.k(0, rightArm=NEUTRAL_R, head=Z3)
    sp.k(8, "OUTQUAD", rightArm=(-2.9, 0.1, 0.1), head=(-0.35, 0, 0))
    sp.k(16, rightArm=(-2.95, 0.1, 0.1), head=(-0.3, 0, 0))
    sp.k(20, "INQUAD", rightArm=(-1.2, 0.1, 0.1), head=(0.15, 0, 0))
    sp.k(30, rightArm=NEUTRAL_R, head=Z3)
    sp.save()
    anims["spears"] = sp

    # Wing beat: arms thrown back as the wings sweep forward
    g = A("angel_gust", 16)
    g.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    g.k(4, "OUTQUAD", rightArm=(0.5, 0, 0.5), leftArm=(0.5, 0, -0.5), torso=(-0.15, 0, 0))
    g.k(8, rightArm=(0.3, 0, 0.3), leftArm=(0.3, 0, -0.3), torso=(0.1, 0, 0))
    g.k(16, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    g.save()
    anims["gust"] = g
    return anims


def entity_animations():
    moves = player_moves()
    out_ = [dk.humanoid_idle(), flight(), dk.humanoid_death()]
    # idle: the wings breathe
    idle = out_[0]
    for i in range(9):
        t = idle.length * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("wing_right", t, (0, -4 - 3 * math.sin(ph), 0))
        idle.rot("wing_left", t, (0, 4 + 3 * math.sin(ph), 0))
    for geo_name, a in moves.items():
        g = dk.from_player_anim(a, geo_name)
        if geo_name == "unleash":
            g.name = "manifest"
            for b, s in (("wing_right", -1), ("wing_left", 1)):
                g.rot(b, 0, (0, 0, 0)).rot(b, 0.5, (0, s * 50, s * -25), "easeOutQuad").rot(b, 1.0, (0, 0, 0))
        if geo_name == "gust":
            for b, s in (("wing_right", -1), ("wing_left", 1)):
                g.rot(b, 0, (0, 0, 0)).rot(b, 0.2, (0, s * 55, s * -20), "easeOutQuad")
                g.rot(b, 0.4, (0, s * -30, s * 10), "easeInQuad").rot(b, 0.8, (0, 0, 0))
        if geo_name == "spears":
            g.pos("fx_spears_ring", 0, (0, 0, 0)).pos("fx_spears_ring", 0.9, (0, 2, 0)).pos("fx_spears_ring", 1.1,
                                                                                             (0, -30, 0), "easeInQuad")
            g.rot("fx_spears_ring", 0, (0, 0, 0)).rot("fx_spears_ring", 0.9, (0, 120, 0))
        out_.append(g)
    out_.append(Anim("retract", 0.3))
    out_.append(Anim("drink", 1.0))
    return out_


def flight():
    """The Angel flies: slow deep wingbeats, legs trailing, body leaning into the flight."""
    a = Anim("move", 1.2, loop=True)
    for i in range(9):
        t = 1.2 * i / 8
        ph = 2 * math.pi * i / 8
        beat = math.sin(ph)
        for b, s in (("wing_right", -1), ("wing_left", 1)):
            a.rot(b, t, (10 * beat, s * (40 + 25 * beat), s * (-30 * beat)))
        a.rot("waist", t, (14, 0, 0))
        a.rot("right_leg", t, (12 + 4 * beat, 0, 2))
        a.rot("left_leg", t, (18 + 4 * beat, 0, -2))
        a.rot("right_arm", t, (8, 0, 10))
        a.rot("left_arm", t, (8, 0, -10))
        a.rot("head", t, (-10, 0, 0))
        a.pos("root", t, (0, 1.2 * math.sin(ph - 0.8), 0))
    return a


def render_previews(geo, tex, anim):
    hid = ("fx_sword_blade", "fx_spears_ring")
    shots = [
        preview.render(geo, tex, preview_path("angel_front.png"), anim, "idle", 0, yaw=20, pitch=4, show_body=False,
                       scale=11, center=(0, 1.2), size=(520, 620), hidden=hid),
        preview.render(geo, tex, preview_path("angel_back.png"), anim, "move", 0.3, yaw=150, pitch=8, show_body=False,
                       scale=11, center=(0, 1.2), size=(520, 620), hidden=hid),
        preview.render(geo, tex, preview_path("angel_face.png"), anim, "idle", 0, yaw=15, pitch=2, show_body=False,
                       scale=40, center=(0, 1.75), size=(520, 620), hidden=hid),
        preview.render(geo, tex, preview_path("angel_sword.png"), anim, "sword", 0.35, yaw=60, pitch=6,
                       show_body=False, scale=10, center=(0, 1.2), size=(520, 620), hidden=("fx_spears_ring",)),
    ]
    return preview.contact_sheet(shots, preview_path("angel_sheet.png"), cols=4)


if __name__ == "__main__":
    g, t, a = build_entity()
    build_parts()
    print(render_previews(g, t, a))
