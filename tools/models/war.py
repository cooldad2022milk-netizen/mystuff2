"""
Yoru, the War Devil - mob model (entity/devil/war), the player's devil parts (hybrid/war) and the moves' body
animations (PlayerAnimator + GeckoLib).

Reference points:
  * Asa Mitaka's body: black hair to just above the shoulders with bangs; Fourth East High uniform - white shirt,
    dark pinafore dress, tie, dark tights and loafers
  * when Yoru takes over, scars cut across her face and her eyes are ringed like the other Horsemen's
  * anything she thinks of as hers she can turn into a weapon: the school uniform sword, a thrown spear, a barrage
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


def draw_scars(d, n):
    """Yoru's scars: one straight across the bridge of the nose and both cheeks, and one running down each cheek
    from under the eye. (The decal's image is upside down relative to the face: small y = lower on the face.)"""
    col = (150, 66, 66, 255)
    w = max(2, n // 24)
    d.line([(n * 0.08, n * 0.47), (n * 0.35, n * 0.5), (n * 0.65, n * 0.5), (n * 0.92, n * 0.47)], fill=col, width=w)
    for x in (0.27, 0.73):
        d.line([(n * x, n * 0.46), (n * (x + (-0.03 if x < 0.5 else 0.03)), n * 0.2)], fill=col, width=w)


def materials(size=512):
    a = Atlas(size, 64 if size >= 512 else 32)
    a.add("skin", kind="skin", color=(244, 220, 204))
    a.add("hair", kind="fiber", color=(28, 26, 32))
    a.add("hair_dk", kind="fiber", color=(16, 14, 20))
    a.add("shirt", kind="skin", color=(242, 242, 240))
    a.add("shirt_dk", kind="skin", color=(212, 212, 212))
    a.add("dress", kind="skin", color=(36, 40, 62))
    a.add("dress_dk", kind="skin", color=(24, 26, 42))
    a.add("tie", kind="skin", color=(150, 36, 40))
    a.add("tights", kind="skin", color=(30, 30, 36))
    a.add("shoe", kind="gloss", color=(58, 36, 28))
    a.add("eye", kind="ringeye", color=(120, 24, 32), color2=(236, 160, 70), rings=3, sclera=(240, 234, 226))
    a.add("eye_glow", kind="ringeye", color=(170, 30, 36), color2=(255, 190, 90), rings=3, emissive=True)
    a.add("scars", kind="decal", color=(150, 70, 70), draw=draw_scars)
    a.add("brow", kind="skin", color=(40, 34, 36))
    a.add("lip", kind="skin", color=(210, 140, 136))
    a.add("blade", kind="metal", color=(170, 176, 190), scratches=1)
    a.add("cloth_blade", kind="stripes", color=(36, 40, 62), color2=(236, 236, 236))
    a.add("haft", kind="skin", color=(60, 48, 40))
    return a


def hair(look):
    """Black hair: heavy bangs, falling straight to just above the shoulders."""
    cap = shapes.ellipsoid((0, 28.5, 0.3), (4.6, 4.65, 4.65), e_lat=0.38, e_lon=0.42)
    shapes.shell(look, cap, 16, 10, "hair", v0=0.28, thick=0.45,
                 skip=lambda u, v: (u < 0.2 or u > 0.8) and v < 0.62,
                 mat_fn=lambda u, v: "hair_dk" if v < 0.4 else "hair")
    for k in range(10):
        x = -3.6 + k * 0.8
        top = np.array([x * 0.8, 32.6, -3.4])
        tip = np.array([x * 1.04, 28.9 - 0.25 * (k % 2), -4.45])
        shapes.horn(look, top, tip - top, np.linalg.norm(tip - top), 1.0, mat="hair" if k % 2 else "hair_dk",
                    flat=0.35, up=(0, 0, 1), sections=4, around=6, r1=0.15, thick=0.3)
    for k in range(15):
        a = math.radians(-105 + k * 15)
        if math.cos(a) < -0.45:
            continue
        base = np.array([math.sin(a) * 4.25, 29.5, 0.3 + math.cos(a) * 4.25])
        d = norm(np.array([math.sin(a) * 0.12, -1.0, math.cos(a) * 0.1]))
        shapes.horn(look, base, d, 6.3, 1.3, mat="hair" if k % 2 else "hair_dk", flat=0.45,
                    up=(math.sin(a), 0, math.cos(a)), sections=4, around=6, r1=0.5, thick=0.3, power=0.6)


def face(look, eye_mat="eye"):
    dk.face_eyes(look, eye_mat, y=27.6, spacing=1.95, size=(2.0, 1.45), z=-3.97)
    for s in (-1, 1):
        look.obox((s * 1.95, 29.0, -4.02), (s * 1.0, 0.18, 0), (0.28, 1.8, 0.2), "brow", up=(0, 0, -1))
    look.obox((0, 25.7, -4.0), (1, 0, 0), (0.25, 1.1, 0.15), "lip", up=(0, 0, -1))
    look.obox((0, 26.8, -4.02), (0, 1, 0), (0.35, 0.5, 0.15), "skin", up=(0, 0, -1))


def scars(bone, z=-4.14):
    bone.decal((0, 26.9, z), (0, 0, -1), 7.4, 7.4, "scars", up=(0, 1, 0))


def uniform(bones):
    body, waist = bones["body"], bones["waist"]
    # shirt collar and tie
    for s in (-1, 1):
        body.obox((s * 1.25, 23.5, -2.2), (s * 0.8, -1, 0), (1.5, 1.8, 0.25), "shirt_dk", up=(0, 0, -1))
    body.obox((0, 23.1, -2.3), (0, 1, 0), (0.9, 0.9, 0.35), "tie", up=(0, 0, -1))
    tie = shapes.loft(shapes.polyline([(0, 22.7, -2.3), (0, 19.8, -2.55)]), shapes.profile((0, 0.42), (1, 0.55)), 0.12,
                      up=(0, 0, -1))
    shapes.shell(body, tie, 4, 4, "tie", thick=0.2)
    # the pinafore dress: a bodice over the shirt with wide straps over the shoulders
    bod = shapes.loft(shapes.polyline([(0, 12.2, 0), (0, 16.5, 0), (0, 20.2, 0)]),
                      shapes.profile((0, 3.95), (0.5, 3.75), (1, 4.05)), shapes.profile((0, 2.25), (0.5, 2.2), (1, 2.4)),
                      up=(0, 0, -1))
    shapes.shell(body, bod, 14, 6, "dress", thick=0.35)
    for s in (-1, 1):
        for z in (-1, 1):
            body.obox((s * 2.3, 21.9, z * 2.3), (0, 1, 0), (1.5, 3.8, 0.3), "dress", up=(0, 0, z * 1.0))
        body.obox((s * 2.3, 23.9, 0), (0, 0, 1), (1.5, 4.8, 0.3), "dress", up=(0, 1, 0))
    # the skirt, pleated, to just above the knee - on the waist so the legs move under it
    sk = shapes.loft(shapes.polyline([(0, 13.2, 0), (0, 9.5, 0), (0, 6.4, 0)]),
                     shapes.profile((0, 4.1), (1, 5.3)), shapes.profile((0, 2.4), (1, 3.4)), up=(0, 0, -1))
    shapes.shell(waist, sk, 20, 5, "dress", thick=0.35, mat_fn=lambda u, v: "dress_dk" if int(u * 20) % 2 else "dress")


def uniform_sword(bone, grip):
    """The School Uniform Sword: a blade woven of her uniform - navy with white stripes, a steel edge."""
    grip = np.asarray(grip, dtype=float)
    d = norm(np.array([0, 0.3, -1.0]))
    bone.cylinder(tuple(grip), tuple(d), 0.45, 2.6, "haft", segments=6)
    bone.obox(grip + d * 1.5, (1, 0, 0), (0.5, 3.2, 0.7), "blade", up=d)
    blade = shapes.loft(shapes.polyline([grip + d * 1.7, grip + d * 13.0, grip + d * 17.0]),
                        shapes.profile((0, 1.0), (0.8, 0.9), (1, 0.05)), 0.2, up=(1, 0, 0))
    shapes.shell(bone, blade, 4, 10, "cloth_blade", thick=0.2, mat_fn=lambda u, v: "blade" if abs(u - 0.25) < 0.08 or
                 abs(u - 0.75) < 0.08 else "cloth_blade")


def spear(bone, grip):
    """A spear held overhand, point forward."""
    grip = np.asarray(grip, dtype=float)
    d = norm(np.array([0, 0.1, -1.0]))
    bone.cylinder(tuple(grip + d * 3.0), tuple(d), 0.35, 22.0, "haft", segments=6)
    bone.spike(grip + d * 13.8, d, 4.0, 1.2, 0.4, "blade", steps=4, up=(0, 1, 0))


# ------------------------------------------------------------------------------------------ entity
def build_entity():
    atlas = materials()
    m = Model("csm.war_devil", atlas, density=2.0, seed=291)
    bones = dk.humanoid(m, {"skin": "skin", "shirt": "shirt", "sleeve": "shirt", "cuff": "shirt_dk", "pants": "tights",
                            "shoe": "shoe"}, slim=True)
    uniform(bones)
    face(bones["look"])
    scars(bones["look"])
    hair(bones["look"])
    sw = m.bone("fx_sword_blade", parent="right_arm", pivot=(-5.5, 11.5, -0.4))
    uniform_sword(sw, (-5.5, 11.3, -0.6))
    sp = m.bone("fx_spear_shaft", parent="right_arm", pivot=(-5.5, 11.5, -0.4))
    spear(sp, (-5.5, 11.3, -0.6))
    geo, tex, glow, anim_path = dk.devil_paths("war")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=293)
    anims = entity_animations()
    save_animations(anim_path, anims)
    print("yoru entity: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def build_parts():
    """A player who became the War Devil: Yoru's scars and ringed eyes while she has taken over; her weapons."""
    atlas = materials(256)
    m = Model("csm.war_parts", atlas, density=2.0, seed=297)
    m.bone("head", pivot=(0, 24, 0))
    fe = m.bone("form_face", parent="head", pivot=(0, 27.5, -4))
    for s in (-1, 1):
        fe.decal((s * 2.0, 27.5, -4.1), (0, 0, -1), 2.1, 1.4, "eye_glow")
    fe.decal((0, 26.9, -4.14), (0, 0, -1), 7.6, 7.6, "scars", up=(0, 1, 0))
    m.bone("body", pivot=(0, 24, 0))
    m.bone("right_arm", pivot=(-5, 22, 0))
    sw = m.bone("fx_sword_blade", parent="right_arm", pivot=(-6, 11.5, -0.4))
    uniform_sword(sw, (-6.0, 11.0, -0.6))
    sp = m.bone("fx_spear_shaft", parent="right_arm", pivot=(-6, 11.5, -0.4))
    spear(sp, (-6.0, 11.0, -0.6))
    m.bone("left_arm", pivot=(5, 22, 0))
    geo, tex, glow, anim_path = dk.part_paths("war")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=299)
    A_ = [Anim("idle", 2.0, loop=True)]
    em = Anim("emerge", 0.6)
    em.scale("form_face", 0, 0.2).scale("form_face", 0.3, 1.1, "easeOutBack").scale("form_face", 0.6, 1.0)
    A_.append(em)
    rt = Anim("retract", 0.4, loop="hold_on_last_frame")
    rt.scale("form_face", 0, 1.0).scale("form_face", 0.35, 0.2)
    A_.append(rt)
    un = Anim("unleash", 1.0)
    un.scale("form_face", 0, 0.2).scale("form_face", 0.5, 1.1, "easeOutBack").scale("form_face", 0.7, 1.0)
    A_.append(un)
    for name in ("weaponize", "sword", "spear", "arsenal", "drink"):
        A_.append(Anim(name, 0.5))
    save_animations(anim_path, A_)
    print("yoru parts: %d cubes" % m.cube_count())
    return geo, tex, anim_path


# ------------------------------------------------------------------------------------------ moves (body)
def player_moves():
    anims = {}
    # slot 0: Yoru takes over - the head drops, snaps up, and she grins
    t = A("war_trigger", 20)
    t.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    t.k(6, head=(0.6, 0, 0.1), torso=(0.2, 0, 0), rightArm=(0.1, 0, 0.1), leftArm=(0.1, 0, -0.1))
    t.k(10, "OUTBACK", head=(-0.25, 0.1, -0.1), torso=(-0.1, 0, 0), rightArm=(-0.3, 0.2, 0.35),
        leftArm=(-0.3, -0.2, -0.35))
    t.k(20, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    t.save()
    anims["unleash"] = t
    r = A("war_revert", 12)
    r.k(0, head=Z3).k(5, head=(0.4, 0, 0)).k(12, head=Z3)
    r.save()

    # Weaponize: she grabs, and squeezes
    w = A("war_weaponize", 24)
    w.k(0, rightArm=NEUTRAL_R, head=Z3, torso=Z3)
    w.k(6, "OUTQUAD", rightArm=(-1.5, 0.05, 0.0), torso=(0.15, 0, 0), head=(0.05, 0, 0))
    w.k(10, rightArm=(-1.45, 0.05, 0.0))
    w.k(14, "OUTBACK", rightArm=(-1.1, -0.2, 0.0), torso=(0.05, 0.15, 0), head=(-0.1, 0, 0))
    w.k(24, rightArm=NEUTRAL_R, head=Z3, torso=Z3)
    w.save()
    anims["weaponize"] = w

    # Uniform sword: a two-step - wind up high, a heavy downward cut
    s = A("war_sword", 18)
    s.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    s.k(5, "OUTQUAD", rightArm=(-2.8, 0.3, -0.2), leftArm=(-0.4, 0, -0.2), torso=(-0.1, 0.25, 0))
    s.k(8, "INQUAD", rightArm=(-0.6, -0.2, 0.1), torso=(0.25, -0.2, 0), head=(0.1, 0, 0))
    s.k(11, rightArm=(-0.45, -0.25, 0.1), torso=(0.22, -0.18, 0))
    s.k(18, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    s.save()
    anims["sword"] = s

    # Spear: drawn back overhand, the body winds, and it's hurled
    p = A("war_spear", 22)
    p.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    p.k(8, "OUTQUAD", rightArm=(-2.6, -0.1, 0.35), leftArm=(-1.2, 0, -0.4), torso=(-0.12, 0.45, 0))
    p.k(11, "INQUAD", rightArm=(-1.3, 0.2, 0.0), leftArm=(-0.2, 0, -0.3), torso=(0.25, -0.4, 0))
    p.k(15, rightArm=(-0.9, 0.2, 0.0), torso=(0.2, -0.35, 0))
    p.k(22, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    p.save()
    anims["spear"] = p

    # Arsenal: both arms flung wide, then forward - everything falls
    a = A("war_arsenal", 40)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.k(8, "OUTQUAD", rightArm=(-2.2, 0.3, 0.9), leftArm=(-2.2, -0.3, -0.9), head=(-0.3, 0, 0), torso=(-0.12, 0, 0))
    a.k(14, "INQUAD", rightArm=(-1.5, -0.3, 0.1), leftArm=(-1.5, 0.3, -0.1), head=(0.05, 0, 0), torso=(0.12, 0, 0))
    a.k(34, rightArm=(-1.45, -0.3, 0.1), leftArm=(-1.45, 0.3, -0.1))
    a.k(40, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.save()
    anims["arsenal"] = a
    return anims


def entity_animations():
    moves = player_moves()
    out_ = [dk.humanoid_idle(), dk.humanoid_walk(stride=34, arm=28), dk.humanoid_death()]
    for geo_name, a in moves.items():
        g = dk.from_player_anim(a, geo_name)
        if geo_name == "unleash":
            g.name = "manifest"
        out_.append(g)
    out_.append(Anim("retract", 0.3))
    out_.append(Anim("drink", 1.0))
    return out_


def render_previews(geo, tex, anim):
    hid = ("fx_sword_blade", "fx_spear_shaft")
    shots = [
        preview.render(geo, tex, preview_path("war_front.png"), anim, "idle", 0, yaw=20, pitch=4, show_body=False,
                       scale=13, center=(0, 1.0), size=(520, 620), hidden=hid),
        preview.render(geo, tex, preview_path("war_back.png"), anim, "idle", 0, yaw=160, pitch=4, show_body=False,
                       scale=13, center=(0, 1.0), size=(520, 620), hidden=hid),
        preview.render(geo, tex, preview_path("war_face.png"), anim, "idle", 0, yaw=12, pitch=2, show_body=False,
                       scale=40, center=(0, 1.72), size=(520, 620), hidden=hid),
        preview.render(geo, tex, preview_path("war_sword.png"), anim, "sword", 0.3, yaw=60, pitch=6, show_body=False,
                       scale=11, center=(0, 1.1), size=(520, 620), hidden=("fx_spear_shaft",)),
    ]
    return preview.contact_sheet(shots, preview_path("war_sheet.png"), cols=4)


if __name__ == "__main__":
    g, t, a = build_entity()
    build_parts()
    print(render_previews(g, t, a))
