"""
The Zombie Devil - entity model (entity/devil/zombie), texture atlas and GeckoLib animations.

Reference points (manga ch. 1 / anime ep. 1):
  * a massive LIMBLESS TORSO with an EXPOSED BRAIN where its neck should be
  * its FACE is in its torso (eyes and a huge mouth)
  * its lower half is mainly TENTACLES it stands on - they connect it to the zombies around it
  * a large human-like face emerges from the RIGHT side of the torso
  * bites people into zombies, controls them, raises corpses, heals on blood
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
    a.add("flesh", kind="flesh", color=(150, 110, 96))
    a.add("rot", kind="skin", color=(116, 126, 88))
    a.add("rot_dk", kind="skin", color=(78, 86, 58))
    a.add("rib", kind="bone", color=(220, 206, 178))
    a.add("organ", kind="flesh", color=(170, 56, 60))
    a.add("organ_dk", kind="flesh", color=(110, 30, 38))
    a.add("gut", kind="flesh", color=(196, 120, 120))
    a.add("brain", kind="flesh", color=(214, 150, 160))
    a.add("brain_dk", kind="flesh", color=(170, 100, 116))
    a.add("cord", kind="flesh", color=(150, 74, 90))
    a.add("face", kind="skin", color=(200, 184, 164))
    a.add("face_dk", kind="skin", color=(150, 132, 116))
    a.add("eye", kind="bone", color=(230, 226, 210))
    a.add("pupil", kind="void", color=(14, 12, 12))
    a.add("mouth", kind="void", color=(40, 10, 14))
    a.add("teeth", kind="teeth", color=(226, 214, 186))
    a.add("glow", kind="glow", color=(220, 60, 60), color2=(255, 180, 150), emissive=True)
    return a


TORSO_C = np.array([0.0, 38.0, 0.0])


def build_body(m):
    root = m.bone("root", pivot=(0, 0, 0))
    b = m.bone("body", parent="root", pivot=(0, 34, 0))
    look = m.bone("look", parent="body", pivot=(0, 44, 0))
    # a vast rotting torso tapering to a ragged stump underneath (no limbs: it floats)
    torso = shapes.loft(shapes.polyline([(0, 12.0, 1.0), (0, 22.0, 0.5), (0, 36.0, 0.0), (0, 50.0, 0.5), (0, 56.0, 1.0)]),
                        shapes.profile((0, 3.0), (0.18, 9.0), (0.45, 16.0), (0.8, 15.0), (1, 9.0)),
                        shapes.profile((0, 3.0), (0.18, 7.5), (0.45, 12.5), (0.8, 12.0), (1, 7.0)), up=(0, 0, -1))
    shapes.shell(b, torso, 20, 16, "rot", thick=0.55,
                 mat_fn=lambda u, v: "rot_dk" if v < 0.22 or int(u * 20 + v * 7) % 6 == 0 else "rot")
    # its face is in its torso: two big staring eyes over a huge gaping mouth of human teeth
    for sx in (-1, 1):
        p, n, du, dv = shapes.surface_frame(torso, 0.09 if sx > 0 else 0.91, 0.66)
        shapes.shell(look, shapes.ellipsoid(p + n * 0.6, (2.6, 2.2, 1.6)), 10, 6, "eye", thick=0.3)
        look.cylinder(p + n * 2.0, n, 1.0, 0.3, "pupil", segments=8)
        shapes.shell(look, shapes.ellipsoid(p + n * 0.8 + np.array([0, 2.3, 0]), (3.0, 0.8, 1.2)), 8, 4, "rot_dk",
                     thick=0.3)
    mp, mn, _, _ = shapes.surface_frame(torso, 0.0, 0.44)
    shapes.shell(look, shapes.ellipsoid(mp + mn * 0.3, (7.0, 4.2, 1.6)), 12, 8, "mouth", thick=0.3)
    for k in range(11):
        x = -5.5 + k * 1.1
        look.obox((x, mp[1] + 3.3, mp[2] - 1.0), (0, -1, 0), (0.95, 1.6, 0.6), "teeth", up=(0, 0, -1))
        look.obox((x + 0.3, mp[1] - 3.2, mp[2] - 0.9), (0, 1, 0), (0.95, 1.4, 0.6), "teeth", up=(0, 0, -1))
    for sx in (-1, 1):  # lips
        look.curve([mp + np.array([x, sx * 4.2 - 0.02 * x * x * sx, -1.2]) for x in np.linspace(-7.0, 7.0, 7)], 1.0,
                   1.0, 0.9, 0.9, "flesh")
    # the severed human face stuck onto its right side (her right = -x)
    face_c = np.array([-15.0, 38.0, -2.0])
    fb = m.bone("face", parent="look", pivot=tuple(face_c))
    face = shapes.ellipsoid(face_c, (3.4, 7.5, 6.0), frame=np.eye(3))
    shapes.shell(fb, face, 12, 12, "face", u0=0.55, u1=0.95, thick=0.4)
    fn = np.array([-1.0, 0.0, -0.25])
    for dz in (-2.6, 2.2):
        c = face_c + np.array([-2.3, 2.2, dz])
        fb.cylinder(c, fn, 1.3, 0.5, "eye", segments=10)
        fb.cylinder(c + fn * 0.3, fn, 0.55, 0.2, "pupil", segments=8)
    fb.obox(face_c + np.array([-2.6, -3.6, -0.2]), (0, 0, 1), (0.8, 4.4, 0.5), "mouth", up=fn)
    for k in range(6):
        fb.cbox(face_c + np.array([-2.7, -3.25, -2.0 + k * 0.8]), (0.3, 0.5, 0.55), "teeth")
    fb.obox(face_c + np.array([-2.9, 0.4, -0.2]), (0, 1, 0), (1.0, 2.0, 0.8), "face_dk", up=fn)   # nose
    fb.scale_about(face_c + np.array([-2.0, 0, 0]), 1.4)
    return root, b, look


def build_brain(m):
    br = m.bone("brain", parent="look", pivot=(0, 56, 0))
    rng = np.random.default_rng(12)
    for k in range(26):
        u = rng.uniform(-1, 1)
        a = rng.uniform(0, 2 * math.pi)
        p = np.array([math.cos(a) * 6.5 * math.sqrt(1 - u * u), 58.0 + abs(u) * 5.0, math.sin(a) * 5.5 * math.sqrt(1 - u * u)])
        d = norm([rng.uniform(-1, 1), rng.uniform(-0.3, 0.3), rng.uniform(-1, 1)])
        frame = __import__("csmgen.geo", fromlist=["frame_from"]).frame_from(d, (0, 1, 0))
        shapes.shell(br, shapes.ellipsoid(p, (1.5, 2.6, 1.3), frame=frame), 6, 4, "brain" if k % 2 else "brain_dk",
                     thick=0.35)
    shapes.shell(br, shapes.ellipsoid((0, 58.5, 0), (6.8, 4.8, 5.8)), 12, 8, "brain_dk", v0=0.3, thick=0.4)
    # its lower half is tentacles: it stands on them, and they are the cords that tether its zombies
    names = []
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        base = np.array([math.cos(a) * 5.0, 15.0, math.sin(a) * 4.0])
        name = "tendril%d" % k
        t = m.bone(name, parent="body", pivot=tuple(base))
        out_d = np.array([math.cos(a), 0, math.sin(a)])
        pts = [base, base + out_d * 5 + np.array([0, -3, 0]), base + out_d * 10 + np.array([0, -9, 0]),
               base + out_d * 14 + np.array([0, -14.2, 0]), base + out_d * 20 + np.array([0, -14.6, 0])]
        shapes.shell(t, shapes.loft(shapes.polyline(pts), shapes.profile((0, 2.4), (0.5, 1.6), (1, 0.5)),
                                    shapes.profile((0, 2.2), (1, 0.45))), 7, 12, "cord", thick=0.3)
        t.cbox(pts[-1], (0.8, 0.8, 0.8), "glow")
        names.append(name)
    return names


def build():
    atlas = materials()
    m = Model("csm.zombie_devil", atlas, density=2.0, seed=171)
    build_body(m)
    tendrils = build_brain(m)
    geo, tex, glow, anim_path = dk.devil_paths("zombie")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=173)
    anims = animations(tendrils)
    save_animations(anim_path, anims)
    print("zombie devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def sway(a, bones, t0, t1, amp, freq, lift=0.0):
    steps = max(2, int((t1 - t0) * 8))
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        for k, b in enumerate(bones):
            ph = 2 * math.pi * freq * t + k * 1.1
            a.rot(b, t, (amp * math.sin(ph) - lift, amp * 0.5 * math.cos(ph), amp * 0.4 * math.sin(ph * 1.3)))


def animations(tendrils):
    A = []
    idle = Anim("idle", 4.0, loop=True)
    sway(idle, tendrils, 0, 4.0, 10, 0.25)
    for i in range(9):
        t = 4.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.pos("root", t, (0, 1.5 * math.sin(ph), 0))
        idle.rot("body", t, (2 * math.sin(ph), 0, 1.5 * math.cos(ph)))
    A.append(idle)
    mv = Anim("move", 2.0, loop=True)
    sway(mv, tendrils, 0, 2.0, 16, 0.5)
    for i in range(9):
        t = 2.0 * i / 8
        ph = 2 * math.pi * i / 8
        mv.pos("root", t, (0, 1.5 * math.sin(ph), 0))
        mv.rot("body", t, (10 + 2 * math.sin(ph), 0, 3 * math.cos(ph)))
    A.append(mv)

    # Infectious bite: it lunges forward and down, the maw snapping
    bt = Anim("bite", 1.0)
    bt.rot("body", 0, (0, 0, 0)).rot("body", 0.3, (-10, 0, 0)).rot("body", 0.45, (28, 0, 0), "easeInQuad")
    bt.rot("body", 1.0, (0, 0, 0))
    bt.pos("root", 0.45, (0, -4, -3), "easeInQuad").pos("root", 1.0, (0, 0, 0))
    A.append(bt)
    # Call the horde: the tendrils rear up and plunge into the ground
    hd = Anim("horde", 2.0)
    for k, b in enumerate(tendrils):
        hd.rot(b, 0, (0, 0, 0)).rot(b, 0.5, (-50, 0, 0), "easeOutQuad").rot(b, 0.8, (60, 0, 0), "easeInQuad")
        hd.rot(b, 1.6, (55, 0, 0)).rot(b, 2.0, (0, 0, 0))
    hd.rot("body", 0.5, (-8, 0, 0)).rot("body", 0.8, (6, 0, 0)).rot("body", 2.0, (0, 0, 0))
    A.append(hd)
    # Brain tendrils: they whip round in a full circle
    td = Anim("tendrils", 1.2)
    for k, b in enumerate(tendrils):
        td.rot(b, 0, (0, 0, 0)).rot(b, 0.3, (-30, 0, 0)).rot(b, 0.55, (45, 90, 0), "easeOutQuad")
        td.rot(b, 0.8, (40, 200, 0)).rot(b, 1.2, (0, 360, 0))
    td.rot("brain", 0, (0, 0, 0)).rot("brain", 1.2, (0, 360, 0))
    A.append(td)
    # Blood feast: it swells as it gorges
    fs = Anim("feast", 2.0)
    for i in range(11):
        t = 2.0 * i / 10
        fs.scale("body", t, 1.0 + 0.08 * math.sin(i * 1.4) + 0.04 * i / 10)
    fs.scale("body", 2.0, 1.0)
    sway(fs, tendrils, 0, 2.0, 22, 1.5, lift=-20)
    A.append(fs)
    A.append(Anim("drink", 1.0))
    death = Anim("death", 1.8, loop="hold_on_last_frame")
    death.pos("root", 0, (0, 0, 0)).pos("root", 1.2, (0, -12, 0), "easeInQuad")
    death.rot("body", 1.2, (20, 0, 35), "easeInQuad")
    for b in tendrils:
        death.rot(b, 0.8, (80, 0, 0))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("zombie_front.png"), anim, "idle", 0.0, yaw=15, pitch=8, show_body=False,
                       scale=5.2, center=(0, 2.2), size=(620, 620)),
        preview.render(geo, tex, preview_path("zombie_side.png"), anim, "idle", 0.0, yaw=-80, pitch=8,
                       show_body=False, scale=5.2, center=(0, 2.2), size=(620, 620)),
        preview.render(geo, tex, preview_path("zombie_back.png"), anim, "idle", 0.0, yaw=160, pitch=8,
                       show_body=False, scale=5.2, center=(0, 2.2), size=(620, 620)),
    ]
    return preview.contact_sheet(shots, preview_path("zombie_sheet.png"), cols=3)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
