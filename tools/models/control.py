"""
Makima - the Control Devil. Mob model (entity/devil/control), the player's devil parts (hybrid/control) and the moves'
body animations, authored once and used by both the player (PlayerAnimator) and the mob (GeckoLib).

Reference points:
  * auburn hair with bangs, a long braid down her back; yellow eyes ringed with concentric red circles
  * white shirt, black tie, dark trousers and shoes (Public Safety)
  * dominates anyone she considers beneath her; an unseen crushing force obliterates the targets she names from afar,
    a finger-gun "Bang"; chains that draw on the power of those she controls; the Prime Minister's contract
    redirects fatal damage onto random citizens
"""
import math
import os
import sys

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from player_anims import A, NEUTRAL_R, NEUTRAL_L, Z3  # noqa: E402

HAIR = (176, 74, 52)
HAIR_DK = (132, 48, 36)


def materials(size=512):
    a = Atlas(size, 64)
    a.add("skin", kind="skin", color=(244, 214, 196))
    a.add("hair", kind="fiber", color=HAIR)
    a.add("hair_dk", kind="fiber", color=HAIR_DK)
    a.add("shirt", kind="skin", color=(240, 238, 234))
    a.add("shirt_dk", kind="skin", color=(214, 212, 210))
    a.add("tie", kind="skin", color=(26, 26, 30))
    a.add("pants", kind="skin", color=(38, 38, 48))
    a.add("shoe", kind="gloss", color=(22, 22, 24))
    a.add("belt", kind="gloss", color=(30, 26, 24))
    a.add("buckle", kind="metal", color=(190, 186, 170), scratches=1)
    a.add("eye", kind="ringeye", color=(236, 196, 60), color2=(196, 42, 34), rings=3)
    a.add("eye_glow", kind="ringeye", color=(255, 220, 90), color2=(255, 70, 50), rings=3, emissive=True)
    a.add("brow", kind="skin", color=(150, 62, 44))
    a.add("lip", kind="skin", color=(214, 150, 140))
    a.add("chain", kind="chain", color=(150, 150, 158))
    a.add("glint", kind="glow", color=(255, 60, 60), color2=(255, 210, 200), emissive=True)
    return a


# ------------------------------------------------------------------------------------------ hair
def hair(m, look, rng):
    """Auburn hair: a cap over the skull, bangs across the forehead, side locks framing the face, and the braid."""
    cap = shapes.ellipsoid((0, 28.4, 0.35), (4.45, 4.45, 4.5), e_lat=0.45, e_lon=0.5)
    # everything but the face (front, below the hairline)
    shapes.shell(look, cap, 16, 10, "hair", v0=0.28, thick=0.45,
                 skip=lambda u, v: (u < 0.2 or u > 0.8) and v < 0.62,
                 mat_fn=lambda u, v: "hair_dk" if v < 0.4 else "hair")
    # bangs: flat locks falling over the forehead, parted slightly off-centre
    for k in range(9):
        x = -3.4 + k * 0.85
        top = np.array([x * 0.8, 32.3, -3.0])
        tip = np.array([x * 1.02 + 0.25 * math.sin(k * 1.7), 28.9 - 0.35 * (k % 3), -4.4])
        shapes.horn(look, top, tip - top, np.linalg.norm(tip - top), 1.0, mat="hair" if k % 2 else "hair_dk",
                    flat=0.35, up=(0, 0, 1), sections=4, around=6, r1=0.1, thick=0.3)
    # side locks down to the jaw
    for s in (-1, 1):
        for j in range(2):
            top = np.array([s * (3.9 + 0.2 * j), 30.5, -2.4 + 1.3 * j])
            shapes.horn(look, top, (s * 0.12, -1, -0.1), 6.0 - j * 1.2, 0.9, mat="hair", flat=0.4, up=(s * 1, 0, 0),
                        sections=5, around=6, r1=0.15, thick=0.3)
    # the braid: from the nape down past the shoulder blades
    look.cylinder((0, 26.6, 4.3), (0, 0.6, 1), 1.0, 1.2, "hair_dk", segments=8)
    return dk.braid(m, "look", (0, 26.4, 4.55), 13.0, 4, "hair", "tie", radius=1.05)


