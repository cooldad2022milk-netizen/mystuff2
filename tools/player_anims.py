"""
Generates the PlayerAnimator (emotecraft v3 JSON) body animations in assets/csm/player_animation.

Conventions (vanilla model space): angles in radians, pitch = xRot (negative raises an arm forward),
yaw = yRot, roll = zRot (positive swings the RIGHT arm outward, negative the LEFT arm).
Part positions are absolute (right arm rests at x=-5, y=2).  Parts that are never keyframed keep their
vanilla motion (e.g. legs keep walking during upper-body attacks).

Tick numbers line up with the server logic (Ability classes) and with the GeckoLib animations.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "models"))
import poses  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "src", "main", "resources", "assets", "csm", "player_animation")
PI = math.pi
DEFAULT_POS = {"rightArm": (-5, 2, 0), "leftArm": (5, 2, 0), "rightLeg": (-1.9, 12, 0), "leftLeg": (1.9, 12, 0),
               "head": (0, 0, 0), "body": (0, 0, 0), "torso": (0, 0, 0)}


class A:
    def __init__(self, name, end, stop=None, return_fade=3):
        self.name = name
        self.end = end
        self.stop = end + return_fade if stop is None else stop
        self.moves = []

    def k(self, tick, ease="INOUTSINE", turn=0, **parts):
        """parts: name=(pitch, yaw, roll) or name=dict(rot=(..), pos=(..))"""
        mv = {"tick": int(tick), "easing": "EASE" + ease if ease != "linear" else "linear", "turn": turn}
        for part, v in parts.items():
            if isinstance(v, dict) and any(key in v for key in ("pitch", "yaw", "roll", "x", "y", "z")):
                d = {key: round(val, 4) for key, val in v.items()}
            elif isinstance(v, dict):
                d = {}
                if "rot" in v:
                    d.update(pitch=round(v["rot"][0], 4), yaw=round(v["rot"][1], 4), roll=round(v["rot"][2], 4))
                if "pos" in v:
                    d.update(x=round(v["pos"][0], 3), y=round(v["pos"][1], 3), z=round(v["pos"][2], 3))
            else:
                d = {"pitch": round(v[0], 4), "yaw": round(v[1], 4), "roll": round(v[2], 4)}
            if part == "torso" and "pitch" in d:
                d["pitch"] = -d["pitch"]  # authored as positive = lean forward
            mv[part] = d
        self.moves.append(mv)
        return self

    def save(self):
        data = {
            "version": 3,
            "name": self.name,
            "author": "CSM Hybrids",
            "description": "Chainsaw Man hybrid animation",
            "emote": {
                "beginTick": 0, "endTick": self.end, "stopTick": self.stop, "isLoop": False, "returnTick": 0,
                "nsfw": False, "degrees": False, "moves": self.moves,
            },
        }
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, self.name + ".json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)


NEUTRAL_R = (0.0, 0.0, 0.08)
NEUTRAL_L = (0.0, 0.0, -0.08)
Z3 = (0.0, 0.0, 0.0)


def lerp3(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def arm_at(rot, shift=(0, 0, 0), base=(-5, 2, 0)):
    return {"rot": tuple(float(r) for r in rot), "pos": tuple(float(b + s) for b, s in zip(base, shift))}


# ============================================================================ CHAINSAW
def chainsaw():
    dj = poses.denji_pull()
    grab = tuple(dj["grab"]["rot"])
    yank = tuple(dj["yank"]["rot"])
    head_down = poses.DJ_HEAD

    a = A("chainsaw_pull_cord", 24)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.k(3, "OUTQUAD", rightArm=lerp3(NEUTRAL_R, grab, 0.7), leftArm=(-0.25, 0.1, -0.12), head=head_down, torso=Z3)
    a.k(5, "INOUTQUAD", rightArm=grab, leftArm=(-0.3, 0.1, -0.15), head=head_down, torso=(0.06, 0.0, 0.0))
    # brace: wind the body up, fist pulls the cord out a little
    a.k(8, "INQUAD", rightArm=lerp3(grab, (-0.85, 0.15, -0.9), 0.5), leftArm=(0.35, 0.0, -0.3),
        head=(0.36, -0.12, 0.0), torso=(0.12, 0.14, 0.0))
    # YANK
    a.k(10, "linear", rightArm=lerp3(grab, yank, 0.55), leftArm=(-0.1, 0.0, -0.4), head=(0.12, 0.08, 0.0),
        torso=(0.05, -0.18, 0.0))
    a.k(12, "OUTBACK", rightArm=yank, leftArm=(-0.55, 0.1, -0.55), head=(-0.3, 0.1, 0.0), torso=(-0.08, -0.32, 0.0))
    # the engine catches: devil roar
    a.k(14, "OUTQUAD", rightArm=(-0.35, 0.25, 0.95), leftArm=(-0.35, -0.25, -0.95), head=(-0.5, 0.0, 0.0),
        torso=(-0.14, 0.0, 0.0))
    a.k(18, "INOUTSINE", rightArm=(-0.55, 0.3, 1.15), leftArm=(-0.55, -0.3, -1.15), head=(-0.55, 0.0, 0.05),
        torso=(-0.16, 0.0, 0.0))
    a.k(24, "INOUTSINE", rightArm=(-0.2, 0.0, 0.3), leftArm=(-0.2, 0.0, -0.3), head=(0.0, 0.0, 0.0), torso=Z3)
    a.save()

    r = A("chainsaw_revert", 12)
    r.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.k(3, rightArm=(0.25, 0.0, 0.25), leftArm=(0.25, 0.0, -0.25), head=(0.35, 0.0, 0.0))
    r.k(5, rightArm=(0.15, 0.0, 0.1), leftArm=(0.3, 0.0, -0.15), head=(0.4, 0.1, 0.0))
    r.k(7, rightArm=(0.28, 0.0, 0.2), leftArm=(0.18, 0.0, -0.2), head=(0.3, -0.1, 0.0))
    r.k(12, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.save()

    s = A("chainsaw_slash", 14)
    s.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    s.k(2, "INQUAD", rightArm=(-2.3, 0.9, 0.45), leftArm=(-0.6, -0.3, -0.2), torso=(0.0, 0.45, 0.0))
    s.k(4, "OUTQUAD", rightArm=(-1.35, -1.05, -0.2), leftArm=(-0.7, -0.2, -0.3), torso=(0.08, -0.35, 0.0))
    s.k(6, "INQUAD", rightArm=(-0.8, -0.6, 0.1), leftArm=(-2.3, -0.9, -0.45), torso=(0.0, -0.4, 0.0))
    s.k(9, "OUTQUAD", rightArm=(-0.7, 0.2, 0.3), leftArm=(-1.35, 1.05, 0.2), torso=(0.08, 0.35, 0.0))
    s.k(12, rightArm=(-0.6, 0.1, 0.2), leftArm=(-0.6, -0.1, -0.2), torso=Z3)
    s.k(14, rightArm=(-0.3, 0.0, 0.15), leftArm=(-0.3, 0.0, -0.15), torso=Z3)
    s.save()

    h = A("chainsaw_headsaw", 18)
    h.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    h.k(3, "OUTQUAD", rightArm=(0.95, 0.0, 0.35), leftArm=(0.95, 0.0, -0.35), head=(-0.08, 0.0, 0.0),
        torso=(0.55, 0.0, 0.0), rightLeg=(-0.7, 0, 0), leftLeg=(0.6, 0, 0))
    for i, t in enumerate(range(5, 15, 2)):
        sgn = 1 if i % 2 == 0 else -1
        h.k(t, "INOUTSINE", rightArm=(1.0, 0.0, 0.4), leftArm=(1.0, 0.0, -0.4), head=(-0.1, 0.0, 0.0),
            torso=(0.58, 0.0, 0.0), rightLeg=(0.7 * sgn, 0, 0), leftLeg=(-0.7 * sgn, 0, 0))
    h.k(16, rightArm=(0.2, 0, 0.2), leftArm=(0.2, 0, -0.2), head=(-0.1, 0, 0), torso=(0.15, 0, 0),
        rightLeg=Z3, leftLeg=Z3)
    h.k(18, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    h.save()

    c = A("chainsaw_chain_throw", 9)
    c.k(0, rightArm=NEUTRAL_R, torso=Z3)
    c.k(1, "INQUAD", rightArm=(-2.7, 0.35, 0.3), torso=(0.0, 0.3, 0.0))
    c.k(3, "OUTBACK", rightArm=(-1.6, -0.05, 0.0), torso=(0.05, -0.2, 0.0))
    c.k(6, rightArm=(-1.5, 0.0, 0.0), torso=(0.0, -0.1, 0.0))
    c.k(9, rightArm=(-0.4, 0.0, 0.1), torso=Z3)
    c.save()

    rp = A("chainsaw_rip", 32)
    rp.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    rp.k(2, "OUTQUAD", rightArm=(-1.5, 0.35, 0.0), leftArm=(-1.5, -0.35, 0.0), torso=(0.15, 0.0, 0.0))
    for i, t in enumerate(range(4, 29, 2)):
        a1 = i % 2 == 0
        rp.k(t, "INOUTSINE", rightArm=(-1.3 if a1 else -1.72, 0.28, 0.1 if a1 else -0.08),
             leftArm=(-1.72 if a1 else -1.3, -0.28, -0.1 if a1 else 0.08),
             torso=(0.18, 0.05 if a1 else -0.05, 0.0))
    rp.k(29, "OUTBACK", rightArm=(-1.65, -0.1, 0.45), leftArm=(-1.65, 0.1, -0.45), torso=(0.25, 0.0, 0.0))
    rp.k(32, rightArm=(-0.4, 0, 0.2), leftArm=(-0.4, 0, -0.2), torso=Z3)
    rp.save()

    # full spin: PlayerAnimator "turn" = arrive at yaw 0, leave at yaw -2pi, so the spin ends back at 0
    # (only the torso yaw axis is keyframed in the turn moves so nothing else spins)
    ls = A("chainsaw_leg_spin", 17)
    TP = lambda pitch: {"pitch": pitch, "roll": 0.0}
    ls.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=TP(0.0), rightLeg=Z3, leftLeg=Z3)
    ls.k(3, "OUTQUAD", rightArm=(-0.2, 0, 0.6), leftArm=(-0.2, 0, -0.6), torso=TP(0.2),
        rightLeg=(-0.35, 0, 0.35), leftLeg=(0.15, 0, 0))
    ls.k(5, "INQUAD", rightArm=(0.0, 0, 1.25), leftArm=(0.0, 0, -1.25), torso=TP(0.1),
        rightLeg=(-0.1, 0, 1.35), leftLeg=(0.1, 0, -0.1))
    ls.k(5, "OUTQUAD", turn=-1, torso={"yaw": 0.0})
    ls.k(11, "OUTQUAD", torso={"yaw": 0.0})
    ls.k(11, rightArm=(0.0, 0, 1.25), leftArm=(0.0, 0, -1.25), torso=TP(0.1),
        rightLeg=(-0.1, 0, 1.35), leftLeg=(0.1, 0, -0.1))
    ls.k(14, rightArm=(-0.1, 0, 0.4), leftArm=(-0.1, 0, -0.4), torso=TP(0.05), rightLeg=(0, 0, 0.1), leftLeg=Z3)
    ls.k(17, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=TP(0.0), rightLeg=Z3, leftLeg=Z3)
    ls.save()

    # Chain Bind: fling the chains, then wrap both arms round the target and hold it against you (tick 66 lets go)
    cb = A("chainsaw_chain_bind", 70)
    HUG_R, HUG_L = (-1.35, 0.55, -0.1), (-1.35, -0.55, 0.1)
    cb.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    cb.k(1, "INQUAD", rightArm=(-2.6, 0.3, 0.3), leftArm=(-0.4, 0, -0.2), torso=(0.0, 0.3, 0.0))
    cb.k(3, "OUTBACK", rightArm=(-1.6, -0.1, 0.0), leftArm=(-0.9, -0.2, -0.1), torso=(0.05, -0.15, 0.0))
    cb.k(7, "OUTQUAD", rightArm=HUG_R, leftArm=HUG_L, torso=(0.12, 0.0, 0.0), head=(0.15, 0, 0))
    for i, t in enumerate(range(12, 64, 8)):
        j = 0.06 if i % 2 == 0 else -0.06
        cb.k(t, "INOUTSINE", rightArm=(HUG_R[0] + j, HUG_R[1], HUG_R[2]), leftArm=(HUG_L[0] - j, HUG_L[1], HUG_L[2]),
             torso=(0.14, j, 0.0), head=(0.18, -j, 0))
    cb.k(66, "OUTQUAD", rightArm=(-1.1, -0.3, 0.4), leftArm=(-1.1, 0.3, -0.4), torso=(-0.05, 0, 0), head=Z3)
    cb.k(70, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    cb.save()

    # Hero of Hell: clutching his chest while something pushes out through it, then thrown open (tick 29: it's out)
    hh = A("chainsaw_hero_of_hell", 30)
    CLUTCH_R, CLUTCH_L = (-1.0, 0.75, 0.0), (-1.0, -0.75, 0.0)
    hh.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3, rightLeg=Z3, leftLeg=Z3)
    hh.k(4, "OUTQUAD", rightArm=CLUTCH_R, leftArm=CLUTCH_L, torso=(0.35, 0, 0), head=(0.5, 0, 0),
         rightLeg=(-0.2, 0, 0.05), leftLeg=(0.1, 0, -0.05))
    for i, t in enumerate(range(7, 22, 3)):
        j = 0.08 if i % 2 == 0 else -0.08
        hh.k(t, "INOUTSINE", rightArm=(CLUTCH_R[0] + j, CLUTCH_R[1], j), leftArm=(CLUTCH_L[0] - j, CLUTCH_L[1], j),
             torso=(0.45 + j, j, 0), head=(0.6, j * 2, 0), rightLeg=(-0.25, 0, 0.1), leftLeg=(0.15, 0, -0.1))
    hh.k(24, "INQUAD", rightArm=(-0.6, 0.3, 0.9), leftArm=(-0.6, -0.3, -0.9), torso=(-0.2, 0, 0), head=(-0.7, 0, 0),
         rightLeg=Z3, leftLeg=Z3)
    hh.k(30, "OUTQUAD", rightArm=(-0.4, 0.2, 1.3), leftArm=(-0.4, -0.2, -1.3), torso=(-0.3, 0, 0), head=(-0.8, 0, 0),
         rightLeg=Z3, leftLeg=Z3)
    hh.save()


# ============================================================================ CROSSBOW
def crossbow():
    q = poses.quanxi_pull()
    fr = q["frames"]
    head = poses.QX_HEAD
    grab = fr["grab"]
    mid = fr["mid"]
    out = fr["out"]

    a = A("crossbow_pull_arrow", 30)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.k(4, "OUTQUAD", rightArm=arm_at(lerp3(NEUTRAL_R, tuple(grab["rot"]), 0.75)), leftArm=(-0.2, 0.0, -0.15),
        head=head, torso=Z3)
    a.k(7, "INOUTQUAD", rightArm=arm_at(grab["rot"], grab["shift"]), leftArm=(-0.25, 0.0, -0.2), head=head, torso=Z3)
    a.k(9, "INOUTSINE", rightArm=arm_at(tuple(grab["rot"] + [0.03, 0, 0]), grab["shift"]),
        leftArm=(-0.25, 0.0, -0.25), head=head, torso=(-0.03, 0, 0))
    # slow, deliberate draw of the arrow out of the socket
    a.k(13, "INOUTSINE", rightArm=arm_at(mid["rot"], mid["shift"]), leftArm=(-0.2, 0.0, -0.3), head=head,
        torso=(-0.06, 0, 0))
    a.k(17, "INOUTSINE", rightArm=arm_at(out["rot"], out["shift"]), leftArm=(-0.2, 0.0, -0.3), head=head,
        torso=(-0.08, 0, 0))
    # flick the bloody arrow aside
    a.k(19, "OUTQUAD", rightArm=(-1.1, 0.85, 1.25), leftArm=(-0.2, 0, -0.3), head=(0.0, 0.0, 0.0),
        torso=(0.0, -0.1, 0))
    # devil form bursts out
    a.k(21, "OUTBACK", rightArm=(-0.45, 0.25, 1.05), leftArm=(-0.45, -0.25, -1.05), head=(-0.3, 0, 0),
        torso=(-0.1, 0, 0))
    a.k(25, rightArm=(-0.5, 0.3, 1.1), leftArm=(-0.5, -0.3, -1.1), head=(-0.35, 0, 0), torso=(-0.1, 0, 0))
    a.k(30, rightArm=(-0.1, 0, 0.2), leftArm=(-0.1, 0, -0.2), head=Z3, torso=Z3)
    a.save()

    r = A("crossbow_revert", 12)
    r.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.k(4, rightArm=(-1.2, 0.55, 0.0), leftArm=(-1.2, -0.55, 0.0), head=(0.25, 0, 0))
    r.k(8, rightArm=(-0.2, 0, 0.1), leftArm=(-0.2, 0, -0.1), head=(0.1, 0, 0))
    r.k(12, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.save()

    AIM_R = (-1.57, -0.08, 0.0)
    AIM_L = (-1.57, 0.08, 0.0)
    v = A("crossbow_volley", 13)
    v.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L)
    v.k(2, "OUTQUAD", rightArm=AIM_R, leftArm=AIM_L)
    v.k(3, "linear", rightArm=(-1.82, -0.08, 0.05), leftArm=AIM_L)
    v.k(5, "OUTQUAD", rightArm=AIM_R, leftArm=AIM_L)
    v.k(7, "linear", rightArm=AIM_R, leftArm=(-1.82, 0.08, -0.05))
    v.k(9, "OUTQUAD", rightArm=AIM_R, leftArm=AIM_L)
    v.k(13, rightArm=(-0.5, 0, 0.1), leftArm=(-0.5, 0, -0.1))
    v.save()

    p = A("crossbow_piercing", 27)
    p.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    p.k(3, "OUTQUAD", rightArm=(-1.57, 0.0, 0.0), leftArm=(-1.35, 0.6, 0.0), torso=(0.0, 0.35, 0.0))
    for i, t in enumerate(range(5, 18, 2)):
        amp = 0.01 + 0.004 * i
        sgn = 1 if i % 2 == 0 else -1
        p.k(t, "linear", rightArm=(-1.57 + amp * sgn, amp * sgn, 0.0), leftArm=(-1.35 + amp * sgn, 0.6, 0.0),
            torso=(0.0, 0.35, 0.0))
    p.k(18, "OUTQUAD", rightArm=(-2.25, 0.1, 0.2), leftArm=(-1.1, 0.5, -0.2), torso=(-0.25, 0.35, 0.0))
    p.k(22, rightArm=(-1.4, 0, 0.1), leftArm=(-0.8, 0.3, 0.0), torso=(-0.05, 0.2, 0.0))
    p.k(27, rightArm=(-0.2, 0, 0.1), leftArm=(-0.2, 0, -0.1), torso=Z3)
    p.save()

    f = A("crossbow_flash_step", 9)
    f.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    f.k(2, "INQUAD", rightArm=(0.95, 0, 0.25), leftArm=(0.95, 0, -0.25), torso=(0.45, 0, 0),
        rightLeg=(-0.85, 0, 0), leftLeg=(0.7, 0, 0))
    f.k(3, "OUTBACK", rightArm=(-0.25, 0.95, 1.3), leftArm=(-0.25, -0.95, -1.3), torso=(0.22, 0.0, 0),
        rightLeg=(0.3, 0, 0.1), leftLeg=(-0.4, 0, -0.1))
    f.k(6, rightArm=(-0.3, 0.8, 1.1), leftArm=(-0.3, -0.8, -1.1), torso=(0.1, 0, 0), rightLeg=Z3, leftLeg=Z3)
    f.k(9, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    f.save()

    st = A("crossbow_storm", 34)
    UP_R = (-2.95, 0.0, 0.18)
    UP_L = (-2.95, 0.0, -0.18)
    st.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    st.k(3, "OUTQUAD", rightArm=UP_R, leftArm=UP_L, head=(-0.6, 0, 0))
    for i, t in enumerate(range(4, 11, 2)):
        right = i % 2 == 0
        st.k(t, "linear", rightArm=(-2.75, 0, 0.25) if right else UP_R, leftArm=UP_L if right else (-2.75, 0, -0.25),
             head=(-0.6, 0, 0))
    st.k(13, "OUTQUAD", rightArm=(-1.55, 0.05, 0.15), leftArm=(0.15, 0, -0.35), head=(0.1, 0, 0))
    st.k(30, rightArm=(-1.6, 0.05, 0.18), leftArm=(0.18, 0, -0.35), head=(0.12, 0, 0))
    st.k(34, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    st.save()


# ============================================================================ FLAMETHROWER
def flamethrower():
    a = A("flame_bite_molar", 20)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.k(4, "OUTQUAD", rightArm=(-0.45, 0.1, 0.35), leftArm=(-0.45, -0.1, -0.35), head=(0.45, 0, 0),
        torso=(0.32, 0, 0))
    a.k(6, "INQUAD", rightArm=(-0.5, 0.15, 0.4), leftArm=(-0.5, -0.15, -0.4), head=(0.55, 0, 0.05),
        torso=(0.36, 0, 0))
    # clench... click
    a.k(7, "linear", rightArm=(-0.55, 0.2, 0.42), leftArm=(-0.55, -0.2, -0.42), head=(0.62, 0, -0.05),
        torso=(0.38, 0, 0))
    a.k(9, "OUTBACK", rightArm=(-0.55, 0.4, 1.25), leftArm=(-0.55, -0.4, -1.25), head=(-0.55, 0, 0),
        torso=(-0.25, 0, 0))
    a.k(14, rightArm=(-0.5, 0.45, 1.2), leftArm=(-0.5, -0.45, -1.2), head=(-0.5, 0, 0.05), torso=(-0.22, 0, 0))
    a.k(20, rightArm=(-0.1, 0, 0.25), leftArm=(-0.1, 0, -0.25), head=Z3, torso=Z3)
    a.save()

    r = A("flame_revert", 12)
    r.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.k(4, rightArm=(0.2, 0, 0.3), leftArm=(0.2, 0, -0.3), head=(0.4, 0, 0))
    r.k(12, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.save()

    s = A("flame_stream", 60)
    FR = (-1.55, -0.14, 0.0)
    FL = (-1.55, 0.14, 0.0)
    s.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    s.k(4, "OUTQUAD", rightArm=FR, leftArm=FL, torso=(0.08, 0, 0))
    for i, t in enumerate(range(6, 57, 2)):
        j = 0.035 if i % 2 == 0 else -0.035
        s.k(t, "linear", rightArm=(FR[0] + j, FR[1], j * 0.5), leftArm=(FL[0] - j, FL[1], -j * 0.5),
            torso=(0.08, 0, 0))
    s.k(60, rightArm=(-0.4, 0, 0.1), leftArm=(-0.4, 0, -0.1), torso=Z3)
    s.save()

    n = A("flame_napalm", 12)
    n.k(0, rightArm=NEUTRAL_R, torso=Z3)
    n.k(3, "INQUAD", rightArm=(-1.2, 0.0, 0.25), torso=(0, 0.2, 0))
    n.k(5, "OUTQUAD", rightArm=(-1.62, -0.05, 0.0), torso=(0, -0.1, 0))
    n.k(6, "linear", rightArm=(-1.95, -0.05, 0.05), torso=(-0.06, -0.1, 0))
    n.k(12, rightArm=(-0.3, 0, 0.1), torso=Z3)
    n.save()

    b = A("flame_burst", 20)
    b.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    b.k(5, "OUTQUAD", rightArm=(-2.95, 0, 0.3), leftArm=(-2.95, 0, -0.3), torso=(-0.22, 0, 0),
        rightLeg=Z3, leftLeg=Z3)
    b.k(9, "INQUAD", rightArm=(-0.75, 0, 0.3), leftArm=(-0.75, 0, -0.3), torso=(0.5, 0, 0),
        rightLeg=(-0.45, 0, 0.15), leftLeg=(-0.45, 0, -0.15))
    b.k(12, rightArm=(-0.7, 0, 0.35), leftArm=(-0.7, 0, -0.35), torso=(0.48, 0, 0),
        rightLeg=(-0.45, 0, 0.15), leftLeg=(-0.45, 0, -0.15))
    b.k(17, rightArm=(-0.2, 0, 0.2), leftArm=(-0.2, 0, -0.2), torso=(0.1, 0, 0), rightLeg=Z3, leftLeg=Z3)
    b.k(20, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    b.save()

    c = A("flame_conflagration", 40)
    TR = (0.0, 0.0, 1.45)
    TL = (0.0, 0.0, -1.45)
    c.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L)
    c.k(6, "OUTQUAD", rightArm=TR, leftArm=TL)
    c.k(36, "linear", rightArm=TR, leftArm=TL)
    # two full turns with the flamethrowers roaring outward
    c.k(8, "linear", turn=-1, torso={"yaw": 0.0})
    c.k(22, "linear", turn=-1, torso={"yaw": 0.0})
    c.k(36, "OUTQUAD", torso={"yaw": 0.0})
    c.k(40, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L)
    c.save()

    g = A("flame_regen", 14)
    g.k(0, rightArm=NEUTRAL_R, head=Z3)
    g.k(3, "OUTQUAD", rightArm=(-2.3, -0.7, 0.4), head=(0.1, 0.0, 0.25))
    g.k(5, "linear", rightArm=(-2.35, -0.75, 0.42), head=(0.25, 0.0, 0.3))
    g.k(7, "OUTBACK", rightArm=(-0.5, 0.2, 0.8), head=(-0.3, 0, 0))
    g.k(14, rightArm=NEUTRAL_R, head=Z3)
    g.save()


# ============================================================================ WHIP
def whip():
    # trigger: raise the right hand beside the face and SNAP - whips tear out of both hands
    a = A("whip_snap_fingers", 16)
    SNAP_UP = (-2.25, -0.35, 0.1)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.k(4, "OUTQUAD", rightArm=SNAP_UP, leftArm=(-0.1, 0, -0.15), head=(0.05, -0.25, 0), torso=(0, -0.12, 0))
    a.k(6, "INOUTSINE", rightArm=(SNAP_UP[0] - 0.08, SNAP_UP[1], SNAP_UP[2] - 0.05), leftArm=(-0.1, 0, -0.15),
        head=(0.08, -0.3, 0), torso=(0, -0.14, 0))
    # snap!
    a.k(7, "linear", rightArm=(SNAP_UP[0] + 0.3, SNAP_UP[1] + 0.1, SNAP_UP[2] + 0.2), leftArm=(-0.1, 0, -0.15),
        head=(0.02, -0.3, 0), torso=(0, -0.14, 0))
    # the whips burst out: both arms thrown down and out, head back
    a.k(9, "OUTBACK", rightArm=(0.25, 0.1, 0.65), leftArm=(0.25, -0.1, -0.65), head=(-0.45, 0, 0),
        torso=(-0.12, 0, 0))
    a.k(12, rightArm=(0.2, 0.1, 0.55), leftArm=(0.2, -0.1, -0.55), head=(-0.35, 0, 0.05), torso=(-0.08, 0, 0))
    a.k(16, rightArm=(0.0, 0, 0.3), leftArm=(0.0, 0, -0.3), head=Z3, torso=Z3)
    a.save()

    r = A("whip_revert", 12)
    r.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.k(4, rightArm=(-0.5, 0.4, 0.1), leftArm=(-0.5, -0.4, -0.1), head=(0.3, 0, 0))
    r.k(8, rightArm=(-0.3, 0.2, 0.1), leftArm=(-0.3, -0.2, -0.1), head=(0.15, 0, 0))
    r.k(12, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.save()

    # three lashes: right, left, right; the arm stops forward on ticks 4 / 8 / 12
    UP_R, DN_R = (-2.95, 0.25, 0.25), (-1.05, -0.3, 0.05)
    UP_L, DN_L = (-2.95, -0.25, -0.25), (-1.05, 0.3, -0.05)
    l = A("whip_lash", 16)
    l.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    l.k(2, "INQUAD", rightArm=UP_R, leftArm=(-0.3, 0, -0.2), torso=(-0.08, 0.25, 0))
    l.k(4, "OUTQUAD", rightArm=DN_R, leftArm=(-0.4, 0, -0.2), torso=(0.12, -0.25, 0))
    l.k(6, "INQUAD", rightArm=(-0.6, -0.2, 0.1), leftArm=UP_L, torso=(-0.08, -0.25, 0))
    l.k(8, "OUTQUAD", rightArm=(-0.5, 0, 0.1), leftArm=DN_L, torso=(0.12, 0.25, 0))
    l.k(10, "INQUAD", rightArm=UP_R, leftArm=(-0.6, 0.2, -0.1), torso=(-0.08, 0.25, 0))
    l.k(12, "OUTQUAD", rightArm=DN_R, leftArm=(-0.4, 0, -0.2), torso=(0.14, -0.3, 0))
    l.k(16, rightArm=(-0.3, 0, 0.15), leftArm=(-0.2, 0, -0.15), torso=Z3)
    l.save()

    # storm: arms flung out, two full spins with the whips flailing
    st = A("whip_storm", 26)
    TR, TL = (-0.15, 0.0, 1.45), (-0.15, 0.0, -1.45)
    st.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L)
    st.k(3, "OUTQUAD", rightArm=TR, leftArm=TL)
    for i, t in enumerate(range(5, 22, 2)):
        j = 0.12 if i % 2 == 0 else -0.12
        st.k(t, "linear", rightArm=(TR[0] + j, 0, TR[2] - abs(j)), leftArm=(TL[0] - j, 0, TL[2] + abs(j)))
    st.k(4, "linear", turn=-1, torso={"yaw": 0.0})
    st.k(13, "linear", turn=-1, torso={"yaw": 0.0})
    st.k(22, "OUTQUAD", torso={"yaw": 0.0})
    st.k(26, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L)
    st.save()

    # snare: cast the right whips at the target, then yank it in
    sn = A("whip_snare", 14)
    sn.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    sn.k(2, "INQUAD", rightArm=(-2.3, 0.2, 0.2), leftArm=(-0.3, 0, -0.2), torso=(-0.05, 0.2, 0))
    sn.k(4, "OUTQUAD", rightArm=(-1.6, -0.05, 0.0), leftArm=(-0.5, 0.3, -0.2), torso=(0.1, -0.15, 0))
    sn.k(7, rightArm=arm_at((-1.55, -0.05, 0.0)), leftArm=(-0.5, 0.3, -0.2), torso=(0.1, -0.15, 0))
    sn.k(9, "OUTBACK", rightArm=arm_at((-0.55, 0.35, 0.35), (0, 0, 1.2)), leftArm=(-0.2, 0, -0.3),
         torso=(-0.12, 0.35, 0))
    sn.k(14, rightArm=arm_at(NEUTRAL_R), leftArm=NEUTRAL_L, torso=Z3)
    sn.save()

    # swing: whip lashed up at a ledge, hold on while flying
    sw = A("whip_swing", 14)
    sw.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, rightLeg=Z3, leftLeg=Z3)
    sw.k(2, "OUTQUAD", rightArm=(-2.75, -0.1, 0.1), leftArm=(-0.4, 0, -0.5), rightLeg=(-0.3, 0, 0),
         leftLeg=(0.2, 0, 0))
    sw.k(9, rightArm=(-2.85, -0.1, 0.15), leftArm=(-0.2, 0, -0.7), rightLeg=(-0.9, 0, 0.1), leftLeg=(-0.5, 0, -0.1))
    sw.k(14, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, rightLeg=Z3, leftLeg=Z3)
    sw.save()

    # sonic crack: both whips overhead, then one supersonic crack at tick 10
    c = A("whip_crack", 20)
    c.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    c.k(6, "INOUTQUAD", rightArm=(-2.95, 0.3, 0.2), leftArm=(-2.95, -0.3, -0.2), torso=(-0.22, 0, 0),
        head=(-0.3, 0, 0))
    c.k(8, "INQUAD", rightArm=(-3.1, 0.3, 0.25), leftArm=(-3.1, -0.3, -0.25), torso=(-0.26, 0, 0), head=(-0.3, 0, 0))
    c.k(10, "OUTQUAD", rightArm=(-1.1, -0.15, 0.1), leftArm=(-1.1, 0.15, -0.1), torso=(0.35, 0, 0), head=(0.05, 0, 0))
    c.k(14, rightArm=(-1.0, -0.1, 0.1), leftArm=(-1.0, 0.1, -0.1), torso=(0.3, 0, 0), head=Z3)
    c.k(20, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    c.save()


# ============================================================================ BOMB
def bomb():
    rz = poses.reze_pull()
    grab = tuple(rz["grab"]["rot"])
    yank = tuple(rz["yank"]["rot"])
    chin = poses.REZE_HEAD

    # trigger: finger through the pin under the choker, pull (tick 9), BOOM (tick 12)
    a = A("bomb_pull_pin", 22)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.k(5, "OUTQUAD", rightArm=lerp3(NEUTRAL_R, grab, 0.75), leftArm=(-0.1, 0, -0.1), head=chin, torso=Z3)
    a.k(8, "INOUTQUAD", rightArm=grab, leftArm=(-0.1, 0, -0.12), head=chin, torso=(-0.04, 0, 0))
    a.k(9, "OUTQUAD", rightArm=lerp3(grab, yank, 0.7), leftArm=(-0.1, 0, -0.12), head=(-0.2, 0.1, 0),
        torso=(0.02, -0.1, 0))
    a.k(11, "INOUTSINE", rightArm=yank, leftArm=(-0.12, 0, -0.15), head=(-0.1, 0.15, 0.05), torso=(0, -0.12, 0))
    # she goes off where she stands
    a.k(13, "OUTBACK", rightArm=(-0.6, 0.3, 1.3), leftArm=(-0.6, -0.3, -1.3), head=(-0.55, 0, 0),
        torso=(-0.2, 0, 0), rightLeg=(0.0, 0, 0.25), leftLeg=(0.0, 0, -0.25))
    a.k(17, rightArm=(-0.5, 0.3, 1.1), leftArm=(-0.5, -0.3, -1.1), head=(-0.45, 0, 0), torso=(-0.15, 0, 0),
        rightLeg=(0.0, 0, 0.2), leftLeg=(0.0, 0, -0.2))
    a.k(22, rightArm=(-0.1, 0, 0.2), leftArm=(-0.1, 0, -0.2), head=Z3, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    a.save()

    r = A("bomb_revert", 12)
    r.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.k(4, rightArm=(-1.3, 0.7, 0.0), leftArm=(-1.3, -0.7, 0.0), head=(0.3, 0, 0))
    r.k(8, rightArm=(-0.4, 0.2, 0.1), leftArm=(-0.4, -0.2, -0.1), head=(0.15, 0, 0))
    r.k(12, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.save()

    # explosive combo: right hook (4), left straight (9), spinning roundhouse kick (13)
    c = A("bomb_combo", 16)
    c.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    c.k(2, "INQUAD", rightArm=arm_at((-1.2, 0.8, 0.5)), leftArm=arm_at((-1.1, -0.3, -0.2), base=(5, 2, 0)), torso=(0.05, 0.4, 0))
    c.k(4, "OUTQUAD", rightArm=arm_at((-1.6, -0.25, 0.0), (0, 0, -1.5)), leftArm=arm_at((-1.0, -0.2, -0.2), base=(5, 2, 0)),
        torso=(0.12, -0.35, 0))
    c.k(7, "INQUAD", rightArm=arm_at((-1.0, 0.2, 0.2)), leftArm=arm_at((-1.1, -0.6, -0.4), base=(5, 2, 0)), torso=(0.05, -0.35, 0))
    c.k(9, "OUTQUAD", rightArm=arm_at((-0.9, 0.2, 0.2)), leftArm=arm_at((-1.62, 0.2, 0.0), (0, 0, -1.5), base=(5, 2, 0)),
        torso=(0.12, 0.35, 0))
    c.k(11, "INQUAD", rightArm=arm_at((-0.6, 0, 0.6)), leftArm=arm_at((-0.6, 0, -0.6), base=(5, 2, 0)), torso=(-0.1, 0.2, 0), rightLeg=(0.4, 0, 0),
        leftLeg=Z3)
    c.k(13, "OUTQUAD", rightArm=(-0.3, 0, 0.9), leftArm=(-0.4, 0, -0.9), torso=(-0.22, -0.3, 0),
        rightLeg=(-1.55, 0.3, 0.2), leftLeg=(0.1, 0, 0))
    c.k(16, rightArm=arm_at(NEUTRAL_R), leftArm=arm_at(NEUTRAL_L, base=(5, 2, 0)), torso=Z3, rightLeg=Z3, leftLeg=Z3)
    c.save()

    # flick: fingers flick a spark forward
    f = A("bomb_flick", 10)
    f.k(0, rightArm=NEUTRAL_R)
    f.k(3, "INQUAD", rightArm=(-1.35, 0.1, -0.2))
    f.k(4, "OUTBACK", rightArm=(-1.6, -0.05, 0.15))
    f.k(10, rightArm=NEUTRAL_R)
    f.save()

    # propulsion: arms and legs flung back, blasts out of the palms - rocketing forward
    pr = A("bomb_propulsion", 30)
    pr.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3, head=Z3)
    pr.k(3, "OUTQUAD", rightArm=(0.7, 0.2, 0.35), leftArm=(0.7, -0.2, -0.35), torso=(0.75, 0, 0),
         rightLeg=(0.35, 0, 0.1), leftLeg=(0.55, 0, -0.1), head=(-0.6, 0, 0))
    for i, t in enumerate(range(5, 25, 4)):
        j = 0.08 if i % 2 == 0 else -0.08
        pr.k(t, "INOUTSINE", rightArm=(0.75 + j, 0.2, 0.35), leftArm=(0.75 - j, -0.2, -0.35), torso=(0.8, 0, j * 0.5),
             rightLeg=(0.3 + j, 0, 0.1), leftLeg=(0.5 - j, 0, -0.1), head=(-0.65, 0, 0))
    pr.k(30, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3, head=Z3)
    pr.save()

    # torpedo: the right forearm becomes a torpedo and she rides it forward
    tp = A("bomb_torpedo", 20)
    tp.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    tp.k(4, "OUTQUAD", rightArm=(-1.3, 0.3, 0.2), leftArm=(-0.4, 0, -0.3), torso=(0.1, 0.35, 0))
    tp.k(6, "OUTQUAD", rightArm=(-1.57, 0.0, 0.0), leftArm=(0.6, 0, -0.3), torso=(0.55, 0, 0), rightLeg=(0.5, 0, 0),
         leftLeg=(0.35, 0, 0))
    tp.k(13, rightArm=(-1.6, 0.0, 0.0), leftArm=(0.65, 0, -0.3), torso=(0.6, 0, 0), rightLeg=(0.55, 0, 0),
         leftLeg=(0.4, 0, 0))
    tp.k(15, "OUTQUAD", rightArm=(-1.9, 0.2, 0.4), leftArm=(-0.5, 0, -0.6), torso=(-0.2, 0, 0), rightLeg=(-0.3, 0, 0),
         leftLeg=(0.2, 0, 0))
    tp.k(20, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    tp.save()

    # head throw: both hands take hold of her bomb head (3-5), pin (4), tear it off (7) and hurl it (9)
    h = A("bomb_head_throw", 26)
    GR, GL = (-2.55, 0.55, -0.25), (-2.55, -0.55, 0.25)
    h.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    h.k(3, "OUTQUAD", rightArm=GR, leftArm=GL, torso=Z3, head=Z3)
    h.k(5, rightArm=(GR[0] - 0.1, GR[1], GR[2]), leftArm=(GL[0] - 0.1, GL[1], GL[2]), torso=(-0.05, 0, 0),
        head=(-0.1, 0, 0))
    h.k(7, "OUTQUAD", rightArm=(-2.9, 0.1, 0.35), leftArm=(-1.2, -0.3, -0.3), torso=(-0.15, 0.35, 0),
        head=(-0.1, 0, 0))
    h.k(9, "OUTBACK", rightArm=(-1.2, -0.35, 0.0), leftArm=(-0.2, 0.2, -0.4), torso=(0.25, -0.4, 0), head=Z3)
    h.k(14, rightArm=(-0.8, -0.2, 0.1), leftArm=(-0.2, 0, -0.3), torso=(0.12, -0.2, 0), head=Z3)
    h.k(26, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    h.save()


# ============================================================================ SPEAR
def spear():
    sp = poses.spear_pull()
    fr = sp["frames"]
    bow = poses.SPEAR_HEAD
    grab, mid, out = fr["grab"], fr["mid"], fr["out"]

    # trigger: over the shoulder, draw the spear out of the nape (7-14), twirl it, burst (18)
    a = A("spear_pull_spear", 26)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.k(4, "OUTQUAD", rightArm=arm_at(lerp3(NEUTRAL_R, tuple(grab["rot"]), 0.8)), leftArm=(-0.15, 0, -0.2),
        head=lerp3(Z3, bow, 0.7), torso=(0.05, 0, 0))
    a.k(6, "INOUTQUAD", rightArm=arm_at(grab["rot"], grab["shift"]), leftArm=(-0.2, 0, -0.25), head=bow,
        torso=(0.1, 0, 0))
    a.k(10, "INOUTSINE", rightArm=arm_at(mid["rot"], mid["shift"]), leftArm=(-0.2, 0, -0.3), head=bow,
        torso=(0.08, 0, 0))
    a.k(14, "INOUTSINE", rightArm=arm_at(out["rot"], out["shift"]), leftArm=(-0.2, 0, -0.3), head=(0.2, 0, 0),
        torso=(0.02, 0, 0))
    a.k(16, "OUTQUAD", rightArm=arm_at((-2.7, 0.1, 0.1)), leftArm=(-0.3, 0, -0.35), head=(-0.2, 0, 0), torso=(-0.08, 0, 0))
    # the devil bursts out: spear levelled at the enemy
    a.k(18, "OUTBACK", rightArm=(-1.5, -0.1, 0.0), leftArm=(-0.4, 0.4, -0.5), head=(-0.25, 0, 0),
        torso=(0.15, -0.2, 0))
    a.k(22, rightArm=(-1.45, -0.1, 0.0), leftArm=(-0.4, 0.4, -0.5), head=(-0.2, 0, 0), torso=(0.12, -0.2, 0))
    a.k(26, rightArm=(-0.3, 0, 0.1), leftArm=(-0.1, 0, -0.2), head=Z3, torso=Z3)
    a.save()

    r = A("spear_revert", 12)
    r.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.k(4, rightArm=(-0.4, 0, 0.4), leftArm=(-0.4, 0, -0.4), head=(0.35, 0, 0))
    r.k(8, rightArm=(-0.2, 0, 0.2), leftArm=(-0.2, 0, -0.2), head=(0.2, 0, 0))
    r.k(12, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.save()

    # three thrusts (3 / 7 / 11)
    t = A("spear_thrust", 14)
    BACK = arm_at((-1.35, 0.1, 0.1), (0, 0, 2.2))
    LUNGE = arm_at((-1.57, 0.0, 0.0), (0, 0, -2.2))
    t.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    for t0 in (3, 7, 11):
        t.k(t0 - 2, "INQUAD", rightArm=BACK, leftArm=(-0.5, 0.3, -0.3), torso=(0.0, 0.3, 0))
        t.k(t0, "OUTQUAD", rightArm=LUNGE, leftArm=(-0.3, 0.1, -0.4), torso=(0.14, -0.25, 0))
    t.k(14, rightArm=arm_at((-0.4, 0, 0.1)), leftArm=NEUTRAL_L, torso=Z3)
    t.save()

    # javelin throw (release on tick 6)
    w = A("spear_throw", 14)
    w.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, leftLeg=Z3, rightLeg=Z3)
    w.k(4, "INOUTQUAD", rightArm=arm_at((-2.75, 0.15, 0.3), (0, 0, 1.5)), leftArm=(-1.55, 0.25, 0.0),
        torso=(-0.12, 0.55, 0), leftLeg=(-0.35, 0, 0), rightLeg=(0.25, 0, 0))
    w.k(6, "OUTQUAD", rightArm=arm_at((-1.3, -0.3, 0.0)), leftArm=(-0.3, 0.2, -0.3), torso=(0.25, -0.45, 0),
        leftLeg=(-0.2, 0, 0), rightLeg=(0.1, 0, 0))
    w.k(9, rightArm=(-1.0, -0.4, 0.05), leftArm=(-0.1, 0.1, -0.3), torso=(0.15, -0.35, 0))
    w.k(14, rightArm=arm_at(NEUTRAL_R), leftArm=NEUTRAL_L, torso=Z3, leftLeg=Z3, rightLeg=Z3)
    w.save()

    # volley: arms raised - spears sprout in the air behind him - then point: fire (14)
    v = A("spear_volley", 24)
    v.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    v.k(4, "OUTQUAD", rightArm=(-2.4, 0.3, 0.6), leftArm=(-2.4, -0.3, -0.6), head=(-0.35, 0, 0), torso=(-0.1, 0, 0))
    v.k(12, rightArm=(-2.5, 0.3, 0.7), leftArm=(-2.5, -0.3, -0.7), head=(-0.35, 0, 0), torso=(-0.12, 0, 0))
    v.k(14, "OUTBACK", rightArm=(-1.57, -0.05, 0.0), leftArm=(-0.2, 0, -0.5), head=Z3, torso=(0.08, 0, 0))
    v.k(19, rightArm=(-1.5, -0.05, 0.0), leftArm=(-0.2, 0, -0.4), head=Z3, torso=(0.05, 0, 0))
    v.k(24, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    v.save()

    # impale: vanish, reappear behind the target (2) and drive the spear through its back (5)
    im = A("spear_impale", 16)
    im.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    im.k(2, "OUTQUAD", rightArm=arm_at((-1.3, 0.2, 0.2), (0, 0, 2.5)), leftArm=(-0.9, 0.3, -0.2), torso=(0.3, 0.3, 0),
         rightLeg=(0.4, 0, 0), leftLeg=(-0.5, 0, 0))
    im.k(5, "OUTQUAD", rightArm=arm_at((-1.45, -0.05, 0.0), (0, 0, -2.8)), leftArm=(-1.3, -0.3, 0.0),
         torso=(0.35, -0.2, 0), rightLeg=(0.5, 0, 0), leftLeg=(-0.6, 0, 0))
    im.k(10, rightArm=arm_at((-1.4, -0.05, 0.0), (0, 0, -2.5)), leftArm=(-1.25, -0.3, 0.0), torso=(0.3, -0.2, 0),
         rightLeg=(0.45, 0, 0), leftLeg=(-0.55, 0, 0))
    im.k(12, "OUTQUAD", rightArm=arm_at((-1.1, 0.2, 0.2), (0, 0, 1.0)), leftArm=(-0.5, 0, -0.2), torso=(0.05, 0.2, 0),
         rightLeg=Z3, leftLeg=Z3)
    im.k(16, rightArm=arm_at(NEUTRAL_R), leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    im.save()

    # eruption: both hands raise the spear-arm and drive it into the ground (5); spears burst out ahead
    e = A("spear_eruption", 22)
    e.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3, rightLeg=Z3, leftLeg=Z3)
    e.k(3, "INOUTQUAD", rightArm=(-2.95, 0.1, 0.15), leftArm=(-2.9, -0.35, -0.1), torso=(-0.2, 0, 0),
        head=(-0.3, 0, 0))
    e.k(5, "OUTQUAD", rightArm=(-0.75, -0.1, 0.1), leftArm=(-0.8, -0.35, -0.1), torso=(0.55, 0, 0),
        head=(0.25, 0, 0), rightLeg=(-0.5, 0, 0.1), leftLeg=(-0.5, 0, -0.1))
    e.k(16, rightArm=(-0.7, -0.1, 0.1), leftArm=(-0.75, -0.35, -0.1), torso=(0.5, 0, 0), head=(-0.2, 0, 0),
        rightLeg=(-0.45, 0, 0.1), leftLeg=(-0.45, 0, -0.1))
    e.k(22, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3, rightLeg=Z3, leftLeg=Z3)
    e.save()


# ============================================================================ KATANA / LONGSWORD
def blade_pull(prefix, trigger_id, hand_side):
    """Pull off one hand with the other; the blade rises out of the stump (hand_side = the hand that comes off)."""
    R = hand_side == "right"          # Longsword pulls off the right hand, Katana the left
    grab_off = (-1.05, 0.55 if R else -0.55, 0.0)      # the arm that loses its hand, held out in front
    puller = (-1.05, -0.75 if R else 0.75, 0.25 if not R else -0.25)
    yank = (-0.5, -0.35 if R else 0.35, -1.0 if R else 1.0)
    stump_up = (-1.6, 0.1 if R else -0.1, 0.0)

    def arms(off, pull):
        return {"rightArm": off, "leftArm": pull} if R else {"rightArm": pull, "leftArm": off}

    a = A("%s_%s" % (prefix, trigger_id), 24)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.k(3, "OUTQUAD", head=(0.3, 0, 0), torso=(0.05, 0, 0), **arms(grab_off, puller))
    a.k(5, "INQUAD", head=(0.35, 0, 0), torso=(0.08, 0.1 if R else -0.1, 0),
        **arms((grab_off[0] - 0.05, grab_off[1], grab_off[2]), (puller[0] + 0.05, puller[1], puller[2])))
    # yank: the hand comes off
    a.k(6, "OUTBACK", head=(0.1, -0.2 if R else 0.2, 0), torso=(0.0, -0.25 if R else 0.25, 0), **arms(grab_off, yank))
    a.k(9, "INOUTSINE", head=(0.25, 0, 0), torso=(0.0, -0.1 if R else 0.1, 0), **arms(stump_up, yank))
    a.k(11, head=(0.2, 0, 0), torso=Z3, **arms((stump_up[0] - 0.1, stump_up[1], stump_up[2]), yank))
    # the devil bursts out
    a.k(13, "OUTBACK", rightArm=(-0.4, 0.3, 1.1), leftArm=(-0.4, -0.3, -1.1), head=(-0.45, 0, 0), torso=(-0.15, 0, 0))
    a.k(18, rightArm=(-0.7, 0.2, 0.3), leftArm=(-0.7, -0.2, -0.3), head=(-0.1, 0, 0), torso=(0.05, 0, 0))
    a.k(24, rightArm=(-0.4, 0.1, 0.2), leftArm=(-0.4, -0.1, -0.2), head=Z3, torso=Z3)
    a.save()

    # sliding the blade back in leaves them spent
    r = A("%s_revert" % prefix, 16)
    r.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    r.k(5, "INOUTQUAD", head=(0.3, 0, 0), torso=(0.1, 0, 0), **arms(grab_off, puller))
    r.k(8, "INQUAD", head=(0.35, 0, 0), torso=(0.12, 0, 0), **arms(grab_off, (puller[0] + 0.3, puller[1] * 0.6, puller[2])))
    r.k(12, "OUTQUAD", rightArm=(0.15, 0, 0.1), leftArm=(0.15, 0, -0.1), head=(0.5, 0, 0.1), torso=(0.2, 0, 0))
    r.k(16, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=(0.2, 0, 0), torso=(0.05, 0, 0))
    r.save()


def katana():
    blade_pull("katana", "pull_left_hand", "left")
    # Sword-Draw Dash: crouch as if to draw, bolt past, the cut opens a beat later
    i = A("katana_iai", 28)
    i.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3, rightLeg=Z3, leftLeg=Z3)
    i.k(3, "OUTQUAD", rightArm=(-0.45, 0.95, 0.35), leftArm=(-0.9, 0.35, -0.1), torso=(0.45, 0.25, 0), head=(-0.35, -0.2, 0),
        rightLeg=(-0.6, 0, 0.1), leftLeg=(0.45, 0, -0.05))
    i.k(8, "linear", rightArm=(-0.5, 1.0, 0.38), leftArm=(-0.95, 0.38, -0.12), torso=(0.5, 0.28, 0), head=(-0.4, -0.22, 0),
        rightLeg=(-0.65, 0, 0.1), leftLeg=(0.5, 0, -0.05))
    i.k(9, "OUTEXPO", rightArm=(-1.45, -1.1, 0.25), leftArm=(0.35, -0.2, -0.3), torso=(0.25, -0.45, 0), head=(-0.2, 0.3, 0),
        rightLeg=(0.45, 0, 0), leftLeg=(-0.5, 0, 0))
    i.k(18, rightArm=(-1.4, -1.05, 0.25), leftArm=(0.35, -0.2, -0.3), torso=(0.22, -0.45, 0), head=(-0.2, 0.3, 0),
        rightLeg=(0.4, 0, 0), leftLeg=(-0.45, 0, 0))
    i.k(21, "OUTQUAD", rightArm=(-0.7, -0.4, 0.15), leftArm=(0.1, 0, -0.2), torso=(0.05, -0.2, 0), head=(0.1, 0.4, 0),
        rightLeg=Z3, leftLeg=Z3)
    i.k(28, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3, rightLeg=Z3, leftLeg=Z3)
    i.save()

    t = A("katana_twin", 14)
    t.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    t.k(3, "INQUAD", rightArm=(-2.5, -0.45, 0.2), leftArm=(-2.5, 0.45, -0.2), torso=(-0.1, 0, 0))
    t.k(5, "OUTQUAD", rightArm=(-0.7, 0.7, 0.0), leftArm=(-0.7, -0.7, 0.0), torso=(0.25, 0, 0))
    t.k(10, rightArm=(-0.6, 0.6, 0.0), leftArm=(-0.6, -0.6, 0.0), torso=(0.2, 0, 0))
    t.k(14, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    t.save()

    f = A("katana_flurry", 22)
    f.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    for k, tk in enumerate(range(2, 20, 3)):
        right = k % 2 == 0
        hi = k % 3 == 0
        f.k(tk, "OUTQUAD", rightArm=(-1.9 if hi else -1.3, -0.7 if right else 0.3, 0.2) if right else (-0.6, 0.2, 0.2),
            leftArm=(-0.6, -0.2, -0.2) if right else (-1.9 if hi else -1.3, 0.7, -0.2),
            torso=(0.1, -0.3 if right else 0.3, 0))
    f.k(22, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    f.save()

    c = A("katana_counter", 30)
    c.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    c.k(4, "OUTQUAD", rightArm=(-0.4, 0.9, 0.3), leftArm=(-0.6, 0.4, -0.1), torso=(0.3, 0.3, 0), rightLeg=(-0.5, 0, 0.1),
        leftLeg=(0.35, 0, 0))
    c.k(26, rightArm=(-0.42, 0.92, 0.32), leftArm=(-0.62, 0.42, -0.1), torso=(0.32, 0.3, 0), rightLeg=(-0.5, 0, 0.1),
        leftLeg=(0.35, 0, 0))
    c.k(30, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    c.save()


def longsword():
    blade_pull("longsword", "pull_right_hand", "right")
    c = A("longsword_cleave", 16)
    c.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    c.k(5, "INOUTQUAD", rightArm=(-2.9, 0.15, 0.1), leftArm=(-2.9, -0.15, -0.1), torso=(-0.2, 0, 0))
    c.k(8, "OUTQUAD", rightArm=(-0.9, 0.1, 0.05), leftArm=(-0.9, -0.1, -0.05), torso=(0.4, 0, 0))
    c.k(12, rightArm=(-0.85, 0.1, 0.05), leftArm=(-0.85, -0.1, -0.05), torso=(0.35, 0, 0))
    c.k(16, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    c.save()

    w = A("longsword_whirl", 24)
    TR, TL = (-0.2, 0.0, 1.4), (-0.2, 0.0, -1.4)
    w.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L)
    w.k(3, "OUTQUAD", rightArm=TR, leftArm=TL)
    w.k(20, "linear", rightArm=TR, leftArm=TL)
    w.k(4, "linear", turn=-1, torso={"yaw": 0.0})
    w.k(12, "linear", turn=-1, torso={"yaw": 0.0})
    w.k(20, "OUTQUAD", torso={"yaw": 0.0})
    w.k(24, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L)
    w.save()

    l = A("longsword_lunge", 14)
    l.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    l.k(2, "INQUAD", rightArm=arm_at((-1.3, 0.1, 0.1), (0, 0, 2.0)), leftArm=(-0.4, 0.2, -0.3), torso=(0.1, 0.3, 0))
    l.k(4, "OUTQUAD", rightArm=arm_at((-1.57, 0.0, 0.0), (0, 0, -2.5)), leftArm=(0.4, 0, -0.3), torso=(0.35, -0.2, 0),
        rightLeg=(-0.8, 0, 0), leftLeg=(0.6, 0, 0))
    l.k(9, rightArm=arm_at((-1.55, 0.0, 0.0), (0, 0, -2.3)), leftArm=(0.4, 0, -0.3), torso=(0.3, -0.2, 0),
        rightLeg=(-0.7, 0, 0), leftLeg=(0.55, 0, 0))
    l.k(14, rightArm=arm_at(NEUTRAL_R), leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    l.save()

    g = A("longsword_guard", 40)
    GR, GL = (-1.75, -0.65, 0.2), (-1.75, 0.65, -0.2)
    g.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    g.k(4, "OUTQUAD", rightArm=GR, leftArm=GL, torso=(0.1, 0, 0), head=(0.2, 0, 0))
    g.k(36, rightArm=(GR[0] - 0.05, GR[1], GR[2]), leftArm=(GL[0] - 0.05, GL[1], GL[2]), torso=(0.1, 0, 0), head=(0.2, 0, 0))
    g.k(40, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    g.save()


# ============================================================================ FIENDS
def possession():
    """Letting a devil's remains in: you choke, you die, and something else stands your corpse back up."""
    h = A("fiend_possession", 50)
    CR, CL = (-2.45, 0.6, -0.55), (-2.45, -0.6, 0.55)
    h.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    h.k(5, "OUTQUAD", rightArm=CR, leftArm=CL, head=(0.35, 0, 0), torso=(0.15, 0, 0))
    for k, t in enumerate(range(7, 17, 2)):
        j = 0.12 if k % 2 == 0 else -0.12
        h.k(t, "linear", rightArm=(CR[0] + j, CR[1], CR[2]), leftArm=(CL[0] - j, CL[1], CL[2]), head=(0.4, j, j * 2),
            torso=(0.2 + abs(j), j, 0))
    # the body gives out
    h.k(19, "INQUAD", rightArm=(0.25, 0, 0.12), leftArm=(0.25, 0, -0.12), head=(0.75, 0.1, 0.2), torso=(0.95, 0, 0),
        rightLeg=(-0.9, 0, 0.1), leftLeg=(-0.7, 0, -0.1))
    h.k(32, "linear", rightArm=(0.3, 0, 0.15), leftArm=(0.3, 0, -0.15), head=(0.8, 0.1, 0.25), torso=(1.0, 0, 0),
        rightLeg=(-0.95, 0, 0.1), leftLeg=(-0.75, 0, -0.1))
    # ...and the devil jerks it back up
    h.k(35, "OUTBACK", rightArm=(-0.3, 0.3, 0.6), leftArm=(-0.3, -0.3, -0.6), head=(-0.6, 0, 0.1), torso=(-0.25, 0, 0),
        rightLeg=Z3, leftLeg=Z3)
    h.k(38, rightArm=(-0.1, 0.2, 0.4), leftArm=(-0.5, -0.3, -0.7), head=(-0.3, 0.2, -0.2), torso=(-0.1, 0, 0))
    h.k(41, rightArm=(-0.5, 0.3, 0.7), leftArm=(-0.1, -0.2, -0.3), head=(-0.2, -0.3, 0.25), torso=(-0.05, 0, 0))
    h.k(46, rightArm=(-0.1, 0, 0.2), leftArm=(-0.1, 0, -0.2), head=(0.05, 0.1, 0.3), torso=Z3)
    h.k(50, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    h.save()


def fiend_awaken(name, length, burst, pre, arms_burst, head_burst=(-0.5, 0, 0)):
    """Generic awakening: `pre` builds up to `burst` (tick), then arms_burst / head_burst, and it settles."""
    a = A(name, length)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    for tick, kw in pre:
        a.k(tick, "INOUTSINE", **kw)
    a.k(burst, "OUTBACK", rightArm=arms_burst[0], leftArm=arms_burst[1], head=head_burst, torso=(-0.18, 0, 0))
    a.k(burst + 5, rightArm=lerp3(arms_burst[0], NEUTRAL_R, 0.4), leftArm=lerp3(arms_burst[1], NEUTRAL_L, 0.4),
        head=lerp3(head_burst, Z3, 0.4), torso=(-0.1, 0, 0))
    a.k(length, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.save()


def simple_revert(prefix, length=12):
    r = A("%s_revert" % prefix, length)
    r.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.k(length // 3, rightArm=(-0.4, 0.2, 0.3), leftArm=(-0.4, -0.2, -0.3), head=(0.35, 0, 0))
    r.k(length, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    r.save()


def blood():
    DR = (-2.2, -0.55, 0.3)
    fiend_awaken("blood_blood_awakening", 20, 10,
                 [(4, dict(rightArm=DR, head=(0.2, 0, 0))), (7, dict(rightArm=(DR[0] - 0.1, DR[1], DR[2]), head=(-0.45, 0, 0)))],
                 ((-0.5, 0.4, 1.25), (-0.5, -0.4, -1.25)), (-0.6, 0, 0))
    simple_revert("blood")
    h = A("blood_hammer", 20)
    h.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    h.k(6, "INOUTQUAD", rightArm=(-3.05, 0.1, 0.25), leftArm=(-2.8, -0.2, -0.1), torso=(-0.25, 0, 0))
    h.k(11, "OUTQUAD", rightArm=(-0.55, 0.05, 0.1), leftArm=(-0.6, -0.1, -0.1), torso=(0.5, 0, 0))
    h.k(16, rightArm=(-0.5, 0.05, 0.1), leftArm=(-0.55, -0.1, -0.1), torso=(0.45, 0, 0))
    h.k(20, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    h.save()
    sp = A("blood_spear", 12)
    sp.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    sp.k(4, "INOUTQUAD", rightArm=(-2.8, 0.15, 0.35), leftArm=(-1.4, 0.3, 0.0), torso=(-0.1, 0.5, 0))
    sp.k(6, "OUTQUAD", rightArm=(-1.3, -0.3, 0.0), leftArm=(-0.3, 0.1, -0.3), torso=(0.2, -0.4, 0))
    sp.k(12, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    sp.save()
    sc = A("blood_scythe", 18)
    sc.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    sc.k(6, "INOUTQUAD", rightArm=(-1.45, 1.25, 0.35), leftArm=(-0.6, 0.6, -0.2), torso=(0, 0.6, 0))
    sc.k(9, "OUTQUAD", rightArm=(-1.3, -1.1, 0.1), leftArm=(-0.4, -0.3, -0.3), torso=(0.1, -0.6, 0))
    sc.k(14, rightArm=(-1.1, -1.0, 0.1), leftArm=(-0.3, -0.2, -0.3), torso=(0.05, -0.5, 0))
    sc.k(18, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    sc.save()
    c = A("blood_control", 18)
    c.k(0, rightArm=NEUTRAL_R, head=Z3)
    c.k(4, "OUTQUAD", rightArm=(-1.6, -0.05, 0.0), head=(0.1, 0, 0))
    c.k(12, rightArm=(-1.6, -0.05, 0.05), head=(0.1, 0, 0))
    c.k(15, "INQUAD", rightArm=(-0.9, 0.3, 0.2), head=(-0.2, 0, 0))
    c.k(18, rightArm=NEUTRAL_R, head=Z3)
    c.save()
    r = A("blood_rain", 34)
    r.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    r.k(5, "OUTQUAD", rightArm=(-2.9, 0.3, 0.3), leftArm=(-2.9, -0.3, -0.3), head=(-0.7, 0, 0), torso=(-0.15, 0, 0))
    r.k(28, rightArm=(-2.95, 0.3, 0.35), leftArm=(-2.95, -0.3, -0.35), head=(-0.7, 0, 0), torso=(-0.15, 0, 0))
    r.k(34, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    r.save()


def shark():
    fiend_awaken("shark_shark_devil", 18, 9,
                 [(4, dict(rightArm=(0.3, 0, 0.4), leftArm=(0.3, 0, -0.4), head=(0.5, 0, 0), torso=(0.35, 0, 0)))],
                 ((-0.3, 0.3, 1.0), (-0.3, -0.3, -1.0)), (-0.6, 0, 0))
    simple_revert("shark")
    DIVE = dict(rightArm=(-2.9, 0.0, 0.12), leftArm=(-2.9, 0.0, -0.12), head=(-0.2, 0, 0), torso=(0.6, 0, 0))
    sw = A("shark_swim", 100)
    sw.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    sw.k(3, "OUTQUAD", **DIVE)
    sw.k(96, **DIVE)
    sw.k(100, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    sw.save()
    b = A("shark_bite", 12)
    b.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    b.k(3, "INQUAD", rightArm=(0.5, 0, 0.3), leftArm=(0.5, 0, -0.3), head=(-0.4, 0, 0), torso=(0.1, 0, 0))
    b.k(5, "OUTQUAD", rightArm=(0.7, 0, 0.35), leftArm=(0.7, 0, -0.35), head=(0.3, 0, 0), torso=(0.55, 0, 0))
    b.k(12, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    b.save()
    am = A("shark_ambush", 24)
    am.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    am.k(2, "OUTQUAD", **DIVE)
    am.k(19, **DIVE)
    am.k(21, "OUTBACK", rightArm=(-2.9, 0.3, 0.4), leftArm=(-2.9, -0.3, -0.4), head=(-0.6, 0, 0), torso=(-0.2, 0, 0))
    am.k(24, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    am.save()
    f = A("shark_form", 200)
    f.k(0, head=Z3, torso=Z3)
    f.k(200, head=Z3, torso=Z3)
    f.save()
    sc = A("shark_scent", 20)
    sc.k(0, head=Z3, torso=Z3)
    for k, t in enumerate(range(3, 17, 3)):
        sc.k(t, head=(-0.45, 0.25 if k % 2 else -0.25, 0), torso=(-0.1, 0, 0))
    sc.k(20, head=Z3, torso=Z3)
    sc.save()


def violence():
    MR = (-2.05, -0.35, 0.2)
    a = A("violence_remove_mask", 24)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.k(5, "OUTQUAD", rightArm=MR, leftArm=(-0.1, 0, -0.15), head=(0.15, 0, 0))
    a.k(7, rightArm=(MR[0] - 0.05, MR[1], MR[2]), leftArm=(-0.1, 0, -0.15), head=(0.2, 0, 0))
    a.k(9, "OUTQUAD", rightArm=(-0.8, 0.5, 1.0), leftArm=(-0.1, 0, -0.15), head=(-0.1, -0.2, 0))
    a.k(11, rightArm=(-0.7, 0.5, 1.0), leftArm=(-0.1, 0, -0.2), head=(0.3, 0, 0), torso=(0.2, 0, 0))
    # he swells to his real size: double-biceps roar
    a.k(13, "OUTBACK", rightArm=(-0.15, 0.3, 1.4), leftArm=(-0.15, -0.3, -1.4), head=(-0.55, 0, 0), torso=(-0.2, 0, 0))
    a.k(18, rightArm=(-0.2, 0.3, 1.3), leftArm=(-0.2, -0.3, -1.3), head=(-0.45, 0, 0), torso=(-0.15, 0, 0))
    a.k(24, rightArm=(-0.1, 0, 0.25), leftArm=(-0.1, 0, -0.25), head=Z3, torso=Z3)
    a.save()
    r = A("violence_revert", 16)
    r.k(0, rightArm=NEUTRAL_R, head=Z3)
    r.k(6, "OUTQUAD", rightArm=MR, head=(0.15, 0, 0))
    r.k(10, rightArm=(MR[0] - 0.05, MR[1], MR[2]), head=(0.15, 0, 0))
    r.k(16, rightArm=NEUTRAL_R, head=Z3)
    r.save()
    pu = A("violence_punch", 16)
    pu.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    pu.k(4, "INQUAD", rightArm=(0.5, 0.3, 0.3), leftArm=(-1.0, -0.3, -0.1), torso=(0, 0.55, 0))
    pu.k(7, "OUTQUAD", rightArm=arm_at((-1.6, -0.1, 0.0), (0, 0, -2.0)), leftArm=(0.3, 0, -0.2), torso=(0.2, -0.5, 0))
    pu.k(11, rightArm=arm_at((-1.55, -0.1, 0.0), (0, 0, -1.8)), leftArm=(0.3, 0, -0.2), torso=(0.15, -0.45, 0))
    pu.k(16, rightArm=arm_at(NEUTRAL_R), leftArm=NEUTRAL_L, torso=Z3)
    pu.save()
    k = A("violence_kick", 18)
    k.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    k.k(5, "OUTQUAD", rightArm=(-0.6, 0, 0.7), leftArm=(-0.6, 0, -0.7), torso=(-0.15, 0, 0), rightLeg=(-1.45, 0, 0.1),
        leftLeg=(0.1, 0, 0))
    k.k(9, "INEXPO", rightArm=(-0.3, 0, 0.5), leftArm=(-0.3, 0, -0.5), torso=(0.35, 0, 0), rightLeg=(0.1, 0, 0.05),
        leftLeg=(0.2, 0, 0))
    k.k(14, rightArm=(-0.2, 0, 0.4), leftArm=(-0.2, 0, -0.4), torso=(0.3, 0, 0), rightLeg=(0.05, 0, 0.05), leftLeg=(0.15, 0, 0))
    k.k(18, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    k.save()
    ma = A("violence_mouth_arm", 22)
    ma.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    ma.k(4, "OUTQUAD", rightArm=(0.3, 0, 0.6), leftArm=(0.3, 0, -0.6), head=(-0.4, 0, 0), torso=(-0.1, 0, 0))
    ma.k(8, "OUTBACK", rightArm=(0.4, 0, 0.7), leftArm=(0.4, 0, -0.7), head=(0.05, 0, 0), torso=(0.2, 0, 0))
    ma.k(13, "OUTQUAD", rightArm=(0.4, 0, 0.7), leftArm=(0.4, 0, -0.7), head=(0.2, -0.3, 0), torso=(0.3, -0.2, 0))
    ma.k(22, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    ma.save()
    ra = A("violence_rampage", 32)
    ra.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    for n, t in enumerate(range(3, 29, 3)):
        right = n % 2 == 0
        ra.k(t, "OUTQUAD", rightArm=(-1.6, -0.1, 0.0) if right else (0.3, 0.2, 0.3),
             leftArm=(0.3, -0.2, -0.3) if right else (-1.6, 0.1, 0.0), torso=(0.15, -0.35 if right else 0.35, 0))
    ra.k(32, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    ra.save()


def cosmos():
    fiend_awaken("cosmos_open_cosmos", 20, 10,
                 [(5, dict(rightArm=(-0.4, 0.2, 0.6), leftArm=(-0.4, -0.2, -0.6), head=(-0.2, 0, 0.15)))],
                 ((-0.9, 0.3, 1.2), (-0.9, -0.3, -1.2)), (-0.55, 0, 0.2))
    simple_revert("cosmos")
    h = A("cosmos_halloween", 14)
    h.k(0, rightArm=NEUTRAL_R, head=Z3)
    h.k(4, "OUTQUAD", rightArm=(-1.55, -0.05, 0.0), head=(0.0, 0, 0.35))
    h.k(10, rightArm=(-1.55, -0.05, 0.0), head=(0.0, 0, 0.35))
    h.k(14, rightArm=NEUTRAL_R, head=Z3)
    h.save()
    a = A("cosmos_all_out", 32)
    a.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.k(10, "INOUTSINE", rightArm=(-0.3, 0.2, 1.3), leftArm=(-0.3, -0.2, -1.3), head=(-0.3, 0, 0.1), torso=(-0.1, 0, 0))
    a.k(14, "OUTBACK", rightArm=(-2.6, 0.3, 0.5), leftArm=(-2.6, -0.3, -0.5), head=(-0.7, 0, 0), torso=(-0.2, 0, 0))
    a.k(26, rightArm=(-2.55, 0.3, 0.5), leftArm=(-2.55, -0.3, -0.5), head=(-0.65, 0, 0), torso=(-0.18, 0, 0))
    a.k(32, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    a.save()
    kn = A("cosmos_knowledge", 20)
    kn.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    kn.k(5, "OUTQUAD", rightArm=(-2.5, 0.95, -0.45), leftArm=(-2.5, -0.95, 0.45), head=(0.2, 0, 0))
    kn.k(9, "OUTBACK", rightArm=(-1.2, 0.3, 0.9), leftArm=(-1.2, -0.3, -0.9), head=(-0.4, 0, 0))
    kn.k(20, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    kn.save()
    c = A("cosmos_collapse", 16)
    c.k(0, rightArm=NEUTRAL_R, head=Z3)
    c.k(5, "OUTQUAD", rightArm=(-1.9, -0.1, 0.0), head=(-0.1, 0, 0))
    c.k(8, "INQUAD", rightArm=(-0.8, -0.1, 0.0), head=(0.25, 0, 0))
    c.k(16, rightArm=NEUTRAL_R, head=Z3)
    c.save()


def gun():
    fiend_awaken("gun_gun_devil", 20, 10,
                 [(5, dict(rightArm=(0.3, 0, 0.3), leftArm=(0.3, 0, -0.3), head=(0.6, 0, 0), torso=(0.4, 0, 0)))],
                 ((-0.2, 0.3, 1.2), (-0.2, -0.3, -1.2)), (-0.6, 0, 0))
    simple_revert("gun")
    AIM = (-1.57, 0.1, 0.0)
    b = A("gun_burst", 24)
    b.k(0, leftArm=NEUTRAL_L, head=Z3)
    b.k(3, "OUTQUAD", leftArm=AIM, head=Z3)
    for t0 in (4, 12, 20):
        for dt in range(3):
            b.k(t0 + dt, "linear", leftArm=(AIM[0] - (0.12 if dt % 2 == 0 else 0.0), AIM[1], AIM[2]))
        b.k(t0 + 3, "OUTQUAD", leftArm=AIM)
    b.k(24, leftArm=NEUTRAL_L, head=Z3)
    b.save()
    h = A("gun_headshot", 20)
    h.k(0, head=Z3, torso=Z3, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L)
    h.k(6, "OUTQUAD", head=(0.0, 0, 0), torso=(0.15, 0, 0), rightArm=(0.1, 0, 0.3), leftArm=(0.1, 0, -0.3))
    h.k(11, head=(0.05, 0, 0), torso=(0.2, 0, 0), rightArm=(0.15, 0, 0.3), leftArm=(0.15, 0, -0.3))
    h.k(12, "OUTEXPO", head=(-0.55, 0, 0), torso=(-0.2, 0, 0), rightArm=(-0.3, 0, 0.5), leftArm=(-0.3, 0, -0.5))
    h.k(20, head=Z3, torso=Z3, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L)
    h.save()
    st = A("gun_storm", 40)
    st.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    st.k(5, "OUTQUAD", rightArm=(-0.6, 0.2, 1.2), leftArm=(-1.57, 0.1, 0), torso=(-0.1, 0, 0), head=(-0.2, 0, 0))
    for k, t in enumerate(range(6, 36, 2)):
        j = 0.05 if k % 2 else -0.05
        st.k(t, "linear", rightArm=(-0.6 + j, 0.2, 1.2), leftArm=(-1.6 + j, 0.1, 0), torso=(-0.1 + j, j, 0), head=(-0.2, j, 0))
    st.k(40, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    st.save()
    m = A("gun_massacre", 40)
    m.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    m.k(8, "OUTQUAD", rightArm=(-1.0, 0.3, 1.3), leftArm=(-1.0, -0.3, -1.3), head=(-0.5, 0, 0), torso=(-0.2, 0, 0))
    for k, t in enumerate(range(12, 32, 2)):
        j = 0.06 if k % 2 else -0.06
        m.k(t, "linear", rightArm=(-1.0 + j, 0.3, 1.3), leftArm=(-1.0 - j, -0.3, -1.3), head=(-0.5, j * 3, 0),
            torso=(-0.2, j * 2, 0))
    m.k(40, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, head=Z3)
    m.save()


# ============================================================================ shared
def shared():
    d = A("blood_drink", 20)
    d.k(0, rightArm=NEUTRAL_R, head=Z3)
    d.k(4, "OUTQUAD", rightArm=(-1.5, -0.2, 0.0), head=(0.2, 0, 0))
    d.k(8, "INOUTQUAD", rightArm=(-2.05, -0.6, 0.3), head=(-0.1, 0, 0))
    d.k(10, rightArm=(-2.35, -0.5, 0.2), head=(-0.42, 0, 0))
    d.k(14, rightArm=(-2.3, -0.45, 0.2), head=(-0.45, 0, 0.05))
    d.k(17, "INOUTQUAD", rightArm=(-1.8, -0.95, 0.3), head=(-0.1, 0, 0))
    d.k(20, rightArm=NEUTRAL_R, head=Z3)
    d.save()

    dj = poses.denji_pull()
    chest_r = tuple(dj["grab"]["rot"])
    chest_l = (chest_r[0], -chest_r[1], -chest_r[2])
    h = A("heart_replace", 50)
    h.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    h.k(6, "OUTQUAD", rightArm=chest_r, leftArm=(-1.0, -0.2, 0.0), head=(0.35, 0, 0), torso=(0.05, 0, 0))
    for i, t in enumerate(range(9, 21, 2)):
        j = 0.05 if i % 2 == 0 else -0.05
        h.k(t, "linear", rightArm=(chest_r[0] + j, chest_r[1], chest_r[2] + j), leftArm=(-1.0, -0.2, 0.0),
            head=(0.4, 0, j), torso=(0.15, 0, 0))
    # RIP: tear the old heart out
    h.k(22, "OUTBACK", rightArm=(-1.9, 0.3, 0.55), leftArm=(-0.9, -0.2, 0.0), head=(-0.25, 0, 0),
        torso=(-0.12, 0, 0))
    h.k(26, "INOUTQUAD", rightArm=(0.15, 0.0, 0.35), leftArm=chest_l, head=(0.3, 0, 0), torso=(0.05, 0, 0))
    # shove the devil's heart in
    h.k(32, "INQUAD", rightArm=(0.1, 0.0, 0.3), leftArm=(chest_l[0] + 0.15, chest_l[1], chest_l[2] - 0.1),
        head=(0.42, 0, 0), torso=(0.25, 0, 0))
    h.k(34, "linear", rightArm=(0.1, 0.0, 0.3), leftArm=chest_l, head=(0.45, 0, 0), torso=(0.28, 0, 0))
    h.k(40, "OUTBACK", rightArm=(-0.25, 0.3, 0.95), leftArm=(-0.25, -0.3, -0.95), head=(-0.55, 0, 0),
        torso=(-0.15, 0, 0))
    h.k(46, rightArm=(-0.2, 0.2, 0.7), leftArm=(-0.2, -0.2, -0.7), head=(-0.4, 0, 0), torso=(-0.1, 0, 0))
    h.k(50, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    h.save()


# ============================================================================ full devils
def devils():
    """Shared by every full devil: swallowing an essence, and a monster devil tearing out of (or back into) its human
    shell. The puppet model takes over at the transform tick, so only the build-up of devil_manifest is ever seen."""
    c = A("devil_consume", 50)
    MOUTH_R = (-2.35, -0.45, 0.1)
    c.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    c.k(6, "OUTQUAD", rightArm=MOUTH_R, head=(0.1, 0, 0))
    c.k(12, rightArm=(MOUTH_R[0] - 0.1, MOUTH_R[1], MOUTH_R[2]), head=(-0.45, 0, 0))          # swallow
    c.k(16, "INOUTQUAD", rightArm=(-0.3, 0, 0.2), head=(0.2, 0, 0), torso=(0.15, 0, 0))
    CR, CL = (-2.2, 0.55, -0.4), (-2.2, -0.55, 0.4)
    c.k(20, "OUTBACK", rightArm=CR, leftArm=CL, head=(0.55, 0, 0), torso=(0.55, 0, 0))            # it floods in
    for k, t in enumerate(range(22, 38, 2)):
        j = 0.14 if k % 2 == 0 else -0.14
        c.k(t, "linear", rightArm=(CR[0] + j, CR[1], CR[2] + j), leftArm=(CL[0] - j, CL[1], CL[2] - j),
            head=(0.5 + j, j, j * 1.5), torso=(0.5 + abs(j), j, 0))
    c.k(40, "OUTBACK", rightArm=(-0.4, 0.35, 1.2), leftArm=(-0.4, -0.35, -1.2), head=(-0.55, 0, 0), torso=(-0.15, 0, 0))
    c.k(46, rightArm=(-0.2, 0.2, 0.6), leftArm=(-0.2, -0.2, -0.6), head=(-0.3, 0, 0), torso=(-0.05, 0, 0))
    c.k(50, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    c.save()

    m = A("devil_manifest", 24)
    m.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    m.k(4, "OUTQUAD", rightArm=(-0.9, 0.4, 0.2), leftArm=(-0.9, -0.4, -0.2), head=(0.5, 0, 0), torso=(0.45, 0, 0))
    for k, t in enumerate(range(5, 12)):
        j = 0.16 if k % 2 == 0 else -0.16
        m.k(t, "linear", rightArm=(-0.9 + j, 0.4, 0.2 + j), leftArm=(-0.9 - j, -0.4, -0.2 - j),
            head=(0.55 + j * 0.5, j, 0), torso=(0.5, j * 0.5, 0))
    m.k(12, "OUTBACK", rightArm=(-0.5, 0.4, 1.4), leftArm=(-0.5, -0.4, -1.4), head=(-0.7, 0, 0), torso=(-0.25, 0, 0))
    m.k(24, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    m.save()

    r = A("devil_revert", 16)
    r.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    r.k(8, rightArm=(0.2, 0, 0.3), leftArm=(0.2, 0, -0.3), head=(0.6, 0, 0), torso=(0.5, 0, 0))
    r.k(11, rightArm=(-0.3, 0.3, 0.2), leftArm=(0.1, 0, -0.2), head=(0.4, 0.1, 0), torso=(0.3, 0, 0))
    r.k(16, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    r.save()


# ============================================================================ contracts
def contracts():
    """A contractor stays human: these are the gestures that call a contract devil (contract.ContractAbilities) and the
    signing itself (item.ContractItem). Ticks line up with the moves' summon ticks."""
    import numpy as np
    # Aki holds the fox sign up in front of his eye like a lens, then points it: "Kon!"
    lens = tuple(poses.ik_arm(poses.SHOULDER_R, poses.GRIP_R, np.array([-1.2, -3.6, -9.5]), zr_hint=0.0)[0])
    point = (-1.62, -0.12, 0.0)
    k = A("contract_kon", 18)
    k.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    k.k(3, "OUTQUAD", rightArm=lens, leftArm=(-0.2, 0.0, -0.1), head=(0.06, 0.0, 0.0), torso=Z3)
    k.k(5, rightArm=lens, leftArm=(-0.2, 0.0, -0.1), head=(0.08, 0.0, 0.0), torso=Z3)
    k.k(7, "OUTBACK", rightArm=point, leftArm=(-0.1, 0.0, -0.15), head=(0.0, 0.0, 0.0), torso=(0.08, 0.0, 0.0))
    k.k(14, rightArm=(point[0] + 0.1, point[1], point[2]), leftArm=(-0.1, 0.0, -0.15), head=Z3, torso=(0.05, 0, 0))
    k.k(18, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    k.save()

    # the paw: point up at the sky, then bring the finger down on the prey as the paw drops
    w = A("contract_paw", 14)
    w.k(0, rightArm=NEUTRAL_R, head=Z3, torso=Z3)
    w.k(2, "OUTQUAD", rightArm=(-2.75, -0.1, 0.1), head=(-0.2, 0, 0), torso=(-0.05, 0, 0))
    w.k(4, "INQUAD", rightArm=(-1.45, -0.12, 0.0), head=(0.05, 0, 0), torso=(0.1, 0, 0))
    w.k(10, rightArm=(-1.4, -0.1, 0.0), head=(0.05, 0, 0), torso=(0.08, 0, 0))
    w.k(14, rightArm=NEUTRAL_R, head=Z3, torso=Z3)
    w.save()

    # the paw sweeping across: the arm leads it from the right to the left
    sw = A("contract_paw_swipe", 14)
    sw.k(0, rightArm=NEUTRAL_R, torso=Z3)
    sw.k(2, "OUTQUAD", rightArm=(-1.5, 0.95, 0.35), torso=(0.0, 0.3, 0.0))
    sw.k(7, "OUTQUAD", rightArm=(-1.4, -1.0, -0.2), torso=(0.05, -0.35, 0.0))
    sw.k(10, rightArm=(-1.1, -0.8, -0.1), torso=(0.03, -0.25, 0.0))
    sw.k(14, rightArm=NEUTRAL_R, torso=Z3)
    sw.save()

    # the nail: draw back, drive it in
    n = A("contract_curse_nail", 12)
    n.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    n.k(2, "OUTQUAD", rightArm=arm_at((-1.1, 0.25, 0.25), (0, 0, 1.5)), leftArm=(-0.5, 0.2, -0.1), torso=(0.0, 0.25, 0))
    n.k(5, "INQUAD", rightArm=arm_at((-1.58, -0.12, 0.0), (0, 0, -2.5)), leftArm=(-0.3, 0.1, -0.2),
        torso=(0.12, -0.18, 0.0))
    n.k(8, rightArm=arm_at((-1.5, -0.1, 0.0), (0, 0, -2.0)), leftArm=(-0.3, 0.1, -0.2), torso=(0.1, -0.12, 0.0))
    n.k(12, rightArm=arm_at(NEUTRAL_R), leftArm=NEUTRAL_L, torso=Z3)
    n.save()

    # the Future Devil lives in the right eye: two fingers to it
    eye = tuple(poses.ik_arm(poses.SHOULDER_R, poses.GRIP_R, poses.RIGHT_EYE + np.array([0.3, 0.6, -2.4]),
                             zr_hint=0.0)[0])
    f = A("contract_future", 16)
    f.k(0, rightArm=NEUTRAL_R, head=Z3)
    f.k(4, "OUTQUAD", rightArm=eye, head=(0.05, -0.08, 0.0))
    f.k(8, rightArm=eye, head=(-0.12, 0.0, 0.0))
    f.k(11, rightArm=(-0.7, 0.0, 0.1), head=(-0.05, 0, 0))
    f.k(16, rightArm=NEUTRAL_R, head=Z3)
    f.save()

    # Himeno's arm: the ghost's invisible arm does what hers does - reach, close on the throat, lift and squeeze
    g = A("contract_ghost_grab", 20)
    g.k(0, rightArm=NEUTRAL_R, torso=Z3)
    g.k(3, "OUTQUAD", rightArm=(-1.62, -0.15, 0.05), torso=(0.06, 0, 0))
    g.k(6, "INOUTQUAD", rightArm=(-1.95, -0.1, 0.0), torso=(0.0, 0, 0))
    for i, t in enumerate(range(8, 17, 2)):
        j = 0.04 if i % 2 == 0 else -0.04
        g.k(t, "linear", rightArm=(-2.0 + j, -0.1, j), torso=Z3)
    g.k(20, rightArm=NEUTRAL_R, torso=Z3)
    g.save()

    fl = A("contract_ghost_fling", 16)
    fl.k(0, rightArm=NEUTRAL_R, torso=Z3)
    fl.k(3, "OUTQUAD", rightArm=(-1.6, -0.15, 0.05), torso=(0.05, 0, 0))
    fl.k(9, "INOUTQUAD", rightArm=(-2.3, 0.45, 0.2), torso=(0.0, 0.25, 0))
    fl.k(12, "OUTQUAD", rightArm=(-1.3, -1.05, -0.3), torso=(0.05, -0.35, 0))
    fl.k(16, rightArm=NEUTRAL_R, torso=Z3)
    fl.save()

    # Sawatari: her hand up, fingers spread, then brought down as she gives the command ("Snake - swallow it")
    sn = A("contract_snake", 16)
    sn.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    sn.k(3, "OUTQUAD", rightArm=(-2.5, -0.15, 0.25), leftArm=(-0.2, 0, -0.1), head=(-0.1, 0, 0))
    sn.k(6, "INQUAD", rightArm=(-1.5, -0.1, 0.0), leftArm=(-0.2, 0, -0.1), head=(0.05, 0, 0), torso=(0.06, 0, 0))
    sn.k(12, rightArm=(-1.45, -0.1, 0.0), leftArm=(-0.2, 0, -0.1), head=(0.05, 0, 0), torso=(0.05, 0, 0))
    sn.k(16, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    sn.save()

    # "Release": palm out towards the spot, the other hand to the nose (the nosebleed)
    nose = tuple(poses.ik_arm(poses.SHOULDER_L, np.array([1.0, 9.4, 0.0]), np.array([0.6, -2.6, -5.0]),
                              zr_hint=0.0)[0])
    sr = A("contract_snake_release", 16)
    sr.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    sr.k(3, "OUTQUAD", rightArm=(-1.55, 0.05, -0.1), leftArm=nose, head=(0.12, 0, 0))
    sr.k(12, rightArm=(-1.6, 0.05, -0.1), leftArm=nose, head=(0.15, 0, 0))
    sr.k(16, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    sr.save()

    # the tail: a sweep of the arm from right to left, as the tail sweeps
    st = A("contract_snake_tail", 14)
    st.k(0, rightArm=NEUTRAL_R, torso=Z3)
    st.k(3, "OUTQUAD", rightArm=(-1.3, 1.0, 0.4), torso=(0.0, 0.35, 0.0))
    st.k(9, "OUTQUAD", rightArm=(-1.2, -1.1, -0.2), torso=(0.05, -0.4, 0.0))
    st.k(14, rightArm=NEUTRAL_R, torso=Z3)
    st.save()

    # Yoshida: index and middle fingers crossed, held up, then pointed at the target
    oc = A("contract_octopus", 16)
    cross = (-2.0, -0.45, 0.2)
    oc.k(0, rightArm=NEUTRAL_R, head=Z3, torso=Z3)
    oc.k(3, "OUTQUAD", rightArm=cross, head=(0.1, 0.1, 0))
    oc.k(5, rightArm=cross, head=(0.1, 0.1, 0))
    oc.k(7, "OUTBACK", rightArm=(-1.6, -0.1, 0.0), head=Z3, torso=(0.06, 0, 0))
    oc.k(13, rightArm=(-1.55, -0.1, 0.0), head=Z3, torso=(0.04, 0, 0))
    oc.k(16, rightArm=NEUTRAL_R, head=Z3, torso=Z3)
    oc.save()

    # Ink: both hands thrown out as the cloud bursts
    ik = A("contract_octopus_ink", 12)
    ik.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    ik.k(2, "INQUAD", rightArm=(-0.8, 0.6, 0.2), leftArm=(-0.8, -0.6, -0.2), torso=(0.15, 0, 0))
    ik.k(4, "OUTBACK", rightArm=(-1.3, -0.4, 0.9), leftArm=(-1.3, 0.4, -0.9), torso=(-0.05, 0, 0))
    ik.k(12, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3)
    ik.save()

    # Tentacle Lift: crouch on the tentacle, then flung - arms up, knees tucked, and land
    tl = A("contract_octopus_lift", 40)
    tl.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    tl.k(4, "OUTQUAD", rightArm=(0.4, 0, 0.3), leftArm=(0.4, 0, -0.3), torso=(0.3, 0, 0), rightLeg=(-0.6, 0, 0),
         leftLeg=(-0.6, 0, 0))
    tl.k(8, "OUTQUAD", rightArm=(-2.6, 0, 0.3), leftArm=(-2.6, 0, -0.3), torso=(-0.1, 0, 0), rightLeg=(-0.9, 0, 0),
         leftLeg=(-0.7, 0, 0))
    tl.k(22, rightArm=(-1.9, 0, 0.6), leftArm=(-1.9, 0, -0.6), torso=(0.0, 0, 0), rightLeg=(-0.4, 0, 0),
         leftLeg=(-0.3, 0, 0))
    tl.k(40, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, torso=Z3, rightLeg=Z3, leftLeg=Z3)
    tl.save()

    # Santa Claus: a light touch of the fingertips
    dt = A("contract_doll_touch", 10)
    dt.k(0, rightArm=NEUTRAL_R, torso=Z3)
    dt.k(3, "OUTQUAD", rightArm=(-1.5, -0.05, 0.0), torso=(0.12, 0, 0))
    dt.k(6, rightArm=(-1.55, -0.05, 0.0), torso=(0.14, 0, 0))
    dt.k(10, rightArm=NEUTRAL_R, torso=Z3)
    dt.save()

    # her dolls, go: the arm sweeps out and points
    dc = A("contract_doll_command", 12)
    dc.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    dc.k(3, "OUTQUAD", rightArm=(-1.3, 0.6, 0.6), leftArm=(-0.3, 0, -0.2), head=(-0.05, 0, 0))
    dc.k(5, "OUTBACK", rightArm=(-1.62, -0.1, 0.0), leftArm=(-0.3, 0, -0.2), head=Z3)
    dc.k(12, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3)
    dc.save()

    # signing: bite the thumb, then press it to the paper held in the other hand
    MOUTH_R = (-2.35, -0.5, 0.2)
    c = A("contract_sign", 40)
    c.k(0, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    c.k(4, "OUTQUAD", rightArm=MOUTH_R, leftArm=(-0.95, 0.3, -0.1), head=(0.15, 0, 0))
    c.k(8, rightArm=(MOUTH_R[0] - 0.05, MOUTH_R[1], MOUTH_R[2]), leftArm=(-0.95, 0.3, -0.1), head=(-0.08, 0, 0))
    c.k(12, rightArm=MOUTH_R, leftArm=(-0.95, 0.3, -0.1), head=(0.1, 0, 0))
    c.k(18, "INOUTQUAD", rightArm=(-1.15, -0.35, 0.1), leftArm=(-1.0, 0.3, -0.1), head=(0.45, 0, 0), torso=(0.1, 0, 0))
    c.k(22, "INQUAD", rightArm=(-1.0, -0.38, 0.1), leftArm=(-1.0, 0.3, -0.1), head=(0.5, 0, 0), torso=(0.18, 0, 0))
    c.k(30, rightArm=(-1.0, -0.38, 0.1), leftArm=(-1.0, 0.3, -0.1), head=(0.45, 0, 0), torso=(0.15, 0, 0))
    c.k(35, rightArm=(-0.4, -0.1, 0.1), leftArm=(-0.6, 0.2, -0.1), head=(0.1, 0, 0), torso=Z3)
    c.k(40, rightArm=NEUTRAL_R, leftArm=NEUTRAL_L, head=Z3, torso=Z3)
    c.save()


if __name__ == "__main__":
    chainsaw()
    crossbow()
    flamethrower()
    whip()
    bomb()
    spear()
    katana()
    longsword()
    possession()
    blood()
    shark()
    violence()
    cosmos()
    gun()
    shared()
    devils()
    contracts()
    print("wrote", len(os.listdir(OUT)), "player animations to", OUT)
