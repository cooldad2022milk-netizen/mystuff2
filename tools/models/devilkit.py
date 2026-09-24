"""
Shared pieces for the full-devil models (tools/models/devils/*.py): a smooth rigged humanoid with clothes for the
devils in human shape (Makima, Angel, Yoru, Fami), and the animation plumbing every devil model shares.

Every devil entity model follows the same rules so DevilEntity/DevilRenderer can drive it:
  * animations: idle, move (walk or fly), death, manifest, retract, drink, plus one per move (its geoAnim)
  * a bone named `look` (never keyed by animations) may be turned toward the target by the renderer
  * fx_<group>_ bones only show while that effect group is active
Coordinates are Bedrock pixels (feet at y=0, facing -z, the character's right is -x).
"""
import math

import numpy as np

from common import out
from csmgen.geo import Anim
from csmgen import shapes

# vanilla player part pivots (Bedrock pixels) and the PlayerAnimator part names they correspond to
PARTS = {"head": (0, 24, 0), "body": (0, 24, 0), "right_arm": (-5, 22, 0), "left_arm": (5, 22, 0),
         "right_leg": (-1.9, 12, 0), "left_leg": (1.9, 12, 0)}
PA_TO_BONE = {"head": "head", "body": "body", "rightArm": "right_arm", "leftArm": "left_arm", "rightLeg": "right_leg",
              "leftLeg": "left_leg", "torso": "waist"}
DEFAULT_POS = {"rightArm": (-5, 2, 0), "leftArm": (5, 2, 0), "rightLeg": (-1.9, 12, 0), "leftLeg": (1.9, 12, 0),
               "head": (0, 0, 0), "body": (0, 0, 0), "torso": (0, 0, 0)}
EASE = {"EASEINOUTSINE": "easeInOutSine", "EASEINSINE": "easeInSine", "EASEOUTSINE": "easeOutSine",
        "EASEINQUAD": "easeInQuad", "EASEOUTQUAD": "easeOutQuad", "EASEINOUTQUAD": "easeInOutQuad",
        "EASEINCUBIC": "easeInCubic", "EASEOUTCUBIC": "easeOutCubic", "EASEINOUTCUBIC": "easeInOutCubic",
        "EASEOUTBACK": "easeOutBack", "EASEINBACK": "easeInBack", "EASEINOUTBACK": "easeInOutBack",
        "EASEOUTBOUNCE": "easeOutBounce", "EASEOUTELASTIC": "easeOutElastic", "linear": None}


# --------------------------------------------------------------------------- humanoid body
def rbox(bone, center, half, mat, e=0.32, nu=12, nv=8, thick=0.4, v0=0.0, v1=1.0, mat_fn=None, skip=None):
    """A rounded box (superellipsoid): Minecraft proportions without the hard edges."""
    f = shapes.ellipsoid(center, half, e_lat=e, e_lon=e)
    shapes.shell(bone, f, nu, nv, mat, thick=thick, v0=v0, v1=v1, mat_fn=mat_fn, skip=skip)
    return f


