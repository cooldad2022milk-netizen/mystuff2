"""Shared sword-making helpers for the Katana / Longsword hybrids (and anything else with a blade)."""
import math

import numpy as np

from csmgen.geo import norm


def katana_blade(bone, base, direction, length, up, width=1.3, thick=0.35, curve=0.08, mats=("steel", "edge", "hamon")):
    """Slightly curved single-edged blade. `up` = the side the cutting edge faces."""
    D = norm(direction)
    U = norm(np.asarray(up, dtype=float) - np.dot(up, D) * D)
    steps = 12
    pts = []
    for i in range(steps + 1):
        t = i / steps
        # sori: the blade bows away from the edge
        pts.append(np.asarray(base, dtype=float) + D * (length * t) - U * (curve * length * math.sin(t * math.pi) * 0.5))
    for i in range(steps):
        t = (i + 0.5) / steps
        w = width * (1 - 0.35 * t) if t < 0.9 else width * 0.65 * (1 - (t - 0.9) / 0.1 * 0.7)
        a, b = pts[i], pts[i + 1]
        seg = b - a
        bone.seg(a + U * (w * 0.25), b + U * (w * 0.25), thick, w * 0.5, mats[0], up=U, overlap=0.1)   # spine half
        bone.seg(a - U * (w * 0.2), b - U * (w * 0.2), thick * 0.7, w * 0.45, mats[2], up=U, overlap=0.1)  # temper line
        bone.seg(a - U * (w * 0.47), b - U * (w * 0.47), thick * 0.4, w * 0.12, mats[1], up=U, overlap=0.1)  # edge
        _ = seg
    tip = pts[-1]
    bone.spike(tip - D * 0.6, D - U * 0.4, 1.4, width * 0.55, thick * 0.8, mats[1], steps=2, up=U)
    return pts


def tsuba(bone, center, axis, radius, mat="iron", up=(0, 1, 0)):
    """Round sword guard."""
    bone.cylinder(center, axis, radius, 0.4, mat, segments=10, up=up)
    bone.ring(center, axis, radius + 0.05, 0.2, 0.5, "gold", count=10, up=up)


def tsuka(bone, a, b, radius=0.55, wrap="wrap", mats=("same", "gold")):
    """Wrapped katana grip from a to b with a pommel cap."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    bone.tube(a, b, radius, mats[0], segments=6)
    d = norm(b - a)
    L = np.linalg.norm(b - a)
    for k in range(int(L / 0.9)):
        p = a + d * (0.45 + k * 0.9)
        bone.ring(p, d, radius + 0.05, 0.14, 0.35, wrap, count=6)
    bone.cylinder(b + d * 0.15, d, radius + 0.1, 0.4, mats[1], segments=6)


def longsword_blade(bone, base, direction, length, flat_up, width=2.6, thick=0.5, mats=("steel", "edge", "fuller")):
    """Straight double-edged blade with a fuller down the middle and a pointed tip."""
    D = norm(direction)
    U = norm(np.asarray(flat_up, dtype=float) - np.dot(flat_up, D) * D)  # normal of the flat
    W = np.cross(D, U)                                                     # across the blade
    base = np.asarray(base, dtype=float)
    body = length * 0.86
    bone.obox(base + D * (body / 2), D, (width, body, thick), mats[0], up=U)
    bone.obox(base + D * (body * 0.45), D, (width * 0.28, body * 0.85, thick + 0.1), mats[2], up=U)
    for s in (-1, 1):
        bone.obox(base + D * (body / 2) + W * s * (width / 2 - 0.12), D, (0.24, body, thick * 0.6), mats[1], up=U)
    tip_len = length - body
    for i in range(4):
        t = (i + 0.5) / 4
        w = width * (1 - t)
        bone.obox(base + D * (body + tip_len * t), D, (max(w, 0.15), tip_len / 4 * 1.1, thick * (1 - 0.5 * t)), mats[1],
                  up=U)
    return base + D * length


def crossguard(bone, center, along, span, mat="guard", up=(0, 1, 0)):
    """Bar-shaped cross-guard with flared ends."""
    A = norm(along)
    c = np.asarray(center, dtype=float)
    bone.obox(c, A, (0.9, span, 0.9), mat, up=up)
    for s in (-1, 1):
        bone.obox(c + A * s * (span / 2), A, (1.2, 0.6, 1.2), mat, up=up)
