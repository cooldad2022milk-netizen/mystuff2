"""
Princi, the Spider Devil - entity model (entity/devil/spider), texture atlas and GeckoLib animations.

Reference points (manga, part 1 - she serves Makima):
  * from the waist up a young woman with waist-length black hair and a zipper running down the front of her face
  * in her human disguise a button-down shirt and a bowtie (kept on the woman half here)
  * below the waist a spider: eight legs ending in curved, scythe-like points sharp enough to stab through flesh
  * she walks on walls, sinks into the ground and comes up under her prey, and unzips herself to let Makima through
"""
import math

import numpy as np

from common import preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk

LIFT = np.array([0.0, 12.0, -5.5])  # where the woman half sits: on the front of the spider's body


def materials():
    a = Atlas(512, 64)
    a.add("skin", kind="skin", color=(240, 222, 208))
    a.add("hair", kind="fiber", color=(22, 20, 26))
    a.add("hair_dk", kind="fiber", color=(12, 10, 14))
    a.add("shirt", kind="skin", color=(244, 244, 242))
    a.add("shirt_dk", kind="skin", color=(214, 214, 216))
    a.add("bow", kind="skin", color=(26, 24, 30))
    a.add("button", kind="bone", color=(230, 226, 214))
    a.add("chitin", kind="gloss", color=(38, 30, 36))
    a.add("chitin_dk", kind="gloss", color=(20, 16, 20))
    a.add("chitin_lt", kind="gloss", color=(70, 56, 64))
    a.add("joint", kind="flesh", color=(90, 50, 60))
    a.add("blade", kind="metal", color=(206, 204, 200), scratches=4)
    a.add("zip", kind="metal", color=(180, 176, 168), scratches=1)
    a.add("zip_dk", kind="metal", color=(96, 92, 88), scratches=1)
    a.add("eye", kind="ringeye", color=(40, 30, 34), color2=(20, 14, 16), rings=1, sclera=(240, 234, 228))
    a.add("brow", kind="skin", color=(30, 26, 30))
    a.add("lip", kind="skin", color=(196, 130, 130))
    a.add("mouth", kind="void", color=(40, 8, 12))
    a.add("hairs", kind="fiber", color=(52, 42, 48))
    return a


# ---------------------------------------------------------------------------------------- the woman half
def zipper(look):
    """The zipper down the middle of her face, forehead to chin, with its pull tab at the top."""
    for k in range(15):
        y = 31.2 - k * 0.5
        for s in (-1, 1):
            look.cbox((s * 0.17 + (0.07 if k % 2 else -0.07), y, -4.08), (0.3, 0.26, 0.16), "zip")
    look.cbox((0, 31.35, -4.12), (0.5, 0.6, 0.2), "zip_dk")
    look.obox((0, 30.6, -4.3), (0, 1, 0), (0.45, 1.2, 0.14), "zip", up=(0, 0, -1))  # the pull tab


def face(look):
    for s in (-1, 1):
        look.decal((s * 1.95, 27.6, -4.03), (0, 0, -1), 1.9, 1.3, "eye")
        look.obox((s * 1.95, 28.9, -4.03), (s * 1.0, 0.12, 0), (0.25, 1.7, 0.2), "brow", up=(0, 0, -1))
        look.obox((s * 0.9, 25.7, -4.0), (1, 0, 0), (0.22, 0.9, 0.14), "lip", up=(0, 0, -1))
    look.obox((0, 26.8, -4.02), (0, 1, 0), (0.35, 0.5, 0.15), "skin", up=(0, 0, -1))
    zipper(look)


def hair(look, body):
    """Black hair, centre-parted, falling straight past her shoulders to her waist."""
    cap = shapes.ellipsoid((0, 28.5, 0.3), (4.6, 4.65, 4.65), e_lat=0.38, e_lon=0.42)
    shapes.shell(look, cap, 16, 10, "hair", v0=0.3, thick=0.45,
                 skip=lambda u, v: (u < 0.17 or u > 0.83) and v < 0.66,
                 mat_fn=lambda u, v: "hair_dk" if abs(u - 0.5) < 0.02 else "hair")
    # side locks framing the face, over the shoulders
    for s in (-1, 1):
        for k in range(3):
            base = np.array([s * (3.2 + k * 0.45), 30.8 - k * 0.3, -3.2 + k * 1.1])
            shapes.horn(look, base, (s * 0.12, -1.0, -0.05), 10.5 - k, 1.1, mat="hair" if k % 2 else "hair_dk",
                        flat=0.45, up=(s * 1.0, 0, 0), sections=4, around=6, r1=0.35, thick=0.3, power=0.7)
    # the long curtain down her back to the waist
    back = shapes.loft(shapes.polyline([(0, 31.5, 2.6), (0, 26.0, 4.6), (0, 18.0, 4.2), (0, 11.0, 4.6)]),
                       shapes.profile((0, 4.4), (0.3, 4.8), (1, 4.4)), shapes.profile((0, 1.2), (1, 0.8)),
                       up=(0, 0, 1))
    shapes.shell(body, back, 12, 10, "hair", thick=0.4,
                 mat_fn=lambda u, v: "hair_dk" if int(u * 12) % 3 == 0 else "hair")


