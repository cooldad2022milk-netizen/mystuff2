"""
The Gun Devil (the full devil, not the fiend) - entity model (entity/devil/gun_devil) and animations.

Reference points:
  * a towering airborne humanoid; rifle arms the size of buildings
  * a skeletal torso crammed with shrieking human heads; a pistol barrel juts from its bony face
  * six belts of 7.62 ammunition hang where its legs should be
  * it kills with precise mass volleys (the Gun Devil killed a million people in minutes)
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
    a.add("bone", kind="bone", color=(214, 204, 184))
    a.add("bone_dk", kind="bone", color=(150, 140, 124))
    a.add("flesh", kind="flesh", color=(150, 50, 50))
    a.add("head", kind="skin", color=(200, 170, 150))
    a.add("scream", kind="void", color=(30, 6, 10))
    a.add("steel", kind="metal", color=(70, 72, 80), scratches=6)
    a.add("steel_dk", kind="metal", color=(40, 42, 48), scratches=3)
    a.add("wood", kind="fiber", color=(110, 70, 40))
    a.add("brass", kind="metal", color=(206, 164, 82), scratches=2)
    a.add("belt", kind="fiber", color=(110, 100, 70))
    a.add("muzzle", kind="glow", color=(255, 160, 40), color2=(255, 240, 200), emissive=True)
    a.add("eye", kind="glow", color=(255, 60, 30), color2=(255, 200, 120), emissive=True)
    return a


def rifle(bone, stock, muzzle, scale=1.0):
    """A rifle along stock->muzzle: stock, receiver with magazine, handguard, long barrel, front sight."""
    stock = np.asarray(stock, dtype=float)
    muzzle = np.asarray(muzzle, dtype=float)
    d = norm(muzzle - stock)
    L = np.linalg.norm(muzzle - stock)
    down = norm(np.cross(d, np.cross(np.array([0, 1.0, 0]), d)) * -1) if abs(d[1]) < 0.95 else np.array([0, 0, -1.0])
    s = scale
    bone.obox(stock + d * L * 0.12, d, (3.0 * s, L * 0.24, 4.0 * s), "wood", up=down)
    bone.obox(stock + d * L * 0.33, d, (3.4 * s, L * 0.2, 4.4 * s), "steel", up=down)
    bone.obox(stock + d * L * 0.33 + down * 4.2 * s, down, (2.4 * s, 5.0 * s, 1.6 * s), "steel_dk", up=d)   # magazine
    bone.obox(stock + d * L * 0.5, d, (2.6 * s, L * 0.16, 3.0 * s), "wood", up=down)
    bone.cylinder(stock + d * L * 0.78, d, 0.9 * s, L * 0.44, "steel_dk", segments=10)
    bone.cylinder(muzzle - d * 0.6, d, 1.2 * s, 1.4, "steel", segments=10)
    bone.obox(muzzle - d * 2.5 - down * 1.4 * s, d, (0.5 * s, 1.2, 1.6 * s), "steel", up=down)
    return d


def belt(bone, top, bottom, sway=0.0):
    """A hanging belt of cartridges (brass cases, steel tips, canvas webbing)."""
    top = np.asarray(top, dtype=float)
    bottom = np.asarray(bottom, dtype=float)
    mid = (top + bottom) / 2 + np.array([sway, 0, 1.5])
    path = shapes.polyline([top, mid, bottom])
    f = shapes.loft(path, 1.6, 0.3, up=(0, 0, 1))
    shapes.shell(bone, f, 4, 12, "belt", thick=0.25)
    n = 16
    for k in range(n):
        t = (k + 0.5) / n
        p = np.asarray(path(t), dtype=float)
        q = np.asarray(path(min(1.0, t + 0.01)), dtype=float)
        along = norm(q - p)
        side = norm(np.cross(along, np.array([0, 0, 1.0])))
        bone.cylinder(p + np.array([0, 0, -0.5]), side, 0.45, 2.6, "brass", segments=6)
        bone.cbox(p + side * 1.5 + np.array([0, 0, -0.5]), (0.5, 0.5, 0.5), "steel")


def build():
    atlas = materials()
    m = Model("csm.gun_devil", atlas, density=2.0, seed=221)
    root = m.bone("root", pivot=(0, 0, 0))
    body = m.bone("body", parent="root", pivot=(0, 50, 0))
    # skeletal torso: spine, flaring ribs, and heads crammed between them
    spine = [np.array([0, 48.0, 3.0]), np.array([0, 66.0, 4.0]), np.array([0, 86.0, 3.0])]
    shapes.shell(body, shapes.loft(shapes.polyline(spine), 2.4, 2.4), 8, 10, "bone_dk", thick=0.35)
    for k in range(8):
        y = 56.0 + k * 4.0
        w = 16.0 - abs(k - 4) * 1.0
        for s in (-1, 1):
            pts = [np.array([s * (1.5 + w * t), y - 2.2 * t * t, 3.5 - 15.0 * math.sin(t * math.pi * 0.8)])
                   for t in np.linspace(0, 1, 6)]
            body.curve(pts, 1.6, 1.1, 1.4, 1.0, "bone")
    body.curve([np.array([0, 56.0, -11.5]), np.array([0, 72.0, -12.0]), np.array([0, 86.0, -11.0])], 2.0, 2.0, 1.6, 1.6,
               "bone")
    rng = np.random.default_rng(41)
    heads = []
    for k in range(14):
        c = np.array([rng.uniform(-10.0, 10.0), 56.0 + k * 2.3 + rng.uniform(-1, 1), rng.uniform(-7.0, 0.0)])
        shapes.shell(body, shapes.ellipsoid(c, (3.4, 3.9, 3.4)), 8, 6, "head", thick=0.3)
        body.obox(c + np.array([0, -1.2, -3.3]), (0, 1, 0), (1.9, 2.6, 0.5), "scream", up=(0, 0, -1))
        for s in (-1, 1):
            body.cbox(c + np.array([s * 1.1, 0.9, -3.2]), (0.8, 0.8, 0.4), "scream")
        heads.append(c)
    # pelvis
    shapes.shell(body, shapes.ellipsoid((0, 50.0, 1.0), (12.0, 5.0, 7.0), e_lat=0.8, e_lon=0.8), 12, 6, "bone",
                 thick=0.4)
    # six belts of ammunition where the legs should be
    belts = []
    for k in range(6):
        x = -10.0 + k * 4.0
        name = "belt%d" % k
        b = m.bone(name, parent="body", pivot=(x, 47.0, 1.0))
        belt(b, (x, 47.0, 1.0), (x * 1.3, 2.0 + (k % 2) * 5.0, 3.0), sway=(k - 2.5) * 1.2)
        belts.append(name)
    # rifle arms the size of buildings
    for side, name in ((-1, "right_arm"), (1, "left_arm")):
        sh = np.array([side * 19.0, 86.0, 2.0])
        arm = m.bone(name, parent="body", pivot=tuple(sh))
        shapes.shell(arm, shapes.ellipsoid(sh, (7.5, 7.5, 7.5)), 10, 6, "flesh", thick=0.4)
        mz = sh + np.array([side * 8.0, -46.0, -50.0])
        rifle(arm, sh + np.array([side * 2.0, -4.0, 6.0]), mz, scale=3.0)
        fl = m.bone("fx_volley_" + ("right" if side < 0 else "left"), parent=name, pivot=tuple(mz))
        d = norm(mz - sh)
        fl.spike(mz + d * 0.5, d, 9.0, 5.0, 5.0, "muzzle", steps=3)
    # the bony face with a pistol barrel through it
    head = m.bone("head", parent="body", pivot=(0, 88, 2))
    look = m.bone("look", parent="head", pivot=(0, 90, 2))
    shapes.shell(look, shapes.ellipsoid((0, 96.0, 1.0), (6.0, 7.0, 6.0), e_lat=0.8, e_lon=0.8), 12, 10, "bone",
                 thick=0.4)
    for s in (-1, 1):
        look.cylinder((s * 2.4, 97.5, -4.6), (0, 0, -1), 1.5, 0.5, "scream", segments=10)
        look.cbox((s * 2.4, 97.5, -5.0), (0.8, 0.8, 0.3), "eye")
    for k in range(7):
        look.spike((-2.4 + k * 0.8, 91.2, -4.6), (0, -1, -0.2), 1.4, 0.6, 0.4, "bone", steps=2)
    look.cylinder((0, 95.0, -6.0), (0, 0, -1), 1.1, 9.0, "steel_dk", segments=10)
    look.obox((0, 95.0, -3.0), (0, 0, -1), (2.8, 5.0, 3.6), "steel", up=(0, 1, 0))
    look.obox((0, 97.4, -2.5), (0, 0, 1), (1.2, 3.0, 1.0), "steel_dk", up=(0, 1, 0))      # hammer
    fx = m.bone("fx_storm_face", parent="look", pivot=(0, 95, -11))
    fx.spike((0, 95.0, -10.8), (0, 0, -1), 5.0, 3.0, 3.0, "muzzle", steps=3)
    for name in ("look", "fx_storm_face"):
        m.by_name[name].scale_about((0, 88.0, 2.0), 1.7)
    geo, tex, glow, anim_path = dk.devil_paths("gun_devil")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=223)
    anims = animations(belts)
    save_animations(anim_path, anims)
    print("gun devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def belt_sway(a, belts, t0, t1, amp, freq):
    steps = max(2, int((t1 - t0) * 8))
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        for k, b in enumerate(belts):
            ph = 2 * math.pi * freq * t + k * 0.8
            a.rot(b, t, (amp * math.sin(ph), 0, amp * 0.5 * math.cos(ph)))


def animations(belts):
    A = []
    idle = Anim("idle", 3.0, loop=True)
    belt_sway(idle, belts, 0, 3.0, 5, 1 / 3.0)
    for i in range(9):
        t = 3.0 * i / 8
        ph = 2 * math.pi * i / 8
        idle.pos("root", t, (0, 2.0 * math.sin(ph), 0))
        idle.rot("right_arm", t, (4 * math.sin(ph), 0, 3))
        idle.rot("left_arm", t, (4 * math.sin(ph + 1), 0, -3))
    A.append(idle)
    mv = Anim("move", 2.0, loop=True)
    belt_sway(mv, belts, 0, 2.0, 16, 0.5)
    for i in range(9):
        t = 2.0 * i / 8
        ph = 2 * math.pi * i / 8
        mv.pos("root", t, (0, 2.0 * math.sin(ph), 0))
        mv.rot("body", t, (14, 0, 2 * math.sin(ph)))
    A.append(mv)
    # Massacre: arms thrown wide, every barrel firing
    ms = Anim("massacre", 2.0)
    for side, s in (("right_arm", 1), ("left_arm", -1)):
        ms.rot(side, 0, (0, 0, 0)).rot(side, 0.4, (-40, 0, s * 60), "easeOutQuad")
        for i in range(10):
            ms.rot(side, 0.5 + i * 0.1, (-40 + (5 if i % 2 else -5), 0, s * 60))
        ms.rot(side, 2.0, (0, 0, 0))
    ms.rot("head", 0.4, (-20, 0, 0)).rot("head", 2.0, (0, 0, 0))
    ms.scale("fx_storm_face", 0, 1.0).scale("fx_storm_face", 2.0, 1.0)
    A.append(ms)
    # Rifle volley: the arms swing up to aim and recoil shot after shot
    vl = Anim("volley", 1.5)
    for side in ("right_arm", "left_arm"):
        vl.rot(side, 0, (0, 0, 0)).rot(side, 0.35, (-35, 0, 0), "easeOutQuad")
        for i in range(9):
            t = 0.4 + i * 0.1
            vl.rot(side, t, (-35 + (6 if (i + (side == "left_arm")) % 2 else 0), 0, 0))
        vl.rot(side, 1.5, (0, 0, 0))
    A.append(vl)
    # Belt lash: the ammunition belts whip round
    bl = Anim("belts", 1.2)
    for k, b in enumerate(belts):
        bl.rot(b, 0, (0, 0, 0)).rot(b, 0.35, (-60, 0, (k - 2.5) * 12), "easeOutQuad")
        bl.rot(b, 0.6, (50, 0, -(k - 2.5) * 12), "easeInOutQuad").rot(b, 1.2, (0, 0, 0))
    bl.rot("body", 0, (0, 0, 0)).rot("body", 0.4, (0, 90, 0)).rot("body", 0.8, (0, 270, 0)).rot("body", 1.2, (0, 360, 0))
    A.append(bl)
    # Bullet storm: shudders as every barrel fires in all directions
    st = Anim("storm", 2.0)
    for i in range(21):
        t = i * 0.1
        j = 3 if i % 2 else -3
        st.rot("body", t, (j, j, 0))
        st.pos("root", t, (0, 0.5 * j, 0))
    A.append(st)
    A.append(Anim("drink", 1.0))
    death = Anim("death", 2.0, loop="hold_on_last_frame")
    death.pos("root", 0, (0, 0, 0)).pos("root", 1.6, (0, -30, 0), "easeInQuad")
    death.rot("body", 1.6, (40, 0, 25), "easeInQuad")
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 1.0, from_scale=0.1))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


def render_previews(geo, tex, anim):
    shots = [
        preview.render(geo, tex, preview_path("gundevil_front.png"), anim, "idle", 0.0, yaw=20, pitch=6,
                       show_body=False, scale=2.8, center=(0, 3.4), size=(620, 760), bg=(150, 170, 200)),
        preview.render(geo, tex, preview_path("gundevil_side.png"), anim, "idle", 0.0, yaw=90, pitch=6,
                       show_body=False, scale=2.8, center=(0, 3.4), size=(620, 760), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("gundevil_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
