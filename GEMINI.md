# Daily Learn 3.0 (GMZ) — Project Memory & Locked Production Rules (v5.3 "Bulletproof Zero-Defect Cinema" Engine)

This workspace (`f:\Daily Learn 3.0`) produces **10–18 minute 16:9 @ 60fps Hindi AI Documentary & Engineering Explainer YouTube videos** modeled directly on forensic study of `@DailyLearn3.0`'s 1.16M-view viral hits, branded under **`GMZ`**.

## Always Activate
- Global Skill: `daily-learn-doc-studio` (`C:\Users\shahz\.gemini\config\skills\daily-learn-doc-studio\SKILL.md`)
- Global Topic Discovery Skill: `gmz-viral-topic-hunter` (`C:\Users\shahz\.gemini\config\skills\gmz-viral-topic-hunter\SKILL.md`) — ALWAYS run BEFORE picking a new documentary/Short topic to mine 31 Hindi & Global Engineering + Business Case-Study benchmark channels (including `@HinExpofficial`, `@DailyLearn3.0`, `@BranchEducation`, `@MagnatesMedia`, etc.) via `yt-dlp` outlier multipliers & Global-to-Hindi arbitrage (`--min-views 150000` long-form / `500000` shorts).
- Reference forensic study files: `f:\Daily Learn 3.0\reference_study\`
- Local API key: `f:\Daily Learn 3.0\.env` (`GEMINI_API_KEY` + backup keys preserved as comments)

## Locked Decisions (Do NOT Ask Again)
1. **Channel Brand Badge (LOCKED):** Sleek Playwright translucent dark glassmorphism pill PNG **`• GMZ`** (`gmz_badge.png`) with subtle gold border/glow at bottom-right. **NEVER write `DL 3.0` or use flat yellow `drawtext`!**
2. **Language & Tone:** Hinglish conversation with user; gripping, conversational **Hindi documentary narration** (NOT bookish/stiff Hindi).
3. **Mandatory Permanent Outro CTA (LOCKED v4.0+ — EVERY VIDEO):**
   - At the end of Act 8, right after asking *"अगला वीडियो किस टॉपिक पर होना चाहिए? नीचे कमेंट करके ज़रूर बताइए!"*, **ALWAYS close with the 1-Click Website Lead-Gen CTA** so interested viewers/clients reach out:
     > *"और हाँ, अगर आप भी ऐसा ही सिनेमैटिक वीडियो सिर्फ एक क्लिक में बनवाना चाहते हैं, तो नीचे डिस्क्रिप्शन में दी गई वेबसाइट पर ज़रूर विज़िट करें!"*
   - Pair that closing beat with a sleek gold glassmorphism website CTA lower-third card!
4. **Voiceover Engine (LOCKED v3.5+ — Single Model, Zero Tone Shifts):**
   - Lock **ONE single TTS model** (`gemini-3.1-flash-tts-preview` with **`Fenrir`** voice) across ALL acts with the exact same `STYLE_HEADER` — **NEVER mix 2.5 & 3.1 mid-video!**
   - Sentence-level chunking (`80–120` words on `। / ? / !`) with atomic per-chunk disk caching (`chunks/*.wav`), `429` exponential backoff, `150ms` breath + `40ms` `acrossfade`, and automatic post-chunk silence (`>2.5s`) / WPM sanity retries.
   - **NO `loudnorm` during TTS or concat.** Single true two-pass `loudnorm` (`I=-13:TP=-1.5:LRA=9`) runs ONLY ONCE on final mix. **NEVER use Edge-TTS.**
5. **Research Engine:** Use **`notebooklm` MCP** or verified web sources ONLY for grounded, zero-hallucination research.
6. **Visual Engine v5.1 — Daily Learn 3.0 / `cash code` "1M-View" Cinema Rules (HARD RULES):**
   - **`Omni 1.2 Flash` Variable-Length (`3s–15s`, `~3 credits/sec`, `count=1`) + Multi-Beat Director Prompting (MANDATORY!):**
     - **`3s–5s` (`9–15 cr`):** Quick single-beat punch metaphors & reactions (*1 plate paneer, ATM balance ₹0, rubber stamp thud, shock reaction*) — saves 40–60% credits!
     - **`8s` (`24 cr`):** Standard **3-beat mini-movie** (`[0–2.5s] Setup -> [2.5–5.5s] Camera Move/Action Peak -> [5.5–8s] Hero Payoff`).
     - **`12s–15s` (`36–45 cr`):** Continuous **5-beat hero sequence** (Act 1 cold-open hook, full 3D underground cutaway journey, or `cash code` 7-Lock reveal).
     - Every prompt MUST include lens specs, lighting, and synced diegetic Foley SFX (*metal clank, spark zap, engine roar, water rush, drill hum — NO speech, NO text*).
   - **Zero-Skip Video Failure & Retry Protocol (NEVER SILENTLY SKIP!):**
     1. **Retry #1 (`flow_retry` / fresh queue after 20–30s cooldown):** For `PUBLIC_ERROR_UNUSUAL_ACTIVITY` or transient server timeouts (and ensure no duplicate browser tab is open on the same Flow project).
     2. **Retry #2 (Smart Prompt / Model Rescue):** If safety filter or complex motion fails, simplify sensitive words / switch between `Omni 1.2 Flash` & `veo-3.1-fast` (or adjust duration e.g. `12s -> 8s`) and regenerate.
     3. **Controlled Fallback (ONLY if 2 retries fail or credits/quota hit 0):** NEVER leave a blank gap or silently drop the beat — immediately replace with a **dedicated custom 3D Nano-Banana-2 / Imagen cutaway** (with smooth 60fps Ken Burns + procedural Foley SFX) OR notify the user if it's a hero Act-1 clip so zero story beats are ever lost!
   - **ZERO Static PowerPoint / Blueprint Text Slides!** NEVER use dark static text-card slides as full-screen shots! Instead, put **Giant Bold Kinetic Hindi/English Impact Text** (`सन्नाटा।`, `500 FEET`, `₹80,000 vs ₹15,000`), **Thin Glowing HUD Pointer Callouts**, and **Split-Screen Comparisons (`1. PROBLEM | 2. SOLUTION`)** directly ON TOP of moving Veo / 3D cinema footage (`scripts/render_kinetic_overlays.py`)!
   - **Sentence-by-Sentence Visual Noun & Metaphor Audit (`visual_noun_map.json`):** Every concrete object AND every everyday analogy (*ATM machine, blocked heart artery, NASA satellite, computer 3D CAD map*) gets its OWN dedicated moving visual pinned to the exact Whisper timestamp!
   - **High-Diversity Visual Library (`60–85+` UNIQUE verified assets per 10–15 min video):** `15–22` Multi-Beat Veo 3.1 clips + `25–35` 3D cutaway/metaphor scenes + `20–30` visually audited real photos. Target **1–2 uses** per image (`HARD FAIL > 4` in `preflight_qa.py`), **`>=12` shots cooldown**, and fast **`2.0–3.2s` cut pacing**!
   - **Character Consistency:** Lock recurring human characters via `flow_character` / identical wardrobe description across all scenes so the documentary feels like a real film.
   - **Foley & Transition SFX:** Layer procedural cinema SFX (`whoosh`, `bass_hit`, `pop`, `riser`) on impact text drops, split-screens, and act transitions!
   - **Google Flow Rate-Limit Rule (HARD):** Queue strictly **1 job at a time** + `flow_wait` with brief breathing pauses — NEVER burst multiple jobs (`PUBLIC_ERROR_UNUSUAL_ACTIVITY`).
   - **Clean Crops (LOCKED):** `3d_images/` pre-cropped `12%` (`crop=iw*0.88:ih*0.88:0:0`) to eliminate AI star watermarks; Veo clips cropped `1.14x–1.28x`. Disable `keep_native_sfx` if Veo ever generates speech!
7. **Ultra-Fast Bulletproof Rendering (`assemble_documentary.py` v5.3):**
   - **EOF Shield (`v5.3`):** Auto-probes every video clip's true duration, auto-clamps `start` offsets safely (`real_dur - render_dur - 0.15s`), adds `tpad=stop_mode=clone` + `apad` when needed, verifies cached clip durations, cleans stale `batch_*.mkv` files, and **HARD ABORTS** if `xfade` drift `> 0.25s` — **ZERO black-screen drops ever again!**
   - Auto-detects **Intel QuickSync GPU (`h264_qsv`)** (+ `libx264` fallback), **Parallel Workers (`--workers 3`)**, **SHA-1 Smart Clip Caching**, **`2560x1440` Ken Burns**, batched `0.25s` `xfade` with lossless PCM `.mkv` intermediates & `drift = 0.000s` sync verification.
8. **Realistic Civilian Wardrobe & Anti-Police Guardrail (LOCKED):**
   - NEVER use ambiguous words like "khaki" or generic "uniform" for civilian managers, staff, or shopkeepers, as video AI models hallucinate Indian Police uniforms (epaulets, badges, stars).
   - ALWAYS specify exact civilian clothing: *"civilian formal light-blue/white button-down collared shirt with pen and spectacles"*, *"corporate navy polo shirt"*, and explicitly include *"Civilian attire ONLY, NO police uniform, NO badges, NO military epaulets"*.
9. **Smart Resolution Allocation (LOCKED):**
   - Use **`720p`** for all important narrative scenes, office interiors, close-ups, 3D financial vaults, and hero locks where clarity and realism matter.
   - Use **`360p` (14 credits)** strictly for distant expressway aerials, ambient night traffic, or rapid transitional B-roll to conserve user credits.

## Mandatory 2-Layer "Eyes & Ears" Autonomous Zero-Defect QA & Auto-Fix Gates (v5.3 — NEVER SKIP — 100% LOCAL, ZERO API!)
1. **ZERO Blind Round-Robin, ZERO Cross-Act Global Swaps & Mandatory Sub-Beat Mapping (HARD RULE):**
   - **NEVER** auto-cycle (`clip_ptr % len(clips)`) clips across an Act and **NEVER** fall back to unrelated global assets from other Acts! Before writing `shot_plan.json`, extract a 5-frame sub-beat strip of EVERY Flow clip so you know the exact second-by-second visuals inside each clip, and surgically trim out bad AI sub-beats (background police/khaki guards, Bitcoin `₿` / foreign currency, unrelated logos/fire icons, American semi-trucks where Indian trucks exist).
   - Map **every single sentence/clause** from Whisper `segments.json` (or clean sentence-proportional alignment across `narration_manifest.json` Act windows whenever Whisper drops Hindi transcription!) directly to its exact matching visual + clean `[start, start+duration]` sub-beat, and anchor **every overlay (`k01`–`k22`, including the Website Outro CTA!)** to the exact second that phrase is spoken!
   - Whenever a user-approved 1-minute Pilot (`pilot_shot_plan.json`) exists, preserve its exact Act 1 scene mapping in the full master plan.
2. **Layer 1 — Pre-Flight Automated QA (`scripts/preflight_qa.py` v5.3 BEFORE Rendering):**
   - Inspect BOTH `preflight_assets_grid.png` and `preflight_callouts_grid.png` with `read_file` before rendering.
   - **Video Clip EOF Bounds Gate (`v5.3`):** Probes every `.mp4` clip and **HARD FAILS** if ANY shot's `start + duration + xfade` exceeds real clip duration (zero black-screen xfade surprises!).
   - **Static Slide Blocker (`v5.3`):** Flags any shot using `diagrams/` or `slides/` folders.
   - Runs **100% Local Voice-Tone Consistency Forensics**, **TTS Stage-Direction / Hallucinated-Word Scanner** (catches rogue spoken *"Pause" / "पॉज़" / "बास"* or English leaks not in `acts.json` so they are surgically silenced before render!), `>=55` unique assets gate (or exact verified clip count for 100%-Flow videos), `<=4` max reuse, `>=12` shots cooldown, and `silencedetect` (`>2.5s` = FAIL).
3. **Layer 2 — Autonomous 100% Full-Video "Watch & Listen" + Black-Frame Detector + Auto-Fix Loop (`scripts/make_qa_proxy.py` v5.3 AFTER Rendering):**
   - Auto-cleans stale proxies and **auto-flags any chunk `<1.1 MB/min`** as a critical black/frozen frame anomaly!
   - **NEVER inspect only 1–2 chunks!** Open & WATCH + LISTEN to **EVERY SINGLE 2-min proxy MP4 chunk (`Part 1` through `Part N`)** directly with `read_file`.
   - Audit EVERY chunk for: (1) spoken audio glitches/rogue words, (2) literal sentence-by-sentence spoken-vs-visual alignment, (3) exact overlay & Outro CTA timing, (4) `• GMZ` badge watermark coverage, and (5) background wardrobe/currency/AI artifacts.
   - **Mandatory Auto-Fix Before Delivery:** If ANY defect is spotted in ANY chunk, **FIX IT IMMEDIATELY** (patch audio / remap `shot_plan.json` / fix overlay timestamp), re-render via SHA-1 clip cache, rebuild proxies, and re-verify BEFORE presenting the final video to the user!

## Active YouTube Channel & Publishing Workflow (Permanent Memory)
- **Channel:** **`GMZ DECODED`** (`@GMZDECODED`, Channel ID: `UCJ6emCfdgkWnLxvEjl9Zj-Q`, Email: `gmzdecoded@gmail.com`)
- **Contact / CTA Placeholder in Descriptions:** `👉 gmzdecoded@gmail.com (Website Coming Soon!)` *(update once user's website goes live)*
- **Publishing Division of Labor (LOCKED):**
  - User directly selects/drops local `F:\` `.mp4` videos and custom thumbnails in Chrome YouTube Studio (browser automation cannot upload `F:\` paths directly).
  - Agent automates all YouTube Studio metadata via Chrome remote debugging (`127.0.0.1:9222`): High-CTR Hindi+English Title, Hindi Description with exact `narration_manifest.json` chapters + CTA + 10 hashtags, `No, it's not Made for Kids`, `Yes, AI was used`, `<500 char` SEO Tags, `Hindi` Video & Title/Description Language, `Education` Category, and **Schedule** (`17:45 IST`, every **3 days** — NEVER publish early!).
  - After scheduling each video, always give the user a **1-Click Copy ChatGPT High-CTR Thumbnail Prompt** (clean bottom-right corner, 3 bold Hindi blocks: Yellow + White + Red badge) and keep the Studio Edit page open.
- **Completed Launch Calendar (`GMZ DECODED`):**
  1. **Petrol Pump Business** (`25 Nov 2026, 17:45 IST`) — `https://youtu.be/nYnXIsVMPN8`
  2. **Soviet Buran Shuttle v3.5** (`28 Nov 2026, 17:45 IST`) — `https://youtu.be/Lt7MQL1HCkA`
  3. **Dubai Palm Jumeirah** (`1 Dec 2026, 17:45 IST`) — `https://youtu.be/Ae6V5VH52ac`
  4. **Svalbard Global Seed Vault** (`4 Dec 2026, 17:45 IST`) — `https://youtu.be/cQhfUIWODoI`
  - **Next scheduled slot:** `7 Dec 2026, 17:45 IST` (every 3 days).
- **GitHub Skill Repo (Synced at v5.3):** `https://github.com/gmakercodeby-arch/ai-documentary-video-studio-skill` (local sync folder: `f:\Daily Learn 3.0\_gh_skill_sync\ai-documentary-video-studio-skill`)

## v5.4 Upgrade — 97%-Video Sub-Beat Lock & Full-Screen 9:16 Viral Tech Shorts (Locked)
- **97%-Video Documentary Mode:** Audit every Flow clip via 5-frame sub-beat strip (`veo_subbeats_grid.png`), lock clean `[win_start, win_end]` windows to trim AI morphs/props, force-pin matching hero clips to kinetic overlays (`FORCE_OVERLAY_CLIP`), and run a strict `<3` cooldown post-pass (`0` violations).
- **Full-Screen 9:16 Tech/AI Shorts (NEVER Movie-Recap Black Bars!):**
  - Generate native `9:16` Flow clips (`aspect="9:16"`, `crop 88%` top-left to erase Flow diamond) for full-bleed `1080×1920` immersion; frame any `16:9` contrast shots inside a **Blurred Motion Bokeh Background** (`gblur=sigma=28`).
  - **Zero permanent top banner boxes:** Use a temporary `0–2.65s` kinetic hook + floating 2.5s spec badges, **multi-layered cinema SFX** (`sub-bass hit`, `whoosh`, `zap`, `riser`, `pop`), **Whisper word-locked Devanagari ASS captions** (`Spacing=0`, `MarginV=405`, `0` overlap with `bottom: 235px` CTA pill), and a **Curiosity-Gap CTA** driving clicks to the 16:9 master.
  - **FFmpeg Short Stability:** Enforce even crop dimensions (`trunc(.../2)*2`), `-video_track_timescale 30000`, and re-encoded concat (`libx264`) instead of `-c copy`.
