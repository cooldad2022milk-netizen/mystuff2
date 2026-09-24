"""Shared helpers for the hybrid model scripts."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)

from csmgen.geo import norm  # noqa: E402

ASSETS = os.path.join(ROOT, "src", "main", "resources", "assets", "csm")
PREVIEW_DIR = os.environ.get("CSM_PREVIEW_DIR", os.path.join(ROOT, "build", "previews"))


def out(*parts):
    p = os.path.join(ASSETS, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def preview_path(name):
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    return os.path.join(PREVIEW_DIR, name)


def arc_point(ax, az, phi_deg, y, cz=0.0):
    p = math.radians(phi_deg)
    return np.array([ax * math.sin(p), y, cz - az * math.cos(p)])


def arc_normal(ax, az, phi_deg):
    p = math.radians(phi_deg)
    return norm([math.sin(p) / ax, 0.0, -math.cos(p) / az])


def arc_tangent(ax, az, phi_deg):
    p = math.radians(phi_deg)
    return norm([ax * math.cos(p), 0.0, az * math.sin(p)])


def arc_band(bone, ax, az, phi0, phi1, y0, y1, thick, mat, steps=14, cz=0.0):
    """Curved vertical band following an ellipse (lips, jaw, mouth cavity)."""
    for i in range(steps):
        pa = phi0 + (phi1 - phi0) * i / steps
        pb = phi0 + (phi1 - phi0) * (i + 1) / steps
        a = arc_point(ax, az, pa, (y0 + y1) / 2, cz)
        b = arc_point(ax, az, pb, (y0 + y1) / 2, cz)
        n = arc_normal(ax, az, (pa + pb) / 2)
        bone.seg(a, b, thick, y1 - y0, mat, up=(0, 1, 0), overlap=0.25)
        _ = n


def saw_chain_along(bone_links, start, step_vec, count, edge_offset, tooth_dir, link_dims, tooth_len, mats,
                    side_axis, alternate=0.18):
    """Chain links + cutter teeth marching from `start` in `step_vec` increments.

    edge_offset: vector from blade centreline to the edge where the chain rides.
    tooth_dir:   outward direction of the cutters (perpendicular to blade edge).
    side_axis:   blade thickness axis (cutters alternate left/right along it).
    """
    chain_mat, tooth_mat = mats
    step_vec = np.asarray(step_vec, dtype=float)
    tooth_dir = norm(tooth_dir)
    side_axis = norm(side_axis)
    along = norm(step_vec)
    for i in range(count):
        c = np.asarray(start, dtype=float) + step_vec * i + np.asarray(edge_offset, dtype=float)
        # link plate
        bone_links.obox(c + tooth_dir * (link_dims[2] / 2), along, (link_dims[0], link_dims[1], link_dims[2]),
                        chain_mat, up=tooth_dir)
        # cutter: leans back like a real chainsaw tooth
        side = alternate if i % 2 == 0 else -alternate
        base = c + tooth_dir * link_dims[2] + side_axis * side
        bone_links.obox(base + tooth_dir * (tooth_len / 2) - along * 0.1, along,
                        (0.42, link_dims[1] * 0.55, tooth_len), tooth_mat, up=tooth_dir)
        # hooked tip
        bone_links.obox(base + tooth_dir * (tooth_len - 0.1) + along * 0.18, along, (0.42, 0.34, 0.2), tooth_mat,
                        up=tooth_dir)
