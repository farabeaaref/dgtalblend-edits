# CLAUDE.md — Mercedes-AMG G 63 · COLD START (edit brief)

You are editing a 17.2 s vertical Reel for Farabe Aaref (DgtalBlend). All shots are AI-generated clips from Google Flow, one folder per shot in `05_flow_generations/`. Build the finished edit from them following this brief and `07_edit/timeline.json` exactly. Work with ffmpeg + Python (OpenCV, numpy, Pillow, librosa, soundfile). Intermediates in `07_edit/work/`, finals in `08_exports/`.

## Spec
- 1080×1920, 30 fps, 17.2 s, H.264 high, yuv420p, CRF 16, AAC 320 kbps 48 kHz stereo, `-movflags +faststart`.
- Flow clips are 8 s each and may be 720p/1080p or 24 fps: conform (scale/crop with Lanczos, retime to 30 fps with frame blending only if needed).

## Style rules (Farabe's, non-negotiable)
- The hook is the most tension-filled moment: the flame pop opens the video (0.2 s) and echoes once at 6.9 s.
- On-screen hook text in the first 2 s: bold, short: `Wait for the pop.`
- Every cut lands on a kick. Keep the reference's transitions only (Pass through, Shape, Whip, Roll, Wipe, whiteout loop). No stock presets, no extra text, no emoji, no dealer names or plates.
- Premium and restrained. 17.2 s total (limit 30–40 s).

## Reference
G63 "Rate this edit 1–10" reel (17.2 s). Contact sheets: `01_reference/contact_sheet_*.jpg`. Skeleton kept: soft build → silence dip → drop on the grille → shape-chained montage (star, grille, hub, ring) → interior rolls → long still hero hold → second car passes → loop.

## Shots, timing, transitions
| Shot | In–Out (s) | Role | Out transition |
|---|---|---|---|
| S01 | 0.0–0.6 | Flame pop (hook) | hard cut |
| S02 | 0.6–2.2 | Wide push-in + badge fly-in (edit) | **Pass through** (6 f) |
| S03 | 2.2–4.3 | Drop, grille macro → star | **Shape** (star → hub) |
| S04 | 4.3–5.4 | Wheel cap → wheel | Whip right |
| S05 | 5.4–6.8 | Fender whip | Whip right |
| S06 | 6.8–7.7 | Rear tilt + flame echo | **Roll** clockwise 90° |
| S07 | 7.7–8.9 | Headlight ring | Shape match |
| S08 | 8.9–9.8 | Wheel spin | Roll |
| S09 | 9.8–11.0 | Steering wheel | Roll |
| S10 | 11.0–12.5 | Dash, AMG badge, seat | Whip right |
| S11 | 12.5–13.4 | Cabin wide | hard cut |
| S12 | 13.4–15.0 | **Hero hold** (longest still) | **Wipe** (car passes) |
| S13 | 15.0–17.2 | Pass-by, drive-away | **Whiteout → loops to S01** |

Machine-readable: `07_edit/timeline.json` (also SFX cues, grade, exports). Recipes + Flow hand-off cues: `04_prompts/TRANSITIONS.md`. Prompts used to generate the clips: `04_prompts/FLOW_PROMPTS.md`.