def woman(m, mats):
    parts = dk.humanoid(m, mats, slim=True)
    for leg in ("right_leg", "left_leg"):  # a spider's body below the waist
        b = m.by_name.pop(leg)
        m.bones.remove(b)
    body, look = parts["body"], parts["look"]
    # the shirt: collar, buttons and the bowtie
    for s in (-1, 1):
        body.obox((s * 1.3, 23.4, -2.2), (s * 0.8, -1, 0), (1.5, 1.7, 0.25), "shirt_dk", up=(0, 0, -1))
        body.obox((s * 0.75, 23.0, -2.4), (s * 1.0, 0.1, 0), (0.9, 1.6, 0.35), "bow", up=(0, 0, -1))
    body.cbox((0, 23.0, -2.45), (0.6, 0.7, 0.4), "bow")
    for k in range(4):
        body.cbox((0, 21.4 - k * 2.3, -2.2 + 0.05 * k), (0.4, 0.4, 0.14), "button")
    face(look)
    hair(look, body)
    # move the woman up onto the front of the spider
    for name in ("waist", "body", "head", "look", "right_arm", "left_arm"):
        m.by_name[name].offset(LIFT)
    return parts


# ---------------------------------------------------------------------------------------- the spider half
LEGS = [(i, s) for s in (-1, 1) for i in range(4)]
LEG_YAW = (32.0, 70.0, 108.0, 146.0)  # degrees from straight ahead


def leg_name(i, s):
    return "leg_%s%d" % ("r" if s < 0 else "l", i + 1)


def leg(m, parent, i, s):
    a = math.radians(LEG_YAW[i])
    d = np.array([s * math.sin(a), 0.0, -math.cos(a)])
    attach = np.array([s * 4.6, 19.5, -4.0 + i * 2.6])
    b = m.bone(leg_name(i, s), parent=parent, pivot=tuple(attach))
    reach = 17.0 if i in (0, 3) else 15.0
    knee = attach + d * (reach * 0.55) + np.array([0, 12.0, 0])
    foot = attach + d * reach + np.array([0, -19.0, 0])
    for p0, p1, r0, r1 in ((attach, knee, 1.5, 1.2), (knee, foot + (knee - foot) * 0.3, 1.2, 0.8)):
        f = shapes.loft(shapes.polyline([p0, p1]), shapes.taper(r0, r1), shapes.taper(r0, r1))
        shapes.shell(b, f, 7, 4, "chitin", thick=0.35)
    shapes.shell(b, shapes.ellipsoid(knee, (1.6, 1.6, 1.6)), 7, 5, "chitin_lt", thick=0.35)
    shapes.shell(b, shapes.ellipsoid(attach, (1.8, 1.8, 1.8)), 7, 5, "joint", thick=0.35)
    # bristles along the leg
    for k in range(4):
        t = (k + 0.5) / 4
        p = attach + (knee - attach) * t
        b.spike(p + np.array([0, 1.0, 0]), norm(np.array([0, 1, 0]) + d * 0.3), 1.2, 0.2, 0.2, "hairs", steps=2)
    # the last joint is a curved blade, sharp as a knife
    blade_top = foot + (knee - foot) * 0.3
    shapes.horn(b, blade_top, foot - blade_top, np.linalg.norm(foot - blade_top) + 1.2, 0.9, mat="chitin_dk",
                tip_mat="blade", tip_from=0.35, flat=0.35, up=np.cross(d, [0, 1, 0]), sections=6, around=6, r1=0.05,
                bend_axis=np.cross(d, [0, 1, 0]), bend=-28)
    return b


