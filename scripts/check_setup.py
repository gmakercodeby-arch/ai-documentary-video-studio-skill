"""
AI Documentary Video-Making Studio Skill (v4.0) — Stage 0 Environment & Setup Doctor
Checks Python, FFmpeg, FFprobe, GPU hardware encoders (Intel QSV / NVIDIA NVENC / VideoToolbox),
required Python packages, .env GEMINI_API_KEY, and studio_config.json so an AI agent or human
can finish setup in seconds!
"""

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_cmd(name: str) -> str | None:
    return shutil.which(name)


def probe_gpu_encoder() -> str:
    if not check_cmd("ffmpeg"):
        return "missing_ffmpeg"
    candidates = [
        ("h264_nvenc", ["-c:v", "h264_nvenc", "-preset", "p4"]),
        ("h264_qsv", ["-c:v", "h264_qsv", "-preset", "faster", "-look_ahead", "0"]),
        ("h264_videotoolbox", ["-c:v", "h264_videotoolbox"]),
    ]
    for enc, args in candidates:
        res = subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=0.3:r=30", *args, "-f", "null", "-"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        if res.returncode == 0:
            return enc
    return "libx264 (CPU)"


def has_gemini_key() -> tuple[bool, str]:
    if os.environ.get("GEMINI_API_KEY") and "YOUR_GEMINI_API_KEY" not in os.environ["GEMINI_API_KEY"]:
        return True, "environment variable"
    for p in [Path.cwd() / ".env", Path(__file__).resolve().parent.parent / ".env", Path.home() / ".env"]:
        if p.exists():
            for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                s = line.strip()
                if s.startswith("GEMINI_API_KEY=") and "YOUR_GEMINI_API_KEY" not in s and len(s.split("=", 1)[1].strip()) > 10:
                    return True, str(p)
    return False, "not configured"


def main():
    ap = argparse.ArgumentParser(description="Check AI Documentary Studio prerequisites and setup state.")
    ap.add_argument("--json", action="store_true", help="Output machine-readable JSON for AI agent wizards")
    args = ap.parse_args()

    pkgs = {
        "google-genai": "google.genai",
        "faster-whisper": "faster_whisper",
        "Pillow": "PIL",
        "playwright": "playwright",
    }
    pkg_status = {}
    for label, mod in pkgs.items():
        try:
            importlib.import_module(mod)
            pkg_status[label] = True
        except Exception:
            pkg_status[label] = False

    ffmpeg_path = check_cmd("ffmpeg")
    ffprobe_path = check_cmd("ffprobe")
    gpu_enc = probe_gpu_encoder() if ffmpeg_path else "missing_ffmpeg"
    key_ok, key_src = has_gemini_key()
    cfg_path = Path.cwd() / "studio_config.json"
    cfg_ok = cfg_path.exists()

    missing_steps = []
    if not ffmpeg_path or not ffprobe_path:
        missing_steps.append("Install FFmpeg & FFprobe (Windows: winget install Gyan.FFmpeg | macOS: brew install ffmpeg)")
    for label, ok in pkg_status.items():
        if not ok:
            missing_steps.append(f"Install Python package: pip install {label}")
    if not key_ok:
        missing_steps.append("Add GEMINI_API_KEY to .env (get a free key at https://aistudio.google.com/apikey)")
    if not cfg_ok:
        missing_steps.append("Run AI Setup Wizard to create studio_config.json (channel badge, language, optional Outro CTA)")

    report = {
        "ready_to_produce": len(missing_steps) == 0,
        "python_version": sys.version.split()[0],
        "ffmpeg": bool(ffmpeg_path),
        "ffprobe": bool(ffprobe_path),
        "detected_encoder": gpu_enc,
        "packages": pkg_status,
        "gemini_api_key_configured": key_ok,
        "gemini_api_key_source": key_src,
        "studio_config_present": cfg_ok,
        "next_setup_steps": missing_steps,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("\n=== AI Documentary Video-Making Studio (v4.0) — Setup Doctor ===")
    print(f"  Python          : {report['python_version']}")
    print(f"  FFmpeg / Probe  : {'OK' if (ffmpeg_path and ffprobe_path) else 'MISSING'}")
    print(f"  Video Encoder   : {gpu_enc}")
    for k, ok in pkg_status.items():
        print(f"  Package {k:14s}: {'OK' if ok else 'MISSING'}")
    print(f"  GEMINI_API_KEY  : {'OK (' + key_src + ')' if key_ok else 'NOT SET (AI Setup Wizard will ask you!)'}")
    print(f"  studio_config   : {'OK' if cfg_ok else 'NOT CREATED YET (AI Setup Wizard will create it!)'}")

    if missing_steps:
        print("\nNext Setup Steps:")
        for i, step in enumerate(missing_steps, 1):
            print(f"  {i}. {step}")
    else:
        print("\nSTATUS: 100% READY TO PRODUCE 1080p @ 60fps DOCUMENTARIES!")


if __name__ == "__main__":
    main()
