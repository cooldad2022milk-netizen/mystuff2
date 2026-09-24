"""
Smooth organic shapes for the procedural models.

Stacking boxes gives stair-stepped, blocky silhouettes. Instead, these helpers cover a parametric surface with thin
oriented plates (one per (u, v) cell, pushed inward so their outer face sits on the surface, slightly oversized so
neighbours overlap): the result reads as a faceted smooth solid, like a low-poly mesh.

Surfaces are functions f(u, v) -> point with u, v in [0, 1]:
  * ellipsoid / superellipsoid (heads, masks, bulbs, eyeballs; exponent < 1 gives a rounded box)
  * loft along a path with elliptical sections (snouts, horns, beaks, limbs, tentacles, bodies)
"""
import math

import numpy as np

from .geo import norm, frame_from


def _sgnpow(x, e):
    return math.copysign(abs(x) ** e, x)


# --------------------------------------------------------------------------- surfaces
def ellipsoid(center, radii, e_lat=1.0, e_lon=1.0, frame=None):
    """u = longitude (0 at the front, -z, going round through +x), v = latitude (0 bottom pole, 1 top pole).

    e_lat / e_lon < 1 square the shape off (0.5 = a rounded box), > 1 pinch it.
    frame: optional 3x3 rotation applied to the local shape (columns = local x, y, z axes).
    """
    c = np.asarray(center, dtype=float)
    rx, ry, rz = radii
    R = np.eye(3) if frame is None else np.asarray(frame, dtype=float)

    def f(u, v):
        lon = u * 2 * math.pi
        lat = (v - 0.5) * math.pi
        cl = _sgnpow(math.cos(lat), e_lat)
        p = np.array([rx * cl * _sgnpow(math.sin(lon), e_lon),
                      ry * _sgnpow(math.sin(lat), e_lat),
                      -rz * cl * _sgnpow(math.cos(lon), e_lon)])
        return c + R @ p
    return f


def loft(path, rx, ry, up=(0, 1, 0), twist=None, offset=None):
    """Tube along path(t) (t = v in [0, 1]); cross-section ellipse rx(t) x ry(t); u runs round the section.

    rx / ry / twist / offset may be numbers or functions of t. `up` orients the section's ry axis (a vector or a
    function of t). offset(t) -> (dx, dy) shifts the section centre in its own frame (asymmetric snouts, jaws).
    """
    def val(x, t):
        return x(t) if callable(x) else x

    def frame(t):
        eps = 1e-3
        a = np.asarray(path(max(0.0, t - eps)), dtype=float)
        b = np.asarray(path(min(1.0, t + eps)), dtype=float)
        tan = norm(b - a)
        upv = np.asarray(val(up, t), dtype=float)
        side = np.cross(tan, upv)
        if np.linalg.norm(side) < 1e-6:
            side = np.cross(tan, [1.0, 0, 0]) if abs(tan[0]) < 0.9 else np.cross(tan, [0, 0, 1.0])
        side = norm(side)
        vert = norm(np.cross(side, tan))
        return tan, side, vert

    def f(u, v):
        t = v
        tan, side, vert = frame(t)
        a = u * 2 * math.pi + math.radians(val(twist, t) if twist is not None else 0.0)
        ox, oy = val(offset, t) if offset is not None else (0.0, 0.0)
        p = np.asarray(path(t), dtype=float)
        return p + side * (ox + val(rx, t) * math.sin(a)) + vert * (oy + val(ry, t) * math.cos(a))
    return f


def polyline(points):
    """Path through points, parametrised by arc length, with Catmull-Rom smoothing."""
    pts = [np.asarray(p, dtype=float) for p in points]
    if len(pts) == 2:
        a, b = pts
        return lambda t: a + (b - a) * t
    seg = [np.linalg.norm(q - p) for p, q in zip(pts, pts[1:])]
    total = sum(seg)
    cum = np.concatenate([[0], np.cumsum(seg)]) / total

    def f(t):
        t = min(max(t, 0.0), 1.0)
        i = min(int(np.searchsorted(cum, t, side="right")) - 1, len(pts) - 2)
        i = max(i, 0)
        s = (t - cum[i]) / max(cum[i + 1] - cum[i], 1e-9)
        p0 = pts[i - 1] if i > 0 else 2 * pts[i] - pts[i + 1]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else 2 * pts[i + 1] - pts[i]
        s2, s3 = s * s, s * s * s
        return 0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s2 + (-p0 + 3 * p1 - 3 * p2 + p3) * s3)
    return f


