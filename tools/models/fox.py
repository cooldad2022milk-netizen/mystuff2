"""
The Fox Devil - the mob (entity/devil/fox) and the two parts of it that contractors call up (entity/contract/fox_head,
entity/contract/fox_paw), with their animations.

Reference points (manga / anime):
  * an oversized ARCTIC fox: white fur (pale in the manga, pure white in the anime)
  * its head is covered in eyes - big ones with concentric rings, glowing red-orange - crowding up the snout and brow
  * a long snout with black lips and rows of fangs, a black nose, tall pointed ears
  * its forelegs are monstrously big, with oversized black claws, and they are covered in eyes too
  * contracts: "Kon!" with the fox hand sign calls ONLY ITS HEAD, which bites the prey clean in half or swallows it
    whole (Aki, the Vice Captain - it only lends its head to handsome hunters); everyone else it deals with gets a PAW
    (a leg or a hand) that swipes or comes down on the prey. The mob is the whole fox; the contracts never are.
"""
import math

import numpy as np

from common import preview_path, out
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk


def materials():
    a = Atlas(512, 64)
    a.add("fur", kind="fiber", color=(242, 240, 234))
    a.add("fur_sh", kind="fiber", color=(214, 212, 210))
    a.add("fur_dk", kind="fiber", color=(62, 58, 60))
    a.add("eye", kind="ringeye", color=(246, 150, 52), color2=(170, 24, 20), rings=3, sclera=(252, 244, 226),
          emissive=True)
    a.add("teeth", kind="teeth", color=(246, 242, 230))
    a.add("mouth", kind="void", color=(84, 14, 22))
    a.add("gum", kind="flesh", color=(176, 60, 76))
    a.add("lip", kind="gloss", color=(28, 24, 26))
    a.add("nose", kind="gloss", color=(22, 18, 20))
    a.add("claw", kind="gloss", color=(30, 26, 28))
    a.add("pad", kind="skin", color=(52, 44, 46))
    a.add("ear_in", kind="skin", color=(186, 150, 150))
    a.add("rift", kind="void", color=(18, 8, 16))
    return a


# ----------------------------------------------------------------------------- the head (mob and Kon)
HEAD_EYES = (
    # (u, v, size): u = 0 is the top of the head, 0.25 its left (+x), 0.75 its right; v runs from the skull to the nose
    (0.14, 0.40, 3.4), (0.86, 0.40, 3.4),      # the main pair
    (0.20, 0.26, 2.6), (0.80, 0.26, 2.6),      # behind them
    (0.05, 0.30, 2.3), (0.95, 0.30, 2.3),      # up on the brow
    (0.0, 0.16, 2.4),                          # the middle of the forehead
    (0.07, 0.52, 2.0), (0.93, 0.52, 2.0),      # climbing the snout
    (0.02, 0.63, 1.7), (0.98, 0.63, 1.7),
    (0.0, 0.74, 1.4),                          # nearly at the nose
    (0.27, 0.34, 1.9), (0.73, 0.34, 1.9),      # the cheeks
)


