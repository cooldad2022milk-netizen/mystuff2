"""
Beam (Shark Fiend) - fiend parts model, texture atlas and GeckoLib animations.

Reference points:
  * from the neck down a brawny young man; a pointed snout and a fin sit where a face would be, no apparent eyes,
    a mouth of razor teeth, and a crop of short, bristling black hair beneath
  * tapping his devil side swells the head into a giant shark's skull studded with three sets of eyes
  * or he remakes his whole body into a shark propped up on several long fins that act as legs (Denji rode it)
  * swims through floors and solid earth
"""
import math

import numpy as np

from common import out, preview_path
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes, shapes


def materials():
    a = Atlas(512, 64)
    a.add("shark", kind="skin", color=(112, 138, 160))
    a.add("shark_dk", kind="skin", color=(74, 96, 118))
    a.add("belly", kind="skin", color=(224, 228, 230))
    a.add("teeth", kind="teeth", color=(242, 240, 232))
    a.add("mouth", kind="void", color=(60, 14, 22))
    a.add("gum", kind="flesh", color=(170, 60, 70))
    a.add("hair", kind="fiber", color=(22, 22, 26))
    a.add("gill", kind="void", color=(40, 50, 62))
    a.add("eye", kind="void", color=(8, 8, 10))
    a.add("eye_shine", kind="glow", color=(150, 170, 190), color2=(230, 240, 250), emissive=True)
    return a


def shark_loft(tail, nose, rx, ry, mid=None):
    pts = [tail, nose] if mid is None else [tail] + list(mid) + [nose]
    return shapes.loft(shapes.polyline(pts), rx, ry, up=(0, 1, 0))


def shark_shell(bone, f, nu=16, nv=18, top="shark", belly="belly", belly_width=0.13, skip=None, thick=0.4):
    """Counter-shaded shark skin: grey back, pale belly along the underside (u = 0.5 is the bottom)."""
    def mat(u, v):
        return belly if abs(u - 0.5) < belly_width else top
    shapes.shell(bone, f, nu, nv, top, mat_fn=mat, skip=skip, thick=thick)


def on_top(f, v, sink=0.4):
    """A point sunk slightly into the crown of lofted surface f at v (u = 0 is the top)."""
    p, n, du, dv = shapes.surface_frame(f, 0.0, v)
    return p - n * sink


def fin(bone, root, direction, length, width, mat="shark_dk", bend=30.0, bend_axis=(1, 0, 0), thin=0.22):
    """A flat, swept fin (a flattened horn: wide in the bend plane, thin along bend_axis)."""
    shapes.horn(bone, root, norm(direction), length, width, bend_axis=bend_axis, bend=bend, mat=mat, flat=thin,
                up=np.asarray(bend_axis, dtype=float), sections=8, around=8, r1=0.15, power=1.1)


def eye(bone, p, normal, r, shine=True):
    n = norm(normal)
    bone.cylinder(p - n * 0.05, n, r, 0.5, "eye", segments=10)
    bone.cylinder(p - n * 0.2, n, r * 1.18, 0.35, "shark_dk", segments=10)
    if shine:
        bone.cbox(p + n * 0.22 + np.array([0, r * 0.35, 0]), (r * 0.45, r * 0.45, r * 0.45), "eye_shine")


def gills(bone, f, u, v0, count, step, length, width=0.3):
    for g in range(count):
        p, n, du, dv = shapes.surface_frame(f, u, v0 + g * step)
        bone.obox(p + n * 0.05, (0, 1, 0.2), (width, length, 0.35), "gill", up=n)


def bristles(bone, y0, y1, radius, count, rng, mat="hair"):
    """Short, bristling black hair round the back and sides of the neck, under the shark head: a cropped band with
    stubble sticking out of it."""
    band = shapes.loft(shapes.polyline([(0, y0, 0.5), (0, y1, 0.9)]), radius, radius * 1.02, up=(0, 0, -1))
    shapes.shell(bone, band, 12, 3, mat, u0=0.16, u1=0.84, thick=0.5)
    for k in range(count):
        a = math.radians(62 + 236 * k / (count - 1))
        y = rng.uniform(y0 + 0.3, y1 - 0.2)
        p = np.array([math.sin(a) * radius, y, -math.cos(a) * radius + 0.6])
        d = norm([math.sin(a), rng.uniform(-0.3, 0.2), -math.cos(a)])
        bone.spike(p - d * 0.3, d, rng.uniform(0.6, 1.0), 0.45, 0.35, mat, steps=2)


