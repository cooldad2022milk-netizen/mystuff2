"""
The Ghost Devil - the mob (entity/devil/ghost) and its right arm, which its contractor controls
(entity/contract/ghost_arm).

Reference points (manga ch. 18-19 / anime ep. 8-9):
  * a large devil with a tall CYLINDRICAL body covered in WHITE FLOWERS
  * SEVERAL ARMS INSTEAD OF LEGS - it walks on its hands
  * an old, desiccated head with LONG DARK WAVY HAIR and SUNKEN CHEEKS; its EYES and MOUTH are SEWN SHUT
  * Himeno paid her right eye for its RIGHT ARM: invisible and intangible to everyone else, it copies whatever her
    own right arm does - reaching, grabbing, strangling
"""
import math

import numpy as np

from common import preview_path, out
from csmgen.geo import Atlas, Model, Anim, save_animations, norm
from csmgen.tex import paint_atlas
from csmgen import preview, shapes
import devilkit as dk


def draw_blossom(d, n):
    """A white camellia seen from the front: layered petals round a pale yellow heart."""
    c = n / 2
    for ring, (r, col) in enumerate(((0.46, (236, 236, 240)), (0.34, (248, 248, 250)), (0.22, (255, 255, 255)))):
        for k in range(6):
            a = math.radians(k * 60 + ring * 30)
            px, py = c + math.cos(a) * n * r * 0.55, c + math.sin(a) * n * r * 0.55
            d.ellipse([px - n * r * 0.5, py - n * r * 0.5, px + n * r * 0.5, py + n * r * 0.5], fill=col + (255,),
                      outline=(200, 200, 210, 255))
    d.ellipse([c - n * 0.09, c - n * 0.09, c + n * 0.09, c + n * 0.09], fill=(236, 214, 130, 255))


