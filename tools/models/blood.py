"""
Power (Blood Fiend) - fiend parts model, texture atlas and GeckoLib animations, plus the blood-spear entity.

Reference points:
  * a pair of light red horns rising from her hair; the more blood she takes in, the longer and more curved they grow,
    and fresh pairs can erupt along the sides of her head
  * cross-shaped marks in red-and-yellow eyes, a mouth lined with pointed fangs
  * blood weapons: a massive crushing hammer, spears, scythes... and her Thousand Tera Blood Rain
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm, rotate_about
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
from spear import spearhead


def materials():
    a = Atlas(512, 64)
    a.add("horn", kind="skin", color=(228, 104, 104))
    a.add("horn_dk", kind="skin", color=(206, 78, 82))
    a.add("horn_tip", kind="skin", color=(186, 60, 66))
    a.add("blood", kind="blood", color=(150, 10, 18))
    a.add("blood_lt", kind="blood", color=(196, 24, 32))
    a.add("blood_glow", kind="glow", color=(200, 16, 24), color2=(255, 90, 80), emissive=True)
    return a


def horn(bone, root, direction, length, r0, bend_axis, bend, sections=10):
    """A smooth light-red horn tapering to a point, curving `bend` degrees about bend_axis as it grows."""
    shapes.horn(bone, root, direction, length, r0, bend_axis=bend_axis, bend=bend, mat="horn", tip_mat="horn_dk",
                sections=sections, around=8, r1=0.06, power=0.85, tip_from=0.7, thick=0.3)


# ------------------------------------------------------------------------------------------ head
def build_head(m):
    m.bone("head", pivot=(0, 24, 0))
    # her everyday horns: a pair of light red horns rising out of her hair near the front of the head,
    # leaning a little outward and curving gently back
    b = m.bone("prop_horns", parent="head", pivot=(0, 32, -1))
    for s in (-1, 1):
        horn(b, (s * 2.2, 31.2, -1.9), (s * 0.28, 1, -0.15), 5.4, 0.95, (1, 0, 0), 18)
    # gorged on blood: the horns grow longer and sweep back, and fresh pairs erupt along the sides of the head
    f = m.bone("form_horns", parent="head", pivot=(0, 32, -1))
    for s in (-1, 1):
        horn(f, (s * 2.2, 31.2, -1.9), (s * 0.34, 1, -0.2), 11.5, 1.25, (1, 0, 0), 62, sections=14)
    for k, (y, z, ln, r) in enumerate(((29.8, -0.6, 6.0, 0.85), (27.8, 0.9, 4.6, 0.7))):
        side_pair = m.bone("form_side_horns_%d" % k, parent="form_horns", pivot=(0, y, z))
        for s in (-1, 1):
            horn(side_pair, (s * 3.7, y, z), (s * 1, 0.55, 0.3), ln, r, (1, 0, 0), 40)


# ------------------------------------------------------------------------------------------ blood weapons (effect props)
def build_weapons(m):
    m.bone("right_arm", pivot=(-5, 22, 0))
    m.bone("left_arm", pivot=(5, 22, 0))
    # Blood Hammer: a long handle running on from the fist and a huge head of congealed blood
    h = m.bone("fx_hammer_right", parent="right_arm", pivot=(-6, 11, 0))
    h.tube((-6, 12.6, 0), (-6, -6.0, 0), 0.6, "blood", segments=6)
    head = shapes.ellipsoid((-6, -9.0, 0), (4.2, 3.6, 3.8), e_lat=0.35, e_lon=0.35)
    shapes.shell(h, head, 16, 10, "blood_lt", thick=0.45)
    for y in (-12.0, -6.0):
        h.ring((-6, y, 0), (0, 1, 0), 4.35, 0.5, 0.8, "blood", count=16)
    for s in (-1, 1):
        shapes.horn(h, (-6, -9.0, s * 3.4), (0, 0, s * 1.0), 2.2, 1.1, mat="blood", sections=4, around=6, r1=0.1)
    # congealing drips hanging off the head
    for k, (dx, dz, ln) in enumerate(((-2.6, -2.0, 1.6), (1.8, 2.4, 2.4), (2.9, -1.2, 1.2), (-1.2, 3.1, 2.0))):
        shapes.horn(h, (-6 + dx, -12.3, dz), (0, -1, 0), ln, 0.45, mat="blood", sections=3, around=6, r1=0.15)
    h.cbox((-6, 12.6, 0), (1.6, 1.0, 1.6), "blood")
    # Blood Spear held for the throw
    sp = m.bone("fx_bspear_right", parent="right_arm", pivot=(-6, 11, 0))
    sp.tube((-6, 16.0, 0), (-6, -4.0, 0), 0.45, "blood", segments=6)
    spearhead(sp, (-6, -4.2, 0), (0, -1, 0), 6.5, 2.6, 0.8, (0, 0, -1), mats=("blood_lt", "blood_glow", "blood"),
              steps=8, socket=False)
    # Blood Scythe: long snath, a great curved blade sweeping forward at the end
    sc = m.bone("fx_scythe_right", parent="right_arm", pivot=(-6, 11, 0))
    sc.tube((-6, 16.0, 0), (-6, -10.0, 0), 0.5, "blood", segments=6)
    pts = []
    for i in range(10):
        t = i / 9
        a = math.radians(-10 + 80 * t)
        pts.append(np.array([-6, -10.0 + 5.0 * math.sin(a) * 0.6, -math.sin(math.radians(90 * t)) * 12.0 - 0.5]))
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        w = 3.6 * (1 - i / 9) + 0.5
        sc.seg(p, q, 0.55, w, "blood_lt", up=(0, 1, 0), overlap=0.25)
        sc.seg(p + np.array([0, -w / 2, 0]), q + np.array([0, -w / 2 * 0.9, 0]), 0.2, 0.3, "blood_glow", up=(0, 1, 0),
               overlap=0.2)


def build_entity():
    """Power's thrown blood spear (same bone name/animation as the iron spear entity)."""
    atlas = Atlas(128, 32)
    atlas.add("blood", kind="blood", color=(150, 10, 18))
    atlas.add("blood_lt", kind="blood", color=(196, 24, 32))
    atlas.add("blood_glow", kind="blood", color=(230, 50, 50))
    m = Model("csm.blood_spear", atlas, density=2.0, seed=81)
    b = m.bone("spear", pivot=(0, 0, 0))
    b.tube((0, 0, 14.0), (0, 0, -6.0), 0.5, "blood", segments=6)
    for z in (12.0, 8.0, 4.0, 0.0):
        b.cylinder((0, 0, z), (0, 0, 1), 0.62, 0.6, "blood_lt", segments=6)
    spearhead(b, (0, 0, -6.2), (0, 0, -1), 9.0, 3.4, 1.1, (0, 1, 0), mats=("blood_lt", "blood_glow", "blood"), steps=10)
    b.spike((0, 0, 14.0), (0, 0, 1), 2.4, 0.9, 0.9, "blood", steps=3)
    m.save(out("geo", "entity", "blood_spear.geo.json"))
    paint_atlas(atlas, out("textures", "entity", "blood_spear.png"), None, seed=83)


