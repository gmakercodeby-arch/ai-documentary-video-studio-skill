"""
AI Documentary Studio v4.0 — Pro Documentary Voiceover Generator
- Locks ONE single TTS model (gemini-3.1-flash-tts-preview) across all acts with identical STYLE_HEADER
  so voice tone NEVER shifts mid-video.
- Splits each act into sentence-level chunks (~60-90 words, splitting ONLY at । / . / ? / !)
  and stitches chunks with 150ms natural breath padding + 40ms acrossfade.
- Keeps warm baritone EQ + gentle compression ONLY (NO premature loudnorm; single true two-pass
  loudnorm runs ONLY once on the final mixed master in assemble_documentary.py).
- Runs automatic post-TTS sanity checks per chunk & act (silence > 2.5s or abnormal WPM) and retries.
"""

import argparse
import json
import os
import re
import subprocess
import time
import wave
from pathlib import Path
from google import genai
from google.genai import types

LOCKED_MODEL = "gemini-3.1-flash-tts-preview"
DEFAULT_VOICE = "Fenrir"

STYLE_HEADER = (
    "Narrate this like a serious, deep-voiced YouTube documentary storyteller "
    "(heavy, warm, chesty baritone male voice, natural conversational delivery). "
    "CRITICAL PACING RULE: Speak at a STEADY, measured documentary pace of ~155-162 words per minute — "
    "NEVER rush, NEVER speed up into breathless fast talking, and NEVER leave long dead pauses! "
    "Give natural 0.25-second breath pauses between sentences, build controlled urgency on key reveals, "
    "and drop your voice deeper with a 0.4-second pause before dramatic punchlines:\n\n"
)

# Warm baritone EQ + gentle compression ONLY (NO loudnorm here — single two-pass loudnorm happens in final mix!)
CINEMA_VOCAL_EQ = (
    "aresample=44100,aformat=channel_layouts=mono,"
    "highpass=f=65,"
    "equalizer=f=115:t=q:w=1.1:g=3.2,"
    "equalizer=f=280:t=q:w=1.2:g=-1.5,"
    "equalizer=f=3200:t=q:w=1.4:g=2.0,"
    "acompressor=threshold=-18dB:ratio=2.8:attack=10:release=80:makeup=2"
)


def load_api_key(env_path: str | None = None) -> str:
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"].strip()
    candidates = [Path(env_path)] if env_path else [Path.cwd() / ".env", Path.home() / ".env"]
    for p in candidates:
        if p and p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("GEMINI_API_KEY not found in environment or .env file! Run scripts/check_setup.py.")


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        text=True,
    ).strip()
    return float(out)


def split_sentence_chunks(text: str, min_words: int = 60, max_words: int = 90) -> list[str]:
    """Split narration ONLY on sentence boundaries (। / . / ? / !) into ~60-90 word chunks."""
    sentences = [s.strip() for s in re.split(r"(?<=[।.?!])\s+", text.strip()) if s.strip()]
    chunks: list[str] = []
    cur: list[str] = []
    cur_words = 0

    for sent in sentences:
        sw = len(sent.split())
        if cur and (cur_words + sw > max_words) and cur_words >= min_words:
            chunks.append(" ".join(cur))
            cur = [sent]
            cur_words = sw
        else:
            cur.append(sent)
            cur_words += sw
    if cur:
        if chunks and cur_words < 25 and (len(chunks[-1].split()) + cur_words <= max_words + 20):
            chunks[-1] = chunks[-1] + " " + " ".join(cur)
        else:
            chunks.append(" ".join(cur))
    return chunks


