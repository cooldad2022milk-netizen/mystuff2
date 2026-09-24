"""
The Ghost Devil - entity model (entity/devil/ghost) and animations.

Reference points:
  * a tall, pale, see-through column of a body studded with pale blossoms
  * it walks on a pair of arms where its legs should be; a second pair of long arms hangs from its shoulders
  * Himeno paid for it with her right eye: its face has that one eye and an empty socket
  * it strangles and lifts with hands no one else can see, and it can smell fear
"""
import math

import numpy as np

from common import preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk


def draw_blossom(d, n):
    c = n / 2
    for k in range(5):
        a = math.radians(k * 72 - 90)
        px, py = c + math.cos(a) * n * 0.24, c + math.sin(a) * n * 0.24
        r = n * 0.2
        d.ellipse([px - r, py - r, px + r, py + r], fill=(246, 214, 226, 255))
    for k in range(5):
        a = math.radians(k * 72 - 90)
        d.line([(c, c), (c + math.cos(a) * n * 0.3, c + math.sin(a) * n * 0.3)], fill=(226, 170, 190, 255), width=2)
    r = n * 0.09
    d.ellipse([c - r, c - r, c + r, c + r], fill=(236, 190, 110, 255))


def materials():
    a = Atlas(512, 64)
    a.add("skin", kind="skin", color=(226, 224, 236))
    a.add("skin_dk", kind="skin", color=(186, 182, 204))
    a.add("blossom", kind="decal", color=(240, 210, 220), draw=draw_blossom)
    a.add("petal", kind="skin", color=(244, 214, 226))
    a.add("eye", kind="ringeye", color=(70, 50, 44), color2=(30, 20, 18), rings=0, sclera=(244, 240, 236))
    a.add("socket", kind="decal", color=(14, 12, 20), draw=lambda d, n: (
        d.ellipse([1, n * 0.12, n - 2, n * 0.88], fill=(150, 140, 170, 255)),
        d.ellipse([n * 0.12, n * 0.22, n * 0.88, n * 0.8], fill=(12, 10, 18, 255))))
    a.add("mouth", kind="void", color=(40, 20, 34))
    a.add("teeth", kind="teeth", color=(240, 236, 230))
    a.add("nail", kind="skin", color=(200, 180, 196))
    return a


def long_arm(bone, sh, el, wr, r0=1.6, mat="skin"):
    pts = [np.asarray(p, dtype=float) for p in (sh, el, wr)]
    f = shapes.loft(shapes.polyline(pts), shapes.profile((0, r0), (0.5, r0 * 0.75), (1, r0 * 0.6)),
                    shapes.profile((0, r0 * 0.9), (0.5, r0 * 0.7), (1, r0 * 0.5)))
    shapes.shell(bone, f, 8, 12, mat, thick=0.3)
    shapes.shell(bone, shapes.ellipsoid(pts[1], (r0 * 0.85, r0 * 0.85, r0 * 0.85)), 6, 4, "skin_dk", thick=0.3)
    return f


def hand(bone, wrist, forward, down, size=1.0, spread=1.0, curl=20):
    """A long-fingered hand: palm along `forward`, fingers splayed, curling towards `down`."""
    wrist = np.asarray(wrist, dtype=float)
    fw = norm(forward)
    dn = norm(down)
    sd = norm(np.cross(fw, dn))
    palm = wrist + fw * 1.8 * size
    shapes.shell(bone, shapes.ellipsoid(palm, (1.9 * size, 0.7 * size, 2.0 * size),
                                        frame=np.column_stack([sd, -dn, -fw])), 8, 5, "skin", thick=0.3)
    for k in range(5):
        thumb = k == 0
        off = (-1.5 + k * 0.75) * size
        base = palm + sd * off + fw * (1.4 if not thumb else -0.4) * size
        d = norm(fw + sd * ((-1.0 if thumb else 0.12 * (k - 2)) * spread))
        length = (3.5 if thumb else 5.5 - abs(k - 2.5) * 0.5) * size
        shapes.horn(bone, base, d, length, 0.42 * size, mat="skin", tip_mat="nail", sections=4, around=5, r1=0.14,
                    bend_axis=sd, bend=curl)


