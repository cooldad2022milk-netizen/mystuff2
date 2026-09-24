"""
Forward/inverse kinematics for the vanilla PlayerModel (model space: pixels, +y DOWN, -z forward).

Used so the trigger animations line up with props on the model:
  * Chainsaw: the hand meets the starter-cord handle in front of the chest
  * Crossbow: the hand grips the arrow sticking out of the RIGHT eye socket and draws it out
Both the PlayerAnimator keyframes (player_anims.py) and the prop geometry (crossbow.py)
import the solved poses from here, so they can never drift apart.
"""
import math

import numpy as np

SHOULDER_R = np.array([-5.0, 2.0, 0.0])
SHOULDER_L = np.array([5.0, 2.0, 0.0])
GRIP_R = np.array([-1.0, 9.4, 0.0])      # centre of the right fist, arm-local (bedrock [-6, 12.6, 0])
RIGHT_EYE = np.array([-2.0, -4.0, -4.05])  # head-local (bedrock [-2, 28, -4.05])


def rzyx(x, y, z):
    cx, sx = math.cos(x), math.sin(x)
    cy, sy = math.cos(y), math.sin(y)
    cz, sz = math.cos(z), math.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def fk(pivot, rot, local):
    return np.asarray(pivot, dtype=float) + rzyx(*rot) @ np.asarray(local, dtype=float)


def ik_arm(pivot, local, target, zr_hint=0.0, bounds=((-3.4, 1.2), (-1.8, 1.8), (-1.2, 1.6))):
    """Brute-force + refine for the arm rotation that puts `local` closest to `target`."""
    best = None
    for xr in np.linspace(*bounds[0], 49):
        for yr in np.linspace(*bounds[1], 37):
            for zr in np.linspace(*bounds[2], 15):
                d = np.linalg.norm(fk(pivot, (xr, yr, zr), local) - target) + 0.02 * abs(zr - zr_hint)
                if best is None or d < best[0]:
                    best = (d, np.array([xr, yr, zr]))
    x = best[1]
    step = 0.05
    for _ in range(300):
        improved = False
        for i in range(3):
            for s in (-1, 1):
                y = x.copy()
                y[i] += s * step
                d = np.linalg.norm(fk(pivot, y, local) - target) + 0.02 * abs(y[2] - zr_hint)
                if d < best[0] - 1e-9:
                    best = (d, y)
                    x = y
                    improved = True
        if not improved:
            step *= 0.5
            if step < 1e-4:
                break
    return x, best[0]


def model_to_bedrock_vec(v):
    return np.array([v[0], -v[1], v[2]])


# ------------------------------------------------------------------------ Crossbow (Quanxi) trigger
QX_HEAD = (0.12, 0.05, -0.06)
QX_OUT = np.array([-0.42, -0.08, -1.0]) / np.linalg.norm([-0.42, -0.08, -1.0])


def quanxi_pull():
    eye = fk((0, 0, 0), QX_HEAD, RIGHT_EYE)
    frames = {}
    for key, d in (("grab", 3.2), ("mid", 4.8), ("out", 6.6)):
        target = eye + QX_OUT * d
        rot, err = ik_arm(SHOULDER_R, GRIP_R, target, zr_hint=0.0)
        reach = fk(SHOULDER_R, rot, GRIP_R)
        shift = target - reach  # tiny shoulder slide to finish the straight-line draw
        frames[key] = {"rot": rot, "shift": shift, "target": target}
    grab = frames["grab"]
    R = rzyx(*grab["rot"])
    arrow_local = model_to_bedrock_vec(R.T @ (-QX_OUT))  # hand -> eye, arm-local bedrock
    return {"eye": eye, "frames": frames, "arrow_dir": arrow_local / np.linalg.norm(arrow_local),
            "embed": 3.2 + 2.6}


# ------------------------------------------------------------------------ Chainsaw (Denji) trigger
DJ_HEAD = (0.28, 0.0, 0.0)  # looks down at the cord


def denji_pull():
    frames = {}
    target = np.array([0.2, 4.2, -7.4])
    rot, err = ik_arm(SHOULDER_R, GRIP_R, target, zr_hint=-0.1)
    frames["grab"] = {"rot": rot, "err": err}
    yank_target = np.array([-13.5, -1.5, -5.0])
    rot2, err2 = ik_arm(SHOULDER_R, GRIP_R, yank_target, zr_hint=0.6)
    frames["yank"] = {"rot": rot2, "err": err2}
    return frames


# ------------------------------------------------------------------------ Bomb (Reze) trigger
# the grenade pin hangs from the front of her choker, just under the chin (head-local model space)
REZE_HEAD = (-0.32, 0.0, 0.0)  # chin up to bare the throat
PIN = np.array([0.0, 0.7, -4.4])


def reze_pull():
    ring = fk((0, 0, 0), REZE_HEAD, PIN)
    frames = {}
    rot, err = ik_arm(SHOULDER_R, GRIP_R, ring, zr_hint=-0.2)
    frames["grab"] = {"rot": rot, "err": err, "target": ring}
    yank = ring + np.array([-6.5, 3.5, -4.5])
    rot2, err2 = ik_arm(SHOULDER_R, GRIP_R, yank, zr_hint=0.3)
    frames["yank"] = {"rot": rot2, "err": err2, "target": yank}
    return frames


# ------------------------------------------------------------------------ Spear trigger
# he reaches over his shoulder and draws a spear out of the nape of his neck
SPEAR_HEAD = (0.38, 0.0, 0.0)  # head bowed to bare the nape
NAPE = np.array([0.0, 0.2, 2.3])  # body-local model space (+y down, +z back)
SPEAR_OUT = np.array([0.0, -0.62, 1.0]) / np.linalg.norm([0.0, -0.62, 1.0])


def spear_pull():
    frames = {}
    for key, d in (("grab", 4.0), ("mid", 6.0), ("out", 8.0)):
        target = NAPE + SPEAR_OUT * d
        rot, err = ik_arm(SHOULDER_R, GRIP_R, target, zr_hint=0.3, bounds=((-3.6, -1.9), (-1.2, 1.4), (-0.6, 1.6)))
        reach = fk(SHOULDER_R, rot, GRIP_R)
        frames[key] = {"rot": rot, "shift": target - reach, "target": target, "err": err}
    R = rzyx(*frames["grab"]["rot"])
    local = model_to_bedrock_vec(R.T @ (-SPEAR_OUT))  # hand -> nape, arm-local bedrock
    return {"frames": frames, "spear_dir": local / np.linalg.norm(local), "embed": 4.0}


if __name__ == "__main__":
    for k, v in reze_pull().items():
        print("reze", k, np.round(v["rot"], 3), "err", round(v["err"], 2))
    sp = spear_pull()
    for k, v in sp["frames"].items():
        print("spear", k, np.round(v["rot"], 3), "err", round(v["err"], 2), "shift", np.round(v["shift"], 2))
    print("spear dir", np.round(sp["spear_dir"], 3))
    q = quanxi_pull()
    for k, v in q["frames"].items():
        print("quanxi", k, np.round(v["rot"], 3), "shift", np.round(v["shift"], 2))
    print("arrow dir (bedrock arm-local)", np.round(q["arrow_dir"], 3))
    d = denji_pull()
    for k, v in d.items():
        print("denji", k, np.round(v["rot"], 3), "err", round(v["err"], 2))
