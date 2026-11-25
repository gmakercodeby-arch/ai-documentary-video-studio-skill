---
name: gmz-viral-topic-hunter
description: Automated Multi-Channel YouTube Outlier & Viral Topic Discovery Skill for GMZ DECODED. Uses local yt-dlp to scan 19+ top Hindi & Global Engineering/Documentary/AI channels, calculates outlier multipliers (views vs channel median), detects Global-to-Hindi content arbitrage opportunities, scores 3D Google Flow visual potential, and outputs high-CTR documentary & 9:16 Short ideas.
---

# GMZ Viral Topic Hunter (`v1.1`)

Use this skill **before picking any new documentary or Short topic** for `GMZ DECODED` so every video rides proven viral psychology instead of random guesses!

## Why Outlier Hunting Beats Guessing
- A `1M` view video on a channel averaging `1M` views is ordinary.
- A `1.5M` view video on a channel whose **median is `150K`** (`10.0x` Outlier!) proves the **topic + title + thumbnail curiosity gap** broke outside subscribers into the broader YouTube Home Feed.
- **Global-to-Hindi Arbitrage Secret:** Global English engineering channels (`@BranchEducation`, `@MustardChannel`, `@RealEngineering`, `@SabinCivil`, `@SabinMechanical`, `@Animagraffs`, `@TheB1M`, `@PracticalEngineeringChannel`, `@fern-tv`, `@Wendoverproductions`, `@ColdFusion`) often discover insane breakthroughs months before Indian Hindi audiences see them. Turning a `4x–15x` English engineering outlier into a **10–16 min Hindi 3D Documentary + Full-Screen 9:16 Short** on `GMZ DECODED` is the highest-ROI growth formula.

---

## Step 1: Run Automated Outlier Scan (Zero API Key Needed!)
Scan all **19 curated** Hindi (`6`) & Global (`13`) benchmark channels (`~20–30s`):

```powershell
# Long-form documentary topics (>= 4 min, >= 150K views noise floor)
python "<SKILL_DIR>/scripts/hunt_viral_topics.py" --group all --min-mult 1.8 --min-views 150000 --out-dir "./topic_research"

# Or scan only Global channels for untapped Hindi arbitrage ideas
python "<SKILL_DIR>/scripts/hunt_viral_topics.py" --group global --min-mult 2.0 --min-views 250000 --out-dir "./topic_research_global"

# Or scan /shorts tabs for viral vertical hooks
python "<SKILL_DIR>/scripts/hunt_viral_topics.py" --shorts --min-mult 2.5 --min-views 500000 --out-dir "./topic_research_shorts"
```

Outputs `viral_report.md` and `viral_report.json` ranked by **`gmz_score`** (`outlier multiplier × 3D cinema fit`).

---

## Step 2: Filter Through the "GMZ 4-Question Viral Gate"
For the top outliers in `viral_report.md`, apply this strict filter before recommending to the user:
1. **Curiosity Paradox Check:** Can the premise be summed up in a 1-sentence paradox? (*e.g., "No jet engine, no propellers — how is this flying?"* / *"Built to fail in 1988, why is this Soviet shuttle still unbeaten?"*)
2. **3D Google Flow Cinema Check (`Score >= 7/10`):** Does it naturally yield X-ray cutaways, wind tunnels, underground vaults, mega-machines, aircraft, ships, or secret factories in Google Flow (`Omni 1.2`) + real proof photos? Avoid pure abstract finance/software talk!
3. **India + Global Relevance:** Will an Indian viewer also care? (*Cost in Crore/₹, comparison to Indian cities/trains/flights/megaprojects, "क्या भारत में भी ऐसा बनेगा?"*).
4. **Freshness / Non-Saturation in Hindi:** Cross-check with `@DailyLearn3.0`, `@GetSetFly`, `@FactTechz`, `@ZemTV.Official` results in the same report — prioritize **untapped Global hits (`en` outliers)** or **2–4x fresher angles**!

---

## Step 3: Present Ranked Ideas as Ready-to-Produce Packages
For each top idea presented to the user, ALWAYS deliver:
1. **Source Outlier Proof** (*Channel + views vs median + multiplier `Xx`*)
2. **High-CTR Hindi+English Title + 3-Block Thumbnail Text** (Yellow + White + Red Badge)
3. **0–15s Opening Paradox Hook + 3-Second Short Spin-off Angle**
4. **Why It Works in Google Flow** (`3–4` killer 3D cutaway scenes!)
