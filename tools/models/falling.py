"""
The Falling Devil - entity model (entity/devil/falling) and animations.

Reference points (Chainsaw Man part 2):
  * a tall, feminine figure assembled out of MANGLED HUMAN CORPSES, with HANDS WHERE ITS FEET SHOULD BE
  * in its "chef" form it has given itself a head: long straight hair tied back in a ponytail under a tall CHEF'S HAT,
    a white chef's dress - and BLOOD RUNNING from its eyes, nose and mouth
  * the fear of falling: it makes people fall UP into the sky, and serves its victims their own trauma as a course
"""
import math

import numpy as np

from common import preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk

SCALE = 2.5  # built at a person's size, then stood up about five blocks tall


def draw_bleeding_face(d, n):
    """Streams of blood from the eyes, the nose and the mouth (decal image: small y = lower on the face)."""
    red = (150, 12, 18, 255)
    w = max(2, n // 18)
    for x in (0.28, 0.72):                                   # from the eyes, down the cheeks
        d.line([(n * x, n * 0.62), (n * (x + 0.01), n * 0.4), (n * (x - 0.01), n * 0.12)], fill=red, width=w)
    d.line([(n * 0.5, n * 0.46), (n * 0.49, n * 0.34)], fill=red, width=w)          # from the nose
    for x in (0.42, 0.58):                                   # from the corners of the mouth, off the chin
        d.line([(n * x, n * 0.26), (n * x, n * 0.02)], fill=red, width=w)


def materials():
    a = Atlas(512, 64)
    a.add("skin", kind="skin", color=(236, 222, 214))
    a.add("corpse", kind="skin", color=(196, 170, 160))
    a.add("corpse_dk", kind="skin", color=(150, 120, 116))
    a.add("hair", kind="fiber", color=(30, 26, 30))
    a.add("chef", kind="skin", color=(246, 246, 244))
    a.add("chef_dk", kind="skin", color=(214, 214, 216))
    a.add("button", kind="gloss", color=(40, 40, 44))
    a.add("eye", kind="gloss", color=(20, 16, 18))
    a.add("mouth", kind="void", color=(60, 10, 16))
    a.add("blood", kind="decal", color=(0, 0, 0), draw=draw_bleeding_face)
    a.add("gore", kind="blood", color=(126, 8, 12))
    a.add("nail", kind="bone", color=(214, 200, 196))
    return a


def hand(bone, wrist, forward, down, size=1.0):
    """A human hand, palm down, fingers spread (it walks on these)."""
    wrist = np.asarray(wrist, dtype=float)
    fw = norm(forward)
    dn = norm(down)
    sd = norm(np.cross(fw, dn))
    palm = wrist + fw * 1.3 * size
    shapes.shell(bone, shapes.ellipsoid(palm, (1.5 * size, 0.6 * size, 1.5 * size),
                                        frame=np.column_stack([sd, -dn, fw])), 8, 4, "corpse", thick=0.25)
    for k in range(5):
        thumb = k == 0
        base = palm + sd * (-1.2 + k * 0.6) * size + fw * (1.0 if not thumb else -0.4) * size
        d = norm(fw + sd * (0.9 if thumb else 0.15 * (k - 2)))
        shapes.horn(bone, base, d, (1.8 if thumb else 2.6 - abs(k - 2.5) * 0.2) * size, 0.3 * size, mat="corpse",
                    tip_mat="nail", tip_from=0.85, sections=3, around=4, r1=0.12, bend_axis=norm(np.cross(d, dn)),
                    bend=-25)


def corpse_bits(bone, rng, center, spread, count):
    """Mangled bodies packed together: heads, arms, a torso or two, blood."""
    c = np.asarray(center, dtype=float)
    for k in range(count):
        p = c + np.array([rng.uniform(-1, 1) * spread[0], rng.uniform(-1, 1) * spread[1], rng.uniform(-1, 1) * spread[2]])
        kind = k % 3
        if kind == 0:  # a head
            shapes.shell(bone, shapes.ellipsoid(p, (1.3, 1.5, 1.3)), 6, 4, "corpse", thick=0.25)
            bone.cbox(p + np.array([0.4, 0.2, -1.2]), (0.3, 0.3, 0.2), "eye")
            bone.cbox(p + np.array([-0.4, 0.2, -1.2]), (0.3, 0.3, 0.2), "eye")
        elif kind == 1:  # an arm
            d = norm(np.array([rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 0.2)]))
            shapes.horn(bone, p, d, rng.uniform(3.0, 4.5), 0.6, mat="corpse_dk", sections=3, around=4, r1=0.35)
        else:  # a twisted torso
            shapes.shell(bone, shapes.ellipsoid(p, (1.8, 1.2, 1.1)), 6, 4, "corpse_dk", thick=0.25)
        if k % 4 == 0:
            bone.cbox(p + np.array([0, -0.8, -0.8]), (0.9, 0.4, 0.3), "gore")