def head(m, parent, jaw_hinge=(0, 0, 0), k=1.0, anchor=(0, 0, 0), ears=True):
    """The fox's head built in its own frame (jaw hinge at the origin, snout toward -z), then scaled by k about the
    origin and moved so the origin lands on `anchor`. Bones: head > look > jaw. Returns them."""
    hb = m.bone("head", parent=parent, pivot=(0, 0, 6.0))
    look = m.bone("look", parent="head", pivot=(0, 0, 4.0))
    # a broad skull and brow, then a shorter snout tapering to the nose
    skull = shapes.loft(shapes.polyline([(0, 2.4, 8.0), (0, 3.4, 3.0), (0, 2.6, -4.0), (0, 1.0, -10.0),
                                         (0, -0.2, -15.0), (0, -0.6, -18.0)]),
                        shapes.profile((0, 3.4), (0.14, 7.4), (0.34, 6.8), (0.55, 4.3), (0.8, 2.8), (1, 1.3)),
                        shapes.profile((0, 3.4), (0.14, 6.6), (0.34, 5.7), (0.55, 3.9), (0.8, 2.7), (1, 1.4)),
                        up=(0, 1, 0))
    mouth = shapes.Mouth(skull, 0.5, 0.26, 0.40, 0.97)

    def skull_mat(u, v):
        if abs(u - 0.5) < 0.31 and 0.36 < v:
            return "lip"                     # black lips round the whole mouth
        if abs(u - 0.5) < 0.2:
            return "fur_sh"                  # the throat and underjaw are a shade darker
        return "fur"
    shapes.shell(look, skull, 18, 16, "fur", skip=mouth.skip, thick=0.4, mat_fn=skull_mat)
    jaw = m.bone("jaw", parent="look", pivot=(0, -1.0, -1.0))
    mouth.build(look, jaw, "fur_sh", upper=13, lower=11, tooth_len=1.7, tooth_w=0.62, nu=6, nv=10, gum_mat="gum")
    # black lip rim on the lower jaw
    shapes.shell(jaw, shapes.scaled(skull, 1.02), 6, 10, "lip", u0=0.5 - 0.27, u1=0.5 - 0.22, v0=0.42, v1=0.96,
                 thick=0.25)
    shapes.shell(jaw, shapes.scaled(skull, 1.02), 6, 10, "lip", u0=0.5 + 0.22, u1=0.5 + 0.27, v0=0.42, v1=0.96,
                 thick=0.25)
    look.cbox((0, 0.7, -18.4), (2.6, 2.0, 1.5), "nose")
    for (u, v, w) in HEAD_EYES:
        p, n, du, dv = shapes.surface_frame(skull, u, v)
        look.decal(p + n * 0.18, n, w * 1.45, w * 0.95, "eye", up=norm(np.array([0, 1.0, 0]) - n * n[1]))
    if ears:
        for s in (-1, 1):
            root_p = np.array([s * 3.8, 6.8, 3.0])
            d = norm((s * 0.28, 1, 0.12))
            shapes.horn(look, root_p, d, 10.5, 3.3, mat="fur", tip_mat="fur_dk", tip_from=0.8, flat=0.32,
                        up=(0, 0, 1), sections=6, around=8, r1=0.2)
            shapes.horn(look, root_p + np.array([0, 0.6, -0.9]), d, 8.0, 2.2, mat="ear_in", flat=0.14, up=(0, 0, 1),
                        sections=4, around=8, r1=0.2)
    # a white ruff on the cheeks
    for s in (-1, 1):
        for i in range(6):
            p = np.array([s * 5.6, -1.0 - i * 0.7, 2.0 + i * 1.3])
            shapes.horn(look, p, norm([s * 1.0, -0.5, 0.45]), 3.4 - i * 0.3, 1.2, mat="fur", sections=2, around=5,
                        r1=0.1)
    bones = [hb, look, jaw]
    for b in bones:
        b.scale_about((0, 0, 0), k)
        b.offset(np.asarray(anchor, dtype=float) - np.asarray(jaw_hinge, dtype=float) * k)
    return bones