def draw_sewn_eye(d, n):
    """A closed eye stitched shut: a dark seam with thread crossing it."""
    d.line([(n * 0.1, n * 0.52), (n * 0.5, n * 0.6), (n * 0.9, n * 0.52)], fill=(40, 30, 30, 255), width=max(2, n // 14))
    for k in range(5):
        x = n * (0.2 + k * 0.15)
        d.line([(x - n * 0.05, n * 0.38), (x + n * 0.05, n * 0.72)], fill=(30, 26, 28, 255), width=max(2, n // 22))


def draw_sewn_mouth(d, n):
    d.line([(n * 0.05, n * 0.5), (n * 0.95, n * 0.5)], fill=(50, 30, 32, 255), width=max(2, n // 12))
    for k in range(8):
        x = n * (0.1 + k * 0.115)
        d.line([(x, n * 0.3), (x, n * 0.7)], fill=(24, 20, 22, 255), width=max(2, n // 24))


def materials():
    a = Atlas(512, 64)
    a.add("body", kind="skin", color=(206, 204, 210))
    a.add("body_sh", kind="skin", color=(172, 170, 180))
    a.add("skin", kind="skin", color=(196, 186, 176))
    a.add("skin_dk", kind="skin", color=(138, 124, 114))
    a.add("hair", kind="fiber", color=(30, 26, 30))
    a.add("blossom", kind="decal", color=(0, 0, 0), draw=draw_blossom)
    a.add("petal", kind="skin", color=(248, 248, 250))
    a.add("sewn_eye", kind="decal", color=(0, 0, 0), draw=draw_sewn_eye)
    a.add("sewn_mouth", kind="decal", color=(0, 0, 0), draw=draw_sewn_mouth)
    a.add("nail", kind="bone", color=(120, 108, 100))
    return a


def long_arm(bone, sh, el, wr, r0=1.5, mat="skin"):
    """A long, thin, withered arm."""
    f = shapes.loft(shapes.polyline([sh, el, wr]), shapes.profile((0, r0), (0.5, r0 * 0.7), (1, r0 * 0.55)),
                    shapes.profile((0, r0 * 0.9), (0.5, r0 * 0.65), (1, r0 * 0.5)))
    shapes.shell(bone, f, 6, 9, mat, thick=0.3)
    shapes.shell(bone, shapes.ellipsoid(el, (r0 * 0.85, r0 * 0.85, r0 * 0.85)), 5, 3, "skin_dk", thick=0.3)
    return f


def hand(bone, wrist, forward, down, size=1.0, spread=1.0, curl=20, finger_bone=None):
    """A bony hand with long fingers; `down` is the palm's normal."""
    wrist = np.asarray(wrist, dtype=float)
    fw = norm(forward)
    dn = norm(down)
    sd = norm(np.cross(fw, dn))
    palm = wrist + fw * 2.0 * size
    shapes.shell(bone, shapes.ellipsoid(palm, (2.2 * size, 0.9 * size, 2.4 * size),
                                        frame=np.column_stack([sd, -dn, fw])), 8, 5, "skin", thick=0.3)
    fb = finger_bone or bone
    for k in range(5):
        thumb = k == 0
        base = palm + sd * (-1.8 + k * 0.9) * size * spread + fw * (1.4 if not thumb else -0.6) * size
        d = norm(fw + sd * (0.9 if thumb else 0.12 * (k - 2)) * spread)
        L = (3.6 if thumb else 6.0 - abs(k - 2.5) * 0.5) * size
        shapes.horn(fb, base, d, L, 0.45 * size, mat="skin", tip_mat="nail", tip_from=0.85, sections=3, around=4,
                    r1=0.12, bend_axis=norm(np.cross(d, dn)) * -1, bend=curl * (0.6 if thumb else 1.0))


def ghost_head(m, parent, c):
    """The old, withered head: sunken cheeks, eyes and mouth sewn shut, long dark wavy hair."""
    c = np.asarray(c, dtype=float)
    head = m.bone("head", parent=parent, pivot=tuple(c + np.array([0, -5.0, 0])))
    look = m.bone("look", parent="head", pivot=tuple(c + np.array([0, -3.0, 0])))
    face = shapes.ellipsoid(c, (4.0, 5.6, 4.2), e_lat=0.9)
    shapes.shell(look, face, 16, 12, "skin", thick=0.4,
                 mat_fn=lambda u, v: "skin_dk" if 0.3 < v < 0.5 and 0.08 < min(u, 1 - u) < 0.2 else "skin")
    # the cheekbones stand out over hollow cheeks, the brow juts over deep-set sewn eyes
    for s in (-1, 1):
        shapes.shell(look, shapes.ellipsoid(c + [s * 2.8, 0.2, -3.0], (1.2, 0.8, 1.0)), 6, 4, "skin", thick=0.3)
        p, n, du, dv = shapes.surface_frame(face, 0.08 if s > 0 else 0.92, 0.58)
        look.decal(p + n * 0.12, n, 2.4, 1.6, "sewn_eye", up=(0, 1, 0))
    shapes.shell(look, shapes.ellipsoid(c + [0, 2.2, -3.2], (3.4, 0.9, 1.2)), 8, 4, "skin", thick=0.3)
    look.cbox(tuple(c + [0, 0.2, -4.2]), (1.0, 2.0, 1.0), "skin")
    p, n, du, dv = shapes.surface_frame(face, 0.0, 0.3)
    look.decal(p + n * 0.12, n, 3.2, 1.2, "sewn_mouth", up=(0, 1, 0))
    # long dark wavy hair: a mass over the crown falling in waves to the middle of the body
    shapes.shell(look, shapes.ellipsoid(c + [0, 1.0, 0.6], (4.5, 5.2, 4.6)), 14, 10, "hair", thick=0.4, v0=0.5,
                 skip=lambda u, v: min(u, 1 - u) < 0.18 and v < 0.8)
    rng = np.random.default_rng(311)
    for k in range(22):
        a = math.radians(-150 + k * 300 / 21)
        if abs(math.degrees(a)) > 150:
            continue
        base = c + np.array([math.sin(a) * 4.2, 2.5, math.cos(a) * 4.2])
        if math.cos(a) < -0.55:
            continue  # leave the face uncovered
        pts = [base]
        d = norm(np.array([math.sin(a) * 0.35, -1.0, math.cos(a) * 0.35]))
        L = 16.0 + rng.uniform(0, 8)
        for i in range(1, 7):
            wave = np.array([math.cos(a), 0, -math.sin(a)]) * math.sin(i * 1.3 + k) * 1.2
            pts.append(base + d * L * i / 6 + wave)
        shapes.shell(look, shapes.loft(shapes.polyline(pts), shapes.taper(1.3, 0.35), shapes.taper(0.5, 0.2),
                                       up=(math.sin(a), 0, math.cos(a))), 4, 7, "hair", thick=0.3)
    return head, look


def body_and_arms(m, root):
    """The flower-covered pillar of a body, walking on arms, with its two long arms at the top."""
    body = m.bone("body", parent="root", pivot=(0, 24, 0))
    pillar = shapes.loft(shapes.polyline([(0, 20.0, 0.5), (0, 30.0, 0.0), (0, 42.0, 0.0), (0, 52.0, 0.5),
                                          (0, 55.0, 0.8)]),
                         shapes.profile((0, 4.0), (0.12, 7.0), (0.5, 7.4), (0.88, 6.4), (1, 3.4)),
                         shapes.profile((0, 4.0), (0.12, 6.6), (0.5, 7.0), (0.88, 6.0), (1, 3.4)), up=(0, 0, -1))
    shapes.shell(body, pillar, 16, 14, "body", thick=0.45,
                 mat_fn=lambda u, v: "body_sh" if v < 0.1 or v > 0.93 else "body")
    # white flowers all over it
    rng = np.random.default_rng(307)
    for k in range(72):
        u, v = rng.uniform(0, 1), rng.uniform(0.08, 0.92)
        p, n, du, dv = shapes.surface_frame(pillar, u, v)
        w = rng.uniform(2.4, 3.6)
        body.decal(p + n * 0.3, n, w, w, "blossom", up=norm(dv), thick=0.3)
        if k % 4 == 0:  # some stand proud of the body
            for i in range(5):
                a = i * 2 * math.pi / 5 + rng.uniform(0, 0.6)
                side = norm(np.cross(n, dv))
                d = norm(n * 0.6 + (side * math.cos(a) + dv * math.sin(a)))
                shapes.horn(body, p + n * 0.4, d, w * 0.55, w * 0.28, mat="petal", flat=0.25, up=n, sections=2,
                            around=4, r1=0.1)
    # the arms it walks on
    for k in range(6):
        a = math.radians(30 + k * 60)
        s = 1 if math.sin(a) >= 0 else -1
        name = "walk_arm%d" % k
        sh = np.array([math.sin(a) * 5.0, 22.0, -math.cos(a) * 5.0])
        el = np.array([math.sin(a) * 12.0, 17.0, -math.cos(a) * 12.0])
        wr = np.array([math.sin(a) * 14.0, 3.0, -math.cos(a) * 14.0])
        arm = m.bone(name, parent="root", pivot=tuple(sh))
        long_arm(arm, sh, el, wr, r0=1.8)
        out_dir = norm(np.array([math.sin(a), 0, -math.cos(a)]))
        hand(arm, wr, out_dir + np.array([0, -0.2, 0]), (0, -1, 0), size=1.2, spread=1.2, curl=-10)
        _ = s
    # the two long arms at its shoulders (the right one is the arm Himeno borrowed)
    for side, name in ((-1, "right_arm"), (1, "left_arm")):
        sh = np.array([side * 6.5, 50.0, 0.0])
        arm = m.bone(name, parent="body", pivot=tuple(sh))
        shapes.shell(arm, shapes.ellipsoid(sh, (2.2, 2.2, 2.2)), 7, 5, "body", thick=0.3)
        el = sh + np.array([side * 4.0, -15.0, 1.0])
        wr = el + np.array([side * 0.5, -15.0, -2.0])
        long_arm(arm, sh, el, wr, r0=1.8)
        hand(arm, wr, (0, -1, -0.2), (-side, 0, 0), size=1.4, curl=25)
    ghost_head(m, "body", (0, 61.0, -0.5))
    return body


def build_mob():
    atlas = materials()
    m = Model("csm.ghost_devil", atlas, density=2.0, seed=301)
    root = m.bone("root", pivot=(0, 0, 0))
    body_and_arms(m, root)
    geo, tex, glow, anim_path = dk.devil_paths("ghost")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=303)
    anims = mob_animations()
    save_animations(anim_path, anims)
    print("ghost devil: %d cubes, %d bones, %d anims" % (m.cube_count(), len(m.bones), len(anims)))
    return geo, tex, anim_path


def mob_animations():
    A = []
    walk = ["walk_arm%d" % k for k in range(6)]
    idle = Anim("idle", 3.5, loop=True)
    for i in range(9):
        t = 3.5 * i / 8
        ph = 2 * math.pi * i / 8
        idle.pos("body", t, (0, 1.0 * math.sin(ph), 0))
        idle.rot("body", t, (2 * math.sin(ph), 4 * math.sin(ph * 0.5), 2 * math.sin(ph + 1)))
        idle.rot("head", t, (4 * math.sin(ph + 1), 12 * math.sin(ph * 0.5), 6 * math.sin(ph)))
        idle.rot("right_arm", t, (-6 + 5 * math.sin(ph), 0, 6 + 3 * math.sin(ph)))
        idle.rot("left_arm", t, (-6 + 5 * math.sin(ph + 2), 0, -6 - 3 * math.sin(ph + 2)))
        for k, b in enumerate(walk):
            idle.rot(b, t, (4 * math.sin(ph + k), 0, 3 * math.sin(ph + k * 0.7)))
    A.append(idle)
    mv = Anim("move", 1.2, loop=True)
    for i in range(9):
        t = 1.2 * i / 8
        ph = 2 * math.pi * i / 8
        for k, b in enumerate(walk):
            a = math.radians(30 + k * 60)
            sgn = 1 if k % 2 == 0 else -1
            mv.rot(b, t, (22 * math.sin(ph) * sgn * -math.cos(a), 0, 22 * math.sin(ph) * sgn * math.sin(a)))
        mv.pos("body", t, (0, 1.2 * abs(math.sin(ph)), 0))
        mv.rot("body", t, (6, 5 * math.sin(ph), 0))
        mv.rot("right_arm", t, (-15 + 10 * math.sin(ph), 0, 8))
        mv.rot("left_arm", t, (-15 - 10 * math.sin(ph), 0, -8))
    A.append(mv)
    st = Anim("strangle", 2.5)
    st.rot("right_arm", 0, (0, 0, 0)).rot("right_arm", 0.3, (-100, 0, 10), "easeOutQuad")
    st.rot("right_arm", 0.6, (-130, 0, 10)).rot("right_arm", 2.2, (-135, 0, 8)).rot("right_arm", 2.5, (0, 0, 0))
    st.rot("head", 0.3, (-10, 0, 0)).rot("head", 2.2, (-12, 0, 8)).rot("head", 2.5, (0, 0, 0))
    A.append(st)
    sn = Anim("snatch", 1.2)
    sn.rot("right_arm", 0, (0, 0, 0)).rot("right_arm", 0.3, (-100, -30, 0), "easeOutQuad")
    sn.rot("right_arm", 0.7, (-120, 40, 0), "easeInOutQuad").rot("right_arm", 1.2, (0, 0, 0))
    sn.rot("body", 0.3, (0, 15, 0)).rot("body", 0.7, (0, -20, 0)).rot("body", 1.2, (0, 0, 0))
    A.append(sn)
    fd = Anim("fade", 0.6)
    fd.scale("root", 0, 1.0).scale("root", 0.3, (0.8, 1.15, 0.8)).scale("root", 0.6, 1.0)
    A.append(fd)
    fr = Anim("fear", 1.3)
    fr.rot("head", 0, (0, 0, 0)).rot("head", 0.3, (-25, 0, 0), "easeOutQuad").rot("head", 1.0, (-20, 25, 0))
    fr.rot("head", 1.3, (0, 0, 0))
    fr.rot("right_arm", 0.3, (-40, 0, 60)).rot("left_arm", 0.3, (-40, 0, -60))
    fr.rot("right_arm", 1.3, (0, 0, 0)).rot("left_arm", 1.3, (0, 0, 0))
    A.append(fr)
    dr = Anim("drink", 1.0)
    dr.rot("head", 0, (0, 0, 0)).rot("head", 0.3, (20, 0, 0)).rot("head", 1.0, (0, 0, 0))
    A.append(dr)
    death = Anim("death", 1.6, loop="hold_on_last_frame")
    death.rot("body", 0, (0, 0, 0)).rot("body", 1.0, (0, 0, 75), "easeInQuad")
    death.pos("body", 1.0, (6, -14, 0))
    for b in walk:
        death.rot(b, 1.0, (0, 0, 20))
    death.rot("head", 1.0, (30, 0, 20))
    A.append(death)
    A.append(dk.scale_in("manifest", "root", 0.8, from_scale=0.2))
    A.append(dk.scale_in("retract", "root", 0.4, from_scale=1.0, loop="hold_on_last_frame"))
    return A


# ----------------------------------------------------------------------------- the arm Himeno controls
def build_arm():
    """entity/contract/ghost_arm: the Ghost Devil's long right arm alone, reaching in from behind its contractor. The
    origin is its grip (the victim's throat); the arm runs back and up toward the contractor (+z)."""
    atlas = materials()
    m = Model("csm.ghost_arm", atlas, density=1.6, seed=313)
    root = m.bone("root", pivot=(0, 0, 0))
    arm = m.bone("arm", parent="root", pivot=(0, 22, 46))
    sh = np.array([0.0, 22.0, 46.0])
    el = np.array([-2.0, 14.0, 22.0])
    wr = np.array([0.0, 2.0, 4.5])
    long_arm(arm, sh, el, wr, r0=2.4)
    # the stump where it comes out of nowhere
    shapes.shell(arm, shapes.ellipsoid(sh, (2.8, 2.8, 1.2)), 8, 4, "body_sh", thick=0.3)
    fingers = m.bone("fingers", parent="arm", pivot=tuple(wr))
    hand(arm, wr, (0, -0.35, -1), (0, -1, 0.3), size=1.7, spread=1.3, curl=70, finger_bone=fingers)
    geo = out("geo", "entity", "contract", "ghost_arm.geo.json")
    tex = out("textures", "entity", "contract", "ghost_arm.png")
    glow = out("textures", "entity", "contract", "ghost_arm_glowmask.png")
    anim_path = out("animations", "entity", "contract", "ghost_arm.animation.json")
    m.save(geo)
    paint_atlas(atlas, tex, glow, seed=303)
    save_animations(anim_path, arm_animations())
    print("ghost arm: %d cubes, %d bones" % (m.cube_count(), len(m.bones)))
    return geo, tex, anim_path


def arm_animations():
    # strangle (54 ticks): reach in, close on the throat (tick 4), squeeze, let go and fade
    s = Anim("strangle", 2.7, loop="hold_on_last_frame")
    s.scale("root", 0, 0.3).scale("root", 0.2, 1.0, "easeOutQuad").scale("root", 2.4, 1.0).scale("root", 2.7, 0.02)
    s.pos("arm", 0, (0, 4, 24)).pos("arm", 0.2, (0, 0, 0), "easeOutQuad")
    s.rot("fingers", 0, (-50, 0, 0)).rot("fingers", 0.2, (-50, 0, 0)).rot("fingers", 0.3, (0, 0, 0), "easeInQuad")
    for i in range(10):
        t = 0.45 + i * 0.2
        s.rot("fingers", t, (6 if i % 2 else -2, 0, 0))
        s.rot("arm", t, (0, 2 if i % 2 else -2, 3 if i % 2 else -3))
    s.rot("fingers", 2.45, (-50, 0, 0), "easeOutQuad")
    # fling (26 ticks): grab, lift, hurl aside on tick 12, gone
    f = Anim("fling", 1.3, loop="hold_on_last_frame")
    f.scale("root", 0, 0.3).scale("root", 0.15, 1.0, "easeOutQuad").scale("root", 1.0, 1.0).scale("root", 1.3, 0.02)
    f.pos("arm", 0, (0, 4, 20)).pos("arm", 0.15, (0, 0, 0), "easeOutQuad").pos("arm", 0.55, (0, 16, 2))
    f.pos("arm", 0.6, (0, 16, 2)).pos("arm", 0.75, (18, 18, -4), "easeOutQuad").pos("arm", 1.3, (20, 18, -4))
    f.rot("fingers", 0, (-50, 0, 0)).rot("fingers", 0.2, (0, 0, 0)).rot("fingers", 0.6, (0, 0, 0))
    f.rot("fingers", 0.7, (-60, 0, 0), "easeOutQuad")
    f.rot("arm", 0.55, (0, 0, 0)).rot("arm", 0.75, (0, -35, -20), "easeOutQuad")
    return [s, f]


def render_previews():
    g, t, _, a = dk.devil_paths("ghost")
    ag, at, aa = (out("geo", "entity", "contract", "ghost_arm.geo.json"),
                  out("textures", "entity", "contract", "ghost_arm.png"),
                  out("animations", "entity", "contract", "ghost_arm.animation.json"))
    shots = [
        preview.render(g, t, preview_path("ghost_front.png"), a, "idle", 0.0, yaw=25, pitch=6, show_body=False,
                       scale=3.6, center=(0, 2.1), size=(620, 620), bg=(150, 170, 200)),
        preview.render(g, t, preview_path("ghost_face.png"), a, "idle", 0.0, yaw=10, pitch=0, show_body=False,
                       scale=10.0, center=(0, 3.8), size=(620, 620), bg=(150, 170, 200)),
        preview.render(ag, at, preview_path("ghost_arm.png"), aa, "strangle", 1.0, yaw=120, pitch=10, show_body=False,
                       scale=4.0, center=(0, 0.6), size=(620, 620), bg=(150, 170, 200)),
    ]
    return preview.contact_sheet(shots, preview_path("ghost_sheet.png"), cols=3)


if __name__ == "__main__":
    build_mob()
    build_arm()
    print(render_previews())