## Edit pipeline (do in order)
1. **Inventory.** List files in `05_flow_generations/S*/` with ffprobe (duration, fps, resolution). Pick the best take per shot: same car/colour as the others, no warped logos/text, correct hand-off motion (whip direction, roll direction, star centred). Write `07_edit/work/takes.md` with picks + reasons. If a shot is missing, use a black placeholder with the shot id and report it.
2. **Music + beat grid.** If a song is in `02_music/`, run `python 07_edit/scripts/beatmap.py 02_music/<file> [section_start_seconds]`; use `07_edit/work/timeline_snapped.json` from then on. Trim the song section to `02_music/song_section.wav` (17.2 s, 20 ms fades). Silence 2.0–2.2 s except ambience. If no song, keep the placeholder grid and say so.
3. **Conform.** 1080×1920 @ 30 fps, each shot trimmed to its window. Choose the in-point of each clip so the hand-off motion starts right at the cut (whip/roll shots start mid-motion).
4. **S01 hook.** Take the flame burst (0.2–0.8 s of the clip), cut on the decay frame; add 2 f bloom flash on the first frame; hook text 0–2.0 s.
5. **S02 badge fly-in (1.0–1.9 s).** Extract the Mercedes star from S03's frame: luma/roto matte, keep alpha. Animate it from camera to the grille centre with perspective scale (300% → 100%), blue rim glow (#3FA9FF, Gaussian 30 px, add 60%), small settle bounce. Track it to S02's push-in with a simple scale/position keyframe set.
6. **T2 Pass through (2.2).** Over 6 f scale S02 100% → 600% centred on the grille slats; S03 revealed through the gaps by a luma mask of the slats; motion blur. Riser ends at 2.0, silence, impact on 2.2.
7. **T3 Shape (4.3).** Circle mask centred on the star, scale-through + 3 f cross into S04's star at the same size/position.
8. **Whips (5.4, 6.8, 12.5).** Cut inside the blurriest frames; add 4–6 f horizontal directional blur, same direction (right) on both sides.
9. **Rolls (7.7, 9.8, 11.0).** Continue clockwise rotation across the cut: last 6 f of A rotate 0 → +90°, first 6 f of B −90° → 0 (scale up to hide corners), rotational blur (average 3 sub-rotations), ease-out.
10. **T7 Shape match (8.9).** Align ring → wheel scale/position on the cut frame; 4 f morph.
11. **T12 Wipe (15.0).** Cut on the frame where the occluder covers the most (lowest variance + darkest coverage); 4 f directional blur right→left.
12. **Loop (17.2 → 0).** Last 3 f white flare; S01 starts in the flame flash so the loop is invisible. Check by SSIM on the white frames and adjust.
13. **Text.** Pillow RGBA frames (not drawtext). Hook: bold sans, white, 84 px, 72% height, soft shadow, 3 f fade. Safe zones: keep bottom 18% and right 12% clear.
14. **Grade.** Match every shot to S12 first (histogram match on luminance + mean colour). Then LUT (`07_edit/luts/` if present), teal-grey shadows / warm highlights, crush blacks slightly, saturation −10%, halation on headlight rings and flame, grain ~12%, soft vignette.
15. **Audio.** Song −2 dB. SFX from `03_sfx/individual/` per `timeline.json → sfx_cues` (whooshes centred on the cut; riser ends at 2.0). If `03_sfx/individual` is empty run `python 07_edit/scripts/make_sfx.py`. Mix, tanh soft-clip, target about −10 LUFS integrated and ≤ −0.5 dBFS true peak (`ebur128`).
16. **Export** to `08_exports/`: `G63_ColdStart_final.mp4` (with text), `G63_ColdStart_clean.mp4` (no text), `G63_ColdStart_cover.jpg` (S12 frame).
17. **QC.** Contact sheet at 4 fps (`08_exports/qc_sheet.jpg`). Check: every cut within 1 f of a kick; no black/duplicate frames; same car in all shots; the loop is invisible; text in the safe zone. Report what you checked and anything you could not do.

## Caption + post (for Farabe, not for the video)
- Caption: `Rate this edit 1–10`
- Cover: S12 frame. Use a library track so the audio stays live; a baked-in unreleased track can be muted.

## Folder map
| Folder | Contents |
|---|---|
| 01_reference | contact sheets of the reference reel |
| 02_music | Farabe's song (drop it here) |
| 03_sfx/individual | synthesized SFX pack (`make_sfx.py` regenerates it) |
| 04_prompts | FLOW_PROMPTS.md, TRANSITIONS.md |
| 05_flow_generations/Snn_* | Flow clips `Snn_take1.mp4`, stills `Snn_image.png`; `_reference_photos/` = G 63 press photos |
| 07_edit | timeline.json, scripts/, work/, luts/ |
| 08_exports | finals + QC |