def spider_body(m):
    sb = m.bone("spider", parent="root", pivot=(0, 20, 2))
    ceph = shapes.ellipsoid((0, 20.0, 0.0), (6.4, 4.6, 7.8), e_lat=0.8, e_lon=0.8)
    shapes.shell(sb, ceph, 14, 8, "chitin", thick=0.45)
    abdomen = m.bone("abdomen", parent="spider", pivot=(0, 22, 8))
    ab = shapes.ellipsoid((0, 23.0, 17.0), (8.6, 7.6, 10.5), e_lat=0.85, e_lon=0.85)
    shapes.shell(abdomen, ab, 16, 10, "chitin", thick=0.45,
                 mat_fn=lambda u, v: "chitin_lt" if (0.55 < v < 0.9 and abs(u - 0.5) < 0.06) else
                 ("chitin_dk" if int(v * 10) % 3 == 0 else "chitin"))
    for k in range(10):
        a = k / 10 * math.pi * 2
        p = np.array([math.sin(a) * 7.8, 25.0 + math.cos(a) * 2.5, 17.0 + math.cos(a) * 9.5])
        abdomen.spike(p, norm(p - np.array([0, 23.0, 17.0])), 1.4, 0.25, 0.25, "hairs", steps=2)
    shapes.shell(abdomen, shapes.ellipsoid((0, 20.5, 27.2), (1.8, 1.4, 0.8)), 6, 4, "chitin_dk", thick=0.3)
    for i, s in LEGS:
        leg(m, "spider", i, s)
    return sb


