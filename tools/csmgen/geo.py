"""
Tiny procedural modelling kit that writes GeckoLib (Bedrock 1.12.0) geometry.

All coordinates are Bedrock/Blockbench pixels: +y up, the character faces -z (north)
and the character's RIGHT side is -x (the player's right arm pivot is [-5, 22, 0]).

Rotations follow GeckoLib's interpretation of Bedrock euler angles, which is verified
against the GeckoLib 4.8 bytecode:  R_bedrock(rx, ry, rz) = Rz(-rz) . Ry(ry) . Rx(-rx)
(right-handed matrices, angles in degrees).  `euler_for()` inverts that so parts can be
oriented along arbitrary directions (horns, teeth, hoses...).
"""
import json
import math
import random

import numpy as np


# --------------------------------------------------------------------------- maths
def _rx(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)


def _ry(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)


def _rz(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def rot_bedrock(rx, ry, rz):
    """3x3 rotation acting on bedrock-space vectors for a Bedrock euler triple (degrees)."""
    return _rz(math.radians(-rz)) @ _ry(math.radians(ry)) @ _rx(math.radians(-rx))


def euler_for(R):
    """Bedrock euler (degrees) that reproduces rotation matrix R under GeckoLib."""
    sb = max(-1.0, min(1.0, -R[2, 0]))
    b = math.asin(sb)
    if abs(math.cos(b)) > 1e-6:
        a = math.atan2(R[1, 0], R[0, 0])
        c = math.atan2(R[2, 1], R[2, 2])
    else:
        a = 0.0
        c = math.atan2(-R[1, 2], R[1, 1])
    return [round(-math.degrees(c), 4), round(math.degrees(b), 4), round(-math.degrees(a), 4)]


def norm(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def frame_from(direction, up_hint=(0, 1, 0)):
    """Rotation whose local +y points along `direction` and local +z leans toward `up_hint`."""
    ey = norm(direction)
    up = np.asarray(up_hint, dtype=float)
    if abs(np.dot(norm(up), ey)) > 0.98:  # degenerate, pick another hint
        up = np.array([1.0, 0, 0]) if abs(ey[0]) < 0.9 else np.array([0, 0, 1.0])
    ez = norm(up - np.dot(up, ey) * ey)
    ex = np.cross(ey, ez)
    return np.column_stack([ex, ey, ez])


def rotate_about(v, axis, deg):
    """Rodrigues rotation of vector v around axis."""
    v = np.asarray(v, dtype=float)
    k = norm(axis)
    t = math.radians(deg)
    return v * math.cos(t) + np.cross(k, v) * math.sin(t) + k * np.dot(k, v) * (1 - math.cos(t))


def lerp(a, b, t):
    return np.asarray(a, dtype=float) * (1 - t) + np.asarray(b, dtype=float) * t


def bezier(p0, p1, p2, p3, t):
    p0, p1, p2, p3 = (np.asarray(p, dtype=float) for p in (p0, p1, p2, p3))
    u = 1 - t
    return u ** 3 * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t ** 3 * p3


# --------------------------------------------------------------------------- atlas
class Atlas:
    """A texture atlas split into square material cells; painted later by tex.py."""

    def __init__(self, size=512, cell=64):
        self.size = size
        self.cell = cell
        self.per_row = size // cell
        self.materials = {}  # name -> (index, spec)

    def add(self, name, **spec):
        if name in self.materials:
            return name
        idx = len(self.materials)
        if idx >= self.per_row * self.per_row:
            raise ValueError("atlas full")
        self.materials[name] = (idx, spec)
        return name

    def region(self, name):
        idx, _ = self.materials[name]
        return ((idx % self.per_row) * self.cell, (idx // self.per_row) * self.cell, self.cell, self.cell)


# --------------------------------------------------------------------------- model
FACE_DIMS = {
    "north": (0, 1), "south": (0, 1),
    "east": (2, 1), "west": (2, 1),
    "up": (0, 2), "down": (0, 2),
}


class Bone:
    def __init__(self, model, name, parent, pivot, rotation):
        self.model = model
        self.name = name
        self.parent = parent
        self.pivot = [round(float(p), 4) for p in pivot]
        self.rotation = rotation
        self.cubes = []

    # ---- primitive -------------------------------------------------------
    def box(self, frm, to, mat, rot=None, pivot=None, inflate=None, faces=None, full_uv=False):
        frm = np.asarray(frm, dtype=float)
        to = np.asarray(to, dtype=float)
        origin = np.minimum(frm, to)
        size = np.abs(to - frm)
        cube = {
            "origin": [round(float(v), 4) for v in origin],
            "size": [round(float(v), 4) for v in size],
            "uv": self.model.face_uvs(size, mat, faces, full=full_uv),
        }
        if rot is not None and any(abs(r) > 1e-4 for r in rot):
            cube["pivot"] = [round(float(v), 4) for v in (pivot if pivot is not None else (origin + size / 2))]
            cube["rotation"] = [round(float(r), 4) for r in rot]
        if inflate:
            cube["inflate"] = round(float(inflate), 4)
        self.cubes.append(cube)
        return cube

    def cbox(self, center, dims, mat, rot=None, inflate=None):
        """Box given by centre and full dimensions; optional euler rotation about its centre."""
        c = np.asarray(center, dtype=float)
        d = np.asarray(dims, dtype=float) / 2
        return self.box(c - d, c + d, mat, rot=rot, pivot=c, inflate=inflate)

    def obox(self, center, direction, dims, mat, up=(0, 1, 0), roll=0.0, inflate=None, full_uv=False):
        """Oriented box: dims = (width, length, height); length runs along `direction`."""
        R = frame_from(direction, up)
        if roll:
            R = R @ _ry(math.radians(roll))
        c = np.asarray(center, dtype=float)
        d = np.asarray(dims, dtype=float) / 2
        return self.box(c - d, c + d, mat, rot=euler_for(R), pivot=c, inflate=inflate, full_uv=full_uv)

    def decal(self, center, normal, width, height, mat, up=(0, 1, 0), thick=0.05):
        """A thin plate facing `normal` that shows the material's whole texture cell (painted eyes, markings)."""
        n = norm(normal)
        u = np.asarray(up, dtype=float)
        u = norm(u - np.dot(u, n) * n)
        # obox's length axis runs along `up` (height), its thin axis along the normal
        return self.obox(center, u, (width, height, thick), mat, up=n, full_uv=True)

    def seg(self, a, b, w, h, mat, up=(0, 1, 0), roll=0.0, overlap=0.0):
        """Oriented box spanning point a -> point b."""
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        L = np.linalg.norm(b - a) + overlap
        return self.obox((a + b) / 2, b - a, (w, L, h), mat, up=up, roll=roll)

    def scale_about(self, center, k, pivot_too=True):
        """Uniformly scale everything already in this bone about `center` (a resize after modelling)."""
        c = np.asarray(center, dtype=float)
        for cube in self.cubes:
            o = np.asarray(cube["origin"], dtype=float)
            sz = np.asarray(cube["size"], dtype=float)
            cube["origin"] = [round(float(v), 4) for v in c + (o - c) * k]
            cube["size"] = [round(float(v), 4) for v in sz * k]
            if "pivot" in cube:
                pv = np.asarray(cube["pivot"], dtype=float)
                cube["pivot"] = [round(float(v), 4) for v in c + (pv - c) * k]
        if pivot_too:
            self.pivot = [round(float(v), 4) for v in c + (np.asarray(self.pivot, dtype=float) - c) * k]
        return self

    def offset(self, delta, pivot_too=True):
        """Move everything already in this bone by `delta`."""
        d = np.asarray(delta, dtype=float)
        for cube in self.cubes:
            cube["origin"] = [round(float(v), 4) for v in np.asarray(cube["origin"], dtype=float) + d]
            if "pivot" in cube:
                cube["pivot"] = [round(float(v), 4) for v in np.asarray(cube["pivot"], dtype=float) + d]
        if pivot_too:
            self.pivot = [round(float(v), 4) for v in np.asarray(self.pivot, dtype=float) + d]
        return self

    # ---- composite shapes -----------------------------------------------------
    def cylinder(self, center, direction, radius, length, mat, segments=8, up=(0, 1, 0), inflate=None):
        """N-gon prism built from segments/2 rotated boxes (the classic Blockbench trick)."""
        R0 = frame_from(direction, up)
        width = 2 * radius * math.tan(math.pi / segments)
        for k in range(segments // 2):
            R = R0 @ _ry(math.radians(k * 360.0 / segments))
            c = np.asarray(center, dtype=float)
            d = np.array([width, length, 2 * radius]) / 2
            self.box(c - d, c + d, mat, rot=euler_for(R), pivot=c, inflate=inflate)

    def tube(self, a, b, radius, mat, segments=6, up=(0, 1, 0)):
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        self.cylinder((a + b) / 2, b - a, radius, np.linalg.norm(b - a), mat, segments=segments, up=up)

    def taper(self, base, direction, length, r0, r1, mat, steps=4, segments=6, up=(0, 1, 0)):
        """Stacked cylinders narrowing from r0 to r1 (cones, nozzles, horns)."""
        d = norm(direction)
        step = length / steps
        for i in range(steps):
            t = (i + 0.5) / steps
            r = r0 + (r1 - r0) * t
            c = np.asarray(base, dtype=float) + d * (step * (i + 0.5))
            self.cylinder(c, d, max(r, 0.05), step * 1.02, mat, segments=segments, up=up)

    def spike(self, base, direction, length, width, depth, mat, steps=3, up=(0, 1, 0), roll=0.0):
        """Tapered flat spike (teeth, arrowheads). width across, depth thickness."""
        d = norm(direction)
        step = length / steps
        for i in range(steps):
            f = 1.0 - i / steps
            c = np.asarray(base, dtype=float) + d * (step * (i + 0.5))
            self.obox(c, d, (max(width * f, 0.12), step * 1.04, max(depth * (0.55 + 0.45 * f), 0.12)), mat,
                      up=up, roll=roll)

    def curve(self, points, w0, w1, h0, h1, mat, up=(0, 1, 0)):
        """Chain of oriented boxes along a polyline with linearly varying thickness."""
        n = len(points) - 1
        for i in range(n):
            t = i / max(n - 1, 1)
            self.seg(points[i], points[i + 1], w0 + (w1 - w0) * t, h0 + (h1 - h0) * t, mat, up=up, overlap=0.35)

    def ring(self, center, axis, radius, thickness, width, mat, count=12, up=(0, 1, 0)):
        """Torus-ish ring of boxes (bands around tanks, nozzle rims)."""
        axis = norm(axis)
        R0 = frame_from(axis, up)
        e1 = R0[:, 0]
        seg_len = 2 * radius * math.tan(math.pi / count) + 0.05
        for k in range(count):
            ang = 360.0 * k / count
            radial = rotate_about(e1, axis, ang)
            c = np.asarray(center, dtype=float) + radial * radius
            tangent = np.cross(axis, radial)
            self.obox(c, tangent, (thickness, seg_len, width), mat, up=axis)


class Model:
    def __init__(self, identifier, atlas, density=2.0, seed=7):
        self.identifier = identifier
        self.atlas = atlas
        self.density = density
        self.rng = random.Random(seed)
        self.bones = []
        self.by_name = {}

    def bone(self, name, parent=None, pivot=(0, 0, 0), rotation=None):
        if name in self.by_name:
            raise ValueError("duplicate bone " + name)
        b = Bone(self, name, parent, pivot, rotation)
        self.bones.append(b)
        self.by_name[name] = b
        return b

    def face_uvs(self, size, mat, faces=None, full=False):
        rx, ry, cw, ch = self.atlas.region(mat)
        out = {}
        for face, (iu, iv) in FACE_DIMS.items():
            if faces is not None and face not in faces:
                continue
            du, dv = size[iu], size[iv]
            if du < 1e-4 or dv < 1e-4:
                continue  # zero-area face of a flat plane
            if full:
                out[face] = {"uv": [rx + 1, ry + 1], "uv_size": [cw - 2, ch - 2]}
                continue
            w = min(max(du * self.density, 1.0), cw - 2)
            h = min(max(dv * self.density, 1.0), ch - 2)
            ox = rx + 1 + self.rng.uniform(0, cw - 2 - w)
            oy = ry + 1 + self.rng.uniform(0, ch - 2 - h)
            out[face] = {"uv": [round(ox, 2), round(oy, 2)], "uv_size": [round(w, 2), round(h, 2)]}
        return out

    def to_json(self, bounds=(4, 4, (0, 1.5, 0))):
        bones = []
        for b in self.bones:
            j = {"name": b.name, "pivot": b.pivot}
            if b.parent:
                j["parent"] = b.parent
            if b.rotation:
                j["rotation"] = [round(float(r), 4) for r in b.rotation]
            if b.cubes:
                j["cubes"] = b.cubes
            bones.append(j)
        return {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": "geometry." + self.identifier,
                    "texture_width": self.atlas.size,
                    "texture_height": self.atlas.size,
                    "visible_bounds_width": bounds[0],
                    "visible_bounds_height": bounds[1],
                    "visible_bounds_offset": list(bounds[2]),
                },
                "bones": bones,
            }],
        }

    def cube_count(self):
        return sum(len(b.cubes) for b in self.bones)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_json(), f, separators=(",", ":"))


# --------------------------------------------------------------------------- animations
class Anim:
    """GeckoLib animation builder. Times in seconds, rotations in degrees (Bedrock convention)."""

    def __init__(self, name, length, loop=False):
        self.name = name
        self.length = length
        self.loop = loop  # True | False | "hold_on_last_frame"
        self.bones = {}

    def key(self, bone, channel, t, vec, easing=None):
        ch = self.bones.setdefault(bone, {}).setdefault(channel, {})
        v = [round(float(x), 4) for x in vec]
        if easing and easing != "linear":
            ch["%.4f" % t] = {"vector": v, "easing": easing}
        else:
            ch["%.4f" % t] = {"vector": v}
        return self

    def rot(self, bone, t, vec, easing=None):
        return self.key(bone, "rotation", t, vec, easing)

    def pos(self, bone, t, vec, easing=None):
        return self.key(bone, "position", t, vec, easing)

    def scale(self, bone, t, vec, easing=None):
        if not hasattr(vec, "__len__"):
            vec = (vec, vec, vec)
        return self.key(bone, "scale", t, vec, easing)

    def to_json(self):
        bones = {}
        for bone, chans in self.bones.items():
            bones[bone] = {c: dict(sorted(v.items(), key=lambda kv: float(kv[0]))) for c, v in chans.items()}
        j = {"animation_length": round(self.length, 4), "bones": bones}
        if self.loop:
            j["loop"] = self.loop
        return j


def save_animations(path, anims):
    data = {"format_version": "1.8.0", "animations": {a.name: a.to_json() for a in anims}}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
