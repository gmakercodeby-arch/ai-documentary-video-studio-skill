---
name: ai-documentary-studio
description: >-
  End-to-end AI Documentary Video-Making Studio Skill (v4.0 Pro Studio) for producing
  12-to-25 minute 16:9 @ 60fps YouTube Documentaries, Engineering Explainers, Factory
  Deep-Dives, and "What If" Science Videos. Features an automatic first-run AI Setup Wizard,
  8-Act retention scripting with literal word-to-object visual grounding (60-85+ unique visuals,
  zero lazy repetition), single-model Gemini 3.1 Flash TTS (Fenrir baritone), Google Flow
  Veo 3.1 + 3D cutaway pipeline, hardware GPU (Intel QSV / NVIDIA NVENC) parallel FFmpeg
  assembly with SHA-1 clip caching, Playwright glassmorphism callouts & badges, and a
  2-Layer Autonomous "Eyes & Ears" Zero-Defect QA Engine.
---

# AI Documentary Video-Making Studio Skill (v4.0 Pro Studio)

Turn any AI coding agent (Antigravity, Claude Code, Cursor, Gemini CLI, Codex) into a **full autonomous 1080p @ 60fps YouTube Documentary Production Studio**.

---

## Stage 0 — Automatic First-Run AI Setup Wizard (RUN FIRST FOR NEW USERS!)

Before producing the first documentary on a new machine, **ALWAYS run the environment doctor**:

```bash
python "<SKILL_DIR>/scripts/check_setup.py"
```

If `.env` or `studio_config.json` is missing (or any required dependency is absent), **guide the user interactively step-by-step**:
1. **Install missing dependencies** automatically (`pip install -r "<SKILL_DIR>/requirements.txt"` and verify `ffmpeg` + `ffprobe` on PATH).
2. **Ask the user 4 quick setup questions** (and save to local `studio_config.json` + `.env` — NEVER commit `.env`!):
   - **Channel Brand Badge Text:** e.g., `GMZ` or their YouTube channel initials (rendered as a sleek dark glassmorphism pill badge at bottom-right).
   - **Narration Language & Style:** e.g., Conversational Hindi documentary (`Fenrir` voice, ~160 WPM) or English documentary.
   - **Gemini API Key (`GEMINI_API_KEY`):** Free or Tier-1 key from Google AI Studio (stored ONLY in local `.env`).
   - **Optional Outro CTA:** Whether to include a closing website / lead-gen CTA line + glassmorphism card at the end of Act 8 (e.g., *"Visit the website in the description..."*).
3. **Optional MCP Integrations:** Check if `google-flow` MCP (Veo 3.1 + Nano-Banana-2) and `notebooklm` MCP (grounded zero-hallucination research) are available; if not, seamlessly fall back to `scripts/generate_cutaway_image.py` + audited Wikimedia/NASA/stock visuals!

---

## 1. Locked Studio Production DNA (v4.0)

| Parameter | Exact Target | Why It Wins |
|---|---|---|
| **Resolution & FPS** | `1920x1080` @ **`60 fps`** | Ultra-smooth Ken Burns pan/zoom & cinema motion |
| **Runtime & Word Count** | **`12–22 min`** (`2,000–3,400` words) | High mid-roll RPM + deep watch-time |
| **Narration Speed** | **`158–168 WPM`** | Gripping documentary pace, zero boredom |
| **Narrator Voice (LOCKED)** | **ONE single TTS model** (`gemini-3.1-flash-tts-preview`, voice `Fenrir`) | **NEVER mix two TTS models mid-video** — guarantees zero timbre shifts |
| **Audio Mastering** | Single true two-pass **`-13.0 LUFS`**, `TP <= -1.5 dBTP`, `LRA 9 LU` | Broadcast clarity, zero loudnorm pumping |
| **Visual Grammar (v4.0)** | **Literal Word-to-Object Grounding + `60–85+` Unique Assets** | **EVERY named object** (*NASA satellite, computer 3D map, cutaway, machine*) gets its OWN exact visual at that exact timestamp! |
| **Anti-Repetition Gate** | Target **1–2 uses** per photo/3D (`HARD FAIL > 4`), **`>= 12` shots cooldown** | Zero viewer fatigue, enforced automatically by `preflight_qa.py` |
| **On-Screen Graphics** | Clean 16:9 frame — NO cluttered subtitles | `10–18` Playwright glassmorphism lower-thirds synced to spoken beats |
| **Brand Badge** | Sleek Playwright translucent dark glassmorphism pill (`• BRAND`) | Cinema-grade channel branding at bottom-right |

