"""
The Future Devil - entity model (entity/devil/future) and animations.

Reference points:
  * it never leaves its cell: a long, gnarled body rooted into the floor of the dark, only the upper half moving
  * a long pale face under drooping strands, crowned with horns; a wide, delighted mouth
  * an eye set in its chest (it lives in its contractor's eye and sees the future through it)
  * long many-jointed arms it throws up when it chants "Future's the best!"
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
    a.add("bark", kind="skin", color=(96, 78, 64))
    a.add("bark_dk", kind="skin", color=(58, 46, 40))
    a.add("skin", kind="skin", color=(206, 196, 176))
    a.add("hair", kind="fiber", color=(30, 26, 26))
    a.add("horn", kind="bone", color=(226, 214, 180))
    a.add("mouth", kind="void", color=(40, 8, 12))
    a.add("teeth", kind="teeth", color=(240, 232, 210))
    a.add("eye", kind="ringeye", color=(236, 196, 70), color2=(120, 60, 20), rings=3, sclera=(246, 238, 210))
    a.add("eye_glow", kind="glow", color=(255, 220, 110), emissive=True)
    a.add("lid", kind="skin", color=(150, 120, 100))
    a.add("nail", kind="bone", color=(60, 48, 40))
    return a


def arm(m, name, side, sh):
    """Upper arm on `name`, forearm + hand on `name`_fore (so the reach can unfold the elbow)."""
    sh = np.asarray(sh, dtype=float)
    b = m.bone(name, parent="body", pivot=tuple(sh))
    el = sh + np.array([side * 5.0, -12.0, -1.0])
    shapes.shell(b, shapes.loft(shapes.polyline([sh, sh + np.array([side * 2.5, -6.5, 0.0]), el]),
                                shapes.profile((0, 2.4), (1, 1.6)), shapes.profile((0, 2.2), (1, 1.5))), 8, 10, "bark",
                 thick=0.35)
    shapes.shell(b, shapes.ellipsoid(sh, (2.6, 2.6, 2.6)), 8, 5, "bark_dk", thick=0.35)
    fb = m.bone(name + "_fore", parent=name, pivot=tuple(el))
    shapes.shell(fb, shapes.ellipsoid(el, (1.8, 1.8, 1.8)), 6, 4, "bark_dk", thick=0.3)
    wr = el + np.array([side * 1.0, -13.0, -3.0])
    mid = el + np.array([side * 1.5, -6.5, -1.0])
    shapes.shell(fb, shapes.loft(shapes.polyline([el, mid, wr]), shapes.profile((0, 1.5), (1, 1.0)),
                                 shapes.profile((0, 1.4), (1, 0.9))), 8, 10, "bark", thick=0.3)
    shapes.shell(fb, shapes.ellipsoid(mid, (1.6, 1.4, 1.6)), 6, 4, "bark_dk", thick=0.3)
    palm = wr + np.array([0, -1.6, -0.4])
    shapes.shell(fb, shapes.ellipsoid(palm, (1.8, 2.0, 1.0)), 7, 5, "skin", thick=0.3)
    for k in range(5):
        thumb = k == 0
        base = palm + np.array([side * (-1.4 + k * 0.7) * (1 if not thumb else 1.2), -1.2 if not thumb else 0.2, -0.3])
        d = norm(np.array([side * (0.9 if thumb else 0.1 * (k - 2)), -1.0, -0.2]))
        shapes.horn(fb, base, d, 3.2 if thumb else 5.0 - abs(k - 2.5) * 0.4, 0.4, mat="skin", tip_mat="nail",
                    sections=4, around=5, r1=0.12, bend_axis=(side * 1.0, 0, 0), bend=25)


def build():
    atlas = materials()
    m = Model("csm.future_devil", atlas, density=2.0, seed=261)
    root = m.bone("root", pivot=(0, 0, 0))
    # the roots: it has grown into the floor
    roots = m.bone("roots", parent="root", pivot=(0, 0, 0))
    for k in range(9):
        a = k * 2 * math.pi / 9 + 0.35
        p0 = np.array([math.cos(a) * 3.5, 6.0, math.sin(a) * 3.0])
        p1 = np.array([math.cos(a) * 8.0, 1.5, math.sin(a) * 7.0])
        p2 = np.array([math.cos(a + 0.25) * (13.0 + (k % 3) * 2.5), 0.3, math.sin(a + 0.25) * (12.0 + (k % 3) * 2.5)])
        shapes.shell(roots, shapes.loft(shapes.polyline([p0, p1, p2]), shapes.profile((0, 2.4), (1, 0.4)),
                                        shapes.profile((0, 2.0), (1, 0.3))), 6, 8, "bark_dk", thick=0.35)
    body = m.bone("body", parent="root", pivot=(0, 14, 0))
    # the long gnarled trunk of its body, twisting up out of the roots
    trunk = shapes.loft(shapes.polyline([(0, 0.0, 0.5), (0.8, 12.0, 1.5), (-0.6, 24.0, 0.5), (0.0, 34.0, -0.5),
                                         (0, 42.0, 0.0)]),
                        shapes.profile((0, 7.0), (0.2, 4.6), (0.5, 4.0), (0.75, 5.6), (1, 6.4)),
                        shapes.profile((0, 6.0), (0.2, 4.0), (0.5, 3.6), (0.75, 4.4), (1, 4.2)), up=(0, 0, -1),
                        twist=lambda t: t * 50)
    shapes.shell(body, trunk, 14, 16, "bark", thick=0.45,
                 mat_fn=lambda u, v: "bark_dk" if (int(u * 14) + int(v * 5)) % 4 == 0 else "bark")
    # gnarls
    rng = np.random.default_rng(263)
    for k in range(10):
        u, v = rng.uniform(0, 1), rng.uniform(0.1, 0.7)
        p, n, du, dv = shapes.surface_frame(trunk, u, v)
        shapes.shell(body, shapes.ellipsoid(p, (1.2, 1.6, 1.2)), 6, 4, "bark_dk", thick=0.3)
    # the chest: broad, with the eye set in its breastbone
    chest = shapes.ellipsoid((0, 39.0, 0.0), (7.8, 6.4, 4.8), e_lat=0.9, e_lon=0.9)
    shapes.shell(body, chest, 16, 10, "bark", thick=0.45)
    ey = m.bone("chest_eye", parent="body", pivot=(0, 39.5, -4.8))
    p, n, du, dv = shapes.surface_frame(chest, 0.0, 0.53)
    ey.decal(p + n * 0.1, n, 3.8, 5.4, "eye", up=(1, 0, 0))
    for s in (-1, 1):
        # heavy lids above and below
        shapes.shell(body, shapes.ellipsoid(p + n * 0.2 + np.array([0, s * 2.9, 0]), (2.6, 0.9, 0.9)), 8, 4, "lid",
                     thick=0.3)
    # neck
    shapes.shell(body, shapes.loft(shapes.polyline([(0, 44.0, 0.5), (0, 48.0, -0.5), (0, 51.0, -1.0)]),
                                   shapes.profile((0, 3.0), (1, 2.2)), shapes.profile((0, 2.8), (1, 2.0)),
                                   up=(0, 0, -1)), 10, 6, "bark", thick=0.35)
    # the head: long pale face, drooping black strands, a crown of horns
    head = m.bone("head", parent="body", pivot=(0, 50, -1))
    look = m.bone("look", parent="head", pivot=(0, 52, -1))
    face = shapes.ellipsoid((0, 55.0, -1.5), (4.2, 6.2, 4.2), e_lat=0.9)
    shapes.shell(look, face, 16, 12, "skin", thick=0.4)
    jaw = m.bone("jaw", parent="look", pivot=(0, 53.0, 1.0))
    # a wide grin that follows the curve of the lower face, teeth above and below
    for k in range(9):
        u = (-0.15 + k * 0.0375) % 1.0
        vv = 0.3 + abs(k - 4) * 0.012
        p, n, du, dv = shapes.surface_frame(face, u, vv)
        look.decal(p + n * 0.12, n, 1.5, 1.3 - abs(k - 4) * 0.08, "mouth", up=(0, 1, 0))
        look.spike(p + n * 0.1 + np.array([0, 0.55, 0]), (0, -1, 0), 0.8, 0.5, 0.2, "teeth", steps=2, up=n)
        q, n2, _, _ = shapes.surface_frame(face, u, vv - 0.05)
        jaw.spike(q + n2 * 0.25 + np.array([0, -0.1, 0]), (0, 1, 0), 0.7, 0.45, 0.2, "teeth", steps=2, up=n2)
    shapes.shell(jaw, shapes.ellipsoid((0, 50.0, -2.0), (3.2, 1.3, 3.4)), 10, 5, "skin", thick=0.35)
    # small gleeful eyes
    for s in (-1, 1):
        p, n, du, dv = shapes.surface_frame(face, 0.08 if s > 0 else 0.92, 0.6)
        look.decal(p + n * 0.1, n, 1.6, 1.0, "eye_glow", up=(0, 1, 0))
    # the crown of horns
    for k in range(7):
        a = math.radians(-75 + k * 25)
        base = np.array([math.sin(a) * 3.4, 59.5 + math.cos(a) * 1.0, -1.5 + math.cos(a) * 0.5])
        d = norm(np.array([math.sin(a) * 0.7, 1.0, 0.25]))
        shapes.horn(look, base, d, 6.0 + 3.0 * math.cos(a), 1.0, mat="horn", sections=5, around=6, r1=0.1,
                    bend_axis=(math.cos(a), 0, -math.sin(a)), bend=-25)
    # hair: long black strands draping down from the crown over the back and shoulders
    for k in range(16):
        a = math.radians(-120 + k * 16)
        base = np.array([math.sin(a) * 4.0, 59.0, -1.5 - math.cos(a) * 4.0])
        if math.cos(a) > 0.55:
            continue  # leave the face clear
        d = norm(np.array([math.sin(a) * 0.3, -1.0, -math.cos(a) * 0.3]))
        shapes.horn(look, base, d, 12.0 + (k % 3) * 3.0, 1.2, mat="hair", flat=0.4, sections=5, around=5, r1=0.3,
                    bend_axis=(math.cos(a), 0, math.sin(a)), bend=15)
    # arms
    arm(m, "right_arm", -1, (-8.5, 42.0, 0.5))
    arm(m, "left_arm", 1, (8.5, 42.0, 0.5))

    geo, tex, glow, anim_path = dk.devil_paths("future")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=265)
    anims = animations()
    save_animations(anim_path, anims)
    print("future devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    idle = Anim("idle", 4.0, loop=True)
    for i in range(9):
        t = 4.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("body", t, (2 * math.sin(ph), 4 * math.sin(ph * 0.5), 2 * math.sin(ph)))
        idle.rot("head", t, (3 * math.sin(ph + 1), 10 * math.sin(ph * 0.5), 6 * math.sin(ph)))
        idle.rot("right_arm", t, (-6 + 5 * math.sin(ph), 0, 8))
        idle.rot("left_arm", t, (-6 + 5 * math.sin(ph + 2), 0, -8))
        idle.rot("right_arm_fore", t, (-20 + 6 * math.sin(ph), 0, 0))
        idle.rot("left_arm_fore", t, (-20 + 6 * math.sin(ph + 2), 0, 0))
        idle.scale("chest_eye", t, (1, 1 + 0.08 * math.sin(ph * 2), 1))
    A.append(idle)
    # it can't walk: "move" is the same restless swaying, a little bigger
    mv = Anim("move", 2.0, loop=True)
    for i in range(9):
        t = 2.0 * i / 8
        ph = 2 * math.pi * i / 8
        mv.rot("body", t, (4 * math.sin(ph), 8 * math.sin(ph), 4 * math.sin(ph)))
        mv.rot("head", t, (0, -8 * math.sin(ph), 0))
        mv.rot("right_arm", t, (-10 + 10 * math.sin(ph), 0, 10))
        mv.rot("left_arm", t, (-10 - 10 * math.sin(ph), 0, -10))
    A.append(mv)
    # foresight: arms spread, the chest eye opens wide and stares
    fs = Anim("foresight", 0.8)
    fs.rot("right_arm", 0, (0, 0, 0)).rot("right_arm", 0.3, (-20, 0, 70), "easeOutQuad").rot("right_arm", 0.8, (0, 0, 0))
    fs.rot("left_arm", 0, (0, 0, 0)).rot("left_arm", 0.3, (-20, 0, -70), "easeOutQuad").rot("left_arm", 0.8, (0, 0, 0))
    fs.scale("chest_eye", 0, 1.0).scale("chest_eye", 0.3, 1.5, "easeOutBack").scale("chest_eye", 0.8, 1.0)
    fs.rot("body", 0.3, (-12, 0, 0)).rot("body", 0.8, (0, 0, 0))
    fs.rot("head", 0.3, (-20, 0, 0)).rot("head", 0.8, (0, 0, 0))
    A.append(fs)
    # the glimpse: it leans in close, grinning, and shows you
    gl = Anim("glimpse", 1.2)
    gl.rot("body", 0, (0, 0, 0)).rot("body", 0.5, (22, 0, 0), "easeOutQuad").rot("body", 0.9, (22, 0, 0))
    gl.rot("body", 1.2, (0, 0, 0))
    gl.rot("head", 0.5, (-15, 0, 12)).rot("head", 0.9, (-15, 0, -12)).rot("head", 1.2, (0, 0, 0))
    gl.rot("jaw", 0.4, (30, 0, 0)).rot("jaw", 0.9, (30, 0, 0)).rot("jaw", 1.2, (0, 0, 0))
    gl.scale("chest_eye", 0.5, 1.4).scale("chest_eye", 1.2, 1.0)
    gl.rot("right_arm", 0.5, (-70, 20, 20)).rot("right_arm", 1.2, (0, 0, 0))
    gl.rot("right_arm_fore", 0.5, (-40, 0, 0)).rot("right_arm_fore", 1.2, (0, 0, 0))
    A.append(gl)
    # the reach: the right arm unfolds and swats
    rc = Anim("reach", 0.9)
    rc.rot("right_arm", 0, (0, 0, 0)).rot("right_arm", 0.3, (-150, -20, 20), "easeOutQuad")
    rc.rot("right_arm", 0.45, (-60, 30, -10), "easeInQuad").rot("right_arm", 0.9, (0, 0, 0))
    rc.rot("right_arm_fore", 0.3, (-30, 0, 0)).rot("right_arm_fore", 0.45, (0, 0, 0))
    rc.pos("right_arm", 0.45, (0, 0, -3)).pos("right_arm", 0.9, (0, 0, 0))
    rc.rot("body", 0.3, (-8, 15, 0)).rot("body", 0.45, (18, -20, 0)).rot("body", 0.9, (0, 0, 0))
    A.append(rc)
    # "Future's the best! Future's the best!"
    dn = Anim("dance", 2.5)
    for i in range(11):
        t = 2.5 * i / 10
        up = i % 2 == 0
        dn.rot("right_arm", t, (-170 if up else -110, 0, 20 if up else 40))
        dn.rot("left_arm", t, (-110 if up else -170, 0, -40 if up else -20))
        dn.rot("right_arm_fore", t, (-10 if up else -50, 0, 0))
        dn.rot("left_arm_fore", t, (-50 if up else -10, 0, 0))
        dn.rot("body", t, (0, 0, 10 if up else -10))
        dn.rot("head", t, (-10, 0, -15 if up else 15))
        dn.rot("jaw", t, (25 if up else 10, 0, 0))
    dn.rot("right_arm", 2.5, (0, 0, 0)).rot("left_arm", 2.5, (0, 0, 0)).rot("body", 2.5, (0, 0, 0))
    A.append(dn)
    dr = Anim("drink", 1.0)
    dr.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.3, (30, 0, 0)).rot("jaw", 1.0, (0, 0, 0))
    A.append(dr)
    death = Anim("death", 2.0, loop="hold_on_last_frame")
    death.rot("body", 0, (0, 0, 0)).rot("body", 1.2, (70, 0, 20), "easeInQuad")
    death.rot("right_arm", 1.2, (-30, 0, 60)).rot("left_arm", 1.2, (10, 0, -40))
    death.rot("head", 1.2, (40, 20, 0)).rot("jaw", 1.2, (35, 0, 0))
    death.scale("chest_eye", 0, 1.0).scale("chest_eye", 1.2, (1, 0.1, 1))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.5, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("future_front.png"), anim, "idle", 0.0, yaw=20, pitch=6, show_body=False,
                       scale=5.5, center=(0, 1.8), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("future_dance.png"), anim, "dance", 0.0, yaw=-30, pitch=6,
                       show_body=False, scale=5.0, center=(0, 2.0), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("future_face.png"), anim, "idle", 0.0, yaw=10, pitch=0, show_body=False,
                       scale=12.0, center=(0, 3.0), size=(620, 620), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("future_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
