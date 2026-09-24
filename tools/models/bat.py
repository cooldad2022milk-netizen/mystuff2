"""
The Bat Devil - entity model (entity/devil/bat), texture atlas and GeckoLib animations. A player who becomes the Bat
Devil wears this same model (scaled down).

Reference points:
  * a hulking, man-shaped bat: broad furry body on short clawed legs, arms that are membrane wings
  * a big head with huge pointed ears, bulging eyes and a squashed snout; rows of fangs
  * purple in the coloured manga (grey in the anime)
  * drinks blood to heal, flies, and reshapes its maw into a gun barrel to fire a blast of compressed air
"""
import math

import numpy as np

from common import preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk


def materials():
    a = Atlas(512, 64)
    a.add("fur", kind="fiber", color=(112, 80, 142))
    a.add("fur_dk", kind="fiber", color=(78, 54, 102))
    a.add("belly", kind="fiber", color=(146, 112, 170))
    a.add("skin", kind="skin", color=(96, 66, 112))
    a.add("wing", kind="skin", color=(72, 46, 90))
    a.add("wing_vein", kind="skin", color=(54, 32, 70))
    a.add("ear_in", kind="flesh", color=(176, 110, 150))
    a.add("eye", kind="gloss", color=(40, 8, 12))
    a.add("eye_glow", kind="glow", color=(220, 30, 40), color2=(255, 170, 120), emissive=True)
    a.add("teeth", kind="teeth", color=(240, 236, 224))
    a.add("mouth", kind="void", color=(60, 12, 24))
    a.add("gum", kind="flesh", color=(170, 64, 90))
    a.add("nose", kind="skin", color=(60, 38, 70))
    a.add("claw", kind="bone", color=(40, 34, 40))
    a.add("barrel", kind="flesh", color=(150, 70, 100))
    a.add("air", kind="glow", color=(200, 220, 255), color2=(255, 255, 255), emissive=True)
    return a


# ------------------------------------------------------------------------------------------ body
def body(m):
    root = m.bone("root", pivot=(0, 0, 0))
    b = m.bone("body", parent="root", pivot=(0, 17, 1))
    # a broad furry trunk, hunched forward, pale belly
    trunk = shapes.loft(shapes.polyline([(0, 14.5, 1.8), (0, 21.0, 0.8), (0, 27.0, -0.2), (0, 31.5, 1.0)]),
                        shapes.profile((0, 4.6), (0.3, 5.8), (0.62, 6.6), (0.85, 6.0), (1, 4.2)),
                        shapes.profile((0, 3.4), (0.3, 4.0), (0.62, 4.4), (0.85, 4.0), (1, 3.0)), up=(0, 0, -1))
    shapes.shell(b, trunk, 16, 12, "fur", thick=0.45,
                 mat_fn=lambda u, v: "belly" if (u < 0.17 or u > 0.83) and 0.15 < v < 0.8 else "fur")
    # a ruff of fur round the shoulders
    for k in range(18):
        a = math.radians(-120 + k * 240 / 17)
        p = np.array([math.sin(a) * 5.8, 30.5, 1.0 - math.cos(a) * 3.8])
        d = norm([math.sin(a), 0.5, -math.cos(a) * 0.6])
        shapes.horn(b, p, d, 2.4, 0.9, mat="fur_dk", sections=3, around=5, r1=0.1, thick=0.3)
    return root, b