def build():
    atlas = materials()
    m = Model("csm.ghost_devil", atlas, density=2.0, seed=271)
    root = m.bone("root", pivot=(0, 0, 0))
    waist = m.bone("waist", parent="root", pivot=(0, 17, 0))
    body = m.bone("body", parent="waist", pivot=(0, 17, 0))
    # the column of its body, leaning a little forward at the top
    col = shapes.loft(shapes.polyline([(0, 13.0, 0.5), (0, 20.0, 0.5), (0, 30.0, 0.0), (0, 40.0, -0.8),
                                       (0, 46.0, -1.2)]),
                      shapes.profile((0, 1.5), (0.1, 4.2), (0.5, 4.8), (0.85, 4.2), (1, 2.8)),
                      shapes.profile((0, 1.5), (0.1, 3.8), (0.5, 4.2), (0.85, 3.6), (1, 2.4)), up=(0, 0, -1))
    shapes.shell(body, col, 14, 16, "skin", thick=0.4,
                 mat_fn=lambda u, v: "skin_dk" if int(u * 14) % 5 == 0 else "skin")
    # blossoms all over it
    rng = np.random.default_rng(273)
    for k in range(34):
        u, v = rng.uniform(0, 1), rng.uniform(0.08, 0.92)
        p, n, du, dv = shapes.surface_frame(col, u, v)
        w = rng.uniform(1.8, 3.0)
        body.decal(p + n * rng.uniform(0.12, 0.35), n, w, w, "blossom", up=norm(dv + du * rng.uniform(-1, 1)))
    # a few blossoms standing proud: petal cups
    for k in range(8):
        u, v = rng.uniform(0, 1), rng.uniform(0.15, 0.85)
        p, n, du, dv = shapes.surface_frame(col, u, v)
        for j in range(5):
            a = j * 2 * math.pi / 5
            d = norm(n * 0.8 + (du * math.cos(a) + dv * math.sin(a)) * 0.9)
            shapes.horn(body, p, d, 1.6, 0.6, mat="petal", flat=0.3, up=n, sections=2, around=5, r1=0.25)
    # the arms it walks on, where legs should be
    for side, name in ((-1, "right_leg"), (1, "left_leg")):
        hip = np.array([side * 2.8, 16.0, 0.5])
        leg = m.bone(name, parent="root", pivot=tuple(hip))
        el = hip + np.array([side * 3.0, -7.0, 2.5])
        wr = np.array([side * 5.2, 1.2, -1.0])
        long_arm(leg, hip, el, wr, r0=1.7)
        hand(leg, wr, (side * 0.15, 0, -1), (0, -1, 0), size=1.1, spread=1.3, curl=-12)
    # the long arms hanging from its shoulders
    for side, name in ((-1, "right_arm"), (1, "left_arm")):
        sh = np.array([side * 4.6, 43.0, -0.8])
        arm = m.bone(name, parent="body", pivot=tuple(sh))
        shapes.shell(arm, shapes.ellipsoid(sh, (2.0, 2.0, 2.0)), 7, 5, "skin", thick=0.3)
        el = sh + np.array([side * 2.0, -12.0, 1.0])
        wr = el + np.array([side * 0.5, -12.0, -2.0])
        long_arm(arm, sh, el, wr, r0=1.3)
        hand(arm, wr, (0, -1, -0.15), (0, 0, -1), size=1.0, spread=0.8, curl=30)
    # the face
    head = m.bone("head", parent="body", pivot=(0, 46, -1))
    look = m.bone("look", parent="head", pivot=(0, 48, -1))
    face = shapes.ellipsoid((0, 51.0, -1.5), (3.8, 5.2, 3.8), e_lat=0.9)
    shapes.shell(look, face, 14, 12, "skin", thick=0.4)
    # Himeno's eye on its right, an empty socket on its left
    p, n, du, dv = shapes.surface_frame(face, 0.93, 0.58)
    look.decal(p + n * 0.12, n, 2.4, 1.5, "eye", up=(0, 1, 0))
    p, n, du, dv = shapes.surface_frame(face, 0.07, 0.58)
    look.decal(p + n * 0.12, n, 2.4, 1.8, "socket", up=(0, 1, 0))
    # a thin mouth line with small teeth
    jaw = m.bone("jaw", parent="look", pivot=(0, 49.0, 0.0))
    for k in range(7):
        u = (-0.09 + k * 0.03) % 1.0
        p, n, du, dv = shapes.surface_frame(face, u, 0.33)
        look.decal(p + n * 0.12, n, 1.1, 0.7, "mouth", up=(0, 1, 0))
        look.spike(p + n * 0.1 + np.array([0, 0.3, 0]), (0, -1, 0), 0.5, 0.35, 0.2, "teeth", steps=2, up=n)
    shapes.shell(jaw, shapes.ellipsoid((0, 47.2, -2.0), (2.6, 1.1, 2.6)), 8, 4, "skin", thick=0.3)
    # a crown of blossoms
    for k in range(9):
        a = math.radians(-100 + k * 25)
        p = np.array([math.sin(a) * 3.2, 55.2 + math.cos(a) * 0.6, -1.5 - math.cos(a) * 1.6])
        n = norm(np.array([math.sin(a) * 0.6, 1.0, -math.cos(a) * 0.4]))
        look.decal(p + n * 0.2, n, 2.6, 2.6, "blossom", up=(0, 0, -1))

    geo, tex, glow, anim_path = dk.devil_paths("ghost")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=275)
    anims = animations()
    save_animations(anim_path, anims)
    print("ghost devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    idle = Anim("idle", 3.5, loop=True)
    for i in range(9):
        t = 3.5 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("body", t, (3 * math.sin(ph), 5 * math.sin(ph * 0.5), 3 * math.sin(ph + 1)))
        idle.rot("head", t, (4 * math.sin(ph + 1), 0, 10 * math.sin(ph * 0.5)))
        idle.rot("right_arm", t, (-5 + 6 * math.sin(ph), 0, 6 + 3 * math.sin(ph)))
        idle.rot("left_arm", t, (-5 + 6 * math.sin(ph + 1.8), 0, -6 - 3 * math.sin(ph + 1.8)))
        idle.pos("waist", t, (0, 0.8 * math.sin(ph), 0))
    A.append(idle)
    # it walks on its hands: they plant, the body swings over them
    mv = Anim("move", 1.2, loop=True)
    for i in range(9):
        t = 1.2 * i / 8
        ph = 2 * math.pi * i / 8
        mv.rot("right_leg", t, (35 * math.sin(ph), 0, 0))
        mv.rot("left_leg", t, (-35 * math.sin(ph), 0, 0))
        mv.rot("body", t, (8, 6 * math.sin(ph), 4 * math.sin(ph)))
        mv.pos("waist", t, (0, 1.2 * abs(math.cos(ph)), 0))
        mv.rot("right_arm", t, (-15 - 15 * math.sin(ph), 0, 8))
        mv.rot("left_arm", t, (-15 + 15 * math.sin(ph), 0, -8))
    A.append(mv)
    # strangle: both arms reach out towards the victim, hands closing round nothing - then lift
    st = Anim("strangle", 2.5)
    for arm, s in (("right_arm", 1), ("left_arm", -1)):
        st.rot(arm, 0, (0, 0, 0)).rot(arm, 0.3, (-95, s * -15, 0), "easeOutQuad")
        st.rot(arm, 1.0, (-110, s * -8, 0)).rot(arm, 2.1, (-135, s * -5, 0)).rot(arm, 2.5, (0, 0, 0))
    st.rot("body", 0.3, (18, 0, 0)).rot("body", 2.1, (6, 0, 0)).rot("body", 2.5, (0, 0, 0))
    st.rot("head", 0.3, (-10, 0, 8)).rot("head", 2.1, (-20, 0, -8)).rot("head", 2.5, (0, 0, 0))
    st.rot("jaw", 0.4, (18, 0, 0)).rot("jaw", 2.1, (18, 0, 0)).rot("jaw", 2.5, (0, 0, 0))
    A.append(st)
    sn = Anim("snatch", 1.2)
    sn.rot("right_arm", 0, (0, 0, 0)).rot("right_arm", 0.3, (-110, 0, 0), "easeOutQuad")
    sn.rot("right_arm", 0.7, (-130, 60, -30), "easeInQuad").rot("right_arm", 1.2, (0, 0, 0))
    sn.rot("body", 0.3, (12, 0, 0)).rot("body", 0.7, (0, 30, 0)).rot("body", 1.2, (0, 0, 0))
    A.append(sn)
    fd = Anim("fade", 0.6)
    fd.scale("root", 0, 1.0).scale("root", 0.2, (0.8, 1.15, 0.8)).scale("root", 0.6, 1.0)
    fd.rot("body", 0.2, (0, 90, 0)).rot("body", 0.6, (0, 0, 0))
    A.append(fd)
    fr = Anim("fear", 1.3)
    fr.rot("head", 0, (0, 0, 0)).rot("head", 0.3, (-15, 25, 0)).rot("head", 0.6, (-15, -25, 0))
    fr.rot("head", 0.9, (-25, 0, 0)).rot("head", 1.3, (0, 0, 0))
    fr.rot("jaw", 0.6, (0, 0, 0)).rot("jaw", 0.8, (40, 0, 0), "easeOutQuad").rot("jaw", 1.3, (0, 0, 0))
    for arm, s in (("right_arm", 1), ("left_arm", -1)):
        fr.rot(arm, 0.8, (-60, 0, s * 70)).rot(arm, 1.3, (0, 0, 0))
    A.append(fr)
    dr = Anim("drink", 1.0)
    dr.rot("jaw", 0, (0, 0, 0)).rot("jaw", 0.3, (30, 0, 0)).rot("jaw", 1.0, (0, 0, 0))
    A.append(dr)
    death = Anim("death", 1.6, loop="hold_on_last_frame")
    death.rot("body", 0, (0, 0, 0)).rot("body", 1.0, (60, 0, 0), "easeInQuad")
    death.scale("root", 0, 1.0).scale("root", 1.6, (1.0, 0.25, 1.0), "easeInQuad")
    death.rot("right_arm", 1.0, (-60, 0, 50)).rot("left_arm", 1.0, (-60, 0, -50))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 0.9, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.5, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("ghost_front.png"), anim, "idle", 0.0, yaw=25, pitch=6, show_body=False,
                       scale=6.0, center=(0, 1.7), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("ghost_strangle.png"), anim, "strangle", 1.0, yaw=70, pitch=6,
                       show_body=False, scale=6.0, center=(0, 1.7), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("ghost_face.png"), anim, "idle", 0.0, yaw=10, pitch=0, show_body=False,
                       scale=13.0, center=(0, 3.0), size=(620, 620), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("ghost_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
