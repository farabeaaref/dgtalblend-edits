"""Synthesize the FRAME · THE GRIND sound-design pack (no licensing issues).
Run:  python 06_edit/scripts/make_sfx.py   -> writes 03_sfx/individual/*.wav (48 kHz, 24-bit, stereo)
"""
import pathlib
import numpy as np
import scipy.signal as sg
import soundfile as sf

SR = 48000
rng = np.random.default_rng(7)
OUT = pathlib.Path(__file__).resolve().parents[2] / '03_sfx' / 'individual'
OUT.mkdir(parents=True, exist_ok=True)


def t(d): return np.arange(int(d * SR)) / SR
def env(n, a, d, c=4):
    x = np.linspace(0, 1, n)
    return np.minimum(1, x / max(a, 1e-4)) * np.exp(-c * np.maximum(0, x - a) / max(d, 1e-4))
def bp(x, lo, hi, o=4): return sg.sosfilt(sg.butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, o=4): return sg.sosfilt(sg.butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=4): return sg.sosfilt(sg.butter(o, f, 'high', fs=SR, output='sos'), x)


def sweep_noise(d, f0, f1, q=0.35):
    n = int(d * SR); x = rng.standard_normal(n); out = np.zeros(n); blk = 512
    for i, fr in enumerate(np.geomspace(f0, f1, n // blk + 1)):
        s = i * blk; e = min(n, s + blk)
        if s >= n: break
        out[s:e] = bp(x[max(0, s - 2048):e], max(30, fr * (1 - q)), min(SR / 2 - 100, fr * (1 + q)), 2)[-(e - s):]
    return out


def rev(x, decay=0.6, mix=0.25):
    ir = lp(rng.standard_normal(int(decay * SR)) * np.exp(-6 * t(decay) / decay), 6000)
    w = sg.fftconvolve(x, ir); w /= np.max(np.abs(w)) + 1e-9
    return (1 - mix) * np.pad(x, (0, len(ir) - 1)) + mix * w * np.max(np.abs(x))


def pan(x, l=1.0, r=1.0): return np.stack([x * l, x * r], 1)


def save(name, x, peak=0.89, width=0.0004):
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    if x.ndim == 1:
        d = int(width * SR); x = np.stack([x, np.pad(x, (d, 0))[:len(x)] if d else x], 1)
    fd = int(0.004 * SR); x[-fd:] *= np.linspace(1, 0, fd)[:, None]
    sf.write(str(OUT / f'{name}.wav'), x.astype(np.float32), SR, subtype='PCM_24')
    print('wrote', name, f'{len(x) / SR:.2f}s')


# wind bed (30 s, gusting)
d = 30.0; n = int(d * SR)
gust = 0.55 + 0.45 * lp(rng.standard_normal(n), 0.4, 2) / 0.02
gust = np.clip(gust / np.max(np.abs(gust)), 0.15, 1)
wind = bp(rng.standard_normal(n), 120, 900, 2) * gust + 0.3 * bp(rng.standard_normal(n), 1500, 4000, 2) * gust
save('wind_bed', wind, peak=0.5, width=0.003)

# dark drone bed (6 s, loopable-ish)
x = t(6.0)
drone = 0.6 * np.sin(2 * np.pi * 41.2 * x) + 0.35 * np.sin(2 * np.pi * 61.7 * x + 0.3) + 0.2 * np.sin(2 * np.pi * 82.4 * x)
drone *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.25 * x)
drone += 0.15 * bp(rng.standard_normal(len(x)), 200, 600, 2)
drone = np.tanh(1.5 * drone) * env(len(x), 0.25, 0.9, 0.5)
save('drone_bed', drone, peak=0.6)

# riser into the silence (1.2 s, ends hard)
d = 1.2; x = t(d)
r = sweep_noise(d, 300, 11000) * np.linspace(0.05, 1, len(x)) ** 2
r += 0.3 * np.sin(2 * np.pi * np.cumsum(np.geomspace(200, 2400, len(x))) / SR) * np.linspace(0, 1, len(x)) ** 3
save('riser_to_drop', r)

# drop impact (sub sweep + crack + body)
d = 2.2; x = t(d)
sub = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 36, len(x))) / SR) * env(len(x), 0.002, 0.5, 3)
crack = hp(rng.standard_normal(len(x)), 2500) * env(len(x), 0.0005, 0.02, 8)
body = bp(rng.standard_normal(len(x)), 80, 400) * env(len(x), 0.001, 0.12, 6)
imp = np.tanh(2.2 * (sub + 0.5 * crack + 0.8 * body))
save('drop_impact', rev(imp, 1.2, 0.2))

# whoosh for the pole wipe (0.6 s, L -> R)
d = 0.6; x = t(d)
w = sweep_noise(d, 400, 4500, 0.5) * np.sin(np.pi * np.linspace(0, 1, len(x))) ** 1.5
p = np.linspace(0, 1, len(x))
save('whoosh_wipe', np.stack([w * np.cos(p * np.pi / 2), w * np.sin(p * np.pi / 2)], 1))

# roll swish (0.5 s, rotating stereo)
d = 0.5; x = t(d)
s = sweep_noise(d, 2400, 300, 0.4) * np.sin(np.pi * np.linspace(0, 1, len(x)))
rot = np.sin(2 * np.pi * 3 * x)
save('roll_swish', np.stack([s * (0.5 + 0.5 * rot), s * (0.5 - 0.5 * rot)], 1))

# clone glitch blip (3 frames = 0.12 s)
d = 0.12; x = t(d)
sq = np.sign(np.sin(2 * np.pi * 180 * x)) * env(len(x), 0.002, 0.08, 3)
crush = np.round(sq * 6) / 6 + 0.4 * hp(rng.standard_normal(len(x)), 3000) * env(len(x), 0.001, 0.05, 5)
save('clone_glitch', crush, peak=0.7)

# white-flash hit (bright impact + shimmer tail)
d = 1.6; x = t(d)
hit = np.sin(2 * np.pi * np.cumsum(np.geomspace(90, 45, len(x))) / SR) * env(len(x), 0.002, 0.3, 4)
shim = bp(rng.standard_normal(len(x)), 5000, 14000, 2) * env(len(x), 0.005, 0.9, 3)
save('flash_hit', rev(np.tanh(1.8 * hit) + 0.5 * shim, 1.4, 0.35))