def head(m):
    h = m.bone("head", parent="body", pivot=(0, 31.5, 0))
    look = m.bone("look", parent="head", pivot=(0, 32, 0))
    skull = shapes.ellipsoid((0, 35.2, -1.8), (4.7, 4.3, 4.4), e_lat=0.85, e_lon=0.85)
    shapes.shell(look, skull, 16, 10, "fur", thick=0.45)
    # squashed snout with a nose leaf and nostrils
    snout = shapes.ellipsoid((0, 33.6, -5.6), (2.6, 1.9, 2.0), e_lat=0.8, e_lon=0.8)
    shapes.shell(look, snout, 12, 8, "skin", thick=0.4)
    shapes.horn(look, (0, 34.6, -7.2), (0, 1, -0.35), 2.4, 1.1, mat="nose", flat=0.3, up=(0, 0, -1), sections=4,
                around=6, r1=0.2)
    for s in (-1, 1):
        look.cylinder((s * 0.75, 34.0, -7.5), (0, -0.2, -1), 0.35, 0.3, "mouth", segments=6)
    # bulging eyes
    for s in (-1, 1):
        c = np.array([s * 2.3, 36.6, -5.2])
        shapes.shell(look, shapes.ellipsoid(c, (1.35, 1.3, 1.2)), 10, 6, "eye", thick=0.3)
        look.cbox(c + np.array([s * 0.1, 0.35, -1.15]), (0.55, 0.55, 0.2), "eye_glow")
    # huge pointed ears (pink inside)
    for s in (-1, 1):
        root = np.array([s * 3.0, 38.4, -0.6])
        d = norm([s * 0.55, 1, 0.15])
        shapes.horn(look, root, d, 8.0, 2.6, mat="fur_dk", flat=0.28, up=(0, 0, 1), sections=6, around=8, r1=0.2,
                    bend_axis=(0, 0, 1), bend=-s * 12)
        shapes.horn(look, root + np.array([0, 0.3, -0.35]), d, 6.8, 2.0, mat="ear_in", flat=0.2, up=(0, 0, 1),
                    sections=5, around=8, r1=0.2, bend_axis=(0, 0, 1), bend=-s * 12)
    # upper fangs along the lip line
    for k in range(9):
        ph = math.radians(-70 + 140 * (k + 0.5) / 9)
        p = np.array([2.2 * math.sin(ph), 32.2, -5.0 - 2.0 * math.cos(ph)])
        o = np.array([math.sin(ph), 0, -math.cos(ph)])
        look.spike(p, norm(np.array([0, -1, 0]) + o * 0.15), 1.4 if k in (1, 7) else 0.9, 0.45, 0.28, "teeth", steps=3,
                   up=o)
    look.box((-2.1, 31.6, -6.6), (2.1, 32.4, -4.0), "mouth")
    # the lower jaw
    jaw = m.bone("jaw", parent="look", pivot=(0, 32.0, -2.0))
    jl = shapes.loft(shapes.polyline([(0, 31.4, -1.6), (0, 31.0, -4.4), (0, 31.3, -6.4)]),
                     shapes.profile((0, 3.2), (0.6, 2.6), (1, 1.2)), shapes.profile((0, 1.0), (1, 0.6)), up=(0, 1, 0))
    shapes.shell(jaw, jl, 12, 6, "fur_dk", thick=0.35)
    jaw.box((-1.9, 31.7, -6.2), (1.9, 32.0, -2.4), "gum")
    for k in range(8):
        ph = math.radians(-66 + 132 * (k + 0.5) / 8)
        p = np.array([1.9 * math.sin(ph), 31.9, -4.4 - 1.9 * math.cos(ph)])
        o = np.array([math.sin(ph), 0, -math.cos(ph)])
        jaw.spike(p, norm(np.array([0, 1, 0]) + o * 0.15), 1.2 if k in (0, 7) else 0.8, 0.42, 0.26, "teeth", steps=3,
                  up=o)
    # the maw reshaped into a gun barrel (air cannon)
    bl = m.bone("fx_blast_barrel", parent="look", pivot=(0, 32.2, -5.5))
    bl.cylinder((0, 32.2, -8.0), (0, 0, -1), 1.9, 5.0, "barrel", segments=12)
    bl.ring((0, 32.2, -10.4), (0, 0, -1), 1.95, 0.5, 0.6, "gum", count=14)
    bl.cylinder((0, 32.2, -10.5), (0, 0, -1), 1.3, 0.3, "mouth", segments=10)
    bl.cylinder((0, 32.2, -11.2), (0, 0, -1), 1.0, 1.2, "air", segments=10)


# ------------------------------------------------------------------------------------------ wings
FINGERS = [((27.0, 27.5, 6.0), 0.55), ((26.5, 19.0, 7.0), 0.5), ((22.0, 11.5, 6.0), 0.45), ((15.5, 8.5, 4.5), 0.42)]