def hinge(f, v):
    """Jaw pivot: just inside the underside of the loft at v."""
    p, n, du, dv = shapes.surface_frame(f, 0.5, v)
    return tuple(p - n * 0.8)


# ------------------------------------------------------------------------------------------ head
def build_head(m):
    rng = __import__("random").Random(5)
    m.bone("head", pivot=(0, 24, 0))
    # everyday: the head is a shark's, snout jutting forward and up; no eyes (prop_ = hidden when the skull swells)
    h = m.bone("prop_shark_head", parent="head", pivot=(0, 24, 0))
    rx = shapes.profile((0, 0.6), (0.07, 3.3), (0.2, 4.5), (0.42, 4.5), (0.66, 3.6), (0.84, 2.3), (0.95, 1.0), (1, 0.15))
    ry = shapes.profile((0, 0.6), (0.07, 3.2), (0.2, 4.1), (0.42, 4.1), (0.66, 3.3), (0.84, 2.1), (0.95, 0.9), (1, 0.15))
    f = shark_loft((0, 27.4, 4.8), (0, 31.4, -10.6), rx, ry)
    mouth = shapes.Mouth(f, 0.5, 0.2, 0.42, 0.83)
    shark_shell(h, f, skip=mouth.skip)
    j = m.bone("prop_jaw", parent="prop_shark_head", pivot=hinge(f, 0.42), rotation=(6, 0, 0))
    mouth.build(h, j, "belly", upper=11, lower=10, tooth_len=1.45, tooth_w=0.62, nu=6, nv=7, gum_mat="gum")
    gills(h, f, 0.26, 0.2, 3, 0.05, 2.4)
    gills(h, f, 0.74, 0.2, 3, 0.05, 2.4)
    fin(h, on_top(f, 0.34), (0, 1, 0.5), 6.2, 2.6, bend=38)
    bristles(h, 24.2, 26.4, 4.1, 24, rng)

    # devil side: the head swells into a giant shark's skull studded with three sets of eyes
    fs = m.bone("form_skull", parent="head", pivot=(0, 24, 0))
    rx2 = shapes.profile((0, 1.0), (0.08, 5.6), (0.22, 7.4), (0.45, 7.2), (0.7, 5.6), (0.87, 3.6), (0.96, 1.6), (1, 0.3))
    ry2 = shapes.profile((0, 1.0), (0.08, 5.2), (0.22, 6.8), (0.45, 6.6), (0.7, 5.0), (0.87, 3.2), (0.96, 1.4), (1, 0.3))
    f2 = shark_loft((0, 29.0, 8.0), (0, 35.0, -18.0), rx2, ry2)
    mouth2 = shapes.Mouth(f2, 0.5, 0.21, 0.36, 0.84)
    shark_shell(fs, f2, 18, 20, skip=mouth2.skip)
    j2 = m.bone("form_jaw", parent="form_skull", pivot=hinge(f2, 0.36), rotation=(9, 0, 0))
    mouth2.build(fs, j2, "belly", upper=13, lower=11, tooth_len=1.8, tooth_w=0.8, nu=7, nv=9, gum_mat="gum")
    for s, u in ((1, 0.2), (-1, 0.8)):
        for k in range(3):
            p, n, du, dv = shapes.surface_frame(f2, u, 0.64 - k * 0.09)
            eye(fs, p, n, 0.95 - 0.08 * k)
    gills(fs, f2, 0.27, 0.18, 4, 0.045, 3.8)
    gills(fs, f2, 0.73, 0.18, 4, 0.045, 3.8)
    fin(fs, on_top(f2, 0.34), (0, 1, 0.5), 9.0, 4.2, bend=40)

    # the fin that cuts through the ground while he swims under it (body sunk ~2 blocks)
    sw = m.bone("fx_swim_fin", parent="head", pivot=(0, 32, 0))
    fin(sw, (0, 30.6, 0.6), (0, 1, 0.42), 18.0, 5.2, bend=34)


# ------------------------------------------------------------------------------------------ full shark body
LEGS = [(-1, -9.5), (1, -9.5), (-1, 0.0), (1, 0.0), (-1, 9.0), (1, 9.0)]