def build():
    atlas = materials()
    m = Model("csm.blood_fiend", atlas, density=2.0, seed=79)
    build_head(m)
    m.bone("body", pivot=(0, 24, 0))
    build_weapons(m)
    geo = out("geo", "hybrid", "blood.geo.json")
    tex = out("textures", "hybrid", "blood.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "blood_glowmask.png"), seed=43)
    anims = animations()
    anim_path = out("animations", "hybrid", "blood.animation.json")
    save_animations(anim_path, anims)
    print("blood: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    build_entity()
    return geo, tex, anim_path


def animations():
    A = []
    e = Anim("emerge", 0.8)
    e.scale("form_horns", 0, 0.5).scale("form_horns", 0.25, 1.12, "easeOutBack").scale("form_horns", 0.4, 1.0)
    for k in range(2):
        bn = "form_side_horns_%d" % k
        t0 = 0.2 + 0.12 * k
        e.scale(bn, 0, 0.02).scale(bn, t0, 0.02).scale(bn, t0 + 0.2, 1.15, "easeOutBack").scale(bn, t0 + 0.3, 1.0)
    A.append(e)
    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    r.scale("form_horns", 0, 1).scale("form_horns", 0.35, 0.5, "easeInQuad")
    A.append(r)
    A.append(Anim("idle", 2.0, loop=True))

    def conjure(anim, bone, t0, t1, t_end, axis_scale=(1, 0.05, 1)):
        anim.scale(bone, 0, axis_scale).scale(bone, t0, axis_scale).scale(bone, t1, (1.05, 1.1, 1.05), "easeOutBack")
        anim.scale(bone, t1 + 0.1, 1.0).scale(bone, t_end, 1.0).scale(bone, t_end + 0.12, axis_scale, "easeInQuad")

    hm = Anim("hammer", 1.0)
    conjure(hm, "fx_hammer_right", 0.05, 0.3, 0.8)
    A.append(hm)
    sp = Anim("spear", 0.6)
    conjure(sp, "fx_bspear_right", 0.0, 0.2, 0.28)
    A.append(sp)
    sc = Anim("scythe", 0.9)
    conjure(sc, "fx_scythe_right", 0.05, 0.3, 0.7)
    A.append(sc)
    A.append(Anim("control", 0.9))
    rn = Anim("rain", 1.7)
    rn.scale("form_horns", 0, 1).scale("form_horns", 0.2, 1.12, "easeOutQuad").scale("form_horns", 1.5, 1.12)
    rn.scale("form_horns", 1.7, 1.0)
    A.append(rn)
    A.append(Anim("drink", 1.0))
    return A


def render_previews(geo, tex, anim):
    fx = ("fx_hammer_right", "fx_bspear_right", "fx_scythe_right")
    arms = {"right_arm": {"rot": (0, 0, 0.1)}, "left_arm": {"rot": (0, 0, -0.1)}}
    shots = [
        preview.render(geo, tex, preview_path("blood_human.png"), anim, "idle", 0, yaw=25, pitch=6, pose=arms,
                       hidden=fx + ("form_horns",), show_head=True, scale=18, center=(0, 1.6), size=(640, 520)),
        preview.render(geo, tex, preview_path("blood_awake.png"), anim, "idle", 0, yaw=35, pitch=6, pose=arms,
                       hidden=fx + ("prop_horns",), show_head=True, scale=18, center=(0, 1.7), size=(640, 520)),
        preview.render(geo, tex, preview_path("blood_hammer.png"), anim, "idle", 0, yaw=-60, pitch=8,
                       pose={"right_arm": {"rot": (-1.4, 0, 0)}}, hidden=("fx_bspear_right", "fx_scythe_right", "form_horns"),
                       show_head=True, scale=7, center=(0, 1.2)),
        preview.render(geo, tex, preview_path("blood_scythe.png"), anim, "idle", 0, yaw=-60, pitch=8,
                       pose={"right_arm": {"rot": (-1.2, 0, 0)}}, hidden=("fx_bspear_right", "fx_hammer_right", "form_horns"),
                       show_head=True, scale=7, center=(0, 1.2)),
    ]
    return preview.contact_sheet(shots, preview_path("blood_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