def humanoid(m, mats, slim=True, root_pivot=(0, 0, 0)):
    """The skeleton (and bare skin) of a person, Minecraft-sized (2 blocks tall), with smooth rounded parts.

    Bones: root > waist > body, head > look, right_arm, left_arm;  root > right_leg, left_leg.
    `mats`: dict with keys skin, shirt, sleeve, cuff, pants, shoe (any may repeat).
    Returns the bones by name so the caller can dress them (hair, collars, ties, wings, halos...).
    """
    aw = 3.0 if slim else 4.0
    root = m.bone("root", pivot=root_pivot)
    waist = m.bone("waist", parent="root", pivot=(0, 12, 0))
    body = m.bone("body", parent="waist", pivot=(0, 24, 0))
    head = m.bone("head", parent="waist", pivot=(0, 24, 0))
    look = m.bone("look", parent="head", pivot=(0, 24, 0))
    ra = m.bone("right_arm", parent="waist", pivot=(-5, 22, 0))
    la = m.bone("left_arm", parent="waist", pivot=(5, 22, 0))
    rl = m.bone("right_leg", parent="root", pivot=(-1.9, 12, 0))
    ll = m.bone("left_leg", parent="root", pivot=(1.9, 12, 0))

    # head + neck
    rbox(look, (0, 28.1, 0), (3.95, 4.0, 3.95), mats["skin"], e=0.38, nu=14, nv=10)
    look.cylinder((0, 24.0, 0.2), (0, 1, 0), 1.6, 1.4, mats["skin"], segments=10)
    # torso: shirt, narrower at the waist
    torso = shapes.loft(shapes.polyline([(0, 12.0, 0), (0, 18.5, 0), (0, 23.7, 0)]),
                        shapes.profile((0, 3.7), (0.45, 3.45), (0.8, 3.95), (1, 3.9)),
                        shapes.profile((0, 2.0), (0.5, 1.95), (0.85, 2.15), (1, 2.05)), up=(0, 0, -1))
    shapes.shell(body, torso, 14, 8, mats["shirt"], thick=0.4)
    rbox(body, (0, 23.6, 0), (3.9, 0.55, 2.05), mats["shirt"], e=0.5, nu=12, nv=4)
    # arms (sleeves + cuffs + hands)
    for bone, sgn in ((ra, -1), (la, 1)):
        cx = sgn * (4 + aw / 2)
        rbox(bone, (cx, 18.3, 0), (aw / 2 + 0.05, 5.75, 2.05), mats["sleeve"], e=0.3, nu=10, nv=8)
        rbox(bone, (cx, 13.4, 0), (aw / 2 + 0.15, 0.55, 2.15), mats["cuff"], e=0.5, nu=10, nv=4)
        rbox(bone, (cx, 11.9, -0.1), (aw / 2 - 0.1, 1.25, 1.75), mats["skin"], e=0.45, nu=8, nv=6)
    # legs (trousers + shoes)
    for bone, sgn in ((rl, -1), (ll, 1)):
        cx = sgn * 1.95
        rbox(bone, (cx, 7.0, 0), (1.95, 5.6, 1.95), mats["pants"], e=0.3, nu=10, nv=8)
        rbox(bone, (cx, 0.9, -0.55), (2.05, 0.95, 2.6), mats["shoe"], e=0.45, nu=10, nv=6)
    return {"root": root, "waist": waist, "body": body, "head": head, "look": look, "right_arm": ra, "left_arm": la,
            "right_leg": rl, "left_leg": ll}


def face_eyes(bone, mat, y=27.6, spacing=2.05, size=(1.9, 1.35), z=-4.0, tilt=0.0):
    """A pair of decal eyes on the front of a head (mat is a 'ringeye' or other eye decal material)."""
    for s in (-1, 1):
        up = (s * math.sin(math.radians(tilt)), math.cos(math.radians(tilt)), 0)
        bone.decal((s * spacing, y, z - 0.06), (0, 0, -1), size[0], size[1], mat, up=up)


def braid(m, parent, top, length, segs, mat, tie_mat, radius=0.95, sway_bones=True, prefix="braid"):
    """A plait hanging from `top` straight down the back: bulging lobes alternating side to side.
    Split over a few bones (<prefix>0..n) so animations can swing it."""
    names = []
    seg_len = length / segs
    p = np.asarray(top, dtype=float)
    par = parent
    for k in range(segs):
        name = "%s%d" % (prefix, k)
        b = m.bone(name, parent=par, pivot=tuple(p))
        for j in range(3):
            t = (j + 0.5) / 3
            c = p + np.array([0.35 * (1 if (k * 3 + j) % 2 else -1), -seg_len * t, 0.15])
            r = radius * (1 - 0.35 * (k + t) / segs)
            e = shapes.ellipsoid(c, (r, seg_len / 3 * 0.75, r * 0.85))
            shapes.shell(b, e, 8, 5, mat, thick=0.3)
        names.append(name)
        p = p + np.array([0, -seg_len, 0.0])
        par = name
    # the tie and the loose end
    last = m.by_name[names[-1]]
    last.cylinder(p + np.array([0, 0.3, 0]), (0, 1, 0), radius * 0.62, 0.6, tie_mat, segments=8)
    shapes.horn(last, p + np.array([0, 0.1, 0]), (0, -1, 0.1), 2.2, radius * 0.7, mat=mat, sections=4, around=6,
                r1=0.1)
    return names


# --------------------------------------------------------------------------- animation plumbing
def from_player_anim(a, name=None, length_pad=0.0):
    """Convert a PlayerAnimator animation built with player_anims.A into a GeckoLib animation for a humanoid() model,
    so a humanoid devil's moves look the same on the mob as on a player who became it.

    Vanilla part rotations (radians) map 1:1 to Bedrock degrees; position offsets (dx, dy, dz) from the vanilla rest
    position map to Bedrock (dx, -dy, dz). The PlayerAnimator 'torso' becomes the `waist` bone (authored as positive =
    lean forward, which is positive Bedrock x on a bone above its pivot).
    """
    g = Anim(name or a.name, a.stop / 20.0 + length_pad)
    for mv in a.moves:
        t = mv["tick"] / 20.0
        ease = EASE.get(mv.get("easing", "linear"))
        for part, d in mv.items():
            if part not in PA_TO_BONE or not isinstance(d, dict):
                continue
            bone = PA_TO_BONE[part]
            if any(k in d for k in ("pitch", "yaw", "roll")):
                pitch = d.get("pitch", 0.0)
                if part == "torso":
                    pitch = -pitch  # A.k stored it negated for PlayerAnimator
                g.rot(bone, t, (math.degrees(pitch), math.degrees(d.get("yaw", 0.0)), math.degrees(d.get("roll", 0.0))),
                      ease)
            if any(k in d for k in ("x", "y", "z")):
                base = DEFAULT_POS.get(part, (0, 0, 0))
                dx = d.get("x", base[0]) - base[0]
                dy = d.get("y", base[1]) - base[1]
                dz = d.get("z", base[2]) - base[2]
                g.pos(bone, t, (dx, -dy, dz), ease)
    return g