def build_shark_form(m):
    """The shark Denji rides: a whole shark propped up on several long fins that act as legs."""
    m.bone("body", pivot=(0, 24, 0))
    s = m.bone("fx_sharkform_body", parent="body", pivot=(0, 16, 0))
    rx = shapes.profile((0, 0.6), (0.12, 2.2), (0.35, 6.2), (0.58, 8.2), (0.78, 7.6), (0.9, 5.4), (0.97, 2.6), (1, 0.4))
    ry = shapes.profile((0, 0.8), (0.12, 2.6), (0.35, 7.0), (0.58, 8.8), (0.78, 8.0), (0.9, 5.6), (0.97, 2.6), (1, 0.4))
    f = shark_loft((0, 17.5, 27.0), (0, 18.6, -27.0), rx, ry, mid=[(0, 18.6, 8.0), (0, 18.2, -12.0)])
    mouth = shapes.Mouth(f, 0.5, 0.2, 0.7, 0.93)
    shark_shell(s, f, 18, 24, belly_width=0.17, skip=mouth.skip)
    jaw = m.bone("fx_sharkform_jaw", parent="fx_sharkform_body", pivot=hinge(f, 0.7), rotation=(10, 0, 0))
    mouth.build(s, jaw, "belly", upper=11, lower=10, tooth_len=1.7, tooth_w=0.8, nu=7, nv=6, gum_mat="gum")
    for side, u in ((1, 0.2), (-1, 0.8)):
        for k in range(3):
            p, n, du, dv = shapes.surface_frame(f, u, 0.88 - k * 0.03)
            eye(s, p, n, 1.0 - 0.08 * k)
        gills(s, f, 0.25 if side > 0 else 0.75, 0.62, 5, 0.022, 5.2, width=0.35)
        # pectoral fins
        fin(s, (side * 7.0, 13.8, -6.0), (side * 1.0, -0.35, 0.45), 8.0, 3.0, bend=-side * 20, bend_axis=(0, 1, 0))
    fin(s, on_top(f, 0.55), (0, 1, 0.55), 10.0, 5.0, bend=35)
    # crescent tail
    fin(s, (0, 18.0, 25.6), (0, 1.0, 0.75), 10.0, 2.6, bend=30)
    fin(s, (0, 17.4, 25.6), (0, -0.8, 0.6), 7.0, 2.2, bend=-20)
    # several long fins standing in for legs, each on its own hip bone so they can stride
    for k, (side, z) in enumerate(LEGS):
        hip = np.array([side * 5.6, 12.6, z])
        leg = m.bone("fx_sharkform_leg%d" % k, parent="fx_sharkform_body", pivot=tuple(hip))
        knee = hip + np.array([side * 5.0, 3.0, 0.8])
        foot = np.array([side * 9.5, 0.0, z + 1.5])
        path = shapes.polyline([hip, hip + (knee - hip) * 0.6, knee, knee + (foot - knee) * 0.5, foot])
        lf = shapes.loft(path, shapes.profile((0, 2.2), (0.4, 2.4), (0.7, 1.6), (1, 0.4)), 0.5, up=(1, 0, 0))
        shapes.shell(leg, lf, 8, 10, "shark_dk" if k % 2 else "shark", thick=0.35)