# ----------------------------------------------------------------------------- the forelegs (mob and the paw)
def foreleg(m, name, parent, top, foot, r_top, r_foot, eyes=5, claws=True):
    """A monstrous foreleg from `top` down to the paw at `foot`: white fur, eyes all over it, black claws."""
    top = np.asarray(top, dtype=float)
    foot = np.asarray(foot, dtype=float)
    b = m.bone(name, parent=parent, pivot=tuple(top))
    knee = top + (foot - top) * 0.55 + np.array([0, 0, 0.12]) * np.linalg.norm(foot - top) * 0.1
    pts = [top, top + (knee - top) * 0.5, knee, foot + np.array([0, r_foot * 1.4, 0])]
    rad = shapes.profile((0, r_top), (0.45, r_top * 0.72), (0.7, r_foot * 1.1), (1, r_foot))
    f = shapes.loft(shapes.polyline(pts), rad, lambda t: rad(t) * 0.92, up=(0, 0, -1))
    shapes.shell(b, f, 12, 14, "fur", thick=0.45, mat_fn=lambda u, v: "fur_sh" if 0.35 < u < 0.65 else "fur")
    # the paw: a broad pad with splayed toes
    paw_c = foot + np.array([0, r_foot * 0.6, -r_foot * 0.7])
    shapes.shell(b, shapes.ellipsoid(paw_c, (r_foot * 1.35, r_foot * 0.75, r_foot * 1.6)), 10, 6, "fur", thick=0.4)
    shapes.shell(b, shapes.ellipsoid(paw_c + np.array([0, -r_foot * 0.55, 0]), (r_foot * 1.1, r_foot * 0.25,
                                                                               r_foot * 1.3)), 8, 4, "pad", thick=0.3)
    if claws:
        for i in range(4):
            x = (-1.5 + i) * r_foot * 0.6
            base = paw_c + np.array([x, -r_foot * 0.2, -r_foot * 1.4])
            shapes.horn(b, base, (x * 0.05, -0.35, -1), r_foot * 1.7, r_foot * 0.26, mat="claw", sections=3,
                        around=5, r1=0.06, bend_axis=(1, 0, 0), bend=50)
    # u = 0 is the front of the leg (the loft's up is -z), 0.5 the back
    us = (0.0, 0.13, 0.87, 0.06, 0.94, 0.2, 0.8)
    for i in range(eyes):
        u = us[i % len(us)]
        v = 0.12 + i * 0.72 / max(1, eyes - 1)
        p, n, du, dv = shapes.surface_frame(f, u, v)
        w = r_top * (0.95 if i < 2 else 0.75)
        b.decal(p + n * 0.15, n, w * 1.4, w * 0.9, "eye", up=norm(-dv))
    return b, f


