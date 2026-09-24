"""
Sword Man (Longsword Hybrid, Miri Sugo) - devil parts model, texture atlas and GeckoLib animations.

Reference points:
  * trigger: he pulls off his RIGHT hand, baring the blade inside the arm
  * head: a pointed, angular metal visor in place of a head; two longswords jut rearward like a rabbit's ears / horns;
    a pointy chin and sharp, ragged teeth; dark skin
  * more blades erupt from the arms; during his Public Safety days the arms bore cross-guards at the elbows
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
from blades import longsword_blade, crossguard


def materials():
    a = Atlas(512, 64)
    a.add("visor", kind="metal", color=(122, 128, 142), scratches=6)
    a.add("visor_dk", kind="metal", color=(66, 70, 82), scratches=4)
    a.add("slit", kind="void", color=(10, 10, 14))
    a.add("skin", kind="skin", color=(92, 64, 56))
    a.add("skin_dk", kind="skin", color=(66, 44, 40))
    a.add("teeth", kind="teeth", color=(230, 224, 206))
    a.add("mouth", kind="void", color=(30, 8, 10))
    a.add("steel", kind="metal", color=(196, 200, 210), scratches=8)
    a.add("edge", kind="metal", color=(236, 238, 244), scratches=3)
    a.add("fuller", kind="metal", color=(150, 156, 168), scratches=3)
    a.add("guard", kind="metal", color=(90, 92, 104), scratches=4)
    a.add("grip", kind="fiber", color=(52, 36, 30))
    a.add("flesh", kind="flesh", color=(150, 40, 40))
    a.add("blood", kind="blood", color=(126, 8, 12))
    return a


# ------------------------------------------------------------------------------------------ head
def build_head(m):
    m.bone("head", pivot=(0, 24, 0))
    f = m.bone("form_head", parent="head", pivot=(0, 24, 0))
    # dark neck and the lower face: a pointy chin and a ragged grin
    f.cylinder((0, 24.6, 0.3), (0, 1, 0), 2.4, 1.6, "skin_dk", segments=10)
    jaw = shapes.ellipsoid((0, 26.5, -0.4), (4.0, 2.0, 3.85), e_lat=0.8, e_lon=0.8)
    shapes.shell(f, jaw, 12, 8, "skin", thick=0.4)
    shapes.horn(f, (0, 25.4, -2.9), (0, -0.75, -0.66), 2.1, 1.3, mat="skin", sections=4, around=6, r1=0.2)
    f.box((-3.0, 25.6, -4.35), (3.0, 27.5, -3.9), "mouth")
    for k in range(9):
        x = -2.7 + k * 0.68
        f.spike((x, 27.5, -4.25), (0.15 * math.sin(k * 2.3), -1, -0.1), 1.3 + 0.4 * (k % 2), 0.55, 0.3, "teeth", steps=2,
                up=(0, 0, -1))
        f.spike((x + 0.3, 25.6, -4.25), (0.15 * math.cos(k * 1.9), 1, -0.1), 0.9 + 0.4 * ((k + 1) % 2), 0.5, 0.3, "teeth",
                steps=2, up=(0, 0, -1))
    # the pointed, angular metal visor that stands in place of the head: a squared-off helm and a faceted prow that
    # comes to a point well in front of the face
    v = m.bone("form_visor", parent="form_head", pivot=(0, 28, 0))
    helm = shapes.ellipsoid((0, 30.0, 0.4), (4.55, 4.4, 4.75), e_lat=0.55, e_lon=0.6)
    shapes.shell(v, helm, 16, 10, "visor", v0=0.38, thick=0.45,
                 mat_fn=lambda u, v_: "visor_dk" if 0.46 < v_ < 0.52 else "visor")
    prow = shapes.loft(shapes.polyline([(0, 30.3, -1.5), (0, 30.5, -5.0), (0, 30.8, -9.6)]),
                       shapes.profile((0, 4.2), (0.35, 3.6), (0.8, 1.2), (1, 0.12)),
                       shapes.profile((0, 2.9), (0.35, 2.5), (0.8, 0.9), (1, 0.12)), up=(0, 1, 0), twist=0.0)
    shapes.shell(v, prow, 6, 18, "visor", thick=0.4, overlap=1.04,
                 mat_fn=lambda u, v_: "visor_dk" if 0.3 < u < 0.7 else "visor")
    # a raised ridge along the top of the prow
    ridge = [np.asarray(prow(0.0, t)) + np.array([0, 0.25, 0]) for t in np.linspace(0.0, 0.97, 8)]
    v.curve(ridge, 0.7, 0.3, 0.6, 0.3, "visor_dk")
    # slanted eye slits cut into the prow's flanks, and rivets round the helm
    for sx in (-1, 1):
        a = np.asarray(prow(0.25 * sx % 1.0, 0.18))
        b = np.asarray(prow(0.25 * sx % 1.0, 0.42))
        p, n, du, dv = shapes.surface_frame(prow, 0.25 * sx % 1.0, 0.3)
        v.seg(a + n * 0.15 + np.array([0, 0.3, 0]), b + n * 0.15 - np.array([0, 0.2, 0]), 0.45, 0.4, "slit", up=n)
    for s_ in (-1, 1):
        for y in (28.6, 32.0):
            p, n, du, dv = shapes.surface_frame(helm, 0.18 * s_ % 1.0, 0.43 if y < 30 else 0.68)
            v.cbox(p + n * 0.1, (0.45, 0.45, 0.45), "guard")
    # two longswords jutting rearward like a rabbit's ears
    for s in (-1, 1):
        e = m.bone("form_ear_" + ("right" if s < 0 else "left"), parent="form_visor", pivot=(s * 2.4, 33.0, 1.2))
        base = np.array([s * 2.4, 33.0, 1.2])
        d = norm([s * 0.28, 0.62, 1.0])
        crossguard(e, base, np.cross(d, [1.0, 0, 0]) * s + np.array([s * 0.6, 0, 0]), 3.4, "guard", up=d)
        e.tube(base - d * 1.6, base, 0.45, "grip", segments=6)
        longsword_blade(e, base + d * 0.3, d, 17.0, (s * 1.0, 0, 0), width=2.2, thick=0.4)


# ------------------------------------------------------------------------------------------ arms
def arm_blade(m, bone_name, parent, side, blade_bone):
    sgn = -1 if side == "right" else 1

    def X(o):
        return sgn * o

    f = m.bone(bone_name, parent=parent, pivot=(X(6), 17, 0))
    # cross-guard at the elbow and a broad longsword sheathing the forearm, running on past the hand
    crossguard(f, (X(6), 17.6, 0), (0, 0, 1), 6.4, "guard", up=(sgn * 1.0, 0, 0))
    f.cylinder((X(6), 17.6, 0), (0, 1, 0), 2.55, 0.9, "guard", segments=8)
    f.box((X(3.7), 11.3, -2.3), (X(8.3), 17.1, 2.3), "skin_dk")   # the flesh the blade tore out of
    f.box((X(3.6), 11.0, -2.4), (X(8.4), 11.5, 2.4), "blood")
    b = m.bone(blade_bone, parent=bone_name, pivot=(X(6), 17, 0))
    longsword_blade(b, (X(6), 17.4, -2.35), (0, -1, 0), 22.0, (0, 0, -1), width=3.2, thick=0.55)
    return f


def build_arms(m):
    for side in ("right", "left"):
        sgn = -1 if side == "right" else 1
        m.bone(side + "_arm", pivot=(sgn * 5, 22, 0))
        arm_blade(m, "form_%s_arm" % side, side + "_arm", side, "%s_sword" % side)


def build_trigger(m):
    """The severed right hand held in the left fist; the right arm's blade sliding out."""
    h = m.bone("trig_right_hand", parent="left_arm", pivot=(6, 11.4, -0.4))
    h.box((4.0, 7.6, -2.0), (8.0, 11.6, 1.0), "skin")
    for k in range(4):
        h.box((4.1 + k * 1.0, 6.2, -1.8), (4.9 + k * 1.0, 7.7, -0.6), "skin")
    h.box((3.95, 11.5, -2.05), (8.05, 12.1, 1.05), "blood")
    arm_blade(m, "trig_right_stump", "right_arm", "right", "trig_right_blade")


