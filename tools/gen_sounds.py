"""
Synthesizes the mod's sound effects (mono Ogg Vorbis) and writes assets/csm/sounds.json.

Needs `soundfile` (pip install soundfile) for the Vorbis encoder.
Everything is procedural: two-stroke engine = pulse train at the firing frequency through resonant filters,
flames = turbulence-modulated filtered noise, strings = Karplus-Strong, etc.
"""
import json
import math
import os

import numpy as np
import soundfile as sf

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "src", "main", "resources", "assets", "csm")
rng = np.random.default_rng(7)


def t_axis(dur):
    return np.arange(int(SR * dur)) / SR


def noise(dur):
    return rng.uniform(-1, 1, int(SR * dur))


def biquad(x, kind, f0, q=0.7):
    w0 = 2 * math.pi * f0 / SR
    alpha = math.sin(w0) / (2 * q)
    cw = math.cos(w0)
    if kind == "lp":
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]
    elif kind == "hp":
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
    else:  # band-pass
        b = [alpha, 0, -alpha]
    a = [1 + alpha, -2 * cw, 1 - alpha]
    b = [v / a[0] for v in b]
    a1, a2 = a[1] / a[0], a[2] / a[0]
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        xi = x[i]
        yi = b[0] * xi + b[1] * x1 + b[2] * x2 - a1 * y1 - a2 * y2
        y[i] = yi
        x2, x1 = x1, xi
        y2, y1 = y1, yi
    return y


def env(n, attack=0.005, release=0.1, dur=None):
    t = np.arange(n) / SR
    total = n / SR
    e = np.minimum(1, t / max(attack, 1e-4))
    e *= np.clip((total - t) / max(release, 1e-4), 0, 1)
    return e


def expdecay(n, tau):
    return np.exp(-np.arange(n) / SR / tau)


def engine(freq_curve, dur, grit=0.6):
    """Two-stroke engine: exhaust pulse per revolution, resonant muffler + chain whine."""
    n = int(SR * dur)
    f = np.asarray(freq_curve(np.arange(n) / SR))
    phase = np.cumsum(f) / SR
    frac = phase % 1.0
    pulse = np.exp(-frac * 9) * (1 + 0.25 * rng.standard_normal(n))
    saw = 2 * frac - 1
    body = 0.7 * pulse + 0.25 * saw
    body = biquad(body, "lp", 900) + 0.35 * biquad(body, "bp", 220, 2.0)
    whine = biquad(noise(dur), "bp", 3200, 3.0) * (0.3 + 0.7 * (f - f.min()) / max(f.max() - f.min(), 1)) * grit
    out = body + whine * 0.5
    return np.tanh(out * 2.2)


def pluck(freq, dur, damp=0.996):
    n = int(SR * dur)
    period = int(SR / freq)
    buf = rng.uniform(-1, 1, period)
    out = np.zeros(n)
    for i in range(n):
        v = buf[i % period]
        out[i] = v
        buf[i % period] = damp * 0.5 * (v + buf[(i + 1) % period])
    return out


def thump(freq, dur, tau=0.08, sweep=0.5):
    t = t_axis(dur)
    f = freq * (1 + sweep * np.exp(-t / 0.03))
    return np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-t / tau)


def ping(freqs, dur, tau=0.15):
    t = t_axis(dur)
    return sum(np.sin(2 * math.pi * f * t) * np.exp(-t / (tau / (1 + k * 0.4))) for k, f in enumerate(freqs)) / len(freqs)


def whoosh(dur, f0=400, f1=2500, q=1.2):
    x = noise(dur)
    n = len(x)
    seg = 256
    out = np.zeros(n)
    for s in range(0, n, seg):
        t = s / n
        f = f0 + (f1 - f0) * t
        out[s:s + seg] = biquad(x[s:s + seg], "bp", f, q)
    return out * np.sin(np.linspace(0, math.pi, n))


def wet(dur, cutoff=700, rate=18):
    x = biquad(noise(dur), "lp", cutoff)
    t = t_axis(dur)
    am = 0.5 + 0.5 * np.sin(2 * math.pi * rate * t + 3 * np.sin(2 * math.pi * 3.1 * t))
    return x * am


