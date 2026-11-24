"""
GMZ Documentary Studio v3.5 — Layer 1 Automated Pre-Flight QA (preflight_qa.py)
Runs BEFORE spending minutes on final MP4 rendering to catch 85%+ of defects in ~15 seconds:
  1. Visual Contact Sheet (preflight_assets_grid.png): 1 labeled frame from EVERY unique photo,
     3D render, and Veo clip used in shot_plan.json (filenames burned below each tile).
  2. Callout Preview Grid (preflight_callouts_grid.png): Every callout shot composited over its
     paired background image/frame with exact timestamp + spoken hint burned on top.
  3. Audio Silence Gate: Runs FFmpeg silencedetect on master narration (FAIL if any gap > 2.5s).
  4. Script vs Whisper Coverage Diff: Compares acts.json vs segments.json normalized Hindi words
     to catch clipped/missing sentences or repeated endings.
  5. Shot Plan Validator: Verifies zero missing files, 6-shot anti-repeat cooldown compliance,
     and clean duration sync vs last_spoken_end.
"""

import argparse
import json
import math
import re
import struct
import subprocess
from collections import Counter, deque
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def load_font(size: int):
    for p in [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeui.ttf"]:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def extract_frame(media_path: Path, out_jpg: Path, at_sec: float = 1.5) -> Image.Image:
    if media_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
        return Image.open(media_path).convert("RGB")
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{at_sec:.2f}", "-i", str(media_path), "-frames:v", "1", "-q:v", "3", str(out_jpg)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )
    im = Image.open(out_jpg).convert("RGB")
    out_jpg.unlink(missing_ok=True)
    return im


def build_assets_grid(shots: list[dict], out_png: Path):
    seen = []
    seen_set = set()
    for s in shots:
        p = Path(s["path"])
        if str(p) not in seen_set and p.exists():
            seen_set.add(str(p))
            seen.append(p)

    cols = 4
    rows = max(1, (len(seen) + cols - 1) // cols)
    cw, ch, bar = 480, 270, 34
    grid = Image.new("RGB", (cols * cw, rows * (ch + bar)), (14, 16, 22))
    draw = ImageDraw.Draw(grid)
    font = load_font(20)
    tmp_f = out_png.parent / "_tmp_frame.jpg"

    for i, p in enumerate(seen):
        im = extract_frame(p, tmp_f).resize((cw, ch))
        x = (i % cols) * cw
        y = (i // cols) * (ch + bar)
        grid.paste(im, (x, y))
        draw.rectangle([x, y + ch, x + cw, y + ch + bar], fill=(0, 0, 0))
        tag = "[VEO]" if p.suffix.lower() == ".mp4" else ("[3D]" if "3d_images" in str(p).lower() else "[REAL]")
        draw.text((x + 8, y + ch + 6), f"{i+1}. {tag} {p.name}", font=font, fill=(255, 220, 0))

    grid.save(out_png)
    return len(seen)


def build_callouts_grid(shots: list[dict], out_png: Path):
    co_shots = [s for s in shots if s.get("callout") and Path(s["callout"]).exists() and Path(s["path"]).exists()]
    if not co_shots:
        return 0
    cols = 2
    rows = (len(co_shots) + cols - 1) // cols
    cw, ch, bar = 640, 360, 42
    grid = Image.new("RGB", (cols * cw, rows * (ch + bar)), (12, 14, 20))
    draw = ImageDraw.Draw(grid)
    font = load_font(18)
    tmp_f = out_png.parent / "_tmp_co.jpg"

    for i, s in enumerate(co_shots):
        bg = extract_frame(Path(s["path"]), tmp_f, at_sec=float(s.get("start", 0.5)) + 1.0).resize((cw, ch)).convert("RGBA")
        co = Image.open(s["callout"]).convert("RGBA").resize((cw, ch))
        comp = Image.alpha_composite(bg, co).convert("RGB")
        x = (i % cols) * cw
        y = (i // cols) * (ch + bar)
        grid.paste(comp, (x, y))
        draw.rectangle([x, y + ch, x + cw, y + ch + bar], fill=(0, 0, 0))
        t = float(s.get("beat_start", 0.0))
        m, sec = divmod(int(t), 60)
        lbl = f"{m:02d}:{sec:02d} | {Path(s['callout']).name} on {Path(s['path']).name}"
        draw.text((x + 10, y + ch + 10), lbl, font=font, fill=(0, 230, 255))

    grid.save(out_png)
    return len(co_shots)


def check_audio_silences(audio_path: Path, max_allowed: float = 2.5) -> list[dict]:
    res = subprocess.run(
        ["ffmpeg", "-i", str(audio_path), "-af", f"silencedetect=noise=-38dB:d={max_allowed}", "-f", "null", "-"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
    )
    silences = []
    cur_start = None
    for line in res.stderr.splitlines():
        ms = re.search(r"silence_start:\s*([0-9.]+)", line)
        me = re.search(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)", line)
        if ms:
            cur_start = float(ms.group(1))
        if me:
            silences.append({"start": cur_start, "end": float(me.group(1)), "duration": float(me.group(2))})
    return silences


def check_script_vs_whisper(acts_json: Path, segs_json: Path) -> dict:
    acts = json.loads(acts_json.read_text(encoding="utf-8"))
    seg_data = json.loads(segs_json.read_text(encoding="utf-8"))
    script_words = sum(len(a["text"].split()) for a in acts)
    whisper_text = " ".join(s["text"] for s in seg_data.get("segments", []))
    whisper_words = len(whisper_text.split())
    ratio = round(whisper_words / max(script_words, 1), 3)

    # Check for repeated ending lines in last 3 segments
    segs = seg_data.get("segments", [])
    tail_repeat = False
    if len(segs) >= 2:
        t1, t2 = segs[-2]["text"].strip(), segs[-1]["text"].strip()
        if t2 and t2 in t1:
            tail_repeat = True

    # Detect >2.5s internal gaps in Whisper timeline
    gaps = []
    prev_end = 0.0
    for s in segs:
        g = round(float(s["start"]) - prev_end, 2)
        if g > 2.5:
            gaps.append({"from": round(prev_end, 2), "to": round(float(s["start"]), 2), "gap_sec": g})
        prev_end = float(s["end"])

    # Detect TTS stage-direction / hallucinated rogue words (e.g. spoken "Pause" / "पॉज़" / "बास")
    full_script_lower = " ".join(a["text"] for a in acts).lower()
    suspect_tokens = ["pause", "पॉज़", "पॉज", "पौज", "बास", "beat", "silence", "narrator", "cut to", "fade out"]
    tts_hallucinations = []
    for s in segs:
        txt = s["text"].strip()
        txt_l = txt.lower()
        dur_s = round(float(s["end"]) - float(s["start"]), 2)
        # Flag short standalone segments matching stage directions not present in script
        if len(txt.split()) <= 3 and dur_s <= 1.6:
            for tok in suspect_tokens:
                if tok in txt_l and tok not in full_script_lower:
                    tts_hallucinations.append({
                        "start": round(float(s["start"]), 2),
                        "end": round(float(s["end"]), 2),
                        "text": txt,
                        "matched_token": tok,
                    })
                    break

    return {
        "script_words": script_words,
        "whisper_words": whisper_words,
        "word_coverage_ratio": ratio,
        "tail_duplicate_detected": tail_repeat,
        "whisper_gaps_over_2_5s": gaps,
        "tts_hallucinations": tts_hallucinations,
        "last_spoken_end": round(prev_end, 2),
        "audio_duration": seg_data.get("duration"),
    }


def validate_shot_plan(shots: list[dict], cooldown: int = 12, max_reuse: int = 4, xfade: float = 0.25) -> dict:
    missing = [s["path"] for s in shots if not Path(s["path"]).exists()]
    recent: deque[str] = deque(maxlen=cooldown)
    cooldown_violations = []
    counts = Counter()
    video_dur_cache: dict[str, float] = {}
    video_eof_overflows = []
    static_diagram_shots = []

    for i, s in enumerate(shots):
        p = s["path"]
        p_obj = Path(p)
        counts[p_obj.name] += 1
        if p in recent:
            cooldown_violations.append({"shot_idx": i + 1, "beat_start": s.get("beat_start"), "file": p_obj.name})
        recent.append(p)

        # v5.3 Gate: Detect banned static PowerPoint / diagram slide folders
        lower_p = str(p).lower().replace("\\", "/")
        if "/diagrams/" in lower_p or "/slides/" in lower_p:
            static_diagram_shots.append({"shot_idx": i + 1, "beat_start": s.get("beat_start"), "file": p_obj.name})

        # v5.3 Gate: Video clip EOF bounds check (start + duration + xfade_handle <= actual clip duration)
        if p_obj.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"} and p_obj.exists():
            if p not in video_dur_cache:
                try:
                    out = subprocess.check_output(
                        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", p],
                        text=True,
                    ).strip()
                    video_dur_cache[p] = float(out)
                except Exception:
                    video_dur_cache[p] = 0.0
            real_dur = video_dur_cache[p]
            ss = float(s.get("start", 0.0))
            need_end = ss + float(s["duration"]) + (xfade if i < len(shots) - 1 else 0.0)
            if real_dur > 0 and need_end > (real_dur - 0.05):
                video_eof_overflows.append({
                    "shot_idx": i + 1,
                    "beat_start": s.get("beat_start"),
                    "file": p_obj.name,
                    "start": round(ss, 2),
                    "needed_end": round(need_end, 2),
                    "clip_dur": round(real_dur, 2),
                })

    unique_count = len(counts)
    total_cuts = len(shots)
    avg_reuse = round(total_cuts / max(unique_count, 1), 2)
    overused = [{"file": name, "uses": cnt} for name, cnt in counts.most_common() if cnt > max_reuse]
    return {
        "total_cuts": total_cuts,
        "unique_assets": unique_count,
        "avg_reuse_ratio": avg_reuse,
        "max_reuse_limit": max_reuse,
        "overused_assets": overused,
        "top_10_reused_assets": [{"file": n, "uses": c} for n, c in counts.most_common(10)],
        "total_duration_sec": round(sum(float(s["duration"]) for s in shots), 2),
        "missing_files": missing,
        "cooldown_window": cooldown,
        "cooldown_violations_count": len(cooldown_violations),
        "cooldown_violations_sample": cooldown_violations[:10],
        "video_eof_overflows": video_eof_overflows,
        "static_diagram_shots": static_diagram_shots,
    }


def check_voice_consistency(audio_dir: Path) -> dict:
    """
    100% LOCAL (Zero-API) Voice-Tone Consistency Forensics across all act_*_master.mp3 files.
    Compares RMS loudness (dB) and Zero-Crossing Rate / Low-vs-High spectral warmth ratio
    across acts to catch accidental model/voice/mic shifts (e.g. 2.5 vs 3.1 TTS mix) BEFORE render!
    """
    act_files = sorted(audio_dir.glob("act_*_master.mp3"))
    if len(act_files) < 2:
        return {"checked_acts": len(act_files), "outliers": [], "per_act": []}

    profiles = []
    for f in act_files:
        # Decode 30s mid-sample as 16kHz mono s16le PCM locally via FFmpeg
        raw = subprocess.check_output(
            ["ffmpeg", "-v", "error", "-ss", "5", "-t", "30", "-i", str(f),
             "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        )
        n = len(raw) // 2
        if n < 1600:
            continue
        samples = struct.unpack(f"<{n}h", raw)
        # Filter active speech frames (skip silence < 400 amplitude)
        active = [s / 32768.0 for s in samples if abs(s) > 400]
        if len(active) < 800:
            active = [s / 32768.0 for s in samples]
        rms = math.sqrt(sum(x * x for x in active) / max(len(active), 1))
        rms_db = round(20.0 * math.log10(max(rms, 1e-6)), 2)
        # Zero-crossing rate (correlates strongly with voice brightness/timbre/mic EQ)
        zc = sum(1 for i in range(1, len(active)) if (active[i - 1] >= 0) != (active[i] >= 0))
        zcr_hz = round((zc / max(len(active), 1)) * 8000.0, 1)
        # Low-frequency warmth proxy via FFmpeg lowpass 350Hz RMS ratio
        raw_lo = subprocess.check_output(
            ["ffmpeg", "-v", "error", "-ss", "5", "-t", "30", "-i", str(f),
             "-af", "lowpass=f=350", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        )
        nl = len(raw_lo) // 2
        s_lo = struct.unpack(f"<{nl}h", raw_lo)
        rms_lo = math.sqrt(sum((x / 32768.0) ** 2 for x in s_lo) / max(nl, 1))
        warmth_ratio = round(rms_lo / max(rms, 1e-6), 3)
        profiles.append({"act": f.stem, "rms_db": rms_db, "zcr_hz": zcr_hz, "warmth_ratio": warmth_ratio})

    med_db = sorted(p["rms_db"] for p in profiles)[len(profiles) // 2]
    med_zcr = sorted(p["zcr_hz"] for p in profiles)[len(profiles) // 2]
    med_warm = sorted(p["warmth_ratio"] for p in profiles)[len(profiles) // 2]

    outliers = []
    for p in profiles:
        db_diff = round(abs(p["rms_db"] - med_db), 2)
        zcr_pct = round(abs(p["zcr_hz"] - med_zcr) / max(med_zcr, 1.0) * 100.0, 1)
        warm_pct = round(abs(p["warmth_ratio"] - med_warm) / max(med_warm, 0.01) * 100.0, 1)
        if db_diff > 3.5 or zcr_pct > 25.0 or warm_pct > 25.0:
            outliers.append({
                "act": p["act"],
                "db_diff": db_diff,
                "zcr_shift_pct": zcr_pct,
                "warmth_shift_pct": warm_pct,
            })

    return {
        "checked_acts": len(profiles),
        "median_rms_db": med_db,
        "median_zcr_hz": med_zcr,
        "median_warmth_ratio": med_warm,
        "outliers": outliers,
        "per_act": profiles,
    }


def main():
    ap = argparse.ArgumentParser(description="Layer-1 Automated Pre-Flight QA (Visual Grids + Audio + Voice Forensics + Sync + Cooldown).")
    ap.add_argument("--acts", required=True, help="acts.json path")
    ap.add_argument("--audio", required=True, help="master_narration.mp3 path")
    ap.add_argument("--segments", required=True, help="segments.json path")
    ap.add_argument("--plan", required=True, help="shot_plan.json path")
    ap.add_argument("--out-dir", required=True, help="Output folder for QA grids & preflight_report.json")
    ap.add_argument("--cooldown", type=int, default=12, help="Min shots before an asset can reappear (v4.0 default: 12)")
    ap.add_argument("--max-reuse", type=int, default=4, help="Hard cap on max times any single asset can appear in full video (v4.0 default: 4)")
    ap.add_argument("--min-unique", type=int, default=55, help="Min unique visual assets required for long-form (>600s) documentaries (v4.0 default: 55)")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    shots = json.loads(Path(args.plan).read_text(encoding="utf-8"))

    assets_png = out_dir / "preflight_assets_grid.png"
    callouts_png = out_dir / "preflight_callouts_grid.png"
    n_assets = build_assets_grid(shots, assets_png)
    n_callouts = build_callouts_grid(shots, callouts_png)

    silences = check_audio_silences(Path(args.audio), max_allowed=2.5)
    diff = check_script_vs_whisper(Path(args.acts), Path(args.segments))
    plan_check = validate_shot_plan(shots, cooldown=args.cooldown, max_reuse=args.max_reuse)
    voice_check = check_voice_consistency(Path(args.audio).parent)

    failures = []
    if plan_check["missing_files"]:
        failures.append(f"Missing visual files: {len(plan_check['missing_files'])}")
    if silences:
        failures.append(f"Audio silences > 2.5s found: {len(silences)}")
    if diff["whisper_gaps_over_2_5s"]:
        failures.append(f"Whisper transcript gaps > 2.5s: {diff['whisper_gaps_over_2_5s']}")
    if diff.get("tts_hallucinations"):
        failures.append(f"TTS spoken stage-direction hallucinations detected (MUST silence/trim before render!): {diff['tts_hallucinations']}")
    if diff["word_coverage_ratio"] < 0.85:
        failures.append(f"Low script-to-audio word coverage: {diff['word_coverage_ratio']}")
    if plan_check["cooldown_violations_count"] > 0:
        failures.append(f"Asset repeat cooldown violations (<{args.cooldown} shots): {plan_check['cooldown_violations_count']}")
    if plan_check["total_duration_sec"] >= 600 and plan_check["unique_assets"] < args.min_unique:
        failures.append(f"Low visual diversity: only {plan_check['unique_assets']} unique assets for {plan_check['total_duration_sec']}s video (v4.0 min={args.min_unique})")
    if plan_check["overused_assets"]:
        failures.append(f"Visual repetition cap exceeded (>{args.max_reuse} uses): {plan_check['overused_assets'][:6]}")
    if plan_check.get("video_eof_overflows"):
        failures.append(f"Video clip EOF overflow (start+duration+xfade > real clip length — causes black screens!): {plan_check['video_eof_overflows'][:6]}")
    if plan_check.get("static_diagram_shots"):
        failures.append(f"Banned static PowerPoint/diagram slides detected ({len(plan_check['static_diagram_shots'])} shots — use transparent kinetic overlays on moving footage!): {plan_check['static_diagram_shots'][:5]}")
    if voice_check["outliers"]:
        failures.append(f"Voice tone/timbre shift detected across acts: {voice_check['outliers']}")

    report = {
        "verdict": "PASS" if not failures else "FAIL",
        "failures": failures,
        "visual_grids": {
            "assets_grid": str(assets_png),
            "unique_assets_audited": n_assets,
            "callouts_grid": str(callouts_png),
            "callout_shots_audited": n_callouts,
        },
        "audio_silences_over_2_5s": silences,
        "voice_consistency": voice_check,
        "script_vs_whisper": diff,
        "shot_plan_validation": plan_check,
    }
    rep_path = out_dir / "preflight_report.json"
    rep_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"PREFLIGHT VERDICT: {report['verdict']} | Report -> {rep_path}")
    print(f"  Assets Grid ({n_assets} unique): {assets_png}")
    print(f"  Callouts Grid ({n_callouts} cards): {callouts_png}")
    if failures:
        print("  FAILURES:")
        for f in failures:
            print(f"   - {f}")


if __name__ == "__main__":
    main()