---

## 2. Stage 1 — Grounded Research & 8-Act Retention Script

1. **Fact-Check First:** Research real numbers, dates, engineering physics, and turning points (via `notebooklm` MCP or verified web/engineering sources) — zero hallucinated stats.
2. **Write `acts.json` Act-by-Act (8 Acts, `~250–420` words each):**
   - **Act 1 — Cinema Cold-Open + Video-End Open Loop:** ZERO *"Hello guys welcome to my channel"*. Drop straight into a tense visual scene and plant a burning mystery loop.
   - **Act 2 — Relatable Everyday Analogy & Scale of the Problem:** Make complex engineering instantly understandable.
   - **Act 3 — Origin Story & Human Stakes:** Introduce the engineers/builders and why failure was not an option.
   - **Act 4 — Why Conventional Methods Failed:** 2–3 numbered flaws (ideal for glassmorphism lower-thirds).
   - **Act 5 — The Core Engineering Reveal (Heart of the Documentary):** Step-by-step physics with vivid 3D cutaways & metaphors.
   - **Act 6 — Crisis, Turning Point & Real-World Proof:** Show what nearly went wrong and how engineers saved it.
   - **Act 7 — Massive Scale & Global Impact:** Accelerate cut pacing (`1.6–2.5s/cut`).
   - **Act 8 — Open-Loop Payoff + Comment Bait + Custom Outro CTA:** Pay off Act 1's mystery → ask viewers *"What topic should we cover next? Comment below!"* → close with the user's configured Outro CTA (from `studio_config.json`, paired with a sleek glassmorphism Website CTA card if enabled).
3. **TTS-Safe Writing Rules:** Write numbers naturally for speech (`15 हजार` instead of raw symbols), space rare acronyms cleanly, and avoid excessive `...` ellipses so pacing stays brisk (`~160 WPM`).

---

## 3. Stage 2 — Single-Model Voiceover & Word-Level Alignment

1. **Generate Voiceover** (sentence-chunked `60–90` words on `। / ? / !`, atomic per-chunk caching, automatic silence `>2.5s` & WPM sanity retry, warm baritone EQ, NO premature loudnorm):
   ```bash
   python "<SKILL_DIR>/scripts/generate_voiceover.py" --acts-json project/acts.json --out-dir project/audio
   ```
2. **Extract Word-Level Timestamps** (`faster-whisper`, `vad_filter=False` so quiet syllables & final words are never clipped):
   ```bash
   python "<SKILL_DIR>/scripts/align_narration.py" --audio project/audio/master_narration.mp3 --out project/audio/segments.json --language hi
   ```

---

## 4. Stage 3 — v5.0 "1M-View Cinema" Visual Engine (Multi-Beat Veo + Zero Static Slides!)

### Step 3A — Multi-Beat Timeline Veo 3.1 Director Prompting (MANDATORY for Every 8s Clip!)
NEVER write a single-action 8-second prompt! Choreograph **3 distinct story beats inside `[0-2.5s] -> [2.5-5.5s] -> [5.5-8.0s]`** with camera motion, lens/lighting, and synced diegetic Foley SFX:
```text
[0-2.5s] Wide/tracking establishing action with clear subject & environment.
[2.5-5.5s] Snap close-up / dynamic camera push-in / mechanism reveal.
[5.5-8.0s] Dramatic hero payoff / reaction / macro detail reveal.
Cinematography: 35mm anamorphic documentary lens, dramatic rim lighting, authentic Foley SFX (specific mechanical/water/wind sounds), NO text, NO spoken dialogue.
```

### Step 3B — Sentence-by-Sentence Visual Noun & Metaphor Audit (`visual_noun_map.json`)
Read EVERY sentence of `acts.json` BEFORE generating/sourcing visuals and list EVERY concrete object, technology, AND everyday analogy (*ATM machine, blocked heart artery, NASA satellite, computer 3D CAD map*) — every concept gets its OWN dedicated visual pinned to the exact Whisper timestamp!

### Step 3C — High-Diversity Asset Quota (`60–85+` UNIQUE Visuals — ZERO Static PowerPoint Slides!)
1. **15–22 UNIQUE Multi-Beat AI Action Clips** (Google Flow `Veo 3.1 Fast` via `google-flow` MCP):
   - **Strict Rate-Limit Rule:** Queue **1 job at a time** + wait for completion.
   - Lock recurring characters (`flow_character` / identical wardrobe description) so the film has movie-grade continuity.
   - Keep natural diegetic Foley SFX (`-16 dB`), but set `"keep_native_sfx": false` if AI ever generates speech! Crop `1.14x–1.28x`.