def flame_noise(dur, cutoff=1400):
    x = biquad(noise(dur), "lp", cutoff) + 0.4 * biquad(noise(dur), "bp", 180, 1.0)
    t = t_axis(dur)
    turb = 0.6 + 0.4 * np.abs(biquad(rng.standard_normal(len(t)), "lp", 12))
    turb /= max(turb.max(), 1e-6)
    return x * (0.5 + turb)


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out


def at(x, offset):
    return np.concatenate([np.zeros(int(SR * offset)), x])


def norm(x, peak=0.9):
    m = np.max(np.abs(x))
    return x / m * peak if m > 0 else x


def fade(x, fin=0.004, fout=0.03):
    n = len(x)
    e = np.ones(n)
    a = int(SR * fin)
    r = int(SR * fout)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return x * e


def save(name, x, peak=0.9):
    path = os.path.join(ASSETS, "sounds", *name.split(".")) + ".ogg"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sf.write(path, norm(fade(x), peak).astype(np.float32), SR, format="OGG", subtype="VORBIS")
    return name


def build():
    made = []
    # ---------------------------------------------------------------- chainsaw
    idle = engine(lambda t: 38 + 3 * np.sin(2 * math.pi * 2 * t), 1.0, grit=0.25)
    made.append(save("chainsaw.idle", idle, 0.6))
    made.append(save("chainsaw.rev", engine(lambda t: 40 + 115 * np.clip(t / 0.35, 0, 1) - 30 * np.clip((t - 0.9) / 0.3, 0, 1),
                                            1.2, grit=0.9)))
    start = mix(engine(lambda t: np.where(t < 0.5, 18 + 30 * t, 33 + 140 * np.clip((t - 0.5) / 0.35, 0, 1)
                                          - 60 * np.clip((t - 1.1) / 0.5, 0, 1)), 1.7, grit=0.8),
                at(thump(70, 0.3, 0.06) * 0.8, 0.0), at(thump(90, 0.25) * 0.6, 0.22))
    made.append(save("chainsaw.start", start))
    sput = np.zeros(int(SR * 0.9))
    for k, o in enumerate((0.0, 0.18, 0.31, 0.52)):
        pop = mix(thump(60 + k * 12, 0.18, 0.05), biquad(noise(0.12), "lp", 1200) * expdecay(int(SR * 0.12), 0.03))
        sput = mix(sput, at(pop * (1 - k * 0.2), o))
    made.append(save("chainsaw.sputter", sput))
    clicks = np.zeros(int(SR * 0.4))
    for k in range(14):
        o = 0.02 + 0.25 * (k / 14) ** 0.7
        c = biquad(noise(0.012), "hp", 2500) * expdecay(int(SR * 0.012), 0.003)
        clicks = mix(clicks, at(c, o))
    made.append(save("chainsaw.cord_pull", mix(clicks * 0.8, whoosh(0.4, 300, 1800) * 0.6, at(thump(55, 0.2) * 0.5, 0.25))))
    cut = mix(engine(lambda t: 150 + 10 * np.sin(2 * math.pi * 9 * t), 0.7, grit=1.4),
              wet(0.7, 900, 22) * 0.9, thump(50, 0.3, 0.1) * 0.8)
    made.append(save("chainsaw.cut", cut))
    rattle = np.zeros(int(SR * 0.55))
    for k in range(30):
        o = rng.uniform(0, 0.45)
        rattle = mix(rattle, at(ping([2300 + rng.uniform(-400, 400), 3900], 0.05, 0.02) * rng.uniform(0.3, 1), o))
    made.append(save("chainsaw.chain_throw", mix(rattle, whoosh(0.5, 500, 3000) * 0.5)))
    made.append(save("chainsaw.chain_hit", mix(ping([820, 1340, 2210, 3170], 0.6, 0.25), thump(80, 0.2, 0.05) * 0.8,
                                                biquad(noise(0.08), "hp", 1500) * expdecay(int(SR * 0.08), 0.02))))

    # ---------------------------------------------------------------- crossbow
    squelch = mix(wet(0.9, 600, 9) * np.linspace(0.4, 1, int(SR * 0.9)),
                  np.sin(2 * math.pi * np.cumsum(180 + 60 * np.sin(2 * math.pi * 7 * t_axis(0.9))) / SR) * 0.15,
                  at(biquad(noise(0.1), "lp", 2500) * expdecay(int(SR * 0.1), 0.02), 0.78))
    made.append(save("crossbow.arrow_pull", squelch))
    made.append(save("crossbow.fire", mix(pluck(98, 0.4, 0.994) * 0.9, thump(120, 0.15, 0.03), whoosh(0.35, 1500, 400) * 0.5)))
    creak = np.sin(2 * math.pi * np.cumsum(60 + 140 * t_axis(0.9) + 15 * np.sin(2 * math.pi * 23 * t_axis(0.9))) / SR)
    creak = np.sign(creak) * np.abs(creak) ** 0.3
    made.append(save("crossbow.charge", biquad(creak, "bp", 900, 1.5) * np.linspace(0.3, 1, len(creak)) +
                     0.2 * biquad(noise(0.9), "bp", 4000, 4)))
    pierce = mix(pluck(70, 0.9, 0.995), thump(45, 0.5, 0.15) * 1.2,
                 biquad(noise(0.05), "hp", 800) * expdecay(int(SR * 0.05), 0.01) * 1.5,
                 at(biquad(noise(0.6), "bp", 1200, 0.8) * expdecay(int(SR * 0.6), 0.2), 0.03))
    made.append(save("crossbow.pierce", pierce))
    made.append(save("crossbow.flash_step", mix(whoosh(0.4, 300, 4000, 1.5), at(ping([5200, 7100], 0.3, 0.08) * 0.4, 0.12))))

    # ---------------------------------------------------------------- flamethrower
    made.append(save("flamethrower.molar", mix(biquad(noise(0.03), "hp", 1800) * expdecay(int(SR * 0.03), 0.006),
                                               at(ping([1900, 2800], 0.1, 0.02) * 0.6, 0.005),
                                               at(biquad(noise(0.15), "lp", 900) * expdecay(int(SR * 0.15), 0.04) * 0.6, 0.02))))
    fl = flame_noise(1.2)
    tt = np.arange(len(fl)) / SR
    ign = mix(thump(40, 0.6, 0.2, 1.0) * 1.2, fl * np.minimum(tt / 0.05, 1) * np.exp(-np.maximum(tt - 0.05, 0) / 0.5))
    made.append(save("flamethrower.ignite", ign))
    made.append(save("flamethrower.stream", flame_noise(1.0, 1800), 0.75))
    made.append(save("flamethrower.burst", mix(thump(35, 0.9, 0.3, 1.5) * 1.3, flame_noise(1.2, 2200) *
                                               np.exp(-t_axis(1.2) / 0.45))))

    # ---------------------------------------------------------------- whip
    def crack(dur=0.35, tail=0.12):
        """Supersonic whip crack: a bipolar N-wave shock plus a hissing tail and a room slap."""
        n = int(SR * dur)
        x = np.zeros(n)
        w = int(SR * 0.0016)
        x[:w] = np.linspace(1, -1, w)
        hiss = biquad(noise(dur), "hp", 2200) * expdecay(n, tail * 0.25)
        slap = at(biquad(noise(0.08), "bp", 1400, 0.9) * expdecay(int(SR * 0.08), 0.02) * 0.35, 0.045)
        return mix(x * 1.4, hiss * 0.8, slap)

    snap = mix(biquad(noise(0.012), "hp", 2600) * expdecay(int(SR * 0.012), 0.002) * 1.4,
               biquad(noise(0.05), "bp", 1900, 3.0) * expdecay(int(SR * 0.05), 0.008),
               thump(180, 0.06, 0.012, 0.2) * 0.4)
    made.append(save("whip.snap", mix(snap, np.zeros(int(SR * 0.25)))))
    made.append(save("whip.crack", mix(whoosh(0.22, 500, 3500, 1.4) * 0.5, at(crack(0.45, 0.2), 0.2))))
    made.append(save("whip.lash", mix(whoosh(0.3, 300, 2600, 1.2) * 0.8, at(crack(0.2, 0.08) * 0.45, 0.24))))

    # ---------------------------------------------------------------- bomb
    def crackle(dur, rate, tau):
        n = int(SR * dur)
        x = np.zeros(n)
        for _ in range(int(rate * dur)):
            o = int(rng.uniform(0, 1) ** 1.6 * (n - 400))
            k = biquad(noise(0.004), "hp", 1500) * rng.uniform(0.3, 1.0)
            x[o:o + len(k)] += k
        return x * expdecay(n, tau)

    pin = mix(biquad(noise(0.07), "bp", 5200, 3.0) * np.linspace(0.3, 1, int(SR * 0.07)) * 0.6,
              at(ping([3180, 5120, 7340], 0.35, 0.09) * 0.9, 0.07), at(ping([2400, 4100], 0.2, 0.05) * 0.4, 0.2))
    made.append(save("bomb.pin", pin))
    made.append(save("bomb.fuse", mix(biquad(noise(0.9), "hp", 3000) * (0.5 + 0.5 * np.abs(np.sin(2 * math.pi * 7 *
                                                                                                       t_axis(0.9)))),
                                      crackle(0.9, 60, 5.0) * 0.8), 0.7))
    blast_ = mix(thump(48, 0.7, 0.22, 1.6) * 1.3, biquad(noise(0.9), "lp", 2600) * expdecay(int(SR * 0.9), 0.22),
                 crackle(0.9, 120, 0.35) * 0.7, biquad(noise(0.02), "hp", 1000) * 1.2)
    made.append(save("bomb.blast", np.tanh(blast_ * 1.6)))
    rumble = biquad(noise(2.4), "lp", 380) * expdecay(int(SR * 2.4), 0.9)
    roll = biquad(noise(2.4), "lp", 160) * (0.6 + 0.4 * np.sin(2 * math.pi * 1.7 * t_axis(2.4))) * expdecay(int(SR * 2.4), 1.4)
    big = mix(thump(32, 1.6, 0.5, 2.0) * 1.5, rumble * 1.4, roll * 1.2, crackle(2.4, 160, 0.7) * 0.8,
              biquad(noise(0.03), "hp", 700) * 1.6, at(biquad(noise(1.2), "bp", 900, 0.7) * expdecay(int(SR * 1.2), 0.3) * 0.5, 0.05))
    made.append(save("bomb.explosion", np.tanh(big * 1.8)))

    # ---------------------------------------------------------------- spear
    scrape = mix(*[at(biquad(noise(0.05), "bp", 900 + 2600 * (k / 16), 6.0) * 0.5, 0.2 + k * 0.03) for k in range(16)])
    made.append(save("spear.pull", mix(wet(0.9, 900, 11) * np.exp(-t_axis(0.9) / 0.5) * 0.8, scrape,
                                       at(ping([1800, 2900, 4300], 0.4, 0.1) * 0.5, 0.68))))
    made.append(save("spear.throw", mix(whoosh(0.32, 2200, 350, 1.6), thump(95, 0.12, 0.03) * 0.5)))
    made.append(save("spear.impact", mix(thump(85, 0.35, 0.07, 0.8) * 1.2, wet(0.3, 1400, 26) * np.exp(-t_axis(0.3) / 0.09),
                                         ping([1250, 2600, 3900], 0.45, 0.12) * 0.45)))
    shing = np.sin(2 * math.pi * np.cumsum(1800 + 1600 * t_axis(0.5)) / SR) * np.exp(-t_axis(0.5) / 0.18)
    made.append(save("spear.erupt", mix(biquad(noise(0.5), "lp", 700) * np.exp(-t_axis(0.5) / 0.12) * 1.2,
                                        thump(60, 0.3, 0.07) * 0.9, at(shing * 0.45, 0.03),
                                        crackle(0.5, 80, 0.15) * 0.6)))

    # ---------------------------------------------------------------- katana / longsword
    def shing(dur, f0, f1, tau):
        t = t_axis(dur)
        f = f0 + (f1 - f0) * np.clip(t / dur, 0, 1)
        return sum(np.sin(2 * math.pi * np.cumsum(f * k) / SR) / k for k in (1, 2.76, 5.4)) * np.exp(-t / tau)

    scrape_ = biquad(noise(0.35), "bp", 4200, 3.0) * np.linspace(1, 0.2, int(SR * 0.35))
    made.append(save("katana.draw", mix(scrape_ * 0.7, at(shing(0.9, 2400, 3000, 0.35) * 0.6, 0.18))))
    made.append(save("katana.slash", mix(whoosh(0.25, 800, 5000, 1.6), at(biquad(noise(0.12), "hp", 3000) *
                                                                            expdecay(int(SR * 0.12), 0.03) * 0.7, 0.18),
                                        at(wet(0.25, 1600, 30) * np.exp(-t_axis(0.25) / 0.07) * 0.5, 0.2))))
    made.append(save("katana.iai", mix(whoosh(0.18, 3000, 600, 2.0) * 0.9, at(shing(1.2, 3200, 2600, 0.5) * 0.8, 0.12),
                                      at(thump(80, 0.2, 0.04) * 0.5, 0.12))))
    made.append(save("katana.sheathe", mix(biquad(noise(0.5), "bp", 2600, 2.5) * np.linspace(0.3, 1, int(SR * 0.5)) * 0.6,
                                          at(ping([1700, 3300], 0.25, 0.05) * 0.8, 0.48))))
    made.append(save("longsword.draw", mix(biquad(noise(0.45), "bp", 3000, 2.5) * np.linspace(1, 0.2, int(SR * 0.45)) * 0.7,
                                          at(shing(1.0, 1500, 1800, 0.45) * 0.6, 0.2))))
    made.append(save("longsword.clang", mix(ping([820, 1650, 2470, 3900], 0.9, 0.35), thump(120, 0.2, 0.04) * 0.6,
                                           biquad(noise(0.05), "hp", 2000) * expdecay(int(SR * 0.05), 0.01))))
    made.append(save("longsword.cleave", mix(whoosh(0.3, 500, 2600, 1.2), at(thump(55, 0.5, 0.12, 1.0), 0.22),
                                            at(ping([600, 1320, 2100], 0.6, 0.2) * 0.4, 0.22))))

    # ---------------------------------------------------------------- blood / shark / violence
    made.append(save("blood.form", mix(wet(0.6, 900, 16) * np.exp(-t_axis(0.6) / 0.3),
                                      biquad(noise(0.6), "lp", 400) * np.linspace(0.2, 1, int(SR * 0.6)) * 0.5)))
    made.append(save("blood.slam", mix(thump(40, 0.8, 0.25, 1.4) * 1.3, wet(0.6, 1200, 24) * np.exp(-t_axis(0.6) / 0.15),
                                      biquad(noise(0.05), "hp", 800))))
    drops = np.zeros(int(SR * 1.6))
    for k in range(40):
        o = rng.uniform(0, 1.4)
        drops = mix(drops, at(thump(rng.uniform(300, 700), 0.08, 0.02, 0.8) * rng.uniform(0.3, 0.8), o))
    made.append(save("blood.rain", mix(drops, wet(1.6, 700, 8) * 0.4)))
    made.append(save("shark.dive", mix(biquad(noise(0.9), "lp", 600) * np.exp(-t_axis(0.9) / 0.35) * 1.2,
                                      thump(50, 0.4, 0.12) * 0.8, crackle(0.9, 70, 0.4) * 0.5)))
    chomp = mix(thump(110, 0.15, 0.03, 1.2), biquad(noise(0.06), "bp", 2500, 2) * expdecay(int(SR * 0.06), 0.015) * 1.2,
                at(wet(0.25, 1200, 26) * 0.5, 0.03))
    made.append(save("shark.bite", mix(whoosh(0.12, 500, 1500) * 0.4, at(chomp, 0.08))))
    hiss = biquad(noise(0.7), "hp", 3500) * np.exp(-t_axis(0.7) / 0.3)
    made.append(save("violence.mask", mix(at(ping([900, 1400], 0.2, 0.04) * 0.6, 0.0), at(hiss * 0.8, 0.05))))
    made.append(save("violence.punch", mix(thump(60, 0.5, 0.12, 1.2) * 1.4, biquad(noise(0.08), "lp", 1800) *
                                          expdecay(int(SR * 0.08), 0.02) * 1.2, whoosh(0.12, 400, 1200) * 0.3)))

    # ---------------------------------------------------------------- cosmos / gun / fiend
    tt = t_axis(1.6)
    chime = sum(np.sin(2 * math.pi * f * tt + 2 * np.sin(2 * math.pi * 3 * tt)) * np.exp(-tt / 0.8) / (k + 1)
                for k, f in enumerate((523, 659, 784, 1046, 1318)))
    whisper = biquad(noise(1.6), "bp", 1800, 4.0) * (0.5 + 0.5 * np.sin(2 * math.pi * 2.5 * tt)) * np.exp(-tt / 0.9)
    made.append(save("cosmos.halloween", mix(chime * 0.6, whisper * 0.6, np.flip(chime) * 0.25)))
    t2 = t_axis(2.2)
    drone = sum(np.sin(2 * math.pi * f * t2 * (1 + 0.004 * np.sin(2 * math.pi * 0.3 * t2))) for f in (55, 82.5, 110, 165))
    made.append(save("cosmos.void", drone * np.sin(np.linspace(0, math.pi, len(t2))) * 0.5 +
                     biquad(noise(2.2), "lp", 300) * 0.3))
    shot = mix(biquad(noise(0.02), "hp", 1500) * 1.5, thump(140, 0.18, 0.03, 1.5), biquad(noise(0.3), "lp", 2500) *
               expdecay(int(SR * 0.3), 0.06) * 0.8)
    made.append(save("gun.shot", np.tanh(shot * 2.0)))
    cannon = mix(thump(45, 1.0, 0.3, 2.0) * 1.5, biquad(noise(1.0), "lp", 1200) * expdecay(int(SR * 1.0), 0.25),
                 biquad(noise(0.03), "hp", 900) * 2.0, crackle(1.0, 40, 0.3) * 0.5)
    made.append(save("gun.cannon", np.tanh(cannon * 1.8)))
    made.append(save("gun.cock", mix(ping([2600, 4100], 0.08, 0.015) * 0.9, at(ping([1900, 3300], 0.1, 0.02), 0.12),
                                    at(biquad(noise(0.04), "bp", 3000, 2) * 0.6, 0.1))))
    beat_slow = mix(thump(48, 0.3, 0.08, 0.3), at(thump(54, 0.3, 0.07, 0.3) * 0.7, 0.28),
                    at(thump(44, 0.3, 0.1, 0.3) * 0.5, 0.9))
    made.append(save("fiend.possess", mix(beat_slow, at(wet(1.2, 500, 5) * np.exp(-t_axis(1.2) / 0.6) * 0.6, 0.2),
                                         at(biquad(noise(1.4), "lp", 180) * np.linspace(0, 1, int(SR * 1.4)) * 0.8, 0.6))))

    # ---------------------------------------------------------------- heart / blood / form
    rip = mix(wet(0.8, 1300, 30) * np.exp(-t_axis(0.8) / 0.35), thump(70, 0.3, 0.07),
              at(biquad(noise(0.25), "bp", 2400, 2) * np.exp(-t_axis(0.25) / 0.08), 0.05))
    made.append(save("heart.rip", rip))
    beat = mix(thump(52, 0.25, 0.07, 0.3), at(thump(60, 0.25, 0.06, 0.3) * 0.8, 0.22))
    made.append(save("heart.beat", mix(beat, np.zeros(int(SR * 0.9)))))
    gulp = mix(thump(140, 0.15, 0.05, 1.5), at(thump(120, 0.15, 0.05, 1.5), 0.35), wet(0.8, 500, 6) * 0.3)
    made.append(save("blood.drink", gulp))
    made.append(save("hybrid.transform", mix(whoosh(1.0, 200, 3000) * 0.7, thump(38, 1.0, 0.3, 1.2),
                                             at(ping([660, 990, 1320], 0.8, 0.3) * 0.25, 0.2))))
    made.append(save("hybrid.revert", mix(whoosh(0.6, 3000, 200) * 0.8, wet(0.6, 800, 14) * 0.5)))

    # ---------------------------------------------------------------- full devils
    # Makima: the finger-gun "bang" is a dry flick followed by a pressure wave; the crush folds a body up wetly
    made.append(save("control.bang", mix(biquad(noise(0.012), "hp", 3000) * 1.4,
                                        at(thump(38, 0.9, 0.3, 2.5) * 1.3, 0.02),
                                        at(biquad(noise(0.7), "lp", 220) * expdecay(int(SR * 0.7), 0.25), 0.02))))
    crush = mix(thump(60, 0.6, 0.12, 1.8) * 1.2, wet(0.7, 1500, 34) * np.exp(-t_axis(0.7) / 0.22),
                crackle(0.7, 120, 0.25) * 0.9, at(biquad(noise(0.2), "bp", 900, 1.5) * expdecay(int(SR * 0.2), 0.05), 0.02))
    made.append(save("control.crush", np.tanh(crush * 1.5)))
    rattle = np.zeros(int(SR * 1.1))
    for k in range(34):
        o = rng.uniform(0, 0.9) ** 1.3
        f = rng.uniform(1800, 4200)
        rattle = mix(rattle, at(ping([f, f * 1.47, f * 2.2], 0.12, 0.03) * rng.uniform(0.25, 0.7), o))
    made.append(save("control.chain", mix(rattle, whoosh(0.4, 300, 1800) * 0.4,
                                         at(thump(90, 0.3, 0.06, 0.5) * 0.7, 0.3))))
    t3 = t_axis(2.0)
    hum = sum(np.sin(2 * math.pi * f * t3) / (k + 1) for k, f in enumerate((73.4, 110, 146.8, 220)))
    swell = np.sin(np.linspace(0, math.pi, len(t3))) ** 1.5
    whisper2 = biquad(noise(2.0), "bp", 1400, 5.0) * (0.5 + 0.5 * np.sin(2 * math.pi * 4 * t3))
    made.append(save("control.dominate", (hum * 0.6 + whisper2 * 0.5) * swell))

    # generic devil voices (pitched per devil in code)
    def roar(dur, f0, f1, grit):
        tt = t_axis(dur)
        f = np.linspace(f0, f1, len(tt)) * (1 + 0.03 * np.sin(2 * math.pi * 7 * tt))
        ph = 2 * math.pi * np.cumsum(f) / SR
        voice = np.sign(np.sin(ph)) * 0.3 + np.sin(ph) * 0.5 + np.sin(2 * ph) * 0.3 + np.sin(3.01 * ph) * 0.2
        body = biquad(voice, "lp", 1400) + biquad(noise(dur), "bp", 700, 0.8) * grit
        envl = np.minimum(1, tt / 0.08) * np.exp(-np.maximum(0, tt - dur * 0.5) / (dur * 0.25))
        return np.tanh(body * envl * 1.6)
    made.append(save("devil.roar", roar(1.4, 120, 70, 0.8)))
    made.append(save("devil.growl", roar(0.8, 70, 60, 1.2) * 0.9))
    made.append(save("devil.screech", mix(roar(0.7, 900, 1500, 0.4), biquad(noise(0.7), "hp", 4000) *
                                         np.exp(-t_axis(0.7) / 0.3) * 0.5)))
    made.append(save("devil.death", mix(roar(1.6, 140, 45, 0.9), at(wet(1.0, 800, 10) * 0.5, 0.5))))
    flap = np.zeros(int(SR * 0.5))
    for o in (0.0, 0.24):
        flap = mix(flap, at(biquad(noise(0.16), "lp", 700) * np.sin(np.linspace(0, math.pi, int(SR * 0.16))) * 1.2, o))
    made.append(save("devil.flap", flap))
    made.append(save("devil.bite", mix(whoosh(0.1, 400, 1200) * 0.4, at(thump(90, 0.2, 0.04, 1.2), 0.07),
                                      at(biquad(noise(0.08), "bp", 2200, 2) * expdecay(int(SR * 0.08), 0.02), 0.07),
                                      at(wet(0.4, 1000, 22) * 0.6, 0.1))))
    made.append(save("devil.slam", np.tanh(mix(thump(35, 1.1, 0.35, 1.6) * 1.6, crackle(1.0, 60, 0.3),
                                                biquad(noise(0.9), "lp", 500) * expdecay(int(SR * 0.9), 0.3)) * 1.4)))
    made.append(save("devil.gust", mix(whoosh(1.2, 150, 900, 0.8) * 1.2, biquad(noise(1.2), "lp", 300) *
                                      np.sin(np.linspace(0, math.pi, int(SR * 1.2))) * 0.8)))
    return made