def build():
    atlas = materials()
    m = Model("csm.shark_fiend", atlas, density=2.0, seed=87)
    build_head(m)
    build_shark_form(m)
    m.bone("right_arm", pivot=(-5, 22, 0))
    m.bone("left_arm", pivot=(5, 22, 0))
    geo = out("geo", "hybrid", "shark.geo.json")
    tex = out("textures", "hybrid", "shark.png")
    m.save(geo)
    paint_atlas(atlas, tex, out("textures", "hybrid", "shark_glowmask.png"), seed=47)
    anims = animations()
    anim_path = out("animations", "hybrid", "shark.animation.json")
    save_animations(anim_path, anims)
    print("shark: %d cubes, %d bones, %d animations" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def animations():
    A = []
    e = Anim("emerge", 0.7)
    e.scale("form_skull", 0, 0.45).scale("form_skull", 0.18, 1.12, "easeOutBack").scale("form_skull", 0.32, 1.0)
    e.rot("form_jaw", 0, (0, 0, 0)).rot("form_jaw", 0.2, (34, 0, 0), "easeOutQuad").rot("form_jaw", 0.5, (26, 0, 0))
    e.rot("form_jaw", 0.7, (0, 0, 0))
    A.append(e)
    r = Anim("retract", 0.4, loop="hold_on_last_frame")
    r.scale("form_skull", 0, 1).scale("form_skull", 0.35, 0.45, "easeInQuad")
    A.append(r)
    idle = Anim("idle", 2.6, loop=True)
    for t, a in ((0, 0), (0.12, 8), (0.24, 0), (1.6, 0), (1.72, 6), (1.84, 0), (2.6, 0)):
        idle.rot("form_jaw", t, (a, 0, 0))
    A.append(idle)
    sw = Anim("swim", 5.0)
    for i in range(26):
        t = i * 0.2
        sw.rot("fx_swim_fin", t, (0, 6 * math.sin(t * 6), 3 * math.sin(t * 6 + 1)))
    A.append(sw)
    bt = Anim("bite", 0.6)
    bt.rot("prop_jaw", 0, (0, 0, 0)).rot("prop_jaw", 0.15, (32, 0, 0), "easeOutQuad").rot("prop_jaw", 0.25, (-2, 0, 0))
    bt.rot("prop_jaw", 0.6, (0, 0, 0))
    bt.rot("form_jaw", 0, (0, 0, 0)).rot("form_jaw", 0.15, (40, 0, 0), "easeOutQuad").rot("form_jaw", 0.25, (-2, 0, 0))
    bt.rot("form_jaw", 0.6, (0, 0, 0))
    A.append(bt)
    am = Anim("ambush", 1.2)
    am.rot("form_jaw", 0.9, (0, 0, 0)).rot("form_jaw", 1.0, (42, 0, 0)).rot("form_jaw", 1.12, (0, 0, 0))
    for i in range(10):
        t = i * 0.1
        am.rot("fx_swim_fin", t, (0, 8 * math.sin(t * 9), 0))
    A.append(am)
    sf = Anim("sharkform", 10.0)
    sf.scale("fx_sharkform_body", 0, 0.3).scale("fx_sharkform_body", 0.3, 1.1, "easeOutBack")
    sf.scale("fx_sharkform_body", 0.45, 1.0).scale("fx_sharkform_body", 9.6, 1.0)
    sf.scale("fx_sharkform_body", 10.0, 0.3, "easeInQuad")
    for i in range(51):
        t = i * 0.2
        sf.rot("fx_sharkform_body", t, (0, 3 * math.sin(t * 5), 1.5 * math.sin(t * 5 + 1)))
    # a scuttling tripod gait on the fin-legs
    for k, (side, z) in enumerate(LEGS):
        phase = 0 if k in (0, 3, 4) else math.pi
        for i in range(61):
            t = i / 6
            a = t * 2 * math.pi * 1.6 + phase
            sf.rot("fx_sharkform_leg%d" % k, t, (-26 * math.sin(a), 0, side * (8 + 10 * max(0, math.cos(a)))))
    A.append(sf)
    sc = Anim("scent", 1.0)
    sc.rot("form_jaw", 0, (0, 0, 0)).rot("form_jaw", 0.3, (10, 0, 0)).rot("form_jaw", 1.0, (0, 0, 0))
    A.append(sc)
    dr = Anim("drink", 1.0)
    dr.rot("prop_jaw", 0, (0, 0, 0)).rot("prop_jaw", 0.3, (28, 0, 0), "easeOutQuad").rot("prop_jaw", 0.5, (0, 0, 0))
    dr.rot("prop_jaw", 0.6, (24, 0, 0)).rot("prop_jaw", 1.0, (0, 0, 0))
    dr.rot("form_jaw", 0, (0, 0, 0)).rot("form_jaw", 0.3, (36, 0, 0), "easeOutQuad").rot("form_jaw", 0.5, (0, 0, 0))
    dr.rot("form_jaw", 0.6, (30, 0, 0)).rot("form_jaw", 1.0, (0, 0, 0))
    A.append(dr)
    return A


def render_previews(geo, tex, anim):
    base_only = ("form_skull", "fx_swim_fin", "fx_sharkform_body")
    shots = [
        preview.render(geo, tex, preview_path("shark_base.png"), anim, "idle", 0, yaw=35, pitch=6,
                       hidden=base_only, scale=18, center=(0, 1.6), size=(640, 520)),
        preview.render(geo, tex, preview_path("shark_devil.png"), anim, "idle", 0, yaw=50, pitch=8,
                       hidden=("prop_shark_head", "fx_swim_fin", "fx_sharkform_body"), scale=12, center=(0, 1.6)),
        preview.render(geo, tex, preview_path("shark_form.png"), anim, "idle", 0, yaw=60, pitch=12,
                       hidden=("prop_shark_head", "form_skull", "fx_swim_fin"), show_body=False, scale=7.5, center=(0, 0.9)),
        preview.render(geo, tex, preview_path("shark_swim.png"), anim, "idle", 0, yaw=30, pitch=8,
                       hidden=("form_skull", "fx_sharkform_body"), scale=9, center=(0, 1.6)),
    ]
    return preview.contact_sheet(shots, preview_path("shark_sheet.png"), cols=2)


if __name__ == "__main__":
    g, t, a = build()
    print(render_previews(g, t, a))