# ----------------------------------------------------------------------------- the whole fox (mob)
def build_mob():
    atlas = materials()
    m = Model("csm.fox_devil", atlas, density=2.0, seed=241)
    root = m.bone("root", pivot=(0, 0, 0))
    body = m.bone("body", parent="root", pivot=(0, 30, 6))
    # a long, deep-chested body on massive forelegs; lean haunches
    torso = shapes.loft(shapes.polyline([(0, 35.0, -20.0), (0, 31.0, -10.0), (0, 31.0, 4.0), (0, 32.0, 16.0),
                                         (0, 33.0, 24.0)]),
                        shapes.profile((0, 7.0), (0.15, 11.0), (0.5, 8.6), (0.8, 9.4), (1, 5.0)),
                        shapes.profile((0, 8.0), (0.15, 12.5), (0.5, 9.0), (0.8, 9.6), (1, 5.0)), up=(0, 1, 0))
    shapes.shell(body, torso, 20, 16, "fur", thick=0.5,
                 mat_fn=lambda u, v: "fur_sh" if abs(u - 0.5) < 0.16 else "fur")
    # eyes along its flanks too
    for (u, v, w) in ((0.22, 0.28, 3.0), (0.3, 0.5, 2.4), (0.2, 0.72, 2.6), (0.78, 0.3, 2.8), (0.7, 0.52, 2.4),
                      (0.82, 0.7, 2.2)):
        p, n, du, dv = shapes.surface_frame(torso, u, v)
        body.decal(p + n * 0.15, n, w * 1.5, w * 0.95, "eye", up=(0, 1, 0))
    # the neck rising to the head
    shapes.shell(body, shapes.loft(shapes.polyline([(0, 34.0, -16.0), (0, 41.0, -21.0), (0, 46.0, -24.0)]),
                                   shapes.profile((0, 9.5), (1, 7.5)), shapes.profile((0, 10.5), (1, 8.0)),
                                   up=(0, 0.4, -1)), 14, 6, "fur", thick=0.45,
                 mat_fn=lambda u, v: "fur_sh" if abs(u - 0.5) < 0.2 else "fur")
    # chest ruff
    for i in range(11):
        a = math.radians(-75 + i * 150 / 10)
        p = np.array([math.sin(a) * 9.5, 33.0 - abs(math.sin(a)) * 2.0, -22.0])
        shapes.horn(body, p, norm([math.sin(a) * 0.4, -1.0, -0.5]), 6.0, 2.4, mat="fur", sections=3, around=5,
                    r1=0.1)
    # a head far too big for the body, crowded with eyes
    head(m, "body", k=1.7, anchor=(0, 47.0, -33.0))
    # the brush of a tail, white to the tip
    tail = m.bone("tail", parent="body", pivot=(0, 33, 23))
    tf = shapes.loft(shapes.polyline([(0, 33.5, 22.0), (0, 35.0, 30.0), (0, 40.0, 38.0), (0, 47.0, 43.0),
                                      (0, 54.0, 45.0)]),
                     shapes.profile((0, 3.4), (0.25, 7.0), (0.55, 8.8), (0.82, 7.0), (1, 1.0)),
                     shapes.profile((0, 3.4), (0.25, 6.4), (0.55, 8.0), (0.82, 6.4), (1, 1.0)))
    shapes.shell(tail, tf, 16, 14, "fur", thick=0.45, mat_fn=lambda u, v: "fur_sh" if 0.4 < u < 0.6 else "fur")
    for side, s in (("right", -1), ("left", 1)):
        foreleg(m, side + "_front_leg", "body", (s * 8.5, 31.0, -12.0), (s * 9.0, 2.5, -15.0), 7.0, 4.2, eyes=5)
        back, _ = foreleg(m, side + "_back_leg", "body", (s * 8.0, 32.0, 16.0), (s * 8.5, 2.5, 19.0), 6.8, 3.0,
                          eyes=2)
    geo, tex, glow, anim_path = dk.devil_paths("fox")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=243)
    anims = mob_animations()
    save_animations(anim_path, anims)
    print("fox devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def mob_animations():
    A = []
    legs = ["right_front_leg", "left_front_leg", "right_back_leg", "left_back_leg"]
    idle = Anim("idle", 3.0, loop=True)
    for i in range(9):
        t = 3.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("tail", t, (6 * math.sin(ph), 16 * math.sin(ph * 0.5), 0))
        idle.rot("head", t, (3 * math.sin(ph), 6 * math.cos(ph * 0.5), 0))
        idle.rot("jaw", t, (3 + 3 * math.sin(ph * 2), 0, 0))
        idle.scale("body", t, (1 + 0.012 * math.sin(ph), 1 + 0.018 * math.sin(ph), 1))
    A.append(idle)
    mv = Anim("move", 0.8, loop=True)
    for i in range(9):
        t = 0.8 * i / 8
        ph = 2 * math.pi * i / 8
        mv.rot("right_front_leg", t, (32 * math.sin(ph), 0, 0))
        mv.rot("left_front_leg", t, (32 * math.sin(ph + 0.6), 0, 0))
        mv.rot("right_back_leg", t, (-30 * math.sin(ph + 0.3), 0, 0))
        mv.rot("left_back_leg", t, (-30 * math.sin(ph + 0.9), 0, 0))
        mv.rot("body", t, (3 * math.sin(2 * ph), 0, 0))
        mv.rot("tail", t, (-12 + 8 * math.sin(2 * ph), 0, 0))
        mv.pos("root", t, (0, 1.6 * abs(math.sin(ph)), 0))
    A.append(mv)
    # its own bite: the head lunges, the jaws gape and snap shut
    kn = Anim("kon", 1.0)
    kn.rot("head", 0, (0, 0, 0)).rot("head", 0.3, (-20, 0, 0), "easeInQuad").rot("head", 0.45, (18, 0, 0), "easeOutQuad")
    kn.rot("head", 1.0, (0, 0, 0))
    kn.pos("head", 0.3, (0, 1, 2)).pos("head", 0.45, (0, -1, -9), "easeOutQuad").pos("head", 1.0, (0, 0, 0))
    kn.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.3, (52, 0, 0), "easeOutQuad").rot("jaw", 0.45, (-4, 0, 0), "easeInQuad")
    kn.rot("jaw", 1.0, (0, 0, 0))
    A.append(kn)
    cl = Anim("claw", 0.9)
    cl.rot("right_front_leg", 0, (0, 0, 0)).rot("right_front_leg", 0.3, (-85, 0, -20), "easeOutQuad")
    cl.rot("right_front_leg", 0.45, (22, 0, 10), "easeInQuad").rot("right_front_leg", 0.9, (0, 0, 0))
    cl.rot("body", 0.3, (-10, 0, 5)).rot("body", 0.45, (8, 0, -5)).rot("body", 0.9, (0, 0, 0))
    A.append(cl)
    po = Anim("pounce", 1.2)
    po.rot("body", 0, (0, 0, 0)).rot("body", 0.25, (12, 0, 0)).rot("body", 0.45, (-22, 0, 0), "easeOutQuad")
    po.rot("body", 0.85, (18, 0, 0), "easeInQuad").rot("body", 1.2, (0, 0, 0))
    for l in legs:
        front = "front" in l
        po.rot(l, 0.25, (30 if front else -30, 0, 0)).rot(l, 0.45, (-70 if front else 55, 0, 0))
        po.rot(l, 0.85, (-20 if front else 20, 0, 0)).rot(l, 1.2, (0, 0, 0))
    po.rot("jaw", 0.7, (45, 0, 0)).rot("jaw", 0.9, (0, 0, 0))
    A.append(po)
    dv = Anim("devour", 1.2)
    for i in range(7):
        t = 0.2 + i * 0.12
        dv.rot("jaw", t, (40 if i % 2 == 0 else 5, 0, 0))
        dv.rot("head", t, (15 + (6 if i % 2 else -6), (12 if i % 2 else -12), 0))
    dv.rot("jaw", 0, (0, 0, 0)).rot("jaw", 1.2, (0, 0, 0)).rot("head", 0, (0, 0, 0)).rot("head", 1.2, (0, 0, 0))
    A.append(dv)
    dr = Anim("drink", 1.0)
    dr.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.3, (30, 0, 0)).rot("jaw", 1.0, (0, 0, 0))
    A.append(dr)
    death = Anim("death", 1.4, loop="hold_on_last_frame")
    death.rot("root", 0, (0, 0, 0)).rot("root", 0.9, (0, 0, 85), "easeInQuad")
    death.pos("root", 0.9, (0, -2, 0))
    for l in legs:
        death.rot(l, 0.9, (0, 0, 30))
    death.rot("jaw", 0.9, (30, 0, 0))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 0.8, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