2. **25–35 UNIQUE Photorealistic 3D Cutaways & Visual Metaphors** (`Nano-Banana-2` / `scripts/generate_cutaway_image.py`):
   - Pre-cropped `12%` (`crop=iw*0.88:ih*0.88:0:0`) on `3d_images/` + silky `2560x1440` 60fps Ken Burns.
3. **20–30 Visually Audited Real Archival / Engineering / NASA Photos** (audited via contact sheet).
4. **Kinetic Typography, HUD Pointers & Split-Screen Overlays (`scripts/render_kinetic_overlays.py`):**
   - **NEVER use full-screen static text/blueprint slides!** Composite **Giant Bold Kinetic Impact Text**, **Thin Glowing HUD Pointer Lines**, **Split-Screen Comparisons**, and the **Gold 1-Click Website Outro CTA** directly over moving footage — paired with procedural cinema SFX (`"sfx": "whoosh" | "bass_hit" | "pop" | "riser"`)!

---

## 5. Stage 4 — Mandatory Layer-1 Pre-Flight QA (BEFORE Rendering)

Run `preflight_qa.py` BEFORE spending compute on rendering:
```bash
python "<SKILL_DIR>/scripts/preflight_qa.py" --acts project/acts.json --audio project/audio/master_narration.mp3 --segments project/audio/segments.json --plan project/shot_plan.json --out-dir project/qa_preflight
```

`preflight_qa.py` automatically checks and FAILS on:
- Missing files or silence gaps `> 2.5s`
- Script-vs-Whisper word coverage drop (`< 85%`)
- **100% Local Voice-Tone Consistency Forensics** (RMS dB, ZCR Hz, 350Hz warmth ratio across all acts to catch any accidental timbre shift!)
- **v4.0 Visual Richness Gate:** `< 55` unique assets for 10+ min videos = **FAIL**
- **v4.0 Anti-Repetition Gate:** Any asset used `> 4` times OR reappearing within `< 12` shots = **FAIL**
- Generates labeled `preflight_assets_grid.png` + `preflight_callouts_grid.png` — visually inspect BOTH grids before rendering!

---

## 6. Stage 5 — GPU-Accelerated Assembly + Layer-2 "Watch & Listen" QA

1. **Assemble Final 1080p @ 60fps Master MP4:**
   ```bash
   python "<SKILL_DIR>/scripts/assemble_documentary.py" --plan project/shot_plan.json --narration project/audio/master_narration.mp3 --bgm project/audio/bgm.mp3 --segments project/audio/segments.json --badge "YOUR_TAG" --workers 3 --out project/output/Final_Master.mp4
   ```
   - Auto-detects **Intel QuickSync (`h264_qsv`)** or **NVIDIA (`h264_nvenc`)** with seamless `libx264` fallback.
   - **Multi-core parallel clip rendering** + **SHA-1 smart clip caching** (fixing 1 bad clip later reuses 95%+ clips in `0.0s`!).
   - Batched `0.25s` `xfade` transitions using lossless PCM `.mkv` intermediates with `±0.15s` sync verification.
   - Single true two-pass `loudnorm` (`I=-13:TP=-1.5:LRA=9`) + automatic BGM sidechain ducking + clean `2.5s` fade-out.
2. **Layer-2 Autonomous "Watch & Listen" Post-Render QA (100% Local, ZERO API Quota!):**
   - `assemble_documentary.py` automatically runs `scripts/make_qa_proxy.py` to split the finished master into lightweight **2-minute** QA proxy MP4 chunks (`480p @ 2fps + 44.1kHz 64k stereo audio`, `~5 MB` each).
   - **Inspect EVERY 2-minute proxy chunk directly** (video + audio) AND check `_QA_25frames.jpg`:
     - Verify zero watermarks, zero edge borders, zero AI voice bleed, zero dead silence, zero A/V sync drift.
     - Verify **Literal Spoken-vs-Visual Alignment**: *"Does the screen show the exact object/concept the narrator is talking about? Does anything feel repetitive?"*
   - Fix any defect in `shot_plan.json` and re-run `assemble_documentary.py` (instant SHA-1 cache!) BEFORE delivering the final video!