def face(look):
    dk.face_eyes(look, "eye", y=27.7, spacing=1.95, size=(1.9, 1.3), z=-3.97)
    for s in (-1, 1):
        look.obox((s * 1.95, 29.05, -4.02), (s * 1.0, 0.12, 0), (0.3, 1.9, 0.2), "brow", up=(0, 0, -1))
    look.obox((0, 25.7, -4.0), (1, 0, 0), (0.28, 1.4, 0.15), "lip", up=(0, 0, -1))   # a faint, calm smile
    look.obox((0, 26.8, -4.02), (0, 1, 0), (0.35, 0.55, 0.15), "skin", up=(0, 0, -1))  # nose


def clothes(bones):
    body = bones["body"]
    # collar points and tie
    for s in (-1, 1):
        body.obox((s * 1.2, 23.4, -2.2), (s * 0.7, -1, 0), (1.6, 1.9, 0.25), "shirt_dk", up=(0, 0, -1))
    body.obox((0, 23.2, -2.25), (0, 1, 0), (0.95, 0.9, 0.35), "tie", up=(0, 0, -1))
    tie = shapes.loft(shapes.polyline([(0, 22.8, -2.25), (0, 18.0, -2.15), (0, 16.4, -2.2)]),
                      shapes.profile((0, 0.4), (0.8, 0.62), (1, 0.1)), 0.12, up=(0, 0, -1))
    shapes.shell(body, tie, 4, 6, "tie", thick=0.2)
    # buttons down the shirt placket
    for y in (21.0, 19.3, 17.6):
        body.cbox((0.9, y, -2.18), (0.25, 0.25, 0.1), "shirt_dk")
    # belt at the waist of the trousers
    body.ring((0, 12.6, 0), (0, 1, 0), 3.8, 0.35, 0.8, "belt", count=16)
    body.cbox((0, 12.6, -2.2), (1.0, 0.8, 0.2), "buckle")
    # trousers rise above the leg joint
    dk.rbox(body, (0, 12.4, 0), (3.75, 0.9, 2.0), "pants", e=0.45, nu=12, nv=4)