def build():
    atlas = materials()
    m = Model("csm.longsword_hybrid", atlas, density=2.0, seed=73)
    build_head(m)
    m.bone("body", pivot=(0, 24, 0))
    build_arms(m)
    build_trigger(m)
    geo = out("geo", "hybrid", "longsword.geo.json")
    tex = out("textures", "hybrid", "longsword.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "longsword_glowmask.png"), seed=41)
    anims = animations()
    anim_path = out("animations", "hybrid", "longsword.animation.json")
    save_animations(anim_path, anims)
    print("longsword: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    SW = ("right_sword", "left_sword")
    EARS = ("form_ear_right", "form_ear_left")
    e = Anim("emerge", 0.8)
    e.scale("form_head", 0, (0.8, 0.5, 0.8)).scale("form_head", 0.14, (1.06, 1.1, 1.06), "easeOutBack")
    e.scale("form_head", 0.28, 1.0)
    for i, ear in enumerate(EARS):
        e.scale(ear, 0, 0.02).scale(ear, 0.12 + 0.05 * i, 0.02).scale(ear, 0.32 + 0.05 * i, 1.12, "easeOutBack")
        e.scale(ear, 0.45, 1.0)
    for i, sw in enumerate(SW):
        o = 0.05 * i
        e.scale(sw, 0, (1, 0.02, 1)).scale(sw, 0.06 + o, (1, 0.02, 1)).scale(sw, 0.28 + o, (1, 1.1, 1), "easeOutBack")
        e.scale(sw, 0.4 + o, 1.0)
    A.append(e)

    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    for sw in SW:
        r.scale(sw, 0, 1).scale(sw, 0.25, (1, 0.02, 1), "easeInBack")
    for ear in EARS:
        r.scale(ear, 0, 1).scale(ear, 0.25, 0.02, "easeInBack")
    r.scale("form_head", 0.1, 1).scale("form_head", 0.4, (0.8, 0.5, 0.8), "easeInQuad")
    A.append(r)

    idle = Anim("idle", 3.0, loop=True)
    for s, ear in ((-1, "form_ear_right"), (1, "form_ear_left")):
        idle.rot(ear, 0, (0, 0, 0)).rot(ear, 1.5, (-3, 0, s * 2), "easeInOutSine").rot(ear, 3.0, (0, 0, 0), "easeInOutSine")
    A.append(idle)

    def ring(anim, t0):
        for sw in SW:
            anim.scale(sw, t0 - 0.02, 1).scale(sw, t0 + 0.03, (1.12, 1.04, 1.12)).scale(sw, t0 + 0.15, 1.0)

    cl = Anim("cleave", 0.8)
    ring(cl, 0.4)
    for ear in EARS:
        cl.rot(ear, 0, (0, 0, 0)).rot(ear, 0.35, (12, 0, 0), "easeInQuad").rot(ear, 0.42, (-10, 0, 0)).rot(ear, 0.8, (0, 0, 0))
    A.append(cl)
    wh = Anim("whirl", 1.2)
    for k in range(5):
        ring(wh, 0.2 + k * 0.2)
    A.append(wh)
    lu = Anim("lunge", 0.7)
    ring(lu, 0.15)
    A.append(lu)
    gu = Anim("guard", 2.0)
    for ear in EARS:
        gu.rot(ear, 0, (0, 0, 0)).rot(ear, 0.2, (15, 0, 0)).rot(ear, 1.8, (15, 0, 0)).rot(ear, 2.0, (0, 0, 0))
    A.append(gu)
    dr = Anim("drink", 1.0)
    for ear in EARS:
        dr.rot(ear, 0, (0, 0, 0)).rot(ear, 0.4, (-8, 0, 0)).rot(ear, 1.0, (0, 0, 0))
    A.append(dr)

    ph = Anim("pull_hand", 1.2)
    ph.scale("trig_right_hand", 0, 0).scale("trig_right_hand", 0.29, 0).scale("trig_right_hand", 0.3, 1)
    ph.scale("trig_right_hand", 0.95, 1).scale("trig_right_hand", 1.05, 0)
    ph.pos("trig_right_hand", 0.8, (0, 0, 0)).pos("trig_right_hand", 1.0, (0, -6, 0), "easeInQuad")
    ph.scale("trig_right_stump", 0, 0).scale("trig_right_stump", 0.29, 0).scale("trig_right_stump", 0.3, 1)
    ph.scale("trig_right_stump", 0.6, 1).scale("trig_right_stump", 0.61, 0)
    ph.scale("trig_right_blade", 0, (1, 0.05, 1)).scale("trig_right_blade", 0.32, (1, 0.05, 1))
    ph.scale("trig_right_blade", 0.58, (1, 1.0, 1), "easeOutQuad")
    A.append(ph)
    return A


def render_previews(geo, tex, anim):
    hide = ("trig_right_hand", "trig_right_stump")
    arms = {"right_arm": {"rot": (0, 0, 0.1)}, "left_arm": {"rot": (0, 0, -0.1)}}
    shots = [
        preview.render(geo, tex, preview_path("longsword_front.png"), anim, "idle", 0, yaw=25, pitch=6, pose=arms,
                       hidden=hide, scale=9.5, center=(0, 1.3)),
        preview.render(geo, tex, preview_path("longsword_head.png"), anim, "idle", 0, yaw=60, pitch=8, show_body=False,
                       scale=16, center=(0, 2.1), size=(640, 520), hidden=hide + ("body", "right_arm", "left_arm")),
        preview.render(geo, tex, preview_path("longsword_guard.png"), anim, "idle", 0, yaw=-50, pitch=8,
                       pose={"right_arm": {"rot": (-1.6, 0.7, 0)}, "left_arm": {"rot": (-1.6, -0.7, 0)}},
                       hidden=hide, scale=8.5, center=(0, 1.2)),
        preview.render(geo, tex, preview_path("longsword_front2.png"), anim, "idle", 0, yaw=0, pitch=4, pose=arms,
                       hidden=hide, scale=16, center=(0, 1.7), size=(640, 520)),
    ]
    return preview.contact_sheet(shots, preview_path("longsword_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