def build():
    atlas = materials()
    m = Model("csm.spider_devil", atlas, density=2.0, seed=511)
    mats = {"skin": "skin", "shirt": "shirt", "sleeve": "shirt", "cuff": "shirt_dk", "pants": "shirt", "shoe": "shirt"}
    woman(m, mats)  # dk.humanoid makes the root; the spider hangs off it too
    spider_body(m)
    geo, tex, glow, anim_path = dk.devil_paths("spider")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=513)
    anims = animations()
    save_animations(anim_path, anims)
    print("spider devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


# ---------------------------------------------------------------------------------------- animations
def legs_rest(a, t):
    for i, s in LEGS:
        a.rot(leg_name(i, s), t, (0, 0, 0))


def animations():
    A = []
    idle = Anim("idle", 3.2, loop=True)
    for k in range(9):
        t = 3.2 * k / 8
        ph = 2 * math.pi * k / 8
        idle.rot("body", t, (1.2 * math.sin(ph), 0, 0))
        idle.rot("head", t, (-1.5 * math.sin(ph), 4 * math.sin(ph * 0.5), 0))
        idle.rot("right_arm", t, (0, 0, 4 + 1.5 * math.sin(ph)))
        idle.rot("left_arm", t, (0, 0, -4 - 1.5 * math.sin(ph)))
        idle.rot("abdomen", t, (2 * math.sin(ph), 0, 0))
        for i, s in LEGS:
            idle.rot(leg_name(i, s), t, (0, 3 * math.sin(ph * 2 + i + (s > 0)), 0))
    A.append(idle)

    mv = Anim("move", 0.8, loop=True)
    for k in range(9):
        t = 0.8 * k / 8
        ph = 2 * math.pi * k / 8
        for i, s in LEGS:
            group = (i + (0 if s < 0 else 1)) % 2
            sw = math.sin(ph + group * math.pi)
            mv.rot(leg_name(i, s), t, (0, 16 * sw * s, 0))
            mv.pos(leg_name(i, s), t, (0, max(0.0, 2.5 * math.cos(ph + group * math.pi)), 0))
        mv.rot("waist", t, (4, 3 * math.sin(ph), 0))
        mv.pos("root", t, (0, 0.5 * abs(math.sin(2 * ph)), 0))
        mv.rot("abdomen", t, (3 * math.sin(2 * ph), 0, 0))
    A.append(mv)

    # Leg Impale (18 ticks): rear up, front legs high, stabs land on ticks 7 and 11
    im = Anim("impale", 0.9)
    im.rot("spider", 0, (0, 0, 0)).rot("spider", 0.25, (-18, 0, 0), "easeOutQuad").rot("spider", 0.6, (-10, 0, 0))
    im.rot("spider", 0.9, (0, 0, 0))
    for (i, s), t_hit in (((0, -1), 0.35), ((0, 1), 0.55)):
        n = leg_name(i, s)
        im.rot(n, 0, (0, 0, 0)).rot(n, t_hit - 0.12, (-75, 0, 0), "easeOutQuad").rot(n, t_hit, (25, 0, 0), "easeInQuad")
        im.rot(n, t_hit + 0.15, (10, 0, 0)).rot(n, 0.9, (0, 0, 0))
    im.rot("waist", 0.25, (-12, 0, 0)).rot("waist", 0.55, (8, 0, 0)).rot("waist", 0.9, (0, 0, 0))
    A.append(im)

    # Scythe Legs (20 ticks): all legs out and up, one full spin over ticks 6-13
    sc = Anim("scythe", 1.0)
    sc.rot("root", 0, (0, 0, 0)).rot("root", 0.3, (0, 0, 0)).rot("root", 0.65, (0, 359, 0), "easeInOutQuad")
    sc.rot("root", 0.66, (0, 0, 0)).rot("root", 1.0, (0, 0, 0))
    for i, s in LEGS:
        n = leg_name(i, s)
        sc.rot(n, 0.2, (0, 0, s * 25)).rot(n, 0.7, (0, 0, s * 25)).rot(n, 1.0, (0, 0, 0))
    sc.pos("root", 0.2, (0, 4, 0)).pos("root", 0.7, (0, 4, 0)).pos("root", 1.0, (0, 0, 0))
    for arm, s in (("right_arm", 1), ("left_arm", -1)):
        sc.rot(arm, 0.3, (0, 0, s * 70)).rot(arm, 0.7, (0, 0, s * 70)).rot(arm, 1.0, (0, 0, s * 4))
    A.append(sc)

    # Burrow (26 ticks): down into the ground by tick 5, under it until 17, bursts up on 18
    bu = Anim("burrow", 1.3)
    bu.pos("root", 0, (0, 0, 0)).pos("root", 0.25, (0, -50, 0), "easeInQuad").pos("root", 0.85, (0, -50, 0))
    bu.pos("root", 0.9, (0, 6, 0), "easeOutQuad").pos("root", 1.1, (0, 0, 0))
    for i, s in LEGS:
        n = leg_name(i, s)
        bu.rot(n, 0.85, (-40 if i == 0 else 0, 0, s * 30)).rot(n, 1.0, (0, 0, s * 10)).rot(n, 1.3, (0, 0, 0))
    bu.rot("waist", 0.9, (-20, 0, 0)).rot("waist", 1.3, (0, 0, 0))
    A.append(bu)

    # Unzip (30 ticks): her hand pulls the zipper from forehead to chin; Makima steps out on tick 16
    uz = Anim("unzip", 1.5)
    uz.rot("right_arm", 0, (0, 0, 4)).rot("right_arm", 0.25, (-165, -25, 0), "easeOutQuad")
    uz.rot("right_arm", 0.7, (-120, -30, 0)).rot("right_arm", 1.0, (-110, -30, 0)).rot("right_arm", 1.5, (0, 0, 4))
    uz.rot("head", 0.25, (-10, 0, 0)).rot("head", 0.75, (22, 0, 0)).rot("head", 1.1, (-35, 0, 0))
    uz.rot("head", 1.5, (0, 0, 0))
    uz.rot("waist", 0.75, (10, 0, 0)).rot("waist", 1.1, (-8, 0, 0)).rot("waist", 1.5, (0, 0, 0))
    A.append(uz)

    dr = Anim("drink", 1.0)
    dr.rot("right_arm", 0, (0, 0, 4)).rot("right_arm", 0.3, (-120, -25, 0)).rot("right_arm", 0.8, (-120, -25, 0))
    dr.rot("right_arm", 1.0, (0, 0, 4)).rot("head", 0.3, (10, 0, 0)).rot("head", 1.0, (0, 0, 0))
    A.append(dr)

    death = Anim("death", 1.8, loop="hold_on_last_frame")
    death.pos("root", 0, (0, 0, 0)).pos("root", 0.8, (0, -8, 0), "easeInQuad")
    death.rot("waist", 0.8, (40, 0, 0), "easeInQuad").rot("head", 0.8, (30, 0, 0))
    for i, s in LEGS:
        n = leg_name(i, s)
        death.rot(n, 0.8, (0, 0, -s * 50), "easeInQuad").rot(n, 1.8, (0, 0, -s * 60))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    bg = (170, 160, 170)
    shots = [
        preview.render(geo, tex, preview_path("spider_front.png"), anim, "idle", 0.0, yaw=25, pitch=10,
                       show_body=False, scale=9.0, center=(0, 1.4), size=(620, 620), bg=bg),
        preview.render(geo, tex, preview_path("spider_side.png"), anim, "idle", 0.0, yaw=110, pitch=12,
                       show_body=False, scale=9.0, center=(0, 1.4), size=(620, 620), bg=bg),
        preview.render(geo, tex, preview_path("spider_face.png"), anim, "idle", 0.0, yaw=-10, pitch=4,
                       show_body=False, scale=28.0, center=(0, 2.5), size=(620, 620), bg=bg),
        preview.render(geo, tex, preview_path("spider_impale.png"), anim, "impale", 0.26, yaw=60, pitch=8,
                       show_body=False, scale=9.0, center=(0, 1.4), size=(620, 620), bg=bg),
        preview.render(geo, tex, preview_path("spider_back.png"), anim, "idle", 0.0, yaw=200, pitch=14,
                       show_body=False, scale=9.0, center=(0, 1.4), size=(620, 620), bg=bg),
        preview.render(geo, tex, preview_path("spider_unzip.png"), anim, "unzip", 0.7, yaw=-20, pitch=4,
                       show_body=False, scale=20.0, center=(0, 2.3), size=(620, 620), bg=bg),
    ]
    return preview.contact_sheet(shots, preview_path("spider_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
