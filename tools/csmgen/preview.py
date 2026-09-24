"""
Software preview renderer that reproduces GeckoLib 4 + vanilla PlayerModel transforms,
so models/animations can be checked without launching Minecraft.

Pipeline for a point of a part bone (e.g. "right_arm"):
  geo point g  --(bone chain, GeckoLib prepMatrixForBone)-->
  translate(-P_g)  (what HybridPartRenderer does)  -->  scale(-1,-1,1)  -->
  vanilla ModelPart.translateAndRotate  -->  entity frame (y up, facing -z).
"""
import json
import math

import numpy as np
from PIL import Image

VANILLA_PARTS = {
    "head": (0, 0, 0), "body": (0, 0, 0),
    "right_arm": (-5, 2, 0), "left_arm": (5, 2, 0),
    "right_leg": (-1.9, 12, 0), "left_leg": (1.9, 12, 0),
}


def T(v):
    m = np.eye(4)
    m[:3, 3] = v
    return m


def S(v):
    m = np.eye(4)
    m[0, 0], m[1, 1], m[2, 2] = v
    return m


def RX(t):
    c, s = math.cos(t), math.sin(t)
    m = np.eye(4)
    m[1:3, 1:3] = [[c, -s], [s, c]]
    return m


def RY(t):
    c, s = math.cos(t), math.sin(t)
    m = np.eye(4)
    m[0, 0], m[0, 2], m[2, 0], m[2, 2] = c, s, -s, c
    return m


def RZ(t):
    c, s = math.cos(t), math.sin(t)
    m = np.eye(4)
    m[0:2, 0:2] = [[c, -s], [s, c]]
    return m


def load_geo(path):
    with open(path, encoding="utf-8") as f:
        g = json.load(f)["minecraft:geometry"][0]
    return g


def load_anim(path, name):
    if path is None or name is None:
        return {}
    with open(path, encoding="utf-8") as f:
        a = json.load(f)["animations"][name]
    out = {}
    for bone, chans in a.get("bones", {}).items():
        out[bone] = {}
        for ch, keys in chans.items():
            ks = []
            for t, v in keys.items():
                vec = v["vector"] if isinstance(v, dict) else v
                ks.append((float(t), [float(x) for x in vec]))
            ks.sort()
            out[bone][ch] = ks
    return out


def sample(keys, t, default):
    if not keys:
        return default
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / max(t1 - t0, 1e-9)
            return [a + (b - a) * f for a, b in zip(v0, v1)]
    return keys[-1][1]


def bone_mats(geo, anim, t):
    bones = {b["name"]: b for b in geo["bones"]}
    mats = {}

    def get(name):
        if name in mats:
            return mats[name]
        b = bones[name]
        parent = get(b["parent"]) if b.get("parent") else np.eye(4)
        piv = np.array([-b["pivot"][0], b["pivot"][1], b["pivot"][2]]) / 16
        r0 = b.get("rotation", [0, 0, 0])
        ab = anim.get(name, {})
        ar = sample(ab.get("rotation"), t, [0, 0, 0])
        ap = sample(ab.get("position"), t, [0, 0, 0])
        asc = sample(ab.get("scale"), t, [1, 1, 1])
        rx = math.radians(-(r0[0] + ar[0]))
        ry = math.radians(-(r0[1] + ar[1]))
        rz = math.radians(r0[2] + ar[2])
        m = (parent @ T(np.array([-ap[0], ap[1], ap[2]]) / 16) @ T(piv) @ RZ(rz) @ RY(ry) @ RX(rx)
             @ S(asc) @ T(-piv))
        mats[name] = m
        return m

    for n in bones:
        get(n)
    return bones, mats


def top_of(bones, name):
    while bones[name].get("parent"):
        name = bones[name]["parent"]
    return name