def sounds_json(names):
    data = {}
    subtitles = {
        "chainsaw.idle": "Chainsaw idles", "chainsaw.rev": "Chainsaw revs", "chainsaw.start": "Chainsaw roars to life",
        "chainsaw.sputter": "Engine sputters", "chainsaw.cord_pull": "Starter cord yanked", "chainsaw.cut": "Chainsaw rips flesh",
        "chainsaw.chain_throw": "Chain lashes out", "chainsaw.chain_hit": "Chain clanks",
        "crossbow.arrow_pull": "Arrow drawn from eye", "crossbow.fire": "Crossbow fires", "crossbow.charge": "Crossbow strains",
        "crossbow.pierce": "Bolt tears through", "crossbow.flash_step": "Blur of motion",
        "flamethrower.molar": "Molar crunches", "flamethrower.ignite": "Flames erupt", "flamethrower.stream": "Flamethrower roars",
        "flamethrower.burst": "Inferno bursts", "heart.rip": "Heart torn out", "heart.beat": "Heart beats",
        "blood.drink": "Blood gulped", "hybrid.transform": "Devil bursts out", "hybrid.revert": "Devil retreats",
        "whip.snap": "Fingers snap", "whip.crack": "Whip cracks", "whip.lash": "Whip lashes",
        "bomb.pin": "Grenade pin pulled", "bomb.blast": "Explosion", "bomb.explosion": "Massive explosion",
        "bomb.fuse": "Fuse sizzles", "spear.pull": "Spear drawn from flesh", "spear.throw": "Spear hurled",
        "spear.impact": "Spear strikes", "spear.erupt": "Spears burst from the ground",
        "katana.draw": "Blade drawn", "katana.slash": "Katana slashes", "katana.iai": "Quick-draw strike",
        "katana.sheathe": "Blade sheathed", "longsword.draw": "Longsword drawn", "longsword.clang": "Swords clash",
        "longsword.cleave": "Longsword cleaves", "blood.form": "Blood takes shape", "blood.slam": "Blood hammer slams",
        "blood.rain": "Blood rains down", "shark.dive": "Something dives into the ground", "shark.bite": "Shark bites",
        "violence.mask": "Gas mask hisses", "violence.punch": "Brutal punch", "cosmos.halloween": "Halloween...",
        "cosmos.void": "The cosmos hums", "gun.shot": "Gunshot", "gun.cannon": "Deafening gunshot",
        "gun.cock": "Gun cocked", "fiend.possess": "A devil takes a body",
        "control.bang": "\"Bang.\"", "control.crush": "Something is crushed", "control.chain": "Chains rattle",
        "control.dominate": "An overwhelming presence", "devil.roar": "Devil roars", "devil.growl": "Devil growls",
        "devil.screech": "Devil screeches", "devil.death": "Devil dies", "devil.flap": "Wings beat",
        "devil.bite": "Devil bites", "devil.slam": "Ground shakes", "devil.gust": "Wind howls",
    }
    for n in names:
        data[n] = {"subtitle": "subtitles.csm." + n, "sounds": [{"name": "csm:" + n.replace(".", "/"),
                                                                    "stream": n == "chainsaw.idle"}]}
    with open(os.path.join(ASSETS, "sounds.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return subtitles


if __name__ == "__main__":
    names = build()
    subs = sounds_json(names)
    with open(os.path.join(HERE, "subtitles.json"), "w", encoding="utf-8") as f:
        json.dump({"subtitles.csm." + k: v for k, v in subs.items()}, f, indent=2)
    print("sounds:", len(names))