def taper(r0, r1, power=1.0):
    """Radius function going from r0 at t=0 to r1 at t=1."""
    return lambda t: r0 + (r1 - r0) * (t ** power)


def profile(*pairs):
    """Piecewise-linear radius profile from (t, r) pairs."""
    ts = [p[0] for p in pairs]
    rs = [p[1] for p in pairs]
    return lambda t: float(np.interp(t, ts, rs))


# --------------------------------------------------------------------------- plating
def plate(bone, p00, p10, p01, p11, mat, thick=0.35, overlap=1.12, min_size=0.12, inside=None):
    """One thin plate covering the quad p00-p10-p11-p01, its outer face on the quad.

    `inside`: a point on the inner side of the surface (the plate is pushed towards it, so the plate's outer face
    stays on the surface whichever way the parametrisation winds)."""
    p00, p10, p01, p11 = (np.asarray(p, dtype=float) for p in (p00, p10, p01, p11))
    du = ((p10 - p00) + (p11 - p01)) / 2
    dv = ((p01 - p00) + (p11 - p10)) / 2
    n = np.cross(du, dv)
    ln = np.linalg.norm(n)
    L = np.linalg.norm(dv)
    if ln < 1e-7 or L < 1e-6:
        # degenerate (pole) cell: use the diagonal
        dv = p11 - p00
        L = np.linalg.norm(dv)
        du = p10 - p01
        n = np.cross(du, dv)
        ln = np.linalg.norm(n)
        if ln < 1e-7 or L < 1e-6:
            return None
    n /= ln
    if inside is not None and np.dot(n, (p00 + p10 + p01 + p11) / 4 - np.asarray(inside, dtype=float)) < 0:
        n = -n  # n must point outward: the plate is then pushed inward by half its thickness
    dvn = dv / L
    du_perp = du - np.dot(du, dvn) * dvn
    W = np.linalg.norm(du_perp)
    c = (p00 + p10 + p01 + p11) / 4 - n * (thick / 2)
    return bone.obox(c, dvn, (max(W * overlap, min_size), max(L * overlap, min_size), thick), mat, up=n)


def shell(bone, f, nu, nv, mat, thick=0.35, overlap=1.12, u0=0.0, u1=1.0, v0=0.0, v1=1.0, mat_fn=None, skip=None,
          flip=False):
    """Cover surface f over [u0,u1] x [v0,v1] with nu x nv plates.

    mat_fn(u, v) -> material name (defaults to `mat`); skip(u, v) -> True leaves a hole (mouths, eye sockets).
    flip puts the plates on the other side of the surface (inside a cavity).
    """
    us = np.linspace(u0, u1, nu + 1)
    vs = np.linspace(v0, v1, nv + 1)
    grid = [[np.asarray(f(u, v), dtype=float) for u in us] for v in vs]
    # the centre of each ring of the full surface tells which side is inside
    centres = [sum(np.asarray(f(w, v), dtype=float) for w in (0.0, 0.25, 0.5, 0.75)) / 4 for v in vs]
    count = 0
    for j in range(nv):
        for i in range(nu):
            uc = (us[i] + us[i + 1]) / 2
            vc = (vs[j] + vs[j + 1]) / 2
            if skip is not None and skip(uc, vc):
                continue
            m = mat_fn(uc, vc) if mat_fn is not None else mat
            if m is None:
                continue
            a, b, c, d = grid[j][i], grid[j][i + 1], grid[j + 1][i], grid[j + 1][i + 1]
            if flip:
                a, b, c, d = b, a, d, c
            inside = (centres[j] + centres[j + 1]) / 2
            if flip:
                inside = None
            if plate(bone, a, b, c, d, m, thick=thick, overlap=overlap, inside=inside) is not None:
                count += 1
    return count