# ----------------------------------------------------------------------------- Kon: the head alone
KON_SCALE = 2.4


def basis(n):
    """A frame whose local y is n."""
    n = norm(n)
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 0, 1.0])
    x = norm(np.cross(a, n))
    return np.column_stack([x, n, np.cross(x, n)])


def rift(bone, center, normal, radius):
    """The tear in the air a summoned part comes through: a dark ragged disc."""
    B = basis(normal)
    shapes.shell(bone, shapes.ellipsoid(center, (radius, radius * 0.12, radius), frame=B), 14, 4, "rift", thick=0.3)
    for i in range(10):
        a = i * 2 * math.pi / 10
        d = B[:, 0] * math.cos(a) + B[:, 2] * math.sin(a)
        shapes.horn(bone, np.asarray(center, dtype=float) + d * radius * 0.8, d, radius * (0.4 + 0.25 * (i % 3)),
                    radius * 0.16, mat="rift", flat=0.3, up=B[:, 1], sections=2, around=5, r1=0.1)


def build_kon():
    """entity/contract/fox_head: the head (and a stump of neck fading into a tear in the air). The origin is where the
    prey is: the jaws close round it at about a block up."""
    atlas = materials()
    m = Model("csm.fox_head", atlas, density=1.4, seed=245)
    root = m.bone("root", pivot=(0, 0, 0))
    k = KON_SCALE
    # the middle of the mouth (local (0, -1.2, -10)) sits on the prey, a block up
    head(m, "root", k=k, anchor=np.array([0, 16.0, 0]) - np.array([0, -1.2, -10.0]) * k)
    z0 = 10.0 * k  # local z = 0 lands here
    neck = m.bone("neck", parent="head", pivot=(0, 16, z0 + 8 * k))
    shapes.shell(neck, shapes.loft(shapes.polyline([(0, 18.5, z0 + 6.0 * k), (0, 17.5, z0 + 10.0 * k),
                                                    (0, 16.0, z0 + 14.0 * k)]),
                                   shapes.profile((0, 6.0 * k), (1, 5.4 * k)), shapes.profile((0, 5.8 * k), (1, 5.2 * k)),
                                   up=(0, 1, 0)), 14, 5, "fur", thick=0.5)
    rift(neck, (0, 16.0, z0 + 14.5 * k), (0, 0, 1), 8.5 * k)
    geo = out("geo", "entity", "contract", "fox_head.geo.json")
    tex = out("textures", "entity", "contract", "fox_head.png")
    glow = out("textures", "entity", "contract", "fox_head_glowmask.png")
    anim_path = out("animations", "entity", "contract", "fox_head.animation.json")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=243)
    save_animations(anim_path, [kon_animation()])
    print("fox head (Kon): %d cubes, %d bones" % (m.cube_count(), len(m.bones)))
    return geo, tex, anim_path


