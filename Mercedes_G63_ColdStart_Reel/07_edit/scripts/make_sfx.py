"""Synthesize the G 63 COLD START sound-design pack (no licensing issues).
Run:  python 07_edit/scripts/make_sfx.py   -> writes 03_sfx/individual/*.wav (48 kHz, 24-bit, stereo)
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


def save(name, x, peak=0.89, width=0.0004):
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    if x.ndim == 1:
        d = int(width * SR); x = np.stack([x, np.pad(x, (d, 0))[:len(x)] if d else x], 1)
    fd = int(0.004 * SR); x[-fd:] *= np.linspace(1, 0, fd)[:, None]
    sf.write(str(OUT / f'{name}.wav'), x.astype(np.float32), SR, subtype='PCM_24')
    print('wrote', name, f'{len(x) / SR:.2f}s')


# ambience bed (17.2 s: distant wind + low lot hum)
d = 17.2; n = int(d * SR)
gust = lp(rng.standard_normal(n), 0.4, 2); gust = np.clip(0.55 + 0.45 * gust / (np.max(np.abs(gust)) + 1e-9), 0.15, 1)
amb = bp(rng.standard_normal(n), 100, 800, 2) * gust + 0.12 * np.sin(2 * np.pi * 55 * t(d))
save('ambience_bed', amb, peak=0.5, width=0.003)

# flame pop (exhaust crack + whoomph + sparks)
d = 1.6; x = t(d)
crack = hp(rng.standard_normal(len(x)), 1800) * env(len(x), 0.0004, 0.03, 8)
whoomph = bp(rng.standard_normal(len(x)), 60, 600) * env(len(x), 0.004, 0.35, 4)
thump = np.sin(2 * np.pi * np.cumsum(np.geomspace(95, 38, len(x))) / SR) * env(len(x), 0.002, 0.25, 4)
sparks = hp(rng.standard_normal(len(x)), 5000) * env(len(x), 0.02, 0.5, 5) * (rng.random(len(x)) > 0.985)
save('flame_pop', rev(np.tanh(2.0 * (0.9 * thump + 0.7 * whoomph + 0.6 * crack)) + 0.6 * sparks, 0.8, 0.2))

# star shimmer (rising band noise + bell arpeggio, 0.9 s)
d = 0.9; x = t(d)
sh = sweep_noise(d, 2000, 12000, 0.3) * np.linspace(0.1, 1, len(x)) ** 2
bells = sum(np.sin(2 * np.pi * f * x) * env(len(x), 0.002 + i * 0.08 / d, 0.25, 6) for i, f in enumerate([1318, 1760, 2093, 2637]))
save('star_shimmer', 0.6 * sh + 0.25 * bells, peak=0.7)

# riser to drop (2.0 s, ends hard)
d = 2.0; x = t(d)
r = sweep_noise(d, 300, 11000) * np.linspace(0.05, 1, len(x)) ** 2
r += 0.3 * np.sin(2 * np.pi * np.cumsum(np.geomspace(180, 2200, len(x))) / SR) * np.linspace(0, 1, len(x)) ** 3
save('riser_to_drop', r)

# drop impact
d = 2.2; x = t(d)
sub = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 36, len(x))) / SR) * env(len(x), 0.002, 0.5, 3)
crack = hp(rng.standard_normal(len(x)), 2500) * env(len(x), 0.0005, 0.02, 8)
body = bp(rng.standard_normal(len(x)), 80, 400) * env(len(x), 0.001, 0.12, 6)
save('drop_impact', rev(np.tanh(2.2 * (sub + 0.5 * crack + 0.8 * body)), 1.2, 0.2))

# grille pass ticks (9 rising band clicks over 0.9 s)
d = 1.0; x = np.zeros(int(d * SR))
for i in range(9):
    s = int((0.02 + i * 0.1) * SR); c = bp(rng.standard_normal(int(0.03 * SR)), 1500 + i * 400, 3500 + i * 600, 2) * env(int(0.03 * SR), 0.001, 0.02, 6)
    x[s:s + len(c)] += c
save('grille_pass_ticks', x, peak=0.6)

# hub hit (thud + metallic ring)
d = 1.0; x = t(d)
thud = np.sin(2 * np.pi * np.cumsum(np.geomspace(160, 60, len(x))) / SR) * env(len(x), 0.001, 0.2, 5)
ring = (np.sin(2 * np.pi * 2200 * x) + 0.5 * np.sin(2 * np.pi * 3300 * x)) * env(len(x), 0.001, 0.4, 6)
save('hub_hit', np.tanh(1.5 * (thud + 0.25 * ring)), peak=0.8)

# whoosh fast (0.32 s, L -> R)
d = 0.32; x = t(d); w = sweep_noise(d, 500, 5000, 0.5) * np.sin(np.pi * np.linspace(0, 1, len(x))) ** 1.3
p = np.linspace(0, 1, len(x)); save('whoosh_fast', np.stack([w * np.cos(p * np.pi / 2), w * np.sin(p * np.pi / 2)], 1))

# roll swish (0.5 s, rotating stereo)
d = 0.5; x = t(d); s = sweep_noise(d, 2400, 300, 0.4) * np.sin(np.pi * np.linspace(0, 1, len(x)))
rot = np.sin(2 * np.pi * 3 * x); save('roll_swish', np.stack([s * (0.5 + 0.5 * rot), s * (0.5 - 0.5 * rot)], 1))

# hero drone (low V8 idle feel, 1.6 s)
d = 1.6; x = t(d)
dr = 0.6 * np.sin(2 * np.pi * 55 * x) + 0.4 * np.sin(2 * np.pi * 82.5 * x) + 0.2 * np.sin(2 * np.pi * 110 * x)
dr *= 0.85 + 0.15 * np.sin(2 * np.pi * 14 * x)
save('hero_drone', np.tanh(1.4 * dr) * env(len(x), 0.15, 1.4, 0.4), peak=0.6)

# car pass whoosh (0.9 s, R -> L, doppler-ish)
d = 0.9; x = t(d)
c = sweep_noise(d, 200, 2500, 0.6) * np.sin(np.pi * np.linspace(0, 1, len(x))) ** 1.2
c += 0.5 * np.sin(2 * np.pi * np.cumsum(np.geomspace(160, 80, len(x))) / SR) * np.sin(np.pi * np.linspace(0, 1, len(x)))
p = np.linspace(1, 0, len(x)); save('car_pass_whoosh', np.stack([c * np.cos(p * np.pi / 2), c * np.sin(p * np.pi / 2)], 1))

# flash hit (loop whiteout, 1.6 s)
d = 1.6; x = t(d)
hit = np.sin(2 * np.pi * np.cumsum(np.geomspace(90, 45, len(x))) / SR) * env(len(x), 0.002, 0.3, 4)
shim = bp(rng.standard_normal(len(x)), 5000, 14000, 2) * env(len(x), 0.005, 0.9, 3)
save('flash_hit', rev(np.tanh(1.8 * hit) + 0.5 * shim, 1.4, 0.35))