def wing(m, side):
    s = -1 if side == "right" else 1

    def X(p):
        return np.array([s * p[0], p[1], p[2]])

    sh = X((6.0, 30.0, 1.0))
    el = X((11.5, 26.5, 3.0))
    wr = X((17.5, 30.5, 5.0))
    w = m.bone(side + "_wing", parent="body", pivot=tuple(sh))
    fa = m.bone(side + "_forearm", parent=side + "_wing", pivot=tuple(el))
    hd = m.bone(side + "_hand", parent=side + "_forearm", pivot=tuple(wr))
    # muscular upper arm and forearm (furred near the body)
    shapes.shell(w, shapes.loft(shapes.polyline([sh, el]), shapes.profile((0, 2.2), (1, 1.4)), shapes.profile((0, 2.0),
                 (1, 1.3))), 8, 5, "fur", thick=0.35)
    shapes.shell(fa, shapes.loft(shapes.polyline([el, wr]), shapes.profile((0, 1.4), (1, 0.9)), 1.0), 8, 5, "skin",
                 thick=0.3)
    # thumb claw at the wrist
    shapes.horn(hd, wr, X((0.3, 1, -0.6)), 2.4, 0.5, mat="claw", sections=3, around=5, r1=0.06, bend_axis=(1, 0, 0),
                bend=-40)
    tips = []
    for tip, r in FINGERS:
        t = X(tip)
        mid = wr + (t - wr) * 0.45 + np.array([0, 1.2, 0.5])
        shapes.shell(hd, shapes.loft(shapes.polyline([wr, mid, t]), shapes.profile((0, r), (1, 0.12)), r * 0.8), 6, 6,
                     "skin", thick=0.25)
        tips.append((mid, t))
    # membranes: body side -> arm, and between the fingers (scalloped trailing edge)
    hip = X((5.0, 17.0, 1.8))
    shapes.membrane(w, [sh + X((0, -1, 0.2)), hip], [el, X((12.0, 18.0, 3.4))], 4, 6, "wing", sag=0.8,
                    sag_dir=(0, 0, 1))
    shapes.membrane(fa, [el, X((12.0, 18.0, 3.4))], [wr, tips[3][1]], 4, 6, "wing", sag=0.6)
    for k in range(len(tips) - 1):
        a_mid, a_tip = tips[k]
        b_mid, b_tip = tips[k + 1]
        trail = (a_tip + b_tip) / 2 + norm(((a_tip + b_tip) / 2) - wr) * -2.0
        shapes.membrane(hd, [wr, a_mid, a_tip], [wr, b_mid, trail * 0.4 + b_tip * 0.6], 3, 6,
                        "wing" if k % 2 == 0 else "wing_vein", sag=0.5)


# ------------------------------------------------------------------------------------------ legs
def leg(m, side):
    s = -1 if side == "right" else 1
    hip = np.array([s * 3.2, 17.0, 1.6])
    knee = np.array([s * 3.7, 10.0, -1.6])
    ankle = np.array([s * 3.5, 4.0, 2.4])
    foot = np.array([s * 3.5, 0.6, -1.0])
    l = m.bone(side + "_leg", parent="root", pivot=tuple(hip))
    sh = m.bone(side + "_shin", parent=side + "_leg", pivot=tuple(knee))
    shapes.shell(l, shapes.loft(shapes.polyline([hip, knee]), shapes.profile((0, 2.8), (0.5, 2.5), (1, 1.6)), 2.4),
                 8, 5, "fur", thick=0.35)
    shapes.shell(sh, shapes.loft(shapes.polyline([knee, ankle, foot]), shapes.profile((0, 1.5), (0.6, 0.9), (1, 1.2)),
                 1.2), 8, 6, "skin", thick=0.3)
    for k in range(3):
        d = norm([s * 0.3 * (k - 1), -0.25, -1])
        shapes.horn(sh, foot + np.array([s * 0.5 * (k - 1), 0, -0.5]), d, 2.2, 0.45, mat="claw", sections=3, around=5,
                    r1=0.05, bend_axis=(1, 0, 0), bend=40)