def build_entity():
    atlas = materials()
    m = Model("csm.control_devil", atlas, density=2.0, seed=131)
    rng = np.random.default_rng(2)
    bones = dk.humanoid(m, {"skin": "skin", "shirt": "shirt", "sleeve": "shirt", "cuff": "shirt_dk", "pants": "pants",
                            "shoe": "shoe"}, slim=True)
    clothes(bones)
    face(bones["look"])
    braid_bones = hair(m, bones["look"], rng)
    # the chains she lashes out with (while the chains move plays)
    ch = m.bone("fx_chains_arm", parent="left_arm", pivot=(5.5, 12, 0))
    for k in range(10):
        p = np.array([5.5, 11.0 - k * 1.05, -0.3 * k])
        ch.obox(p, (0, -1, -0.3), (0.35 if k % 2 else 0.8, 1.2, 0.8 if k % 2 else 0.35), "chain", up=(0, 0, -1))
    # the finger gun's glint
    g = m.bone("fx_bang_hand", parent="right_arm", pivot=(-5.5, 10.5, 0))
    g.cbox((-5.5, 9.8, -0.6), (0.6, 0.6, 0.6), "glint")
    geo, tex, glow, anim_path = dk.devil_paths("control")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=137)
    anims = entity_animations(braid_bones)
    save_animations(anim_path, anims)
    print("makima entity: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


# ------------------------------------------------------------------------------------------ the player's features
def build_parts():
    """A player who became the Control Devil keeps their body; her ringed eyes (lit up while the devil is out) and her
    braid mark them."""
    atlas = materials(256)
    m = Model("csm.control_parts", atlas, density=2.0, seed=139)
    m.bone("head", pivot=(0, 24, 0))
    e = m.bone("base_eyes", parent="head", pivot=(0, 27.5, -4))
    for s in (-1, 1):
        e.decal((s * 2.0, 27.5, -4.06), (0, 0, -1), 2.0, 1.25, "eye")
    fe = m.bone("form_eyes", parent="head", pivot=(0, 27.5, -4))
    for s in (-1, 1):
        fe.decal((s * 2.0, 27.5, -4.12), (0, 0, -1), 2.1, 1.35, "eye_glow")
    m.bone("body", pivot=(0, 24, 0))
    m.bone("right_arm", pivot=(-5, 22, 0))
    g = m.bone("fx_bang_hand", parent="right_arm", pivot=(-6, 10.5, 0))
    g.cbox((-6, 9.6, -0.6), (0.7, 0.7, 0.7), "glint")
    m.bone("left_arm", pivot=(5, 22, 0))
    ch = m.bone("fx_chains_arm", parent="left_arm", pivot=(6, 12, 0))
    for k in range(10):
        p = np.array([6.0, 11.0 - k * 1.05, -0.3 * k])
        ch.obox(p, (0, -1, -0.3), (0.35 if k % 2 else 0.8, 1.2, 0.8 if k % 2 else 0.35), "chain", up=(0, 0, -1))
    geo, tex, glow, anim_path = dk.part_paths("control")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=141)
    A_ = []
    idle = Anim("idle", 2.0, loop=True)
    A_.append(idle)
    em = Anim("emerge", 0.6)
    em.scale("form_eyes", 0, 0.2).scale("form_eyes", 0.3, 1.3, "easeOutBack").scale("form_eyes", 0.6, 1.0)
    A_.append(em)
    rt = Anim("retract", 0.4, loop="hold_on_last_frame")
    rt.scale("form_eyes", 0, 1.0).scale("form_eyes", 0.35, 0.2)
    A_.append(rt)
    un = Anim("unleash", 1.0)
    un.scale("base_eyes", 0, 1.0).scale("base_eyes", 0.3, (1, 0.1, 1)).scale("base_eyes", 0.5, (1, 0.1, 1))
    un.scale("base_eyes", 0.6, 1.0)
    A_.append(un)
    for name in ("bang", "chains", "domination", "kneel", "contract", "drink"):
        A_.append(Anim(name, 0.5))
    save_animations(anim_path, A_)
    print("makima parts: %d cubes" % m.cube_count())
    return geo, tex, anim_path


# ------------------------------------------------------------------------------------------ moves (body)
POINT_R = (-1.55, 0.05, 0.02)       # right arm straight out at the target
TRIG = (-1.62, 0.0, 0.0)


