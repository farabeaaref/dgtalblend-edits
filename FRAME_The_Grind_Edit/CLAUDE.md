# CLAUDE.md — FRAME · THE GRIND (edit brief)

You are editing a 30-second vertical Reel for Farabe Aaref (creative director, DgtalBlend). He shot it solo. Your job: build the finished edit from the footage in `05_footage/`, following this brief and `06_edit/timeline.json` exactly. Work with ffmpeg + Python (OpenCV, numpy, Pillow, librosa, soundfile). Put intermediates in `06_edit/work/` and finals in `07_exports/`.

## Spec
- 1080×1920, 25 fps, 30.0 s, H.264 high, yuv420p, CRF 16, AAC 320 kbps 48 kHz stereo, `-movflags +faststart`.
- Source is 4K vertical (or 4K landscape to crop). Log/flat profile. 50 fps on S03, S05, S06 (slow motion).

## Style rules (from Farabe, non-negotiable)
- The hook is the most tension-filled moment: it opens the video and echoes once inside it (the clone flash at 24.8 s).
- On-screen hook text in the first 3 s: bold, short, tension-first.
- Every cut lands on a kick. Only 4 transition types: Pass through, Wipe, Roll, Whiteout. Everything else is a hard cut.
- Premium and restrained: no flashy presets, no stock transitions, no emoji, no extra text.
- Total length 30–40 s max. This edit is 30.0 s.

## Story
Calm you sits on an old chair in an empty field (mountains on one side, the city below on the other) while a restless you (same person, cloned) paces in front of the lens. Silence, eye contact, drop. Finger-frame around the city, title. Montage of the grind from golden hour to night. Laptop glow, the restless clone flashes back, white flash. Empty chair at first light, then it loops back to him sitting there. Message: every day, same chair.

## Reference
`01_reference/reference_keyframes.jpg` (keyframes of the Renaissance Goa hotel reel, 21 s; the full video is not in git). Same skeleton: soft hook → 0.3–0.4 s silence → drop on the title → cut on every kick → 2–3 beat symmetric breather → roll → 1 white frame → empty room → loop.

## Storyboard
- 3D previz frames: `04_storyboard/frames/S01.jpg … S13.jpg` (S07 has `_a` start and `_b` end). The red marks on the frames are notes, not graphics.
- Online version with the camera map: https://claude.ai/artifact/NqtYByNNfAKHhxudhD5ahN
- Full written plan: https://claude.ai/artifact/HZFFpB42tywTtkxU1Fxspa

## Timeline (placeholder grid until the song is beat-mapped)
| Shot | In–Out (s) | Role | Speed | Out transition | Text / overlay |
|---|---|---|---|---|---|
| S01 | 0.0–5.6 | Hook, clone composite | 1.0 | hard cut on drop | "Nobody claps / for this part." 0–3 s |
| S02 | 5.6–7.6 | Drop, finger frame | 1.0 | Pass through (6 f) | "FRAME · THE GRIND" 5.6–13.6 |
| S03 | 7.6–9.6 | Walk-in | 0.5, ramp out | hard cut | |
| S04 | 9.6–10.6 | Ridge, low angle | 1.0 | hard cut | |
| S05 | 10.6–11.6 | Boots macro | 0.6 | hard cut | |
| S06 | 11.6–13.6 | Low gimbal walk | 0.6, ramp out | hard cut | |
| S07 | 13.6–15.6 | Rack focus thistle → city | 1.0 | hard cut | |
| S08 | 15.6–16.6 | Notebook macro | 1.0 | hard cut | |
| S09 | 16.6–19.6 | Symmetric breather | 1.0 | hard cut | cover still |
| S10 | 19.6–21.6 | Pole wipe | 1.0 | Wipe | |
| S11 | 21.6–23.6 | City roll (night) | 1.0 | Roll (6 f, 25°) | |
| S12 | 23.6–25.6 | Laptop glow | 1.0 | Whiteout (1 f) | clone echo 24.8 s, 3 f |
| S13 | 25.6–30.0 | Empty chair, loop | push 100→112% | loop to S01 | "Back tomorrow." 27–30 s |

Machine-readable version with SFX cues, text styles and grade: `06_edit/timeline.json`.