def detect_max_internal_silence(audio_path: Path, noise_db: str = "-38dB", min_dur: float = 2.5) -> float:
    """Return longest internal silence duration (seconds) above min_dur, or 0.0 if none."""
    res = subprocess.run(
        ["ffmpeg", "-i", str(audio_path), "-af", f"silencedetect=noise={noise_db}:d={min_dur}", "-f", "null", "-"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
    )
    max_sil = 0.0
    for m in re.finditer(r"silence_duration:\s*([0-9.]+)", res.stderr):
        max_sil = max(max_sil, float(m.group(1)))
    return round(max_sil, 3)


def check_chunk_sanity(wav_path: Path, word_count: int) -> tuple[bool, str, float, float]:
    """Validate chunk duration, WPM, and ensure no abnormal internal silence > 2.5s."""
    dur = probe_duration(wav_path)
    wpm = round(word_count / max(dur / 60.0, 0.01), 1)
    max_sil = detect_max_internal_silence(wav_path, min_dur=2.5)
    min_expected_dur = max(1.8, (word_count / 235.0) * 60.0)
    max_expected_dur = (word_count / 100.0) * 60.0 + 4.0

    if max_sil > 2.5:
        return False, f"internal silence {max_sil:.2f}s > 2.5s", dur, wpm
    if dur < min_expected_dur or wpm > 235.0:
        return False, f"abnormal fast/truncated audio ({dur:.2f}s, {wpm} WPM for {word_count} words)", dur, wpm
    if dur > max_expected_dur or wpm < 100.0:
        return False, f"abnormal slow/dead-air audio ({dur:.2f}s, {wpm} WPM for {word_count} words)", dur, wpm
    return True, "ok", dur, wpm


def synth_chunk_locked(
    client: genai.Client,
    text: str,
    raw_wav: Path,
    voice: str,
    model: str,
    max_retries: int = 5,
) -> tuple[float, float, int, int]:
    """Synthesize ONE chunk strictly with the locked model + exponential backoff & sanity retries."""
    words = len(text.split())
    last_reason = "unknown"
    retries_used = 0
    hits_429 = 0

    for attempt in range(1, max_retries + 1):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=STYLE_HEADER + text.strip(),
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                        )
                    ),
                ),
            )
            cand = resp.candidates[0] if resp.candidates else None
            if not cand or not cand.content or not cand.content.parts:
                retries_used += 1
                last_reason = f"empty TTS response (finish_reason={getattr(cand, 'finish_reason', None)})"
                wait_s = min(15 * attempt, 60)
                print(f"    [RETRY {attempt}/{max_retries}] {last_reason} — waiting {wait_s}s...")
                time.sleep(wait_s)
                continue

            pcm = cand.content.parts[0].inline_data.data
            tmp_wav = raw_wav.with_suffix(".tmp.wav")
            with wave.open(str(tmp_wav), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(pcm)

            ok, reason, dur, wpm = check_chunk_sanity(tmp_wav, words)
            if ok:
                tmp_wav.replace(raw_wav)
                return dur, wpm, retries_used, hits_429

            tmp_wav.unlink(missing_ok=True)
            retries_used += 1
            last_reason = f"sanity check failed: {reason}"
            wait_s = min(10 * attempt, 45)
            print(f"    [RETRY {attempt}/{max_retries}] {last_reason} — waiting {wait_s}s...")
            time.sleep(wait_s)
        except Exception as e:
            err_str = str(e)
            last_reason = err_str[:180]
            retries_used += 1
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                hits_429 += 1
                m_retry = re.search(r"retryDelay['\"]?:\s*['\"]?(\d+)s", err_str)
                if m_retry and int(m_retry.group(1)) > 300:
                    raise RuntimeError(f"Daily quota exhausted on {model} (retry in {m_retry.group(1)}s): {last_reason}")
                wait_s = min(30 * (2 ** (hits_429 - 1)), 180)
                print(f"    [429 BACKOFF {attempt}/{max_retries}] Rate limited — sleeping {wait_s}s...")
                time.sleep(wait_s)
            else:
                wait_s = min(12 * (2 ** (attempt - 1)), 90)
                print(f"    [RETRY {attempt}/{max_retries}] {model} error: {last_reason} — sleeping {wait_s}s...")
                time.sleep(wait_s)

    raise RuntimeError(f"Chunk failed after {max_retries} attempts on locked model {model}: {last_reason}")


def stitch_audio_crossfade(
    input_files: list[Path],
    out_path: Path,
    pad_sec: float = 0.15,
    xfade_sec: float = 0.04,
    apply_eq: bool = False,
):
    """Stitch multiple WAV/MP3 files with subtle natural breath padding + 40ms acrossfade."""
    if len(input_files) == 1:
        af = CINEMA_VOCAL_EQ if apply_eq else "aresample=44100,aformat=channel_layouts=mono"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(input_files[0]), "-af", af, "-ar", "44100", "-b:a", "192k", str(out_path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
        return

    ff_inputs: list[str] = []
    filters: list[str] = []
    n = len(input_files)
    for i, f in enumerate(input_files):
        ff_inputs += ["-i", str(f)]
        base_chain = CINEMA_VOCAL_EQ if apply_eq else "aresample=44100,aformat=channel_layouts=mono"
        if i < n - 1 and pad_sec > 0:
            filters.append(f"[{i}:a]{base_chain},apad=pad_dur={pad_sec:.3f}[s{i}];")
        else:
            filters.append(f"[{i}:a]{base_chain}[s{i}];")

    cur_label = "s0"
    for i in range(1, n):
        nxt_label = f"m{i}" if i < n - 1 else "out"
        filters.append(
            f"[{cur_label}][s{i}]acrossfade=d={xfade_sec:.3f}:c1=tri:c2=tri[{nxt_label}];"
        )
        cur_label = nxt_label

    fc = "".join(filters).rstrip(";")
    subprocess.run(
        ["ffmpeg", "-y", *ff_inputs, "-filter_complex", fc, "-map", "[out]",
         "-ar", "44100", "-b:a", "192k", str(out_path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )


def main():
    ap = argparse.ArgumentParser(description="Batch generate consistent documentary voiceover (single locked TTS model).")
    ap.add_argument("--acts-json", required=True, help="JSON file: [{'id': 'act_01', 'title': '...', 'text': '...'}]")
    ap.add_argument("--out-dir", required=True, help="Output directory for act mp3s & master_narration.mp3")
    ap.add_argument("--voice", default=DEFAULT_VOICE, help="Gemini TTS voice name (default: Fenrir)")
    ap.add_argument("--model", default=LOCKED_MODEL, help=f"Locked single TTS model (default: {LOCKED_MODEL})")
    ap.add_argument("--cooldown", type=int, default=22, help="Seconds between API calls (3 RPM safe)")
    ap.add_argument("--min-chunk-words", type=int, default=60)
    ap.add_argument("--max-chunk-words", type=int, default=90)
    ap.add_argument("--env", default=None, help="Optional path to .env file")
    ap.add_argument("--dry-run", action="store_true", help="Print sentence chunking plan without calling TTS API")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    acts = json.loads(Path(args.acts_json).read_text(encoding="utf-8"))

    if args.dry_run:
        print(f"[DRY-RUN] Locked Model: {args.model} | Voice: {args.voice}")
        total_chunks = 0
        for act in acts:
            chunks = split_sentence_chunks(act["text"], args.min_chunk_words, args.max_chunk_words)
            total_chunks += len(chunks)
            print(f"  {act['id']} ({len(act['text'].split())}w) -> {len(chunks)} chunks: {[len(c.split()) for c in chunks]}")
        print(f"[DRY-RUN] Total chunks: {total_chunks} | Zero API calls made.")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir = out_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    client = genai.Client(api_key=load_api_key(args.env))

    manifest = []
    act_files: list[Path] = []
    cursor = 0.0
    act_pad_sec = 0.22
    act_xfade_sec = 0.04

    total_retries = 0
    total_429s = 0

    for idx, act in enumerate(acts, 1):
        act_id = act.get("id") or f"act_{idx:02d}"
        master_mp3 = out_dir / f"{act_id}_master.mp3"
        chunks = split_sentence_chunks(act["text"], args.min_chunk_words, args.max_chunk_words)

        if master_mp3.exists() and master_mp3.stat().st_size > 10000:
            print(f"[{idx}/{len(acts)}] Using cached {master_mp3.name}")
            used_model = f"cached:{args.model}"
        else:
            print(f"[{idx}/{len(acts)}] Synthesizing {act_id} ({len(act['text'].split())} words -> {len(chunks)} chunks) on {args.model}...")
            chunk_wavs: list[Path] = []
            for c_idx, c_text in enumerate(chunks, 1):
                c_wav = chunks_dir / f"{act_id}_c{c_idx:02d}_raw.wav"
                if c_wav.exists() and c_wav.stat().st_size > 10000:
                    ok, reason, c_dur, c_wpm = check_chunk_sanity(c_wav, len(c_text.split()))
                    if ok:
                        print(f"  [{c_idx}/{len(chunks)}] Cached {c_wav.name} ({c_dur:.2f}s, {c_wpm} WPM)")
                        chunk_wavs.append(c_wav)
                        continue
                    print(f"  [{c_idx}/{len(chunks)}] Re-generating bad cached chunk ({reason})...")
                print(f"  [{c_idx}/{len(chunks)}] Synth {len(c_text.split())} words...")
                c_dur, c_wpm, c_ret, c_429 = synth_chunk_locked(client, c_text, c_wav, args.voice, args.model)
                total_retries += c_ret
                total_429s += c_429
                print(f"    -> {c_wav.name}: {c_dur:.2f}s ({c_wpm} WPM, retries={c_ret}, 429s={c_429}) [PASS]")
                chunk_wavs.append(c_wav)
                time.sleep(args.cooldown)

            stitch_audio_crossfade(chunk_wavs, master_mp3, pad_sec=0.15, xfade_sec=0.04, apply_eq=True)
            used_model = args.model

        dur = probe_duration(master_mp3)
        wpm = round(len(act["text"].split()) / max(dur / 60.0, 0.01), 1)
        max_sil = detect_max_internal_silence(master_mp3, min_dur=2.5)
        if max_sil > 2.5:
            print(f"  [WARN] {act_id} contains internal silence of {max_sil:.2f}s — inspect before rendering!")

        manifest.append({
            "id": act_id,
            "title": act.get("title", act_id),
            "model": used_model,
            "chunks": len(chunks),
            "file": str(master_mp3),
            "start_sec": round(cursor, 3),
            "duration_sec": round(dur, 3),
            "end_sec": round(cursor + dur, 3),
            "wpm": wpm,
            "max_internal_silence_sec": max_sil,
        })
        cursor += dur + (act_pad_sec - act_xfade_sec if idx < len(acts) else 0.0)
        act_files.append(master_mp3)
        print(f"  -> {act_id}: {dur:.2f}s ({wpm} WPM, max_sil={max_sil}s)")

    master_out = out_dir / "master_narration.mp3"
    stitch_audio_crossfade(act_files, master_out, pad_sec=act_pad_sec, xfade_sec=act_xfade_sec, apply_eq=False)
    total_dur = probe_duration(master_out)
    master_max_sil = detect_max_internal_silence(master_out, min_dur=2.5)
    (out_dir / "narration_manifest.json").write_text(
        json.dumps(
            {
                "locked_model": args.model,
                "voice": args.voice,
                "total_duration_sec": round(total_dur, 3),
                "max_internal_silence_sec": master_max_sil,
                "total_retries": total_retries,
                "total_429_hits": total_429s,
                "acts": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nDONE! Master narration: {master_out} ({total_dur/60:.2f} min, max_sil={master_max_sil}s)")


if __name__ == "__main__":
    main()