def part_matrix(top_bone, pose):
    """Maps geo-frame points of a top-level part bone to the upright entity frame."""
    piv = np.array([-top_bone["pivot"][0], top_bone["pivot"][1], top_bone["pivot"][2]]) / 16
    name = top_bone["name"]
    if name not in VANILLA_PARTS:
        return np.eye(4)
    px, py, pz = VANILLA_PARTS[name]
    p = pose.get(name, {})
    x, y, z = p.get("pos", (px, py, pz))
    xr, yr, zr = p.get("rot", (0, 0, 0))
    F = np.array([[-1, 0, 0, 0], [0, -1, 0, 1.5], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)
    return F @ T(np.array([x, y, z]) / 16) @ RZ(zr) @ RY(yr) @ RX(xr) @ S((-1, -1, 1)) @ T(-piv)


FACES = {  # geo-frame face -> (bedrock uv key, corner indices in quad order)
    "north": ("north", [0, 1, 3, 2]),   # -z
    "south": ("south", [5, 4, 6, 7]),   # +z
    "up": ("up", [2, 3, 7, 6]),         # +y
    "down": ("down", [4, 5, 1, 0]),     # -y
    "west_g": ("east", [4, 0, 2, 6]),   # -x geo == bedrock +x (east)
    "east_g": ("west", [1, 5, 7, 3]),   # +x geo == bedrock -x (west)
}


def cube_tris(cube, M):
    o = np.array(cube["origin"], dtype=float)
    s = np.array(cube["size"], dtype=float)
    inf = cube.get("inflate", 0.0) / 16
    og = np.array([-(o[0] + s[0]), o[1], o[2]]) / 16 - inf
    sz = s / 16 + 2 * inf
    xs = [og[0], og[0] + sz[0]]
    ys = [og[1], og[1] + sz[1]]
    zs = [og[2], og[2] + sz[2]]
    corners = np.array([[xs[i & 1], ys[(i >> 1) & 1], zs[(i >> 2) & 1], 1.0] for i in range(8)])
    if "rotation" in cube:
        pv = np.array(cube.get("pivot", [0, 0, 0]), dtype=float)
        pg = np.array([-pv[0], pv[1], pv[2]]) / 16
        r = cube["rotation"]
        R = T(pg) @ RZ(math.radians(r[2])) @ RY(math.radians(-r[1])) @ RX(math.radians(-r[0])) @ T(-pg)
        corners = corners @ R.T
    corners = corners @ M.T
    out = []
    uvs = cube.get("uv", {})
    for _, (key, idx) in FACES.items():
        if key not in uvs:
            continue
        u, v = uvs[key]["uv"]
        w, h = uvs[key]["uv_size"]
        q = corners[idx, :3]
        quv = np.array([[u, v], [u + w, v], [u + w, v + h], [u, v + h]], dtype=float)
        out.append((q[[0, 1, 2]], quv[[0, 1, 2]]))
        out.append((q[[0, 2, 3]], quv[[0, 2, 3]]))
    return out


class Canvas:
    def __init__(self, w, h, bg=(38, 36, 44)):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3), dtype=float)
        self.rgb[:] = bg
        yy = np.linspace(0, 1, h)[:, None]
        self.rgb *= (1.1 - 0.35 * yy)[..., None]
        self.z = np.full((h, w), np.inf)

    def tri(self, P, Z, UV, tex, shade, flat=None):
        x0 = int(max(math.floor(P[:, 0].min()), 0))
        x1 = int(min(math.ceil(P[:, 0].max()), self.w - 1))
        y0 = int(max(math.floor(P[:, 1].min()), 0))
        y1 = int(min(math.ceil(P[:, 1].max()), self.h - 1))
        if x1 < x0 or y1 < y0:
            return
        (ax, ay), (bx, by), (cx, cy) = P
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            return
        gy, gx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
        px, py = gx + 0.5, gy + 0.5
        w0 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / den
        w1 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            return
        z = w0 * Z[0] + w1 * Z[1] + w2 * Z[2]
        zb = self.z[y0:y1 + 1, x0:x1 + 1]
        m = inside & (z < zb)
        if not m.any():
            return
        if flat is not None:
            col = np.broadcast_to(np.asarray(flat, dtype=float), m.shape + (3,))
            a = np.full(m.shape, 255)
        else:
            u = w0 * UV[0, 0] + w1 * UV[1, 0] + w2 * UV[2, 0]
            v = w0 * UV[0, 1] + w1 * UV[1, 1] + w2 * UV[2, 1]
            ui = np.clip(u.astype(int), 0, tex.shape[1] - 1)
            vi = np.clip(v.astype(int), 0, tex.shape[0] - 1)
            texel = tex[vi, ui]
            col = texel[..., :3].astype(float)
            a = texel[..., 3]
        m = m & (a > 20)
        region = self.rgb[y0:y1 + 1, x0:x1 + 1]
        region[m] = col[m] * shade
        zb[m] = z[m]

    def save(self, path):
        Image.fromarray(np.clip(self.rgb, 0, 255).astype(np.uint8), "RGB").save(path)


