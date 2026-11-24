"""
GMZ Documentary Studio v3.5 — Layer 2 Native Antigravity "Eyes & Ears" QA Proxy Builder
Compresses any large rendered master MP4 (e.g. 727 MB 1080p60) into lightweight 4-minute
QA proxy chunks (480p @ 2fps + crisp 64k stereo audio = ~4-5 MB per chunk) so the AI agent
can directly WATCH and LISTEN to every minute of the finished documentary via built-in
multimodal read_file — ZERO extra API key and ZERO 429 quota!
"""

import argparse
import math
import subprocess
from pathlib import Path


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        text=True,
    ).strip()
    return float(out)


def build_qa_proxies(video_path: Path, out_dir: Path, chunk_sec: int = 120) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Remove stale proxy files from prior renders so only fresh chunks exist
    for old_p in out_dir.glob("qa_proxy_part*.mp4"):
        old_p.unlink(missing_ok=True)

    dur = probe_duration(video_path)
    n_chunks = max(1, math.ceil(dur / chunk_sec))
    proxies: list[Path] = []
    black_alerts: list[str] = []

    for i in range(n_chunks):
        ss = i * chunk_sec
        seg_dur = min(chunk_sec, dur - ss)
        if seg_dur < 1.0:
            continue
        m1, s1 = divmod(int(ss), 60)
        m2, s2 = divmod(int(ss + seg_dur), 60)
        out_mp4 = out_dir / f"qa_proxy_part{i+1}_{m1:02d}m{s1:02d}s_to_{m2:02d}m{s2:02d}s.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-ss", f"{ss:.2f}", "-t", f"{seg_dur:.2f}", "-i", str(video_path),
            "-vf", "scale=854:480,fps=2,format=yuv420p",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
            "-c:a", "aac", "-ar", "44100", "-b:a", "64k", "-ac", "2", "-movflags", "+faststart",
            str(out_mp4),
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        size_mb = out_mp4.stat().st_size / (1024 * 1024)
        mb_per_min = size_mb / max(seg_dur / 60.0, 0.25)
        flag = ""
        # v5.3 Black-Screen / Frozen-Frame Alert: normal 480p@2fps+64k proxy is ~2.2-3.5 MB/min; <1.1 MB/min = black/frozen!
        if seg_dur >= 20.0 and mb_per_min < 1.1:
            flag = "  <-- [CRITICAL QA ALERT: ANOMALOUSLY TINY CHUNK — CHECK FOR BLACK/FROZEN FRAMES!]"
            black_alerts.append(f"{out_mp4.name} ({size_mb:.2f} MB for {seg_dur:.0f}s)")
        print(f"  [PROXY {i+1}/{n_chunks}] {out_mp4.name} ({size_mb:.2f} MB){flag}")
        proxies.append(out_mp4)

    if black_alerts:
        raise RuntimeError(f"Black/frozen frame anomaly detected in QA proxies: {black_alerts}")
    return proxies


def main():
    ap = argparse.ArgumentParser(description="Build lightweight 2-min QA proxy MP4 chunks for native multimodal Watch & Listen audit.")
    ap.add_argument("--video", required=True, help="Path to rendered final master MP4")
    ap.add_argument("--out-dir", default=None, help="Output directory for proxy chunks (default: <video_dir>/qa_proxies)")
    ap.add_argument("--chunk-sec", type=int, default=120, help="Seconds per proxy chunk (default: 120 = 2 min)")
    args = ap.parse_args()

    vpath = Path(args.video)
    odir = Path(args.out_dir) if args.out_dir else (vpath.parent / "qa_proxies")
    print(f"Building native Watch & Listen QA proxies for: {vpath.name}")
    proxies = build_qa_proxies(vpath, odir, chunk_sec=args.chunk_sec)
    print(f"DONE! {len(proxies)} proxy chunks ready in {odir} — open each with read_file to inspect video + audio directly!")


if __name__ == "__main__":
    main()