def surface_frame(f, u, v, eps=1e-3):
    """Point, outward-ish normal, u-tangent and v-tangent of surface f at (u, v)."""
    p = np.asarray(f(u, v), dtype=float)
    du = np.asarray(f(min(u + eps, 1.0), v), dtype=float) - np.asarray(f(max(u - eps, 0.0), v), dtype=float)
    dv = np.asarray(f(u, min(v + eps, 1.0)), dtype=float) - np.asarray(f(u, max(v - eps, 0.0)), dtype=float)
    n = norm(np.cross(du, dv))
    # make the normal point outward: away from the centre of this ring of the surface
    c = sum(np.asarray(f(w, v), dtype=float) for w in (0.0, 0.25, 0.5, 0.75)) / 4
    if np.dot(n, p - c) < 0:
        n = -n
    return p, n, norm(du), norm(dv)


# --------------------------------------------------------------------------- composites
def horn(bone, root, direction, length, r0, bend_axis=None, bend=0.0, mat="horn", tip_mat=None, sections=8, around=8,
         r1=0.08, flat=1.0, thick=0.3, up=None, power=0.9, tip_from=0.72):
    """A smooth tapering horn curving `bend` degrees in total about bend_axis.

    flat squashes the section along the loft's `up` axis (a fin: flat=0.25 with up across the fin).
    """
    d0 = norm(direction)
    pts = [np.asarray(root, dtype=float)]
    d = d0.copy()
    steps = 12
    for k in range(steps):
        pts.append(pts[-1] + d * (length / steps))
        if bend_axis is not None and bend:
            from .geo import rotate_about
            d = norm(rotate_about(d, bend_axis, bend / steps))
    path = polyline(pts)
    r = taper(r0, r1, power)
    if up is None:
        up = np.cross(d0, [1.0, 0, 0]) if abs(d0[0]) < 0.9 else (0, 1, 0)
    f = loft(path, r, lambda t: r(t) * flat, up=up)
    mf = None
    if tip_mat:
        mf = lambda u, v: tip_mat if v > tip_from else mat
    shell(bone, f, around, sections, mat, thick=thick, mat_fn=mf)
    return path, f