def humanoid_idle(extra_bones=(), braid_bones=(), length=3.2, breathe=1.2):
    a = Anim("idle", length, loop=True)
    for i in range(9):
        t = length * i / 8
        ph = 2 * math.pi * i / 8
        a.rot("body", t, (breathe * 0.6 * math.sin(ph), 0, 0))
        a.rot("head", t, (-breathe * 0.8 * math.sin(ph), 0, 0))
        a.rot("right_arm", t, (0, 0, 3 + 1.5 * math.sin(ph)))
        a.rot("left_arm", t, (0, 0, -3 - 1.5 * math.sin(ph)))
        for k, b in enumerate(braid_bones):
            a.rot(b, t, (2 * math.sin(ph - k * 0.6), 0, 2.5 * math.sin(ph * 0.5 - k * 0.5)))
    return a


def humanoid_walk(braid_bones=(), length=1.0, stride=32.0, arm=26.0):
    a = Anim("move", length, loop=True)
    for i in range(9):
        t = length * i / 8
        ph = 2 * math.pi * i / 8
        s = math.sin(ph)
        a.rot("right_leg", t, (stride * s, 0, 0))
        a.rot("left_leg", t, (-stride * s, 0, 0))
        a.rot("right_arm", t, (-arm * s, 0, 3))
        a.rot("left_arm", t, (arm * s, 0, -3))
        a.rot("body", t, (2, 4 * s, 0))
        a.pos("root", t, (0, -0.4 * abs(math.cos(ph)), 0))
        for k, b in enumerate(braid_bones):
            a.rot(b, t, (6 + 4 * math.sin(2 * ph - k * 0.7), 0, 5 * math.sin(ph - k * 0.6)))
    return a


def humanoid_death(length=1.6):
    """Knees give, then the body falls forward onto the ground."""
    a = Anim("death", length, loop="hold_on_last_frame")
    a.rot("waist", 0, (0, 0, 0)).rot("waist", 0.35, (25, 0, 0), "easeInQuad").rot("waist", 0.9, (80, 0, 0), "easeInQuad")
    a.pos("root", 0, (0, 0, 0)).pos("root", 0.35, (0, -4, 0), "easeInQuad").pos("root", 0.9, (0, -10, -6), "easeInQuad")
    a.rot("right_leg", 0.35, (-70, 0, 5)).rot("left_leg", 0.35, (-70, 0, -5))
    a.rot("right_leg", 0.9, (-5, 0, 5)).rot("left_leg", 0.9, (-10, 0, -5))
    a.rot("right_arm", 0.5, (-40, 0, 20)).rot("left_arm", 0.5, (-40, 0, -20))
    a.rot("right_arm", 0.9, (-160, 0, 15), "easeOutQuad").rot("left_arm", 0.9, (-150, 0, -15), "easeOutQuad")
    a.rot("head", 0.9, (-30, 20, 0))
    a.rot("root", 0, (0, 0, 0)).rot("root", length, (0, 0, 0))
    return a


def scale_in(name, bone, length, from_scale=0.2, loop=False):
    """manifest / retract helpers: the whole model grows out of (or shrinks back into) a person-sized husk."""
    a = Anim(name, length, loop=loop)
    if from_scale < 1:
        a.scale(bone, 0, from_scale).scale(bone, length * 0.7, 1.08, "easeOutBack").scale(bone, length, 1.0)
    else:
        a.scale(bone, 0, 1.0).scale(bone, length, 0.25, "easeInQuad")
    return a


def devil_paths(did):
    return (out("geo", "entity", "devil", did + ".geo.json"), out("textures", "entity", "devil", did + ".png"),
            out("textures", "entity", "devil", did + "_glowmask.png"),
            out("animations", "entity", "devil", did + ".animation.json"))


def part_paths(did):
    return (out("geo", "hybrid", did + ".geo.json"), out("textures", "hybrid", did + ".png"),
            out("textures", "hybrid", did + "_glowmask.png"), out("animations", "hybrid", did + ".animation.json"))