## Edit pipeline (do these in order)
1. **Inventory.** List every file in `05_footage/S*/` with ffprobe (duration, fps, resolution, rotation). Pick the best take per shot: sharpest focus, steadiest, correct action. Write `06_edit/work/takes.md` with your picks and why. If a shot is missing, say so and continue with a black placeholder labelled with the shot id.
2. **Music + beat grid.** If a song is in `02_music/`, run `python 06_edit/scripts/beatmap.py 02_music/<file>` (optionally pass the section start in seconds). Use `06_edit/work/timeline_snapped.json` from then on. Trim the song section to `02_music/song_section.wav` (30.0 s, 20 ms fades). Silence it from 5.2 s to the drop. If there is no song, keep the placeholder grid and note it.
3. **Conform.** Scale/crop every clip to 1080×1920 at 25 fps. 50 fps clips: retime with `setpts` to the speed in the timeline (frame-exact, no frame blending). Speed ramps (`ramp_out`): last 6 frames go 100% → 300% (drop frames progressively), add 2–3 frame directional blur.
4. **S01 clone composite.** S01 is one continuous locked-off take: seated section (A), pacing section (B), empty-chair plate (C, also S13).
   - Find section boundaries by motion (frame-difference energy) and confirm by looking at contact sheets.
   - Matte for the restless you: per-frame absolute difference of B against the median of C, blur 15 px, threshold, morphological close + dilate, feather 25–40 px. Restless you is out of focus, so a soft matte is correct.
   - Composite B (matted) over A. Check for flicker. Stabilise the matte temporally (EMA over 3 frames).
   - The seated you's look to the lens should land at ~5.0 s. Retime A if needed.
5. **S02 → S03 Pass through.** Detect or hand-place the finger rectangle (inner corners of the hands). Over 6 frames, scale S02 from 100% to 800% centred on the rectangle; inside the rectangle mask show S03 (on the drop + 2 frames). Motion blur on the scale.
6. **S10 → S11 Wipe.** Find the frame where the pole/occluder covers the most of the frame (lowest variance + darkest column coverage). Cut there, plus 4 frames of horizontal directional blur across the cut, left to right.
7. **S11 → S12 Roll.** S11 last 6 frames rotate 0 → +25° (scale up to hide corners), S12 first 6 frames −25° → 0. Rotational motion blur (average 3 sub-rotations per frame).
8. **S12 clone echo.** At 24.80 s, replace 3 frames with 3 frames of restless you from S01 section B (graded to match S12, slight RGB split 4 px).
9. **Whiteout.** 1 white frame on the flash kick (25.6 s placeholder). S12 last 3 frames: bloom (threshold 0.7, Gaussian 40 px, add 60%).
10. **S13 loop.** Digital push-in 100% → 112% over the shot (ease-in-out). The final frame must match S01 frame 1 in framing and scale: compare with SSIM and adjust the end scale so the loop is invisible.
11. **Text.** Render with Pillow onto RGBA frames (not ffmpeg drawtext). Hook: bold sans, white, 78 px, centred at 72% height, soft shadow; 3-frame fade in/out. Title: serif, #D9A55B, 46 px, tracking +4%, centred. Fonts: use Inter Bold / Cormorant Garamond if available, else download from Google Fonts into `06_edit/fonts/`.
12. **Grade.** If a LUT is in `06_edit/luts/`, apply it first (`lut3d`). Then: teal shadows / amber highlights (`colorbalance`), crush blacks slightly (`curves`), saturation −15% (`eq`), halation on bright points (threshold + warm blur, add 25%), grain ~15% (`noise=alls=12:allf=t`), soft vignette. The arc: warm golden (S03–S08), cold blue hour (S01, S02, S09, S10), night with amber city (S11, S12), cool dawn (S13). Match S13 to S01 so the loop holds.
13. **Audio.** Song section −2 dB. SFX from `03_sfx/individual/` placed per `timeline.json → sfx_cues` (whooshes centred on the cut; the riser ends at the silence). Keep the location audio for gravel (S05) and paper (S08) at −10 dB. Mix, soft-clip with tanh, target about −10 LUFS integrated and ≤ −0.5 dBFS true peak (check with `ebur128`). If `03_sfx/individual` is empty, run `python 06_edit/scripts/make_sfx.py`.
14. **Export** to `07_exports/`:
    - `FRAME_TheGrind_final.mp4` (with text)
    - `FRAME_TheGrind_clean.mp4` (no text)
    - `FRAME_TheGrind_cover.jpg` (S09 frame + title, 1080×1920)
15. **QC.** Contact sheet at 4 fps of the final (`07_exports/qc_sheet.jpg`). Check: every cut within 1 frame of a kick; no black/duplicate frames; text safe zones (keep the bottom 18% and right 12% clear for the Instagram UI); the loop from the last frame to the first is invisible. Report what you checked and anything you could not do.

## Caption + post (for Farabe, not for the video)
- Caption: `Day 1 or day 1000, same chair. Which day are you on?`
- Pinned comment: `Shot solo in one evening. Comment FRAME and I'll send you the shot list.`

## Folder map
| Folder | Contents |
|---|---|
| 01_reference | reference reel + keyframes |
| 02_music | Farabe's chosen song (drop it here) |
| 03_sfx/individual | synthesized SFX pack (regenerate with make_sfx.py) |
| 04_storyboard/frames | 3D previz frames per shot |
| 05_footage/Sxx_* | raw clips per shot (`Sxx_take1.mp4`, `Sxx_take2.mp4`, …) |
| 06_edit | timeline.json, scripts/, work/, luts/, fonts/ |
| 07_exports | finals + QC |
