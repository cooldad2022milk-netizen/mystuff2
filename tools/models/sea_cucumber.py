"""
The Sea Cucumber Devil - entity model (entity/devil/sea_cucumber), texture atlas and GeckoLib animations.

Reference points (anime ep. 4, Power smashes it):
  * a fleshy, upright cylinder with countless human fingers growing out of it on every side
  * a large orifice on top, and a human skull emerging from just underneath it
  * anime colours: a magenta and blue body, blue fingers, a white skull
"""
import math

import numpy as np

from common import preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk


def materials():
    a = Atlas(256, 64)
    a.add("body", kind="flesh", color=(176, 56, 132))
    a.add("body_dk", kind="skin", color=(64, 70, 168))
    a.add("finger", kind="skin", color=(104, 132, 212))
    a.add("nail", kind="bone", color=(200, 214, 240))
    a.add("skull", kind="bone", color=(226, 214, 190))
    a.add("socket", kind="void", color=(16, 10, 10))
    a.add("maw", kind="void", color=(50, 14, 20))
    a.add("rim", kind="flesh", color=(180, 90, 90))
    a.add("gut", kind="flesh", color=(190, 110, 120))
    return a


def build():
    atlas = materials()
    m = Model("csm.sea_cucumber_devil", atlas, density=2.0, seed=191)
    root = m.bone("root", pivot=(0, 0, 0))
    body = m.bone("body", parent="root", pivot=(0, 2, 0))
    look = m.bone("look", parent="body", pivot=(0, 22, 0))
    # an upright, bulging fleshy cylinder, slightly bent
    path = shapes.polyline([(0, 0.5, 0.5), (0, 8.0, -0.3), (0, 16.0, 0.4), (0, 24.0, 0.0), (0, 27.5, 0.2)])
    f = shapes.loft(path, shapes.profile((0, 5.5), (0.2, 7.0), (0.55, 7.6), (0.85, 6.6), (1, 4.2)),
                    shapes.profile((0, 5.2), (0.2, 6.6), (0.55, 7.2), (0.85, 6.2), (1, 4.0)), up=(0, 0, -1))
    shapes.shell(body, f, 16, 12, "body", thick=0.45,
                 mat_fn=lambda u, v: "body_dk" if math.sin(u * 37.0 + v * 23.0) * math.cos(u * 11.0 - v * 17.0) > 0.45
                 else "body")
    # the opening on top: a ring of lips round a dark hole, tentacle-fingers curling out of it
    body.ring((0, 27.4, 0.2), (0, 1, 0), 3.4, 1.0, 1.0, "rim", count=14)
    body.cylinder((0, 27.2, 0.2), (0, 1, 0), 3.0, 0.8, "maw", segments=12)
    tops = []
    for k in range(8):
        a = math.radians(k * 45)
        d = np.array([math.cos(a) * 0.6, 1, math.sin(a) * 0.6])
        tops.append((np.array([math.cos(a) * 3.0, 27.6, 0.2 + math.sin(a) * 3.0]), d))
    ft = m.bone("top_fingers", parent="body", pivot=(0, 27.5, 0))
    for p, d in tops:
        shapes.horn(ft, p, d, 4.0, 0.55, mat="finger", tip_mat="nail", sections=4, around=6, r1=0.35, tip_from=0.8,
                    bend_axis=np.cross(d, (0, 1, 0)) + np.array([0, 0, 0.001]), bend=50)
    # human fingers bristling all over the body
    rng = np.random.default_rng(19)
    for k in range(120):
        u = rng.uniform(0, 1)
        v = rng.uniform(0.05, 0.92)
        if (u < 0.13 or u > 0.87) and 0.68 < v < 0.97:
            continue  # leave the skull clear
        p, n, du, dv = shapes.surface_frame(f, u, v)
        d = norm(n + np.array([0, rng.uniform(-0.3, 0.6), 0]))
        shapes.horn(body, p - n * 0.2, d, rng.uniform(2.0, 3.6), 0.5, mat="finger", tip_mat="nail", sections=3,
                    around=4, r1=0.38, tip_from=0.75, bend_axis=np.cross(d, (0, 1, 0)) + np.array([0.001, 0, 0]),
                    bend=rng.uniform(-40, 40))
    # the skull pushing out of the body just under the opening
    sk = shapes.ellipsoid((0, 23.6, -6.0), (3.2, 3.4, 2.8), e_lat=0.8, e_lon=0.8)
    shapes.shell(look, sk, 12, 8, "skull", thick=0.35)
    for s in (-1, 1):
        look.cylinder((s * 1.3, 24.4, -8.6), (0, 0, -1), 0.9, 0.3, "socket", segments=10)
    look.obox((0, 23.0, -8.7), (0, 1, 0), (0.6, 0.8, 0.2), "socket", up=(0, 0, -1))
    jaw = m.bone("jaw", parent="look", pivot=(0, 21.6, -4.8))
    shapes.shell(jaw, shapes.ellipsoid((0, 20.8, -6.6), (2.3, 1.2, 1.8)), 8, 5, "skull", thick=0.3)
    for k in range(6):
        jaw.cbox((-1.5 + k * 0.6, 21.5, -8.2), (0.45, 0.6, 0.35), "nail")
    # spewed guts (only while spewing)
    g = m.bone("fx_spew_guts", parent="body", pivot=(0, 27.5, 0))
    guts = [np.array([0, 27.5, 0]), np.array([0, 33.0, -3.0]), np.array([0, 31.0, -9.0]), np.array([0, 24.0, -14.0])]
    shapes.shell(g, shapes.loft(shapes.polyline(guts), shapes.profile((0, 1.4), (1, 0.6)), 1.2), 8, 12, "gut",
                 thick=0.3)
    # stubby tube feet underneath
    for k in range(6):
        a = math.radians(k * 60 + 30)
        p = np.array([math.cos(a) * 4.5, 1.0, math.sin(a) * 4.5])
        shapes.horn(body, p + np.array([0, 1.2, 0]), (math.cos(a) * 0.4, -1, math.sin(a) * 0.4), 1.8, 0.7,
                    mat="finger", sections=2, around=6, r1=0.5)
    geo, tex, glow, anim_path = dk.devil_paths("sea_cucumber")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=193)
    anims = animations()
    save_animations(anim_path, anims)
    print("sea cucumber devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    idle = Anim("idle", 2.8, loop=True)
    for i in range(9):
        t = 2.8 * i / 8
        ph = 2 * math.pi * i / 8
        idle.rot("body", t, (3 * math.sin(ph), 0, 4 * math.cos(ph)))
        idle.scale("body", t, (1 + 0.03 * math.sin(ph), 1 - 0.03 * math.sin(ph), 1 + 0.03 * math.sin(ph)))
        idle.rot("top_fingers", t, (0, 20 * math.sin(ph), 0))
    A.append(idle)
    mv = Anim("move", 1.0, loop=True)
    for i in range(9):
        t = 1.0 * i / 8
        ph = 2 * math.pi * i / 8
        mv.scale("body", t, (1 - 0.06 * math.sin(ph), 1 + 0.1 * math.sin(ph), 1 - 0.06 * math.sin(ph)))
        mv.rot("body", t, (8 + 6 * math.sin(ph), 0, 0))
    A.append(mv)
    gr = Anim("grab", 1.0)
    gr.rot("body", 0, (0, 0, 0)).rot("body", 0.3, (-15, 0, 0)).rot("body", 0.45, (30, 0, 0), "easeInQuad")
    gr.rot("body", 1.0, (0, 0, 0))
    gr.rot("jaw", 0.3, (30, 0, 0)).rot("jaw", 0.5, (0, 0, 0))
    A.append(gr)
    sp = Anim("spew", 1.4)
    sp.scale("fx_spew_guts", 0, 0.1).scale("fx_spew_guts", 0.4, 0.1).scale("fx_spew_guts", 0.6, 1.1, "easeOutQuad")
    sp.scale("fx_spew_guts", 1.2, 1.0).scale("fx_spew_guts", 1.4, 0.1)
    sp.rot("body", 0.4, (-20, 0, 0)).rot("body", 0.6, (25, 0, 0), "easeOutQuad").rot("body", 1.4, (0, 0, 0))
    sp.scale("body", 0.4, (1.1, 0.9, 1.1)).scale("body", 0.6, (0.92, 1.1, 0.92)).scale("body", 1.4, 1.0)
    A.append(sp)
    sl = Anim("slam", 1.0)
    sl.rot("root", 0, (0, 0, 0)).rot("root", 0.35, (-20, 0, 0)).rot("root", 0.55, (75, 0, 0), "easeInQuad")
    sl.rot("root", 0.75, (70, 0, 0)).rot("root", 1.0, (0, 0, 0))
    A.append(sl)
    rg = Anim("regen", 2.0)
    for i in range(11):
        t = 2.0 * i / 10
        rg.scale("body", t, 1 + 0.06 * math.sin(i * 1.9))
    rg.scale("body", 2.0, 1.0)
    A.append(rg)
    A.append(Anim("drink", 1.0))
    death = Anim("death", 1.2, loop="hold_on_last_frame")
    death.rot("root", 0, (0, 0, 0)).rot("root", 0.8, (0, 0, 90), "easeInQuad")
    death.scale("body", 1.2, (1.1, 0.8, 1.1))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 0.7, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("seacu_front.png"), anim, "idle", 0.0, yaw=20, pitch=8, show_body=False,
                       scale=14, center=(0, 1.0), size=(520, 620)),
        preview.render(geo, tex, preview_path("seacu_side.png"), anim, "spew", 0.8, yaw=100, pitch=8, show_body=False,
                       scale=12, center=(0, 1.0), size=(520, 620)),
    ]
    return preview.contact_sheet(shots, preview_path("seacu_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
