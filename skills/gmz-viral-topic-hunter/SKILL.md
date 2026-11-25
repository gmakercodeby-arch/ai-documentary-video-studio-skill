---
name: gmz-viral-topic-hunter
description: Automated Multi-Channel YouTube Outlier & Viral Topic Discovery Skill for GMZ DECODED. Uses local yt-dlp to scan 31+ top Hindi & Global Engineering/Documentary/Business Case-Study channels (including Daily Learn 3.0, HinExp, Think School, Nitish Rajput, Branch Education, Animagraffs, MagnatesMedia), calculates outlier multipliers, detects Global-to-Hindi arbitrage opportunities, and outputs high-CTR documentary & 9:16 Short ideas.
---

# GMZ Viral Topic Hunter (`v2.0`)

Use this skill **before picking any new documentary or Short topic** for `GMZ DECODED` so every video rides proven viral psychology instead of random guesses!

## Dual-Engine Strategy (Engineering + Business Case Studies)
We track **31 curated channels** across **2 proven high-RPM pillars**:
1. **3D Engineering & Megastructures (`@DailyLearn3.0`, `@BranchEducation`, `@Animagraffs`, `@SabinCivil`, `@RealEngineering`, `@TheB1M`, `@MustardChannel`):** Extreme tunnels, jets, microchips, Starlink, underground water & impossible structures.
2. **Desi & Global Business Case Studies (`@HinExpofficial`, `@ThinkSchool`, `@NitishRajput`, `@AevyTV`, `@Zero1byZerodha`, `@LabourLawAdvisor`, `@MagnatesMedia`, `@Moon-Real`, `@HowMoneyWorks`, `@ModernMBA`):** Nostalgia vehicle/brand paradoxes (*Toyota Qualis `4M`, Hero Honda Split `1.8M`, Big Bazaar `1.1M`*), desi unit economics (*Bus `2.1M`, Petrol Pump `1.2M`, Transport `693K`*), and corporate espionage (*Chinese Spy in Nvidia `496K`*).
- **GMZ Unfair Advantage:** Channels like `HinExp` pull `500K–4M` views using *flat 2D AI illustrations*. Producing those exact high-curiosity topics in **GMZ's `1080p @ 60fps` 3D Google Flow cinema + Foley SFX + Playwright HUD callouts** beats 2D explainers on retention & visual authority!

---

## Step 1: Run Automated Outlier Scan (Zero API Key Needed!)
Scan all **31 curated** Hindi (`13`) & Global (`18`) channels (`~25–40s`):

```powershell
# All 31 channels (Engineering + Business Case Studies)
python "<SKILL_DIR>/scripts/hunt_viral_topics.py" --group all --min-mult 1.8 --min-views 150000 --out-dir "./topic_research"

# Focus ONLY on Business Case Studies (HinExp, Think School, MagnatesMedia, Moon, etc.)
python "<SKILL_DIR>/scripts/hunt_viral_topics.py" --group business --min-mult 1.8 --min-views 150000 --out-dir "./topic_research_business"

# Focus ONLY on Science & 3D Engineering Arbitrage
python "<SKILL_DIR>/scripts/hunt_viral_topics.py" --group science --min-mult 1.8 --min-views 150000 --out-dir "./topic_research_science"

# Focus on Global EN channels for untapped Hindi arbitrage
python "<SKILL_DIR>/scripts/hunt_viral_topics.py" --group global --min-mult 2.0 --min-views 250000 --out-dir "./topic_research_global"

# Scan /shorts tabs for high-velocity 9:16 hooks
python "<SKILL_DIR>/scripts/hunt_viral_topics.py" --shorts --min-mult 2.5 --min-views 500000 --out-dir "./topic_research_shorts"
```

Outputs `viral_report.md` and `viral_report.json` ranked by **`gmz_score`** (`outlier multiplier × 3D cinema fit`).

---

## Step 2: Filter Through the "GMZ 4-Question Viral Gate"
1. **Curiosity Paradox Check:** Can the premise fit in 1 punchy contradiction? (*"Peak sales ke bawajood Toyota ne Qualis ko khud kyon band kiya?"* / *"50 km samundar ke niche train kaise chalti hai?"*)
2. **Everyday Indian Stakes or Nostalgia:** Avoid abstract textbooks (*"Indian Finance System"* flopped `19K` on HinExp). Pick things Indians touch, drive, buy, or dream about (**Qualis, Petrol Pump, Bus Business, Tata Nano, Balaji vs Lay's, Starlink, Airport, Skyscraper**).
3. **3D Google Flow Cinema Check (`Score >= 7/10`):** Can Google Flow (`Omni 1.2`) visualize cars/factories/tunnels/chips/boardrooms/spy raids + real proof photos instead of talking heads?
4. **Freshness / Global-to-Hindi Arbitrage:** Prioritize **untapped Global hits (`en` outliers)** OR **2D-to-3D upgrades** over saturated old Hindi topics (*e.g. skip old 2016 Swiss Bank cliches*).

---

## Step 3: Present Ranked Ideas as Ready-to-Produce Packages
For each top idea presented to the user, ALWAYS deliver:
1. **Source Outlier Proof** (*Channel + views vs median + multiplier `Xx`*)
2. **High-CTR Hindi+English Title + 3-Block Thumbnail Text** (Yellow + White + Red Badge)
3. **0–15s Opening Paradox Hook + 3-Second Short Spin-off Angle**
4. **Why It Works in Google Flow** (`3–4` killer 3D cinema / cutaway scenes!)