def player_moves():
    """Her moves as PlayerAnimator animations (also converted for the mob). Returns {geoAnim: A}."""
    anims = {}
    # slot 0: the Control Devil wakes behind her eyes - she lowers her head, then looks up
    t = A("control_trigger", 20)
    t.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    t.k(6, head=(0.45, 0, 0), rightArm=(0.05, 0, 0.05), leftArm=(0.05, 0, -0.05))
    t.k(10, "OUTBACK", head=(-0.2, 0, 0), rightArm=(-0.25, 0.2, 0.25), leftArm=(-0.25, -0.2, -0.25))
    t.k(20, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    t.save()
    anims["unleash"] = t
    r = A("control_revert", 12)
    r.k(0, head=Z3).k(5, head=(0.3, 0, 0)).k(12, head=Z3)
    r.save()

    # Bang: a finger gun, raised at the target; the wrist flicks up on "bang"
    b = A("control_bang", 24)
    b.k(0, rightArm=NEUTRAL_R, head=Z3, torso=Z3)
    b.k(6, "OUTQUAD", rightArm=POINT_R, head=(0.02, -0.08, 0), torso=(0, -0.12, 0))
    b.k(9, rightArm=(POINT_R[0] - 0.02, POINT_R[1], POINT_R[2]), head=(0.02, -0.08, 0))
    b.k(10, "OUTQUAD", rightArm=(-1.95, 0.05, 0.02), head=(0, -0.08, 0))       # bang
    b.k(14, rightArm=(-1.75, 0.05, 0.02))
    b.k(24, rightArm=NEUTRAL_R, head=Z3, torso=Z3)
    b.save()
    anims["bang"] = b

    # Chains: the left hand sweeps low and out; chains burst out of the ground where it points
    c = A("control_chains", 20)
    c.k(0, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    c.k(5, "INQUAD", leftArm=(-0.5, 0.6, -0.9), torso=(0, 0.25, 0))
    c.k(9, "OUTBACK", leftArm=(-1.2, -0.7, -0.5), torso=(0.1, -0.25, 0), head=(0.1, -0.2, 0))
    c.k(15, leftArm=(-1.1, -0.6, -0.4), torso=(0.05, -0.2, 0))
    c.k(20, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    c.save()
    anims["chains"] = c

    # Domination: she lifts a hand, palm down, as if holding everything around her on a leash
    d = A("control_domination", 30)
    d.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    d.k(8, "OUTQUAD", rightArm=(-1.2, -0.35, 0.35), head=(-0.12, 0, 0))
    d.k(14, rightArm=(-1.25, -0.2, 0.9), head=(-0.15, 0.1, 0))
    d.k(22, rightArm=(-1.2, -0.4, 0.2), head=(-0.12, -0.1, 0))
    d.k(30, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    d.save()
    anims["domination"] = d

    # Kneel: she points down at the floor in front of her
    k = A("control_kneel", 16)
    k.k(0, rightArm=NEUTRAL_R, head=Z3)
    k.k(5, "OUTQUAD", rightArm=(-0.75, 0.1, 0.1), head=(0.35, 0, 0))
    k.k(7, "OUTBACK", rightArm=(-0.55, 0.1, 0.1), head=(0.45, 0, 0))
    k.k(16, rightArm=NEUTRAL_R, head=Z3)
    k.save()
    anims["kneel"] = k

    # The Prime Minister's contract: hands pressed together
    p = A("control_contract", 14)
    CR, CL = (-1.05, 0.55, 0.0), (-1.05, -0.55, 0.0)
    p.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    p.k(5, "OUTQUAD", rightArm=CR, leftArm=CL, head=(0.2, 0, 0))
    p.k(10, rightArm=CR, leftArm=CL, head=(0.25, 0, 0))
    p.k(14, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    p.save()
    anims["contract"] = p
    return anims


def entity_animations(braid_bones):
    moves = player_moves()
    out_ = [dk.humanoid_idle(braid_bones=braid_bones), dk.humanoid_walk(braid_bones=braid_bones, stride=28, arm=18),
            dk.humanoid_death()]
    for geo_name, a in moves.items():
        g = dk.from_player_anim(a, geo_name)
        if geo_name == "unleash":
            g.name = "manifest"
        out_.append(g)
    out_.append(Anim("retract", 0.3))
    out_.append(Anim("drink", 1.0))
    return out_


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("control_front.png"), anim, "idle", 0, yaw=10, pitch=4, show_body=False,
                       scale=14, center=(0, 1.0), size=(520, 620)),
        preview.render(geo, tex, preview_path("control_back.png"), anim, "idle", 0, yaw=160, pitch=4, show_body=False,
                       scale=14, center=(0, 1.0), size=(520, 620)),
        preview.render(geo, tex, preview_path("control_face.png"), anim, "idle", 0, yaw=20, pitch=2, show_body=False,
                       scale=40, center=(0, 1.72), size=(520, 620)),
        preview.render(geo, tex, preview_path("control_bang.png"), anim, "bang", 0.5, yaw=60, pitch=6, show_body=False,
                       scale=12, center=(0, 1.0), size=(520, 620)),
    ]
    return preview.contact_sheet(shots, preview_path("control_sheet.png"), cols=4)


if __name__ == "__main__":
    g, t, a = build_entity()
    build_parts()
    print(render_previews(g, t, a))

