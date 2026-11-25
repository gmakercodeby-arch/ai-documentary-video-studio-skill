---
name: ai-documentary-studio
description: >-
  End-to-end AI Documentary Video-Making Studio Skill (v5.2 Zero-Defect Cinema Engine) for producing
  10-to-25 minute 16:9 @ 60fps YouTube Documentaries, Business Case Studies, Engineering Explainers,
  Factory Deep-Dives, and "What If" Science Videos. Features an automatic first-run AI Setup Wizard,
  8-Act retention scripting with sentence-exact Whisper visual grounding, single-model Gemini 3.1
  Flash TTS (Fenrir baritone) with automated TTS stage-direction hallucination scanning, Google Flow
  Omni 1.2 Flash / Veo 3.1 smart 360p/720p credit-saving pipeline, 5-frame sub-beat scrubbing,
  hardware GPU (Intel QSV / NVIDIA NVENC) parallel FFmpeg assembly with SHA-1 clip caching,
  Playwright kinetic HUD overlays & glassmorphism badges, and a 2-Layer Autonomous 100% Full-Video
  "Watch & Listen" + Auto-Fix QA Engine.
---

# AI Documentary Video-Making Studio Skill (v5.2 Zero-Defect Cinema Engine)

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

## 2. Stage 1 — Viral Topic Discovery, Grounded Research & 8-Act Script

0. **Find a High-Outlier Topic First (Recommended):** Before locking a new topic, run the bundled `gmz-viral-topic-hunter` companion skill (`python "<SKILL_DIR>/skills/gmz-viral-topic-hunter/scripts/hunt_viral_topics.py" --group all --min-mult 1.8 --min-views 150000 --out-dir "./topic_research"`) across **32** Hindi & Global Engineering + Business Case-Study channels via `yt-dlp` (zero API key) to spot `2x–35x` channel-median outliers and Global-to-Hindi arbitrage winners.
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

## 4. Stage 3 — v5.1 "1M-View Cinema" Visual Engine (`Omni 1.2 Flash` `3s–15s` + Zero Static Slides!)

### Step 3A — Variable-Length (`3s–15s`) & Multi-Beat Director Prompting (MANDATORY!)
Match clip duration to the story beat (`Omni 1.2 Flash` ~3 credits/sec, `count=1`):
- **`3s–5s` (`9–15 credits`):** Quick single-beat metaphors & reactions (*1 plate paneer, ATM balance zero, rubber stamp thud, shock reaction*) — saves 40–60% credits!
- **`8s` (`24 credits`):** Standard **3-Beat Mini-Movie** (`[0-2.5s] Setup -> [2.5-5.5s] Camera Move/Action Peak -> [5.5-8.0s] Hero Payoff`).
- **`12s–15s` (`36–45 credits`):** Full **5-Beat Continuous Hero Sequence** (Act 1 cold-open hook, full 3D cutaway journey, or gamified lock reveal).
```text
[0-2.5s] Wide/tracking establishing action with clear subject & environment.
[2.5-5.5s] Snap close-up / dynamic camera push-in / mechanism reveal.
[5.5-8.0s] Dramatic hero payoff / reaction / macro detail reveal.
Cinematography: 35mm anamorphic documentary lens, dramatic rim lighting, authentic Foley SFX (specific mechanical/water/wind sounds), NO text, NO spoken dialogue.
```
**Smart Resolution Allocation (70/30 Credit Saver):**
- Use **`720p`** for hero narrative scenes, close-ups, office interiors, 3D financial vaults, and key reveals where crisp detail matters.
- Use **`360p` (~14 credits)** for distant aerial highways, night traffic B-roll, and rapid transitional clips to conserve 50%+ video generation credits without hurting perceived 1080p60 quality.

**Realistic Civilian Wardrobe & Anti-Police Guardrail:**
- NEVER use ambiguous words like `"khaki"` or generic `"uniform"` for civilian managers, staff, or shopkeepers (video AI models hallucinate police uniforms, peaked caps, epaulets, and badges).
- ALWAYS specify exact civilian attire (*"civilian formal light-blue/white button-down shirt with spectacles and pen"*, *"corporate navy polo shirt"*) and explicitly append *"Civilian attire ONLY, NO police uniform, NO badges, NO military epaulets"*.

**Zero-Skip Failure & Retry Protocol (NEVER Silently Skip a Failed Clip!):**
1. **Retry #1 (Cooldown + `flow_retry` / fresh queue):** Pause 20–30s on `PUBLIC_ERROR_UNUSUAL_ACTIVITY` or timeout and retry cleanly (ensure no duplicate browser tab is open on the same project).
2. **Retry #2 (Prompt / Model Rescue):** Simplify safety-trigger words, switch between `Omni 1.2 Flash` and `veo-3.1-fast`, or step duration down (`15s -> 8s`) and regenerate.
3. **Controlled Fallback (ONLY after 2 failed retries or 0 credits):** Replace immediately with a dedicated custom 3D `nano-banana-2` cutaway (60fps Ken Burns + procedural SFX) so zero story beats are ever dropped.

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

## 5. Stage 4 — Sub-Beat Scrubbing & Layer-1 Pre-Flight QA (BEFORE Rendering)

