"""
AI Documentary Studio v4.0 — Layer 2 Native "Eyes & Ears" QA Proxy Builder
Compresses any large rendered master MP4 into lightweight 2-minute QA proxy chunks
(480p @ 2fps + crisp 44.1kHz 64k stereo audio = ~5 MB per chunk) so multimodal AI agents
can directly WATCH and LISTEN to every minute of the finished documentary with ZERO API quota!
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
    dur = probe_duration(video_path)
    n_chunks = max(1, math.ceil(dur / chunk_sec))
    proxies: list[Path] = []

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
        print(f"  [PROXY {i+1}/{n_chunks}] {out_mp4.name} ({size_mb:.2f} MB)")
        proxies.append(out_mp4)
    return proxies


def main():
    ap = argparse.ArgumentParser(description="Build lightweight 2-min QA proxy MP4 chunks for multimodal Watch & Listen audit.")
    ap.add_argument("--video", required=True, help="Path to rendered final master MP4")
    ap.add_argument("--out-dir", default=None, help="Output directory for proxy chunks (default: <video_dir>/qa_proxies)")
    ap.add_argument("--chunk-sec", type=int, default=120, help="Seconds per proxy chunk (default: 120 = 2 min)")
    args = ap.parse_args()

    vpath = Path(args.video)
    odir = Path(args.out_dir) if args.out_dir else (vpath.parent / "qa_proxies")
    print(f"Building native Watch & Listen QA proxies for: {vpath.name}")
    proxies = build_qa_proxies(vpath, odir, chunk_sec=args.chunk_sec)
    print(f"DONE! {len(proxies)} proxy chunks ready in {odir} — inspect each with your multimodal viewer!")


if __name__ == "__main__":
    main()