def kon_animation():
    """24 ticks. It tears out of the air behind the prey with its jaws gaping, lunges, and the jaws snap shut on tick 9
    (ContractSummonEntity#foxHead); it worries the kill, then sinks back into nothing."""
    a = Anim("kon", 1.2, loop="hold_on_last_frame")
    a.scale("root", 0, 0.25).scale("root", 0.18, 1.06, "easeOutBack").scale("root", 0.3, 1.0)
    a.scale("root", 0.85, 1.0).scale("root", 1.2, 0.02, "easeInQuad")
    a.pos("root", 0, (0, 10, 40)).pos("root", 0.2, (0, 8, 26), "easeOutQuad").pos("root", 0.35, (0, 6, 22))
    a.pos("root", 0.45, (0, 0, 0), "easeInQuad").pos("root", 0.85, (0, 0, 2)).pos("root", 1.2, (0, 4, 30), "easeInQuad")
    a.rot("jaw", 0, (10, 0, 0)).rot("jaw", 0.25, (58, 0, 0), "easeOutQuad").rot("jaw", 0.38, (60, 0, 0))
    a.rot("jaw", 0.45, (-2, 0, 0), "easeInQuad").rot("jaw", 1.2, (0, 0, 0))
    a.rot("head", 0, (-12, 0, 0)).rot("head", 0.38, (-18, 0, 0)).rot("head", 0.45, (6, 0, 0), "easeInQuad")
    for i in range(5):
        t = 0.52 + i * 0.07
        a.rot("head", t, (8, 9 if i % 2 else -9, 5 if i % 2 else -5))
    a.rot("head", 0.9, (4, 0, 0)).rot("head", 1.2, (-10, 0, 0))
    return a


# ----------------------------------------------------------------------------- the paw
PAW_TOP = 80.0


def build_paw():
    """entity/contract/fox_paw: one foreleg out of a tear in the air, eyes all over it. Origin = where the paw lands
    (slam) / where the contractor stands (swipe)."""
    atlas = materials()
    m = Model("csm.fox_paw", atlas, density=1.4, seed=247)
    root = m.bone("root", pivot=(0, PAW_TOP, 0))
    arm, _ = foreleg(m, "arm", "root", (0, PAW_TOP, 0), (0, 3.0, 0), 16.0, 9.5, eyes=7)
    rift(m.bone("rift", parent="root", pivot=(0, PAW_TOP, 0)), (0, PAW_TOP + 2.0, 0), (0, 1, 0), 22.0)
    geo = out("geo", "entity", "contract", "fox_paw.geo.json")
    tex = out("textures", "entity", "contract", "fox_paw.png")
    glow = out("textures", "entity", "contract", "fox_paw_glowmask.png")
    anim_path = out("animations", "entity", "contract", "fox_paw.animation.json")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=243)
    save_animations(anim_path, paw_animations())
    print("fox paw: %d cubes, %d bones" % (m.cube_count(), len(m.bones)))
    return geo, tex, anim_path