def body_boxes(show_arms=True, slim=False, show_head=False):
    """Stand-in vanilla player (shirt/pants/skin) for context, as (bone-part, from, to, colour)."""
    aw = 3 if slim else 4
    boxes = [
        ("body", (-4, 12, -2), (4, 24, 2), (225, 225, 230)),
        ("body", (-0.6, 17, -2.15), (0.6, 23.5, -2.0), (30, 30, 36)),  # tie
        ("right_leg", (-3.9, 0, -2), (0.1, 12, 2), (40, 40, 52)),
        ("left_leg", (-0.1, 0, -2), (3.9, 12, 2), (40, 40, 52)),
    ]
    if show_head:
        boxes += [("head", (-4, 24, -4), (4, 32, 4), (224, 176, 140)),
                  ("head", (-4.1, 30, -4.1), (4.1, 32.2, 4.1), (60, 40, 30)),
                  ("head", (2.6, 27.6, -4.05), (1.4, 28.4, -4.0), (40, 40, 60))]
    if show_arms:
        boxes += [
            ("right_arm", (-4 - aw, 12, -2), (-4, 24, 2), (224, 176, 140)),
            ("right_arm", (-4 - aw - 0.1, 18, -2.1), (-3.9, 24.1, 2.1), (225, 225, 230)),
            ("left_arm", (4, 12, -2), (4 + aw, 24, 2), (224, 176, 140)),
            ("left_arm", (3.9, 18, -2.1), (4 + aw + 0.1, 24.1, 2.1), (225, 225, 230)),
        ]
    return boxes


PART_PIVOTS = {"head": (0, 24, 0), "body": (0, 24, 0), "right_arm": (-5, 22, 0), "left_arm": (5, 22, 0),
               "right_leg": (-1.9, 12, 0), "left_leg": (1.9, 12, 0)}


def render(geo_path, tex_path, out_path, anim_path=None, anim=None, t=0.0, pose=None, yaw=30.0, pitch=10.0,
           size=(640, 760), scale=13.0, center=(0, 1.1), hidden=(), show_body=True, show_arms=True,
           focus=None, bg=(38, 36, 44), show_head=False):
    pose = pose or {}
    geo = load_geo(geo_path)
    tex = np.asarray(Image.open(tex_path).convert("RGBA"))
    an = load_anim(anim_path, anim)
    bones, mats = bone_mats(geo, an, t)

    view = RX(math.radians(pitch)) @ RY(math.radians(yaw))
    cv = Canvas(size[0], size[1], bg)
    ppu = scale * 16  # pixels per block
    L = np.array([0.35, 0.8, -0.5])
    L = L / np.linalg.norm(L)

    def project(pts):
        pv = np.c_[pts, np.ones(len(pts))] @ view.T
        sx = -(pv[:, 0] - center[0] * 0) * ppu + size[0] / 2
        sy = -(pv[:, 1] - center[1]) * ppu + size[1] / 2
        return np.c_[sx, sy], pv[:, 2], pv[:, :3]

    def draw(tris, tex_img, flat=None):
        for q, uv in tris:
            P, Z, W = project(q)
            n = np.cross(W[1] - W[0], W[2] - W[0])
            nn = np.linalg.norm(n)
            if nn < 1e-12:
                continue
            n /= nn
            shade = 0.55 + 0.45 * abs(float(np.dot(n, L)))
            cv.tri(P, Z, uv, tex_img, shade, flat)

    tops = {n: b for n, b in bones.items() if not b.get("parent")}
    if show_body:
        for part, frm, to, col in body_boxes(show_arms, show_head=show_head):
            piv = PART_PIVOTS[part]
            fake_top = {"name": part, "pivot": list(piv)}
            M = part_matrix(fake_top, pose)
            cube = {"origin": list(np.minimum(frm, to)), "size": list(np.abs(np.subtract(to, frm))),
                    "uv": {k: {"uv": [0, 0], "uv_size": [1, 1]} for k in
                           ("north", "south", "east", "west", "up", "down")}}
            draw(cube_tris(cube, M), None, flat=col)

    for name, b in bones.items():
        if any(h == name or _is_under(bones, name, h) for h in hidden):
            continue
        top = tops[top_of(bones, name)]
        M = part_matrix(top, pose) @ mats[name]
        for cube in b.get("cubes", []):
            draw(cube_tris(cube, M), tex)
    cv.save(out_path)
    return out_path


def _is_under(bones, name, ancestor):
    while bones[name].get("parent"):
        name = bones[name]["parent"]
        if name == ancestor:
            return True
    return False


def contact_sheet(paths, out, cols=3):
    ims = [Image.open(p) for p in paths]
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows), (20, 20, 24))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(out)
    return out
