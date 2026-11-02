"""Beat-map the song and snap the timeline to its kicks.
Run:  python 06_edit/scripts/beatmap.py 02_music/<song file> [section_start_seconds]
Writes 06_edit/work/beatgrid.json and 06_edit/work/timeline_snapped.json.
- Finds BPM, beats and low-band (<120 Hz) kick onsets.
- If no section start is given, it picks the first strong breakdown -> drop so the drop lands near 5.6 s in edit time.
- Snaps every shot in/out to the nearest kick (in edit time), keeps the drop/flash anchors.
"""
import json, sys, pathlib
import numpy as np
import librosa

ROOT = pathlib.Path(__file__).resolve().parents[2]
song = pathlib.Path(sys.argv[1])
y, sr = librosa.load(str(song), sr=22050, mono=True)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
S = np.abs(librosa.stft(y, hop_length=512)); f = librosa.fft_frequencies(sr=sr)
low = S[f < 120].mean(0); tl = librosa.times_like(low, sr=sr, hop_length=512)
on = librosa.onset.onset_detect(onset_envelope=np.maximum(0, np.diff(low, prepend=0)), sr=sr, hop_length=512, units='time')

if len(sys.argv) > 2:
    start = float(sys.argv[2])
else:
    # drop = largest jump in 1-bar low energy after a quiet bar
    bar = 4 * 60 / float(np.atleast_1d(tempo)[0])
    e = np.array([low[(tl >= b) & (tl < b + bar)].mean() for b in np.arange(0, tl[-1] - bar, bar / 4)])
    jump = np.argmax(np.diff(e)) + 1
    drop_song = jump * bar / 4
    drop_song = min(on, key=lambda o: abs(o - drop_song)) if len(on) else drop_song
    start = max(0.0, drop_song - 5.6)

kicks = [round(o - start, 3) for o in on if 0 <= o - start <= 30.5]
grid = {"song": song.name, "bpm": float(np.atleast_1d(tempo)[0]), "section_start": start, "kicks_edit_time": kicks}
(ROOT / '06_edit/work').mkdir(parents=True, exist_ok=True)
(ROOT / '06_edit/work/beatgrid.json').write_text(json.dumps(grid, indent=2))

tlj = json.loads((ROOT / '06_edit/timeline.json').read_text())
# snap each cut boundary, in order, to the nearest kick that keeps every shot >= 0.4 s long
prev = 0.0
for s in tlj['shots'][1:]:
    cands = [k for k in kicks if k >= prev + 0.4 and k <= 29.0]
    if cands:
        k = min(cands, key=lambda c: abs(c - s['in']))
        if abs(k - s['in']) <= 0.6: s['in'] = k  # never move a cut more than 0.6 s
    s['in'] = max(s['in'], prev + 0.4); prev = s['in']
for a, b in zip(tlj['shots'], tlj['shots'][1:]): a['out'] = b['in']
tlj['shots'][-1]['out'] = 30.0
tlj['beat'].update({"drop": tlj['shots'][1]['in'], "flash": tlj['shots'][12]['in'], "section_start": start, "bpm": grid['bpm']})
(ROOT / '06_edit/work/timeline_snapped.json').write_text(json.dumps(tlj, indent=2, ensure_ascii=False))
print(f"BPM {grid['bpm']:.1f} | section starts {start:.2f}s in song | drop @ {tlj['beat']['drop']}s | {len(kicks)} kicks")