### Step 4A — ZERO Blind Round-Robin & Mandatory 5-Frame Sub-Beat Scrubbing (HARD RULE)
- **NEVER** auto-cycle (`clip_ptr % len(clips)`) clips across an Act or guess overlay timestamps (`14.5`, `185.0`, `635.0`).
- Before writing `shot_plan.json`, generate a **5-frame sub-beat storyboard strip** of EVERY multi-beat Flow clip so you know what each second shows, and **surgically exclude bad AI sub-beats** (background police/khaki guards, Bitcoin `₿` or foreign currency where local currency belongs, unrelated fire/logo transitions, wrong-region trucks).
- Pin **every single sentence/clause AND every kinetic overlay** (including the **1-Click Website Outro CTA card**) directly to its exact Whisper timestamp in `segments.json`.
- Whenever a user-approved 1-minute Pilot (`pilot_shot_plan.json`) exists, preserve its exact Act 1 scene mapping in the full master plan.
- Never drop a vertical split-screen divider line across a single non-split clip; use clean side-by-side comparison cards or real dual-clip split-screen footage.

### Step 4B — Automated Layer-1 Pre-Flight QA (`preflight_qa.py` v5.2)
Run `preflight_qa.py` BEFORE spending compute on rendering:
```bash
python "<SKILL_DIR>/scripts/preflight_qa.py" --acts project/acts.json --audio project/audio/master_narration.mp3 --segments project/audio/segments.json --plan project/shot_plan.json --out-dir project/qa_preflight
```

`preflight_qa.py` (v5.3) automatically checks and FAILS on:
- Missing files or silence gaps `> 2.5s`
- **v5.3 Video Clip EOF Bounds Gate:** Probes every `.mp4` clip and **HARD FAILS** if ANY shot's `start + duration + xfade` exceeds actual clip length (prevents mid-video black-screen `xfade` drops BEFORE rendering!).
- **v5.3 Static Slide / Diagram Blocker:** Flags any shot referencing banned `diagrams/` or `slides/` folders so full-screen PowerPoint cards never slip into a documentary.
- Script-vs-Whisper word coverage drop (`< 85%`)
- **v5.2 TTS Stage-Direction / Hallucinated-Word Scanner:** Flags rogue spoken *"Pause" / "पॉज़" / "बास"* or unexpected short English leaks not in `acts.json` so they are surgically silenced BEFORE render!
- **100% Local Voice-Tone Consistency Forensics** (RMS dB, ZCR Hz, 350Hz warmth ratio across all acts to catch any accidental timbre shift!)
- **Visual Richness & Anti-Repetition Gate:** `< 55` unique assets (for mixed 10+ min videos), `> 4` uses per asset, or `< 12` shots cooldown = **FAIL** (NEVER fall back to unrelated cross-Act global swaps; use clean Act-scoped pools & sentence-proportional Act timing backup when Whisper drops Hindi segments!)
- Generates labeled `preflight_assets_grid.png` + `preflight_callouts_grid.png` — visually inspect BOTH grids before rendering!

---

## 6. Stage 5 — GPU-Accelerated Bulletproof Assembly + Layer-2 100% Full-Video "Watch & Listen" Auto-Fix Loop

1. **Assemble Final 1080p @ 60fps Master MP4 (`assemble_documentary.py` v5.3):**
   ```bash
   python "<SKILL_DIR>/scripts/assemble_documentary.py" --plan project/shot_plan.json --narration project/audio/master_narration.mp3 --bgm project/audio/bgm.mp3 --segments project/audio/segments.json --badge "YOUR_TAG" --workers 3 --out project/output/Final_Master.mp4
   ```
   - **v5.3 Built-in Video EOF Shield:** Probes real video durations before clip rendering, auto-clamps `start` safely (`real_dur - render_dur - 0.15s`), adds `tpad=stop_mode=clone` + `apad` if needed, validates cached clip durations, auto-cleans stale `batch_*.mkv` intermediates, and **HARD ABORTS** if `xfade` drift exceeds `0.25s`!
   - Auto-detects **Intel QuickSync (`h264_qsv`)** or **NVIDIA (`h264_nvenc`)** with seamless `libx264` fallback.
   - **Multi-core parallel clip rendering** + **SHA-1 smart clip caching** (fixing 1–4 bad clips later reuses 95%+ clips in `0.0s`!).
   - Batched `0.25s` `xfade` transitions using lossless PCM `.mkv` intermediates (`drift = 0.000s`).
   - Single true two-pass `loudnorm` (`I=-13:TP=-1.5:LRA=9`) + automatic BGM sidechain ducking + clean `2.5s` fade-out + bottom-right glassmorphism pill badge (`W-w-14:H-h-14`) covering any AI star watermark.
2. **Layer-2 Autonomous 100% Full-Video "Watch & Listen" + Black-Frame Detector + Auto-Fix Loop (100% Local, ZERO API Quota!):**
   - `assemble_documentary.py` automatically runs `scripts/make_qa_proxy.py` (v5.3) to clean stale proxies, split the finished master into lightweight **2-minute** QA proxy MP4 chunks (`480p @ 2fps + 44.1kHz 64k stereo audio`, `~5 MB` each), and **automatically raises a CRITICAL ALERT** if any chunk drops below `1.1 MB/min` (instant black/frozen frame alarm!).
   - **HARD RULE — NO PARTIAL CHECKS:** Open, WATCH, and LISTEN to **EVERY SINGLE 2-minute proxy chunk (`Part 1` through `Part N`)** directly AND inspect `_QA_25frames.jpg`:
     - Verify zero spoken audio glitches/rogue words, zero watermarks, zero edge borders, zero AI voice bleed, zero dead silence, zero A/V sync drift.
     - Verify **Literal Sentence-by-Sentence Spoken-vs-Visual Alignment**, exact overlay & Outro CTA timing, and zero background wardrobe/currency/AI artifacts.
   - **Mandatory Auto-Fix Before Delivery:** If ANY defect is spotted in ANY chunk, **FIX IT IMMEDIATELY** (patch audio / remap `shot_plan.json` / adjust overlay timestamp), re-render via SHA-1 clip cache, rebuild affected proxies, and re-verify to 100% clean BEFORE delivering the final video!
