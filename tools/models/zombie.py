"""
The Zombie Devil - entity model (entity/devil/zombie), texture atlas and GeckoLib animations.

Reference points:
  * a huge, limbless torso that floats, its organs bared through a torn-open front
  * a brain on top sprouting tentacles - the cords that tether its zombies
  * a big severed human face stuck onto its right side
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
    opening = lambda u, v: (u < 0.14 or u > 0.86) and 0.32 < v < 0.74
    shapes.shell(b, torso, 20, 16, "rot", skip=opening, thick=0.55,
                 mat_fn=lambda u, v: "rot_dk" if v < 0.22 else ("flesh" if (u < 0.2 or u > 0.8) else "rot"))
    # the torn-open front: a raw cavity, exposed ribs and organs
    cav = shapes.ellipsoid((0, 34.0, -6.0), (10.0, 11.0, 6.5))
    shapes.shell(b, cav, 12, 10, "organ_dk", u0=-0.25, u1=0.25, thick=0.5)
    for k in range(6):
        y = 27.0 + k * 3.0
        for s in (-1, 1):
            pts = [np.array([s * (1.5 + 10.5 * t), y + 1.5 * math.sin(t * math.pi), -12.2 + 5.0 * t * t]) for t in
                   np.linspace(0, 1, 5)]
            b.curve(pts, 1.1, 0.8, 1.0, 0.7, "rib")
    b.curve([np.array([0, 25.0, -12.0]), np.array([0, 33.0, -13.0]), np.array([0, 43.0, -12.5])], 1.4, 1.4, 1.2, 1.2,
            "rib")
    # a heart, lungs and coils of gut spilling in the cavity
    shapes.shell(b, shapes.ellipsoid((3.0, 38.0, -9.0), (3.2, 3.8, 2.8)), 10, 6, "organ", thick=0.35)
    for s in (-1, 1):
        shapes.shell(b, shapes.ellipsoid((s * 6.5, 37.0, -8.0), (3.5, 5.5, 3.0)), 10, 6, "organ_dk", thick=0.35)
    gut = [np.array([math.sin(t * 5.2) * 5.0, 28.0 - t * 5.0 + math.cos(t * 7) * 1.5, -9.5 - math.cos(t * 5.2) * 1.5])
           for t in np.linspace(0, 1, 12)]
    shapes.shell(b, shapes.loft(shapes.polyline(gut), 1.3, 1.2), 8, 16, "gut", thick=0.3)
    hang = [np.array([-3.0, 23.0, -12.0]), np.array([-4.0, 18.0, -13.0]), np.array([-2.5, 13.0, -12.0])]
    shapes.shell(b, shapes.loft(shapes.polyline(hang), shapes.profile((0, 1.3), (1, 0.8)), 1.1), 8, 8, "gut", thick=0.3)
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
    # its own gaping maw at the top of the torso, under the brain
    shapes.shell(look, shapes.ellipsoid((0, 50.5, -8.5), (5.5, 2.4, 2.0)), 10, 6, "mouth", thick=0.3)
    for k in range(9):
        x = -4.4 + k * 1.1
        look.spike((x, 52.6, -9.6), (0, -1, -0.1), 1.6, 0.7, 0.35, "teeth", steps=3)
        look.spike((x + 0.55, 48.4, -9.4), (0, 1, -0.1), 1.3, 0.6, 0.35, "teeth", steps=3)
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
    # tentacles: the cords that tether its zombies
    names = []
    for k in range(6):
        a = math.radians(k * 60 + 20)
        base = np.array([math.cos(a) * 5.5, 60.0, math.sin(a) * 4.5])
        name = "tendril%d" % k
        t = m.bone(name, parent="brain", pivot=tuple(base))
        out_d = np.array([math.cos(a), 0, math.sin(a)])
        pts = [base, base + out_d * 6 + np.array([0, 4, 0]), base + out_d * 12 + np.array([0, 1, 0]),
               base + out_d * 16 + np.array([0, -8, 0]), base + out_d * 17 + np.array([0, -20, 0])]
        shapes.shell(t, shapes.loft(shapes.polyline(pts), shapes.profile((0, 1.1), (0.5, 0.8), (1, 0.25)),
                                    shapes.profile((0, 1.0), (1, 0.25))), 6, 14, "cord", thick=0.3)
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