def build():
    atlas = materials()
    m = Model("csm.bat_devil", atlas, density=2.0, seed=151)
    body(m)
    head(m)
    for side in ("right", "left"):
        wing(m, side)
        leg(m, side)
    # a big head on the hulking body
    neck = (0, 31.5, 0)
    for name in ("look", "jaw", "fx_blast_barrel"):
        m.by_name[name].scale_about(neck, 1.2)
    geo, tex, glow, anim_path = dk.devil_paths("bat")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=157)
    anims = animations()
    save_animations(anim_path, anims)
    print("bat devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


# ------------------------------------------------------------------------------------------ animations
def flap(a, t0, period, cycles, amp=38.0, lift=1.0, fold=1.0):
    """Wing beats: the arms sweep up and down (right wing = -x: +z rolls it up), forearms and hands lag behind."""
    steps = int(cycles * 8)
    for i in range(steps + 1):
        t = t0 + period * i / 8
        ph = 2 * math.pi * i / 8
        up = math.sin(ph)
        for side, s in (("right", 1), ("left", -1)):
            a.rot(side + "_wing", t, (8 * math.cos(ph), 0, s * (amp * up + 5)))
            a.rot(side + "_forearm", t, (0, s * -12 * fold * max(0, -up), s * 14 * math.sin(ph - 0.7)))
            a.rot(side + "_hand", t, (0, s * -18 * fold * max(0, -up), s * 18 * math.sin(ph - 1.2)))
        a.pos("root", t, (0, lift * -math.sin(ph + 0.6), 0))


def animations():
    A = []
    idle = Anim("idle", 1.2, loop=True)
    flap(idle, 0, 1.2, 1, amp=30, lift=1.0)
    idle.rot("body", 0, (5, 0, 0)).rot("body", 1.2, (5, 0, 0))
    for side, s in (("right", 1), ("left", -1)):
        idle.rot(side + "_leg", 0, (18, 0, 0)).rot(side + "_leg", 1.2, (18, 0, 0))
    A.append(idle)
    mv = Anim("move", 0.7, loop=True)
    flap(mv, 0, 0.7, 1, amp=44, lift=1.6)
    mv.rot("body", 0, (22, 0, 0)).rot("body", 0.7, (22, 0, 0))
    mv.rot("head", 0, (-16, 0, 0)).rot("head", 0.7, (-16, 0, 0))
    for side in ("right", "left"):
        mv.rot(side + "_leg", 0, (45, 0, 0)).rot(side + "_leg", 0.7, (45, 0, 0))
        mv.rot(side + "_shin", 0, (20, 0, 0)).rot(side + "_shin", 0.7, (20, 0, 0))
    A.append(mv)

    bite = Anim("bite", 0.8)
    bite.rot("head", 0, (0, 0, 0)).rot("head", 0.2, (-18, 0, 0), "easeInQuad").rot("head", 0.35, (22, 0, 0), "easeOutQuad")
    bite.rot("head", 0.8, (0, 0, 0))
    bite.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.25, (40, 0, 0), "easeOutQuad").rot("jaw", 0.38, (0, 0, 0), "easeInQuad")
    bite.rot("jaw", 0.55, (15, 0, 0)).rot("jaw", 0.8, (0, 0, 0))
    bite.rot("body", 0, (0, 0, 0)).rot("body", 0.35, (25, 0, 0)).rot("body", 0.8, (0, 0, 0))
    A.append(bite)
    dr = Anim("drink", 1.0)
    dr.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.25, (30, 0, 0)).rot("jaw", 0.45, (5, 0, 0)).rot("jaw", 0.6, (25, 0, 0))
    dr.rot("jaw", 1.0, (0, 0, 0))
    dr.rot("head", 0.3, (20, 0, 0)).rot("head", 1.0, (0, 0, 0))
    A.append(dr)

    # Air cannon: the maw stretches into a barrel, a moment to build pressure, then the blast kicks the head back
    bl = Anim("blast", 1.2)
    bl.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.3, (48, 0, 0), "easeOutBack").rot("jaw", 0.9, (48, 0, 0))
    bl.rot("jaw", 1.2, (0, 0, 0))
    bl.scale("fx_blast_barrel", 0, (1, 1, 0.1)).scale("fx_blast_barrel", 0.35, (1.1, 1.1, 1.2), "easeOutBack")
    bl.scale("fx_blast_barrel", 0.6, (0.95, 0.95, 0.9)).scale("fx_blast_barrel", 0.7, (1.2, 1.2, 1.3), "easeOutQuad")
    bl.scale("fx_blast_barrel", 1.0, 1.0).scale("fx_blast_barrel", 1.2, (1, 1, 0.1))
    bl.rot("head", 0, (0, 0, 0)).rot("head", 0.6, (8, 0, 0)).rot("head", 0.7, (-22, 0, 0), "easeOutQuad")
    bl.rot("head", 1.2, (0, 0, 0))
    bl.rot("body", 0.6, (8, 0, 0)).rot("body", 0.72, (-10, 0, 0)).rot("body", 1.2, (0, 0, 0))
    for side, s in (("right", 1), ("left", -1)):
        bl.rot(side + "_wing", 0, (0, 0, s * 5)).rot(side + "_wing", 0.5, (0, s * 25, s * 20))
        bl.rot(side + "_wing", 0.72, (0, s * 35, s * 40), "easeOutQuad").rot(side + "_wing", 1.2, (0, 0, s * 5))
    A.append(bl)

    # Swoop: wings fold into a dive, the feet reach forward to grab, then heavy beats haul the prey up
    sw = Anim("swoop", 1.7)
    for side, s in (("right", 1), ("left", -1)):
        sw.rot(side + "_wing", 0, (0, 0, s * 5)).rot(side + "_wing", 0.3, (0, s * -40, s * -25), "easeInQuad")
        sw.rot(side + "_forearm", 0.3, (0, s * 60, 0)).rot(side + "_hand", 0.3, (0, s * 70, 0))
        sw.rot(side + "_wing", 0.5, (0, s * -40, s * -25)).rot(side + "_forearm", 0.5, (0, s * 60, 0))
        sw.rot(side + "_hand", 0.5, (0, s * 70, 0))
        sw.rot(side + "_forearm", 0.6, (0, 0, 0)).rot(side + "_hand", 0.6, (0, 0, 0))
        sw.rot(side + "_leg", 0.3, (40, 0, 0)).rot(side + "_leg", 0.5, (-55, 0, 0), "easeOutQuad")
        sw.rot(side + "_shin", 0.5, (-20, 0, 0)).rot(side + "_leg", 1.6, (-40, 0, 0)).rot(side + "_leg", 1.7, (0, 0, 0))
        sw.rot(side + "_shin", 1.7, (0, 0, 0))
    sw.rot("body", 0, (0, 0, 0)).rot("body", 0.3, (45, 0, 0)).rot("body", 0.55, (-15, 0, 0)).rot("body", 1.7, (0, 0, 0))
    flap(sw, 0.6, 0.35, 3, amp=50, lift=0.5)
    A.append(sw)

    # Screech: head thrown back, jaw wide, wings spread and trembling
    sc = Anim("screech", 1.0)
    sc.rot("head", 0, (0, 0, 0)).rot("head", 0.2, (-28, 0, 0), "easeOutQuad").rot("head", 0.8, (-24, 0, 0))
    sc.rot("head", 1.0, (0, 0, 0))
    sc.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.2, (55, 0, 0), "easeOutQuad").rot("jaw", 0.8, (50, 0, 0))
    sc.rot("jaw", 1.0, (0, 0, 0))
    for i in range(9):
        t = 0.2 + i * 0.075
        j = 4 if i % 2 else -4
        for side, s in (("right", 1), ("left", -1)):
            sc.rot(side + "_wing", t, (j, s * 20, s * (42 + j)))
            sc.rot(side + "_hand", t, (0, s * -10, s * 10))
    for side, s in (("right", 1), ("left", -1)):
        sc.rot(side + "_wing", 0, (0, 0, s * 5)).rot(side + "_wing", 1.0, (0, 0, s * 5))
        sc.rot(side + "_hand", 0, (0, 0, 0)).rot(side + "_hand", 1.0, (0, 0, 0))
    A.append(sc)

    death = Anim("death", 1.2, loop="hold_on_last_frame")
    for side, s in (("right", 1), ("left", -1)):
        death.rot(side + "_wing", 0, (0, 0, 0)).rot(side + "_wing", 0.5, (0, s * -50, s * -40), "easeInQuad")
        death.rot(side + "_forearm", 0.5, (0, s * 70, 0)).rot(side + "_hand", 0.5, (0, s * 80, 0))
    death.rot("root", 0, (0, 0, 0)).rot("root", 0.9, (0, 0, 88), "easeInQuad")
    death.pos("root", 0, (0, 0, 0)).pos("root", 0.9, (0, -4, 0), "easeInQuad")
    death.rot("jaw", 0.4, (30, 0, 0))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 0.7, from_scale=0.25))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("bat_front.png"), anim, "idle", 0.3, yaw=15, pitch=6, show_body=False,
                       scale=9, center=(0, 1.35), size=(620, 620)),
        preview.render(geo, tex, preview_path("bat_side.png"), anim, "idle", 0.3, yaw=100, pitch=6, show_body=False,
                       scale=9, center=(0, 1.35), size=(620, 620)),
        preview.render(geo, tex, preview_path("bat_blast.png"), anim, "blast", 0.5, yaw=35, pitch=4, show_body=False,
                       scale=9, center=(0, 1.35), size=(620, 620)),
        preview.render(geo, tex, preview_path("bat_back.png"), anim, "move", 0.2, yaw=200, pitch=20, show_body=False,
                       scale=9, center=(0, 1.35), size=(620, 620)),
    ]
    return preview.contact_sheet(shots, preview_path("bat_sheet.png"), cols=4)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
