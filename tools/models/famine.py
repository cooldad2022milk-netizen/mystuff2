"""
Fami, the Famine Devil - mob model (entity/devil/famine), the player's devil parts (hybrid/famine) and the moves'
body animations (PlayerAnimator + GeckoLib).

Reference points (Chainsaw Man part 2):
  * a young woman with LONG, UNKEMPT BLONDE hair falling in uneven layers, bangs across the forehead and longer
    strands to the collarbones; a black cap
  * multiple-ringed eyes like the other Horsemen's (pink on the coloured covers); usually nervous, often crying
  * FOUR GREEN EARRINGS: two beads in her right ear, two long ones tapering to triangular tips in her left
  * the Fourth East High School uniform she wears to infiltrate the school (white shirt, dark pinafore, red tie)
  * she controls the starving: whatever is hungry enough does as she says; she is suddenly somewhere else; she eats
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


def materials(size=512):
    a = Atlas(size, 64 if size >= 512 else 32)
    a.add("skin", kind="skin", color=(246, 224, 212))
    a.add("hair", kind="fiber", color=(238, 216, 150))
    a.add("hair_dk", kind="fiber", color=(206, 180, 112))
    a.add("shirt", kind="skin", color=(242, 242, 240))
    a.add("shirt_dk", kind="skin", color=(212, 212, 212))
    a.add("dress", kind="skin", color=(36, 40, 62))
    a.add("dress_dk", kind="skin", color=(24, 26, 42))
    a.add("tie", kind="skin", color=(150, 36, 40))
    a.add("tights", kind="skin", color=(30, 30, 36))
    a.add("shoe", kind="gloss", color=(58, 36, 28))
    a.add("cap", kind="skin", color=(26, 26, 30))
    a.add("green", kind="gloss", color=(60, 170, 90))
    a.add("eye", kind="ringeye", color=(236, 150, 180), color2=(130, 30, 70), rings=3, sclera=(246, 240, 236))
    a.add("eye_glow", kind="ringeye", color=(255, 170, 200), color2=(200, 40, 100), rings=3, emissive=True)
    a.add("brow", kind="skin", color=(190, 160, 100))
    a.add("lip", kind="skin", color=(214, 140, 146))
    return a


def hair(look):
    """Long, unkempt blonde hair: uneven bangs and layers, longer strands falling past the collarbones."""
    cap = shapes.ellipsoid((0, 28.5, 0.3), (4.6, 4.65, 4.65), e_lat=0.38, e_lon=0.42)
    shapes.shell(look, cap, 16, 10, "hair", v0=0.28, thick=0.45,
                 skip=lambda u, v: (u < 0.2 or u > 0.8) and v < 0.62,
                 mat_fn=lambda u, v: "hair_dk" if v < 0.4 else "hair")
    for k in range(10):
        x = -3.6 + k * 0.8
        top = np.array([x * 0.8, 32.6, -3.4])
        tip = np.array([x * 1.04, 28.6 - 0.9 * ((k * 7) % 3) / 2, -4.45])  # ragged, uneven bangs
        shapes.horn(look, top, tip - top, np.linalg.norm(tip - top), 1.0, mat="hair" if k % 2 else "hair_dk",
                    flat=0.35, up=(0, 0, 1), sections=4, around=6, r1=0.15, thick=0.3)
    for k in range(17):
        a = math.radians(-120 + k * 15)
        if math.cos(a) < -0.5:
            continue
        base = np.array([math.sin(a) * 4.3, 29.5, 0.3 + math.cos(a) * 4.3])
        front = math.cos(a) < 0.2
        length = (9.0 if front else 16.0) + ((k * 5) % 4) * 1.3 - 2.0   # uneven layers
        d = norm(np.array([math.sin(a) * (0.08 + 0.1 * ((k * 3) % 2)), -1.0,
                           math.cos(a) * 0.1 + (0.1 if not front else 0)]))
        shapes.horn(look, base, d, length, 1.4, mat="hair" if k % 2 else "hair_dk", flat=0.45,
                    up=(math.sin(a), 0, math.cos(a)), sections=6, around=6, r1=0.35, thick=0.3, power=0.5)


def cap_and_earrings(look):
    # a cap: crown over the hair, brim forward
    crown = shapes.ellipsoid((0, 31.2, 0.2), (4.9, 3.0, 4.9), e_lat=0.6, e_lon=0.6)
    shapes.shell(look, crown, 16, 6, "cap", v0=0.5, thick=0.4)
    look.cbox((0, 33.3, 0.2), (0.8, 0.5, 0.8), "cap")
    brim = shapes.ellipsoid((0, 31.3, -5.2), (4.2, 0.35, 2.8), e_lat=0.8, e_lon=0.7)
    shapes.shell(look, brim, 12, 4, "cap", thick=0.3)
    # four green earrings: two beads in her right ear, two long drops tapering to triangular points in her left
    for k in range(2):
        look.cbox((-4.35, 26.3 - k * 1.1, -0.2 + k * 0.5), (0.55, 0.55, 0.55), "green")
    for k in range(2):
        top = np.array([4.35, 26.2, -0.4 + k * 0.9])
        look.cbox(tuple(top), (0.3, 0.5, 0.3), "green")
        look.spike(top - np.array([0, 0.3, 0]), (0, -1, 0), 2.6 - k * 0.5, 0.7, 0.3, "green", steps=3, up=(1, 0, 0))


def face(look, eye_mat="eye"):
    dk.face_eyes(look, eye_mat, y=27.6, spacing=1.95, size=(2.0, 1.45), z=-3.97)
    for s in (-1, 1):
        look.obox((s * 1.95, 29.0, -4.02), (s * 1.0, -0.1, 0), (0.25, 1.8, 0.2), "brow", up=(0, 0, -1))
    look.obox((0, 25.7, -4.0), (1, 0, 0), (0.28, 1.3, 0.15), "lip", up=(0, 0, -1))
    look.obox((0, 26.8, -4.02), (0, 1, 0), (0.35, 0.5, 0.15), "skin", up=(0, 0, -1))


def outfit(bones):
    """The Fourth East High School uniform - the same one Asa (and Yoru) wear."""
    import war
    war.uniform(bones)


# ------------------------------------------------------------------------------------------ entity
def build_entity():
    atlas = materials()
    m = Model("csm.famine_devil", atlas, density=2.0, seed=301)
    bones = dk.humanoid(m, {"skin": "skin", "shirt": "shirt", "sleeve": "shirt", "cuff": "shirt_dk",
                            "pants": "tights", "shoe": "shoe"}, slim=True)
    outfit(bones)
    face(bones["look"])
    hair(bones["look"])
    cap_and_earrings(bones["look"])
    geo, tex, glow, anim_path = dk.devil_paths("famine")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=303)
    anims = entity_animations()
    save_animations(anim_path, anims)
    print("fami entity: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def build_parts():
    """A player who became the Famine Devil: her ringed eyes, lit while the devil is out."""
    atlas = materials(256)
    m = Model("csm.famine_parts", atlas, density=2.0, seed=307)
    m.bone("head", pivot=(0, 24, 0))
    fe = m.bone("form_eyes", parent="head", pivot=(0, 27.5, -4))
    for s in (-1, 1):
        fe.decal((s * 2.0, 27.5, -4.1), (0, 0, -1), 2.1, 1.4, "eye_glow")
    m.bone("body", pivot=(0, 24, 0))
    m.bone("right_arm", pivot=(-5, 22, 0))
    m.bone("left_arm", pivot=(5, 22, 0))
    geo, tex, glow, anim_path = dk.part_paths("famine")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=309)
    A_ = [Anim("idle", 2.0, loop=True)]
    em = Anim("emerge", 0.6)
    em.scale("form_eyes", 0, 0.2).scale("form_eyes", 0.3, 1.3, "easeOutBack").scale("form_eyes", 0.6, 1.0)
    A_.append(em)
    rt = Anim("retract", 0.4, loop="hold_on_last_frame")
    rt.scale("form_eyes", 0, 1.0).scale("form_eyes", 0.35, 0.2)
    A_.append(rt)
    un = Anim("unleash", 1.0)
    un.scale("form_eyes", 0, 0.2).scale("form_eyes", 0.5, 1.3, "easeOutBack").scale("form_eyes", 0.7, 1.0)
    A_.append(un)
    for name in ("starve", "enthrall", "vanish", "bite", "drink"):
        A_.append(Anim(name, 0.5))
    save_animations(anim_path, A_)
    print("fami parts: %d cubes" % m.cube_count())
    return geo, tex, anim_path


# ------------------------------------------------------------------------------------------ moves (body)
def player_moves():
    anims = {}
    # slot 0: she tilts her head and smiles - the hunger wakes
    t = A("famine_trigger", 20)
    t.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    t.k(8, "OUTQUAD", head=(0.1, 0.15, 0.35), rightArm=(-0.3, 0, 0.15))
    t.k(14, head=(0.05, 0.1, 0.3), rightArm=(-0.35, 0, 0.15))
    t.k(20, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    t.save()
    anims["unleash"] = t
    r = A("famine_revert", 12)
    r.k(0, head=Z3).k(5, head=(0.15, 0, -0.2)).k(12, head=Z3)
    r.save()

    # Starve: an open hand held out at the target
    s = A("famine_starve", 20)
    s.k(0, rightArm=NEUTRAL_R, head=Z3)
    s.k(6, "OUTQUAD", rightArm=(-1.5, 0.05, 0.0), head=(0.05, -0.05, 0.2))
    s.k(12, rightArm=(-1.45, 0.05, 0.0))
    s.k(20, rightArm=NEUTRAL_R, head=Z3)
    s.save()
    anims["starve"] = s

    # Enthrall: arms open wide, palms up - come, eat
    e = A("famine_enthrall", 30)
    e.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    e.k(10, "OUTQUAD", rightArm=(-0.9, 0.2, 0.9), leftArm=(-0.9, -0.2, -0.9), head=(-0.2, 0, 0.15),
        torso=(-0.08, 0, 0))
    e.k(22, rightArm=(-0.95, 0.2, 1.0), leftArm=(-0.95, -0.2, -1.0), head=(-0.2, 0, -0.1))
    e.k(30, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    e.save()
    anims["enthrall"] = e

    # Vanish: a small step and she's gone
    v = A("famine_vanish", 10)
    v.k(0, rightLeg=Z3, leftLeg=Z3, torso=Z3)
    v.k(3, "OUTQUAD", rightLeg=(-0.4, 0, 0), leftLeg=(0.3, 0, 0), torso=(0.2, 0, 0))
    v.k(10, rightLeg=Z3, leftLeg=Z3, torso=Z3)
    v.save()
    anims["vanish"] = v

    # Bite: she leans in and eats
    b = A("famine_bite", 18)
    b.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    b.k(6, "OUTQUAD", rightArm=(-1.2, 0.3, 0.0), leftArm=(-1.2, -0.3, 0.0), torso=(0.35, 0, 0), head=(-0.2, 0, 0))
    b.k(9, "OUTBACK", torso=(0.45, 0, 0), head=(0.15, 0, 0))
    b.k(18, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    b.save()
    anims["bite"] = b
    return anims


def entity_animations():
    moves = player_moves()
    out_ = [dk.humanoid_idle(), dk.humanoid_walk(stride=26, arm=16), dk.humanoid_death()]
    for geo_name, a in moves.items():
        g = dk.from_player_anim(a, geo_name)
        if geo_name == "unleash":
            g.name = "manifest"
        if geo_name == "vanish":
            g.scale("root", 0, 1.0).scale("root", 0.15, (0.2, 1.3, 0.2)).scale("root", 0.3, 1.0)
        out_.append(g)
    out_.append(Anim("retract", 0.3))
    out_.append(Anim("drink", 1.0))
    return out_


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("famine_front.png"), anim, "idle", 0, yaw=20, pitch=4, show_body=False,
                       scale=13, center=(0, 1.0), size=(520, 620)),
        preview.render(geo, tex, preview_path("famine_back.png"), anim, "idle", 0, yaw=160, pitch=4,
                       show_body=False, scale=13, center=(0, 1.0), size=(520, 620)),
        preview.render(geo, tex, preview_path("famine_face.png"), anim, "idle", 0, yaw=12, pitch=2,
                       show_body=False, scale=40, center=(0, 1.75), size=(520, 620)),
        preview.render(geo, tex, preview_path("famine_enthrall.png"), anim, "enthrall", 0.8, yaw=35, pitch=6,
                       show_body=False, scale=11, center=(0, 1.1), size=(520, 620)),
    ]
    return preview.contact_sheet(shots, preview_path("famine_sheet.png"), cols=4)


if __name__ == "__main__":
    g, t, a = build_entity()
    build_parts()
    print(render_previews(g, t, a))
