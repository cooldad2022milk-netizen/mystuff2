"""
Katana Man (Katana Hybrid) - devil parts model, texture atlas and GeckoLib animations.

Reference points:
  * trigger: he pulls off his LEFT hand and a katana rises out of the open stump (sliding it back in reverts him and
    leaves him briefly unable to fight)
  * head: opens into a fanged, lipless maw set in raw, skinless flesh with a jutting jaw
  * a gakuran (student) cap with an ornament crowns him
  * a katana blade runs clean through his skull, its grip sticking out behind
  * full-length katana blades push out of both arms
  * technique: the Sword-Draw Dash (iaijutsu)
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
from blades import katana_blade, tsuba, tsuka


def materials():
    a = Atlas(512, 64)
    a.add("flesh", kind="flesh", color=(176, 58, 58))
    a.add("flesh_dk", kind="flesh", color=(120, 30, 34))
    a.add("sinew", kind="fiber", color=(210, 120, 110))
    a.add("teeth", kind="teeth", color=(238, 232, 214))
    a.add("mouth", kind="void", color=(34, 6, 8))
    a.add("eye", kind="bone", color=(236, 230, 214))
    a.add("pupil", kind="void", color=(16, 10, 10))
    a.add("cap", kind="rubber", color=(22, 22, 26))
    a.add("cap_band", kind="rubber", color=(40, 40, 46))
    a.add("gold", kind="metal", color=(212, 170, 70), scratches=2)
    a.add("steel", kind="metal", color=(206, 210, 218), scratches=6)
    a.add("edge", kind="metal", color=(242, 244, 248), scratches=3)
    a.add("hamon", kind="metal", color=(228, 230, 236), scratches=2)
    a.add("iron", kind="metal", color=(52, 52, 58), scratches=4)
    a.add("same", kind="skin", color=(236, 230, 214))
    a.add("wrap", kind="fiber", color=(28, 26, 44))
    a.add("skin", kind="skin", color=(214, 172, 146))
    a.add("blood", kind="blood", color=(126, 8, 12))
    return a


# ------------------------------------------------------------------------------------------ head
def build_head(m):
    m.bone("head", pivot=(0, 24, 0))
    f = m.bone("form_head", parent="head", pivot=(0, 24, 0))
    # raw, skinless head: a rounded skull of exposed muscle
    skull = shapes.ellipsoid((0, 28.7, 0.3), (4.2, 4.5, 4.35), e_lat=0.8, e_lon=0.8)
    shapes.shell(f, skull, 14, 12, "flesh", v0=0.22, thick=0.45)
    # cheek muscles bunching over the jaw hinge
    for sd in (-1, 1):
        shapes.shell(f, shapes.ellipsoid((sd * 3.4, 26.4, -0.6), (1.3, 2.2, 2.2), e_lat=0.9, e_lon=0.9), 8, 6,
                     "flesh_dk", thick=0.35)
    # muscle striations running up the face and over the crown
    for k in range(13):
        u = -0.2 + 0.4 * k / 12
        pts = []
        for i in range(6):
            p, n, du, dv = shapes.surface_frame(skull, u, 0.4 + 0.1 * i)
            pts.append(p + n * 0.12)
        f.curve(pts, 0.42, 0.25, 0.28, 0.18, "sinew")
    # the lipless maw: a dark cavity and a row of long upper fangs hanging over it
    shapes.shell(f, shapes.ellipsoid((0, 25.9, -2.4), (3.3, 1.5, 2.3)), 10, 6, "mouth", thick=0.3)
    for k in range(10):
        ph = math.radians(-78 + 156 * (k + 0.5) / 10)
        p = np.array([3.2 * math.sin(ph), 27.1, -1.2 - 3.35 * math.cos(ph)])
        out_dir = np.array([math.sin(ph), 0, -math.cos(ph)])
        f.spike(p, norm(np.array([0, -1, 0]) + out_dir * 0.15), 1.7 - 0.5 * abs(math.sin(ph)), 0.55, 0.32, "teeth",
                steps=3, up=out_dir)
    # a jutting lower jaw with its own fangs
    j = m.bone("jaw", parent="form_head", pivot=(0, 25.6, 1.0))
    jaw = shapes.loft(shapes.polyline([(0, 25.0, 2.4), (0, 24.6, -2.0), (0, 24.3, -5.2), (0, 24.6, -6.6)]),
                      shapes.profile((0, 3.3), (0.45, 3.5), (0.8, 3.0), (1, 1.4)),
                      shapes.profile((0, 1.4), (0.5, 1.3), (0.85, 1.2), (1, 0.6)), up=(0, 1, 0))
    shapes.shell(j, jaw, 12, 10, "flesh_dk", thick=0.4)
    for k in range(9):
        ph = math.radians(-74 + 148 * (k + 0.5) / 9)
        p = np.array([2.9 * math.sin(ph), 25.85, -2.2 - 3.9 * math.cos(ph)])
        out_dir = np.array([math.sin(ph), 0, -math.cos(ph)])
        j.spike(p, norm(np.array([0, 1, 0]) + out_dir * 0.2), 1.8 - 0.5 * abs(math.sin(ph)), 0.55, 0.32, "teeth",
                steps=3, up=out_dir)
    # bulging lidless eyes
    for sd in (-1, 1):
        c = np.array([sd * 1.95, 29.5, -3.7])
        shapes.shell(f, shapes.ellipsoid(c, (1.25, 1.2, 1.1)), 10, 6, "eye", thick=0.3)
        f.cylinder(c + np.array([0, 0, -1.05]), (0, 0, -1), 0.45, 0.12, "pupil", segments=8)
    # gakuran cap with its badge
    c = m.bone("form_cap", parent="form_head", pivot=(0, 32.6, 0.2))
    c.cylinder((0, 33.5, 0.2), (0, 1, 0), 4.55, 2.0, "cap", segments=14)
    c.cylinder((0, 34.6, 0.3), (0, 1, 0), 4.75, 0.35, "cap", segments=14)
    c.cylinder((0, 32.85, 0.2), (0, 1, 0), 4.6, 0.7, "cap_band", segments=14)
    c.obox((0, 32.55, -5.3), (0, 0, -1), (6.4, 2.6, 0.22), "cap", up=(0, 1, -0.35))
    c.cylinder((0, 33.6, -4.35), (0, 0, -1), 0.8, 0.2, "gold", segments=8)
    c.cbox((0, 33.6, -4.5), (0.5, 0.5, 0.15), "gold")
    # a katana run clean through the skull: grip out the back, blade out through the forehead
    k = m.bone("form_skull_blade", parent="form_head", pivot=(0, 30.0, 0))
    tsuka(k, (0, 30.2, 5.0), (0, 30.6, 10.4), radius=0.55)
    tsuba(k, (0, 30.15, 4.7), (0, 0, 1), 1.5)
    katana_blade(k, (0, 30.1, 4.5), (0, 0.06, -1), 18.0, (0, 1, 0), width=1.3, thick=0.35, curve=0.06)
    k.cbox((0, 30.1, -4.3), (1.8, 1.6, 0.4), "blood")
    k.cbox((0, 30.2, 4.3), (1.6, 1.5, 0.4), "blood")


# ------------------------------------------------------------------------------------------ arms
def stump_with_blade(m, bone_name, parent, side, blade_len=12.5, blade_bone=None):
    """Raw stump where the hand was, a tsuba at the wrist and a katana running on from it."""
    sgn = -1 if side == "right" else 1

    def X(o):
        return sgn * o

    f = m.bone(bone_name, parent=parent, pivot=(X(6), 12, 0))
    for y0, y1, r, mat in ((13.8, 15.4, 2.95, "flesh_dk"), (11.6, 13.9, 2.9, "flesh"), (11.0, 11.7, 2.3, "blood")):
        f.cylinder((X(6), (y0 + y1) / 2, 0), (0, 1, 0), r, y1 - y0, mat, segments=10)
    for kk in range(6):
        a = math.radians(kk * 60 + 30)
        rr = np.array([math.sin(a), 0, -math.cos(a)])
        f.curve([np.array([X(6), 15.2 - 1.1 * i, 0]) + rr * 3.0 for i in range(4)], 0.4, 0.3, 0.35, 0.25, "sinew")
    b = m.bone(blade_bone or (bone_name + "_blade"), parent=bone_name, pivot=(X(6), 11.0, 0))
    tsuba(b, (X(6), 10.8, 0), (0, 1, 0), 1.9, up=(0, 0, -1))
    b.cylinder((X(6), 10.3, 0), (0, 1, 0), 0.7, 0.8, "gold", segments=6)
    katana_blade(b, (X(6), 10.0, 0), (0, -1, 0), blade_len, (0, 0, -1), width=1.4, thick=0.38, curve=0.07)
    return f


def build_arms(m):
    for side in ("right", "left"):
        sgn = -1 if side == "right" else 1
        m.bone(side + "_arm", pivot=(sgn * 5, 22, 0))
        stump_with_blade(m, "form_%s_arm" % side, side + "_arm", side, blade_bone="%s_katana" % side)


def build_trigger(m):
    """The severed left hand held in the right fist, and the left stump with a katana rising out of it."""
    h = m.bone("trig_left_hand", parent="right_arm", pivot=(-6, 11.4, -0.4))
    h.box((-8.0, 7.6, -2.0), (-4.0, 11.6, 1.0), "skin")          # palm/back of the hand
    for k in range(4):
        h.box((-7.9 + k * 1.0, 6.2, -1.8), (-7.1 + k * 1.0, 7.7, -0.6), "skin")  # fingers
    h.box((-8.05, 11.5, -2.05), (-3.95, 12.1, 1.05), "blood")     # torn wrist
    h.cbox((-6, 12.3, -0.5), (2.2, 0.5, 1.8), "flesh")
    stump_with_blade(m, "trig_left_stump", "left_arm", "left", blade_len=12.5, blade_bone="trig_left_blade")


def build():
    atlas = materials()
    m = Model("csm.katana_hybrid", atlas, density=2.0, seed=71)
    build_head(m)
    m.bone("body", pivot=(0, 24, 0))
    build_arms(m)
    build_trigger(m)
    geo = out("geo", "hybrid", "katana.geo.json")
    tex = out("textures", "hybrid", "katana.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "katana_glowmask.png"), seed=37)
    anims = animations()
    anim_path = out("animations", "hybrid", "katana.animation.json")
    save_animations(anim_path, anims)
    print("katana: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    KAT = ("right_katana", "left_katana")
    e = Anim("emerge", 0.8)
    e.scale("form_head", 0, (0.7, 0.4, 0.7)).scale("form_head", 0.14, (1.08, 1.12, 1.08), "easeOutBack")
    e.scale("form_head", 0.3, 1.0)
    e.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.2, (28, 0, 0), "easeOutQuad").rot("jaw", 0.55, (20, 0, 0))
    e.rot("jaw", 0.8, (0, 0, 0), "easeInOutSine")
    e.pos("form_cap", 0, (0, 4, 0)).pos("form_cap", 0.2, (0, 4, 0)).pos("form_cap", 0.4, (0, 0, 0), "easeOutBounce")
    e.scale("form_skull_blade", 0, (1, 1, 0.02)).scale("form_skull_blade", 0.1, (1, 1, 0.02))
    e.scale("form_skull_blade", 0.28, (1, 1, 1.12), "easeOutBack").scale("form_skull_blade", 0.4, 1.0)
    for i, kb in enumerate(KAT):
        o = 0.05 * i
        e.scale(kb, 0, (1, 0.02, 1)).scale(kb, 0.06 + o, (1, 0.02, 1)).scale(kb, 0.26 + o, (1, 1.12, 1), "easeOutBack")
        e.scale(kb, 0.38 + o, 1.0)
    A.append(e)

    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    for kb in KAT + ("form_skull_blade",):
        r.scale(kb, 0, 1).scale(kb, 0.25, (1, 0.02, 1) if kb != "form_skull_blade" else (1, 1, 0.02), "easeInBack")
    r.scale("form_head", 0.1, 1).scale("form_head", 0.4, (0.7, 0.4, 0.7), "easeInQuad")
    A.append(r)

    idle = Anim("idle", 2.4, loop=True)
    for t, a in ((0, 0), (0.15, 4), (0.3, 0), (1.4, 0), (1.5, 3), (1.62, 0), (2.4, 0)):
        idle.rot("jaw", t, (a, 0, 0))
    A.append(idle)

    def glint(anim, t0):
        for kb in KAT:
            anim.scale(kb, t0 - 0.02, 1).scale(kb, t0 + 0.03, (1.15, 1.05, 1.15)).scale(kb, t0 + 0.15, 1.0)

    iai = Anim("iai", 1.4)
    iai.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.4, (6, 0, 0)).rot("jaw", 0.46, (30, 0, 0), "easeOutQuad")
    iai.rot("jaw", 1.1, (0, 0, 0))
    glint(iai, 0.45)
    glint(iai, 0.95)
    A.append(iai)
    tw = Anim("twin", 0.7)
    glint(tw, 0.25)
    A.append(tw)
    fl = Anim("flurry", 1.1)
    for k in range(6):
        glint(fl, 0.15 + k * 0.15)
    A.append(fl)
    st = Anim("stance", 1.5)
    st.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.2, (-4, 0, 0)).rot("jaw", 1.3, (-4, 0, 0)).rot("jaw", 1.5, (0, 0, 0))
    A.append(st)
    dr = Anim("drink", 1.0)
    dr.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.35, (30, 0, 0), "easeOutQuad").rot("jaw", 0.75, (30, 0, 0))
    dr.rot("jaw", 1.0, (0, 0, 0))
    A.append(dr)

    # trigger: at 0.3 s the left hand comes off in the right fist; the katana rises out of the stump
    ph = Anim("pull_hand", 1.2)
    ph.scale("trig_left_hand", 0, 0).scale("trig_left_hand", 0.29, 0).scale("trig_left_hand", 0.3, 1)
    ph.scale("trig_left_hand", 0.95, 1).scale("trig_left_hand", 1.05, 0)
    ph.pos("trig_left_hand", 0.8, (0, 0, 0)).pos("trig_left_hand", 1.0, (0, -6, 0), "easeInQuad")
    ph.scale("trig_left_stump", 0, 0).scale("trig_left_stump", 0.29, 0).scale("trig_left_stump", 0.3, 1)
    ph.scale("trig_left_stump", 0.6, 1).scale("trig_left_stump", 0.61, 0)
    ph.scale("trig_left_blade", 0, (1, 0.05, 1)).scale("trig_left_blade", 0.32, (1, 0.05, 1))
    ph.scale("trig_left_blade", 0.58, (1, 1.0, 1), "easeOutQuad")
    A.append(ph)
    return A


def render_previews(geo, tex, anim):
    hide = ("trig_left_hand", "trig_left_stump")
    arms = {"right_arm": {"rot": (0, 0, 0.1)}, "left_arm": {"rot": (0, 0, -0.1)}}
    shots = [
        preview.render(geo, tex, preview_path("katana_front.png"), anim, "idle", 0, yaw=25, pitch=6, pose=arms,
                       hidden=hide, scale=10, center=(0, 1.2)),
        preview.render(geo, tex, preview_path("katana_head.png"), anim, "idle", 0, yaw=55, pitch=8, show_body=False,
                       scale=18, center=(0, 1.9), size=(640, 520), hidden=hide + ("body", "right_arm", "left_arm")),
        preview.render(geo, tex, preview_path("katana_iai.png"), anim, "idle", 0, yaw=-60, pitch=8,
                       pose={"right_arm": {"rot": (-1.4, 0.3, 0)}, "left_arm": {"rot": (-1.2, -0.3, 0)}},
                       hidden=hide, scale=8.5, center=(0, 1.2)),
        preview.render(geo, tex, preview_path("katana_trigger.png"), anim, "pull_hand", 0.45, yaw=30, pitch=6,
                       pose={"right_arm": {"rot": (-0.9, 0.6, 0.4)}, "left_arm": {"rot": (-0.8, -0.4, -0.2)}},
                       hidden=("form_head", "form_right_arm", "form_left_arm"), show_head=True, scale=14,
                       center=(0, 1.3)),
    ]
    return preview.contact_sheet(shots, preview_path("katana_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
