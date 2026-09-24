"""
The Justice Devil - entity model (entity/devil/justice) and animations. (What Yuko became through her contract.)

Reference points (Chainsaw Man part 2, ch. 111-114):
  * a large, CATERPILLAR-like monster: a long segmented body on rows of little legs, rearing up at the front
  * NO EYES - blind, like Justice with her blindfold
  * a white cloth round its neck like a judge's bib
  * one arm has become a giant GAVEL; tentacles it can't control whip out of it and grow back
  * it can open an ENORMOUS JAW in its belly
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
    a.add("hide", kind="skin", color=(150, 160, 112))
    a.add("hide_dk", kind="skin", color=(96, 106, 70))
    a.add("belly", kind="skin", color=(206, 200, 164))
    a.add("skin", kind="skin", color=(232, 214, 200))
    a.add("hair", kind="fiber", color=(34, 28, 30))
    a.add("bib", kind="skin", color=(246, 246, 244))
    a.add("bib_dk", kind="skin", color=(214, 214, 218))
    a.add("wood", kind="fiber", color=(106, 64, 36))
    a.add("wood_dk", kind="fiber", color=(70, 40, 24))
    a.add("band", kind="metal", color=(200, 170, 90), scratches=1)
    a.add("mouth", kind="void", color=(50, 10, 16))
    a.add("teeth", kind="teeth", color=(236, 230, 212))
    a.add("gum", kind="flesh", color=(170, 70, 84))
    a.add("tentacle", kind="flesh", color=(176, 150, 150))
    return a


# the body's spine: along the ground at the back, rearing up at the front
SPINE = [(0, 7.0, 40.0), (0, 7.0, 26.0), (0, 8.0, 12.0), (0, 11.0, 0.0), (0, 20.0, -8.0), (0, 33.0, -11.0),
         (0, 44.0, -10.0)]


def build():
    atlas = materials()
    m = Model("csm.justice_devil", atlas, density=2.0, seed=351)
    root = m.bone("root", pivot=(0, 0, 0))
    tail = m.bone("tail", parent="root", pivot=(0, 7, 12))
    body = m.bone("body", parent="root", pivot=(0, 11, 0))
    path = shapes.polyline(SPINE)
    radius = shapes.profile((0, 3.0), (0.2, 6.5), (0.5, 8.0), (0.75, 7.5), (0.92, 6.0), (1, 5.0))
    f = shapes.loft(path, radius, lambda t: radius(t) * 0.9, up=(0, 1, 0))

    # segmented: dark bands between the segments; the underside and the belly pale
    def seg_mat(u, v):
        if int(v * 22) % 2 == 0 and abs(((v * 22) % 1.0) - 0.5) > 0.35:
            return "hide_dk"
        return "belly" if 0.35 < u < 0.65 else "hide"
    # the belly jaw: a big split down the front of the rearing part
    jaw_skip = lambda u, v: 0.4 < u < 0.6 and 0.66 < v < 0.9
    shapes.shell(tail, f, 14, 12, "hide", thick=0.5, v0=0.0, v1=0.45, mat_fn=seg_mat)
    shapes.shell(body, f, 14, 14, "hide", thick=0.5, v0=0.45, v1=1.0, mat_fn=seg_mat, skip=jaw_skip)
    # rows of stubby little legs along the ground
    for k in range(8):
        v = 0.05 + k * 0.07
        for s in (-1, 1):
            p, n, du, dv = shapes.surface_frame(f, 0.5 + s * 0.2, v)
            owner = tail if v < 0.45 else body
            shapes.horn(owner, p, norm(np.array([s * 0.4, -1, 0])), 4.0, 1.2, mat="hide_dk", sections=2, around=5,
                        r1=0.5)
    # the jaw in its belly (opens for Belly Jaw)
    jaw = m.bone("belly_jaw", parent="body", pivot=(0, 30.0, -13.0))
    jc = np.array([0, 28.0, -12.6])
    shapes.shell(body, shapes.ellipsoid(jc + np.array([0, 0, 2.6]), (3.8, 7.0, 2.4)), 10, 8, "mouth", thick=0.3)
    for k in range(9):
        y = jc[1] - 6.0 + k * 1.5
        for s in (-1, 1):
            owner = jaw if s > 0 else body
            owner.spike((s * 3.0, y, jc[2] - 0.4), (-s * 1.0, 0, -0.1), 2.2, 0.9, 0.5, "teeth", steps=3,
                        up=(0, 0, -1))
    shapes.shell(jaw, shapes.ellipsoid(jc + np.array([3.4, 0, 0.6]), (1.2, 7.4, 1.4)), 6, 8, "gum", thick=0.3)
    shapes.shell(body, shapes.ellipsoid(jc + np.array([-3.4, 0, 0.6]), (1.2, 7.4, 1.4)), 6, 8, "gum", thick=0.3)
    # the head up top: Yuko's, but with no eyes; black hair; a judge's white bib at the throat
    head = m.bone("head", parent="body", pivot=(0, 46, -10))
    look = m.bone("look", parent="head", pivot=(0, 48, -10))
    hc = np.array([0, 51.5, -10.0])
    shapes.shell(look, shapes.ellipsoid(hc, (4.2, 4.8, 4.2), e_lat=0.8, e_lon=0.8), 14, 10, "skin", thick=0.4)
    look.obox(hc + np.array([0, -2.4, -4.1]), (1, 0, 0), (0.5, 2.4, 0.2), "mouth", up=(0, 0, -1))
    hair = shapes.ellipsoid(hc + np.array([0, 0.6, 0.4]), (4.6, 4.9, 4.6), e_lat=0.6, e_lon=0.6)
    shapes.shell(look, hair, 14, 8, "hair", v0=0.42, thick=0.4, skip=lambda u, v: min(u, 1 - u) < 0.2 and v < 0.75)
    for s in (-1, 1):
        shapes.shell(look, shapes.loft(shapes.polyline([hc + [s * 4.2, 1.5, 0], hc + [s * 4.4, -3.5, 0.4]]), 0.9, 2.6),
                     4, 5, "hair", thick=0.3)
    # the bib: a white cloth tied round the neck, falling in two tabs
    body.ring(hc + np.array([0, -5.4, 0]), (0, 1, 0), 4.0, 0.9, 1.4, "bib_dk", count=14)
    for s in (-1, 1):
        body.obox(hc + np.array([s * 1.0, -8.6, -4.6]), (0, 1, 0), (1.9, 5.2, 0.4), "bib", up=(0, 0, -1), roll=s * 6)
    # the gavel arm (its right) and a clawed left arm
    for side, name in ((-1, "right_arm"), (1, "left_arm")):
        sh = np.array([side * 7.0, 40.0, -9.0])
        arm = m.bone(name, parent="body", pivot=tuple(sh))
        el = sh + np.array([side * 4.0, -8.0, -3.0])
        wr = el + np.array([side * 1.0, -8.0, -5.0])
        shapes.shell(arm, shapes.loft(shapes.polyline([sh, el, wr]), shapes.profile((0, 2.2), (1, 1.6)), 2.0), 8, 10,
                     "hide", thick=0.35)
        if side < 0:
            # the arm itself turns into a judge's gavel: a long handle and a huge barrel-shaped head
            handle_end = wr + np.array([0, -4.0, -6.0])
            arm.tube(wr, handle_end, 1.2, "wood", segments=8)
            hd = handle_end + np.array([0, -1.0, -1.5])
            arm.cylinder(hd, (1, 0, 0), 4.0, 12.0, "wood_dk", segments=12)
            for x in (-4.6, 4.6):
                arm.cylinder(hd + np.array([x, 0, 0]), (1, 0, 0), 4.3, 1.0, "band", segments=12)
        else:
            for j in range(4):
                d = norm(np.array([0.2 * (j - 1.5), -1, -0.5]))
                shapes.horn(arm, wr, d, 4.0, 0.6, mat="hide_dk", sections=3, around=4, r1=0.1, bend_axis=(1, 0, 0),
                            bend=-30)
    # tentacles it can't control, whipping out of its back
    tents = []
    for k in range(6):
        v = 0.55 + k * 0.07
        s = -1 if k % 2 else 1
        p, n, du, dv = shapes.surface_frame(f, 0.0 + s * 0.12, v)
        name = "tentacle%d" % k
        tb = m.bone(name, parent="body", pivot=tuple(p))
        out_d = norm(n + np.array([s * 0.6, 0.4, 0.5]))
        pts = [p, p + out_d * 7 + np.array([0, 2, 0]), p + out_d * 14 + np.array([0, 1, 4]),
               p + out_d * 20 + np.array([0, -3, 6])]
        shapes.shell(tb, shapes.loft(shapes.polyline(pts), shapes.profile((0, 1.4), (1, 0.3)),
                                     shapes.profile((0, 1.3), (1, 0.3))), 6, 10, "tentacle", thick=0.3)
        tents.append(name)
    geo, tex, glow, anim_path = dk.devil_paths("justice")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=353)
    anims = animations(tents)
    save_animations(anim_path, anims)
    print("justice devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def writhe(a, tents, t0, t1, amp, freq):
    steps = max(2, int((t1 - t0) * 8))
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        for k, b in enumerate(tents):
            ph = 2 * math.pi * freq * t + k * 1.1
            a.rot(b, t, (amp * math.sin(ph), amp * 0.7 * math.cos(ph), amp * 0.5 * math.sin(ph * 1.3)))


def animations(tents):
    A = []
    idle = Anim("idle", 3.2, loop=True)
    writhe(idle, tents, 0, 3.2, 12, 0.6)
    for i in range(9):
        t = 3.2 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("body", t, (2 * math.sin(ph), 3 * math.sin(ph * 0.5), 0))
        idle.rot("head", t, (4 * math.sin(ph + 1), 8 * math.sin(ph * 0.5), 5 * math.sin(ph)))
        idle.rot("right_arm", t, (-8 + 4 * math.sin(ph), 0, 4))
        idle.rot("left_arm", t, (-8 + 4 * math.sin(ph + 1), 0, -4))
    A.append(idle)
    mv = Anim("move", 1.4, loop=True)
    writhe(mv, tents, 0, 1.4, 16, 1.0)
    for i in range(9):
        t = 1.4 * i / 8
        ph = 2 * math.pi * i / 8
        # a caterpillar's crawl: a hump runs down the body
        mv.rot("tail", t, (6 * math.sin(ph), 0, 0))
        mv.rot("body", t, (4 * math.sin(ph + 1.5), 0, 0))
        mv.pos("root", t, (0, 0.8 * abs(math.sin(ph)), 0))
    A.append(mv)
    # Gavel: the hammer arm rises high and comes down
    g = Anim("gavel", 1.2)
    g.rot("right_arm", 0, (0, 0, 0)).rot("right_arm", 0.4, (-150, 0, 10), "easeOutQuad")
    g.rot("right_arm", 0.55, (10, 0, 0), "easeInQuad").rot("right_arm", 0.9, (5, 0, 0)).rot("right_arm", 1.2, (0, 0, 0))
    g.rot("body", 0.4, (-12, 0, 0)).rot("body", 0.55, (18, 0, 0), "easeInQuad").rot("body", 1.2, (0, 0, 0))
    A.append(g)
    # Tentacle Lash: every tentacle whips round
    lash = Anim("lash", 1.0)
    for k, b in enumerate(tents):
        lash.rot(b, 0, (0, 0, 0)).rot(b, 0.3, (-50, 0, 40 * (1 if k % 2 else -1)), "easeOutQuad")
        lash.rot(b, 0.55, (40, 0, -60 * (1 if k % 2 else -1)), "easeInOutQuad").rot(b, 1.0, (0, 0, 0))
    lash.rot("body", 0, (0, 0, 0)).rot("body", 0.3, (0, -30, 0)).rot("body", 0.6, (0, 40, 0)).rot("body", 1.0, (0, 0, 0))
    A.append(lash)
    # Belly Jaw: the belly splits open into a huge jaw and slams shut
    j = Anim("jaw", 1.1)
    j.rot("belly_jaw", 0, (0, 0, 0)).rot("belly_jaw", 0.35, (0, -70, 0), "easeOutQuad")
    j.rot("belly_jaw", 0.5, (0, 5, 0), "easeInQuad").rot("belly_jaw", 1.1, (0, 0, 0))
    j.rot("body", 0.35, (-20, 0, 0)).rot("body", 0.5, (25, 0, 0), "easeInQuad").rot("body", 1.1, (0, 0, 0))
    A.append(j)
    dr = Anim("drink", 1.0)
    dr.rot("belly_jaw", 0, (0, 0, 0)).rot("belly_jaw", 0.3, (0, -30, 0)).rot("belly_jaw", 1.0, (0, 0, 0))
    A.append(dr)
    death = Anim("death", 2.0, loop="hold_on_last_frame")
    death.rot("body", 0, (0, 0, 0)).rot("body", 1.2, (70, 0, 20), "easeInQuad")
    death.rot("head", 1.2, (40, 20, 0))
    for b in tents:
        death.rot(b, 1.2, (60, 0, 0))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.5, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("justice_front.png"), anim, "idle", 0.0, yaw=30, pitch=8,
                       show_body=False, scale=3.2, center=(0, 1.9), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("justice_side.png"), anim, "idle", 0.0, yaw=100, pitch=8,
                       show_body=False, scale=3.2, center=(0, 1.9), size=(620, 620), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("justice_jaw.png"), anim, "jaw", 0.35, yaw=10, pitch=4,
                       show_body=False, scale=4.0, center=(0, 2.2), size=(620, 620), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("justice_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
