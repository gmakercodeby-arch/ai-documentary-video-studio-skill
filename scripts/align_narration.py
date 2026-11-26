"""
GMZ Documentary Studio v3.0 — Forced Audio-to-Visual Sentence Alignment Engine
Runs local faster-whisper on master_narration.mp3 with vad_filter=False & word_timestamps=True
so quiet Hindi syllables and ending lines are NEVER dropped from segments.json.
"""

import argparse
import json
from pathlib import Path
from faster_whisper import WhisperModel


def main():
    ap = argparse.ArgumentParser(description="Extract exact Hindi/English sentence & word timestamps from narration audio.")
    ap.add_argument("--audio", required=True, help="Path to master_narration.mp3 or act mp3")
    ap.add_argument("--out", required=True, help="Output JSON path for timestamped segments")
    ap.add_argument("--model", default="small", help="Whisper model size (tiny, base, small, medium)")
    ap.add_argument("--language", default="hi", help="Language code (default: hi)")
    args = ap.parse_args()

    print(f"Loading faster-whisper ({args.model}) on CPU (vad_filter=False, word_timestamps=True)...")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        args.audio,
        language=args.language,
        word_timestamps=True,
        vad_filter=False,
        condition_on_previous_text=True,
    )

    out_segments = []
    prev_end = 0.0
    gap_warnings = []
    for seg in segments:
        words = [
            {"start": round(w.start, 3), "end": round(w.end, 3), "word": w.word.strip()}
            for w in (seg.words or [])
            if w.word and w.word.strip()
        ]
        gap = round(seg.start - prev_end, 3)
        if gap > 2.5:
            gap_warnings.append({"from": round(prev_end, 3), "to": round(seg.start, 3), "gap_sec": gap})
            print(f"  [WARN] Silence/gap of {gap:.2f}s detected ({prev_end:.2f}s -> {seg.start:.2f}s)")
        out_segments.append({
            "id": seg.id,
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "duration": round(seg.end - seg.start, 3),
            "text": seg.text.strip(),
            "words": words,
        })
        prev_end = seg.end
        print(f"  [{seg.start:6.2f}s -> {seg.end:6.2f}s] {seg.text.strip()}")

    trailing_gap = round(info.duration - prev_end, 3)
    if trailing_gap > 2.5:
        gap_warnings.append({"from": round(prev_end, 3), "to": round(info.duration, 3), "gap_sec": trailing_gap})
        print(f"  [WARN] Trailing silence of {trailing_gap:.2f}s detected ({prev_end:.2f}s -> {info.duration:.2f}s)")

    result = {
        "audio": str(Path(args.audio).resolve()),
        "duration": round(info.duration, 3),
        "last_spoken_end": round(prev_end, 3),
        "language": info.language,
        "gap_warnings": gap_warnings,
        "segments": out_segments,
    }
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDONE! Saved {len(out_segments)} aligned segments (audio={info.duration:.2f}s, last_word={prev_end:.2f}s) -> {args.out}")


if __name__ == "__main__":
    main()