def build():
    atlas = materials()
    m = Model("csm.falling_devil", atlas, density=2.0, seed=331)
    bones = dk.humanoid(m, {"skin": "skin", "shirt": "chef", "sleeve": "chef", "cuff": "chef_dk", "pants": "corpse",
                            "shoe": "corpse"}, slim=True)
    body, waist, look = bones["body"], bones["waist"], bones["look"]
    rng = np.random.default_rng(337)
    # the chef's dress: a double-breasted white jacket running down into a long skirt to the ankles
    for s in (-1, 1):
        for k in range(4):
            body.cbox((s * 1.3, 22.6 - k * 2.4, -2.35), (0.5, 0.5, 0.3), "button")
    body.obox((0, 23.9, -1.8), (1, 0, 0), (0.6, 7.2, 1.4), "chef_dk", up=(0, 1, 0))   # the stand-up collar
    skirt = shapes.loft(shapes.polyline([(0, 13.4, 0), (0, 7.0, 0), (0, 1.6, 0)]),
                        shapes.profile((0, 4.1), (1, 5.6)), shapes.profile((0, 2.4), (1, 4.0)), up=(0, 0, -1))
    # the front of the skirt hangs open on what it is made of
    shapes.shell(waist, skirt, 18, 7, "chef", thick=0.35, skip=lambda u, v: min(u, 1 - u) < 0.1 and v < 0.75,
                 mat_fn=lambda u, v: "chef_dk" if int(u * 18) % 3 == 0 else "chef")
    corpse_bits(waist, rng, (0, 7.0, -1.2), (2.4, 4.0, 1.0), 10)
    corpse_bits(body, rng, (0, 16.0, -1.6), (2.0, 1.4, 0.6), 4)
    # hands where its feet should be: each leg ends in a human hand, flat on the ground
    for leg, sgn in ((bones["right_leg"], -1), (bones["left_leg"], 1)):
        hand(leg, (sgn * 1.95, 1.2, 0.2), (0, 0, -1), (0, -1, 0), size=1.1)
    # the head it gave itself: pale, bleeding from the eyes, nose and mouth
    dk.face_eyes(look, "eye", y=27.6, spacing=1.9, size=(1.4, 1.0), z=-3.97)
    look.obox((0, 25.7, -4.0), (1, 0, 0), (0.4, 1.6, 0.15), "mouth", up=(0, 0, -1))
    look.decal((0, 26.3, -4.12), (0, 0, -1), 6.6, 6.6, "blood", up=(0, 1, 0))
    # long straight hair tied back in a ponytail
    capf = shapes.ellipsoid((0, 28.4, 0.3), (4.5, 4.55, 4.55), e_lat=0.38, e_lon=0.42)
    shapes.shell(look, capf, 16, 10, "hair", v0=0.35, thick=0.4, skip=lambda u, v: (u < 0.2 or u > 0.8) and v < 0.62)
    tail = [(0, 30.0, 4.4), (0, 28.0, 6.4), (0, 22.0, 7.2), (0, 15.0, 6.6)]
    shapes.shell(look, shapes.loft(shapes.polyline(tail), shapes.profile((0, 1.4), (0.3, 1.8), (1, 0.6)), 1.3,
                                   up=(0, 0, 1)), 6, 10, "hair", thick=0.3)
    look.cylinder((0, 29.6, 4.6), (0, -0.3, 1), 1.2, 0.8, "chef_dk", segments=8)
    # the chef's hat: a tall white toque with a puffed crown
    look.cylinder((0, 33.4, 0.3), (0, 1, 0), 4.4, 1.6, "chef_dk", segments=16)
    shapes.shell(look, shapes.loft(shapes.polyline([(0, 34.0, 0.3), (0, 38.0, 0.3), (0, 42.0, 0.3)]),
                                   shapes.profile((0, 4.2), (0.6, 4.8), (1, 5.4)),
                                   shapes.profile((0, 4.2), (0.6, 4.8), (1, 5.4)), up=(0, 0, -1)), 16, 6, "chef",
                 thick=0.35)
    for k in range(6):
        a = k * 2 * math.pi / 6
        shapes.shell(look, shapes.ellipsoid((math.cos(a) * 3.0, 42.6, 0.3 + math.sin(a) * 3.0), (2.8, 2.2, 2.8)), 8, 5,
                     "chef", thick=0.3)
    # stand it up to its full height
    for b in m.bones:
        b.scale_about((0, 0, 0), SCALE)
    geo, tex, glow, anim_path = dk.devil_paths("falling")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=339)
    anims = animations()
    save_animations(anim_path, anims)
    print("falling devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = [dk.humanoid_idle(length=3.6, breathe=1.6), dk.humanoid_walk(stride=26, arm=12), dk.humanoid_death()]
    # Fall: both arms swept up - everything round it falls into the sky
    f = Anim("fall", 1.6)
    for arm, s in (("right_arm", 1), ("left_arm", -1)):
        f.rot(arm, 0, (0, 0, 0)).rot(arm, 0.4, (-170, 0, s * 20), "easeOutQuad").rot(arm, 1.2, (-175, 0, s * 25))
        f.rot(arm, 1.6, (0, 0, 0))
    f.rot("head", 0.4, (-35, 0, 0)).rot("head", 1.2, (-40, 0, 0)).rot("head", 1.6, (0, 0, 0))
    f.pos("root", 0.4, (0, 4, 0)).pos("root", 1.2, (0, 6, 0)).pos("root", 1.6, (0, 0, 0))
    A.append(f)
    # The First Course: it serves the dish with both hands and bows its head
    c = Anim("course", 1.4)
    for arm in ("right_arm", "left_arm"):
        c.rot(arm, 0, (0, 0, 0)).rot(arm, 0.4, (-80, 0, 0), "easeOutQuad").rot(arm, 1.0, (-85, 0, 0))
        c.rot(arm, 1.4, (0, 0, 0))
    c.rot("waist", 0.5, (18, 0, 0)).rot("waist", 1.0, (22, 0, 0)).rot("waist", 1.4, (0, 0, 0))
    c.rot("head", 0.5, (20, 0, 10)).rot("head", 1.4, (0, 0, 0))
    A.append(c)
    # Plunge: it tips over and drops head first onto its prey
    p = Anim("plunge", 1.2)
    p.rot("root", 0, (0, 0, 0)).rot("root", 0.35, (-30, 0, 0)).rot("root", 0.6, (160, 0, 0), "easeInQuad")
    p.rot("root", 0.9, (170, 0, 0)).rot("root", 1.2, (0, 0, 0))
    p.pos("root", 0.35, (0, 6, 0)).pos("root", 0.6, (0, 30, -12), "easeInQuad").pos("root", 0.9, (0, 28, -12))
    p.pos("root", 1.2, (0, 0, 0))
    A.append(p)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.5, from_scale=1.0, loop="hold_on_last_frame"))
    dr = Anim("drink", 1.0)
    dr.rot("head", 0, (0, 0, 0)).rot("head", 0.4, (25, 0, 0)).rot("head", 1.0, (0, 0, 0))
    A.append(dr)
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("falling_front.png"), anim, "idle", 0.0, yaw=20, pitch=5,
                       show_body=False, scale=2.9, center=(0, 2.7), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("falling_face.png"), anim, "idle", 0.0, yaw=10, pitch=0,
                       show_body=False, scale=9.0, center=(0, 4.2), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("falling_fall.png"), anim, "fall", 1.0, yaw=35, pitch=5,
                       show_body=False, scale=2.4, center=(0, 3.2), size=(620, 620), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("falling_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