def paw_animations():
    # slam (26 ticks): down out of the sky on tick 8 (ContractSummonEntity#pawSlam), grind, back up
    s = Anim("slam", 1.3, loop="hold_on_last_frame")
    s.scale("root", 0, 0.2).scale("root", 0.15, 1.0, "easeOutBack")
    s.pos("arm", 0, (0, 60, 0)).pos("arm", 0.25, (0, 46, 4), "easeOutQuad").pos("arm", 0.4, (0, 0, 0), "easeInQuad")
    s.pos("arm", 0.9, (0, -1, 0)).pos("arm", 1.2, (0, 70, 0), "easeInQuad")
    s.rot("arm", 0, (0, 0, 0)).rot("arm", 0.25, (-18, 0, 0)).rot("arm", 0.4, (6, 0, 0), "easeInQuad")
    s.rot("arm", 0.6, (2, 6, 0)).rot("arm", 0.8, (2, -6, 0)).rot("arm", 1.0, (0, 0, 0))
    s.scale("rift", 0, 0.2).scale("rift", 0.2, 1.0, "easeOutBack").scale("rift", 1.1, 1.0).scale("rift", 1.3, 0.01)
    s.scale("root", 1.15, 1.0).scale("root", 1.3, 0.02, "easeInQuad")
    # swipe (22 ticks): the paw hangs in front of the contractor and sweeps from their right to their left on tick 8
    w = Anim("swipe", 1.1, loop="hold_on_last_frame")
    w.pos("root", 0, (0, 14, -34)).pos("root", 1.1, (0, 14, -34))
    w.scale("root", 0, 0.2).scale("root", 0.15, 1.0, "easeOutBack")
    w.rot("root", 0, (0, 0, -62)).rot("root", 0.2, (0, 0, -68), "easeOutQuad")
    w.rot("root", 0.42, (0, 0, 64), "easeInOutQuad").rot("root", 0.7, (0, 0, 70)).rot("root", 1.1, (0, 0, 72))
    w.rot("arm", 0.2, (10, 0, 0)).rot("arm", 0.42, (-8, 0, 0)).rot("arm", 1.1, (0, 0, 0))
    w.scale("root", 0.8, 1.0).scale("root", 1.1, 0.02, "easeInQuad")
    return [s, w]


def render_previews():
    g, t, a = dk.devil_paths("fox")[0], dk.devil_paths("fox")[1], dk.devil_paths("fox")[3]
    kg, kt, ka = (out("geo", "entity", "contract", "fox_head.geo.json"),
                  out("textures", "entity", "contract", "fox_head.png"),
                  out("animations", "entity", "contract", "fox_head.animation.json"))
    pg, pt, pa = (out("geo", "entity", "contract", "fox_paw.geo.json"),
                  out("textures", "entity", "contract", "fox_paw.png"),
                  out("animations", "entity", "contract", "fox_paw.animation.json"))
    shots = [
        preview.render(g, t, preview_path("fox_mob.png"), a, "idle", 0.0, yaw=35, pitch=8, show_body=False,
                       scale=3.6, center=(0, 2.0), size=(620, 620), bg=(150, 170, 200)),
        preview.render(g, t, preview_path("fox_face.png"), a, "idle", 0.0, yaw=-70, pitch=6, show_body=False,
                       scale=5.5, center=(0, 2.6), size=(620, 620), bg=(150, 170, 200)),
        preview.render(kg, kt, preview_path("fox_kon_open.png"), ka, "kon", 0.36, yaw=110, pitch=6, show_body=True,
                       scale=2.6, center=(0, 1.4), size=(620, 620), bg=(150, 170, 200)),
        preview.render(kg, kt, preview_path("fox_kon_bite.png"), ka, "kon", 0.5, yaw=140, pitch=8, show_body=True,
                       scale=2.6, center=(0, 1.4), size=(620, 620), bg=(150, 170, 200)),
        preview.render(pg, pt, preview_path("fox_paw_slam.png"), pa, "slam", 0.45, yaw=150, pitch=6, show_body=True,
                       scale=2.3, center=(0, 2.8), size=(620, 620), bg=(150, 170, 200)),
        preview.render(pg, pt, preview_path("fox_paw_swipe.png"), pa, "swipe", 0.3, yaw=150, pitch=10, show_body=True,
                       scale=2.0, center=(0, 2.4), size=(620, 620), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("fox_sheet.png"), cols=3)


if __name__ == "__main__":
    build_mob()
    build_kon()
    build_paw()
    print(render_previews())