def tooth_row(bone, a, b, count, length, width, direction, mat, depth=0.3, jitter=0.0, rng=None, up=None):
    """A row of triangular teeth between points a and b, pointing along direction."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    d = norm(direction)
    u = up if up is not None else norm(np.cross(b - a, d))
    for k in range(count):
        t = (k + 0.5) / count
        p = a + (b - a) * t
        ln = length * (1 + (rng.uniform(-jitter, jitter) if rng is not None and jitter else 0))
        bone.spike(p, d, ln, width, depth, mat, steps=3, up=u)


def scaled(f, k, about=None):
    """Surface f shrunk (k < 1) towards its section centres; `about(v)` gives the centre, else the u-average."""
    def g(u, v):
        p = np.asarray(f(u, v), dtype=float)
        if about is not None:
            c = np.asarray(about(v), dtype=float)
        else:
            c = sum(np.asarray(f(w, v), dtype=float) for w in (0.0, 0.25, 0.5, 0.75)) / 4
        return c + (p - c) * k
    return g


class Mouth:
    """A jaw cut out of a lofted surface: the region |u - uc| < half_u, v0 < v < v1 becomes a separate (animatable)
    lower-jaw shell, a dark cavity lines the inside and teeth run along the lip lines.

    Use `skip` when shelling the main surface, then call `build`.
    """

    def __init__(self, f, uc=0.5, half_u=0.2, v0=0.4, v1=0.85):
        self.f, self.uc, self.half_u, self.v0, self.v1 = f, uc, half_u, v0, v1

    def skip(self, u, v):
        return abs(u - self.uc) < self.half_u and self.v0 < v < self.v1

    def build(self, head_bone, jaw_bone, jaw_mat, cavity_mat="mouth", tooth_mat="teeth", upper=12, lower=10,
              tooth_len=1.0, tooth_w=0.5, nu=6, nv=8, thick=0.35, gum_mat=None, front_teeth=True):
        f, uc, hu, v0, v1 = self.f, self.uc, self.half_u, self.v0, self.v1
        shell(jaw_bone, f, nu, nv, jaw_mat, u0=uc - hu, u1=uc + hu, v0=v0, v1=v1, thick=thick)
        shell(head_bone, scaled(f, 0.72), nu + 2, nv, cavity_mat, u0=uc - hu - 0.04, u1=uc + hu + 0.04, v0=v0 - 0.02,
              v1=v1 + 0.02, thick=0.3)
        if gum_mat:
            shell(jaw_bone, scaled(f, 0.9), nu, nv, gum_mat, u0=uc - hu * 0.8, u1=uc + hu * 0.8, v0=v0 + 0.02,
                  v1=v1 - 0.02, thick=0.25)

        def lip(u, v):
            p, n, du, dv = surface_frame(f, u, v)
            q = np.asarray(f(uc, v), dtype=float)
            return p, n, norm(q - p)

        # upper teeth hang from the lip line into the jaw; lower teeth rise from the jaw edge
        for side in (-1, 1):
            u_edge = uc + side * hu
            for k in range(upper):
                v = v0 + (v1 - v0) * (k + 0.5) / upper
                p, n, inward = lip(u_edge, v)
                grow = 0.6 + 0.4 * (k + 0.5) / upper
                head_bone.spike(p - n * 0.25, norm(inward + n * 0.05), tooth_len * grow, tooth_w, 0.25, tooth_mat,
                                steps=3, up=n)
            for k in range(lower):
                v = v0 + (v1 - v0) * (k + 0.5) / lower
                u_in = uc + side * hu * 0.86
                p, n, inward = lip(u_in, v)
                grow = 0.5 + 0.5 * (k + 0.5) / lower
                jaw_bone.spike(p - n * 0.3, norm(-inward + n * 0.05), tooth_len * 0.8 * grow, tooth_w * 0.9, 0.25,
                               tooth_mat, steps=3, up=n)
        if front_teeth:
            count = max(3, upper // 2)
            for k in range(count):
                u = uc - hu + 2 * hu * (k + 0.5) / count
                p, n, du, dv = surface_frame(f, u, v1)
                back = np.asarray(f(u, v1 - 0.05), dtype=float) - p
                head_bone.spike(p - n * 0.25, norm(back), tooth_len, tooth_w, 0.25, tooth_mat, steps=3, up=n)
        return self


def membrane(bone, edge_a, edge_b, nu, nv, mat, thick=0.28, sag=0.0, sag_dir=(0, 0, 1), mat_fn=None):
    """A skin stretched between two polylines (bat wings, webbing): bilinear sheet from edge_a(t) to edge_b(t),
    optionally sagging towards sag_dir in the middle."""
    a = polyline(edge_a)
    b = polyline(edge_b)
    sd = np.asarray(sag_dir, dtype=float)

    def f(u, v):
        p = np.asarray(a(v), dtype=float) * (1 - u) + np.asarray(b(v), dtype=float) * u
        return p + sd * (sag * math.sin(math.pi * u) * math.sin(math.pi * min(1.0, v * 1.2)))
    # a sheet has no inside: plates sit centred on it
    us = np.linspace(0, 1, nu + 1)
    vs = np.linspace(0, 1, nv + 1)
    grid = [[np.asarray(f(u, v), dtype=float) for u in us] for v in vs]
    for j in range(nv):
        for i in range(nu):
            m = mat_fn((us[i] + us[i + 1]) / 2, (vs[j] + vs[j + 1]) / 2) if mat_fn else mat
            plate(bone, grid[j][i], grid[j][i + 1], grid[j + 1][i], grid[j + 1][i + 1], m, thick=thick, overlap=1.1)
    return f
