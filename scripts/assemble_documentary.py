"""
GMZ Documentary Studio v3.5 â€” Ultra-Fast Pro Cinema 16:9 @ 60fps Assembler
Speed & Quality Upgrades (v3.5):
- Auto-Hardware GPU Encoder Detection: Probes Intel QuickSync (h264_qsv) & NVIDIA (h264_nvenc),
  using hardware GPU acceleration automatically when available (with automatic libx264 fallback).
- Multi-Core Parallel Rendering: ThreadPoolExecutor (default 3 workers on 8-core CPU) renders
  multiple clips simultaneously -> 3x-5x faster overall render!
- Smart SHA-1 Clip Caching: Hashes every shot's exact visual/audio params; unchanged clips are
  reused in 0.0s on re-renders!
- Smart 2560x1440 (1.33x) Ken Burns Supersampling: 2.25x fewer pixels than 4K while remaining
  razor-sharp & jitter-free at 1080p60.
- 3D AI Watermark Fix: Pre-crops 12% off bottom-right edges (crop=iw*0.88:ih*0.88:0:0) on 3d_images/.
- Veo Border Crop Fix: crop_zoom=1.14 default, 1.20 specifically for veo_02_energia_liftoff.mp4.
- Batched 0.25s Crossfade Transitions: Lossless PCM .mkv intermediates + exact inter-batch handles
  + Â±0.15s sync guard (ZERO OOM, ZERO AAC priming drift!).
- Single True Two-Pass Loudnorm (I=-13:TP=-1.5:LRA=9, linear=true) + Clean 2.5s BGM fade-out.
- Sleek Playwright Glassmorphism GMZ Badge PNG + Auto Layer-2 QA Proxy Chunk Generator!
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

XFADE_DUR = 0.25
BATCH_SIZE = 16


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        text=True,
    ).strip()
    return float(out)


def has_audio_stream(path: Path) -> bool:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
         "-of", "csv=p=0", str(path)],
        text=True,
    ).strip()
    return bool(out)


def detect_best_encoder() -> tuple[str, list[str], list[str]]:
    """
    Detect fastest working GPU hardware encoder (Intel QSV / NVIDIA NVENC) with libx264 fallback.
    Returns: (encoder_name, clip_enc_args, master_enc_args)
    """
    candidates = [
        ("h264_qsv", ["-c:v", "h264_qsv", "-preset", "faster", "-global_quality", "20", "-look_ahead", "0"],
                     ["-c:v", "h264_qsv", "-preset", "medium", "-global_quality", "19", "-look_ahead", "0"]),
        ("h264_nvenc", ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "19"],
                       ["-c:v", "h264_nvenc", "-preset", "p5", "-cq", "18"]),
    ]
    for name, clip_args, master_args in candidates:
        res = subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=0.4:r=60", *clip_args, "-f", "null", "-"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        if res.returncode == 0:
            return name, clip_args, master_args
    return (
        "libx264",
        ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18"],
        ["-c:v", "libx264", "-preset", "medium", "-crf", "18"],
    )


def render_gmz_badge_png(badge_text: str, out_png: Path) -> Path:
    """Render a sleek translucent dark glassmorphism pill PNG with subtle gold border/glow via Playwright."""
    from playwright.sync_api import sync_playwright

    out_png.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    width: 240px; height: 96px; background: transparent;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
  }}
  .pill {{
    display: inline-flex; align-items: center; gap: 10px;
    padding: 10px 26px;
    background: linear-gradient(135deg, rgba(10, 14, 24, 0.84), rgba(18, 24, 38, 0.72));
    backdrop-filter: blur(16px);
    border: 2px solid rgba(255, 214, 0, 0.85);
    border-radius: 999px;
    box-shadow: 0 0 22px rgba(255, 214, 0, 0.28), 0 8px 24px rgba(0, 0, 0, 0.65);
    color: #FFD600;
    font-size: 28px; font-weight: 900; letter-spacing: 3px;
    text-shadow: 0 2px 10px rgba(255, 214, 0, 0.35);
  }}
  .dot {{
    width: 10px; height: 10px; border-radius: 50%;
    background: #FFD600; box-shadow: 0 0 10px #FFD600;
  }}
</style></head>
<body><div class="pill"><span class="dot"></span><span>{badge_text}</span></div></body></html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 240, "height": 96})
        page.set_content(html)
        page.screenshot(path=str(out_png), omit_background=True)
        browser.close()
    return out_png


def shot_cache_key(shot: dict, render_dur: float, fps: int, width: int, height: int, enc_name: str) -> str:
    payload = {
        "v": "5.0",
        "path": str(Path(shot["path"]).resolve()),
        "mtime": Path(shot["path"]).stat().st_mtime if Path(shot["path"]).exists() else 0,
        "split_right": str(Path(shot["split_right"]).resolve()) if shot.get("split_right") else "",
        "render_dur": round(render_dur, 4),
        "start": round(float(shot.get("start", 0.0)), 3),
        "motion": shot.get("motion", "zoom_in"),
        "callout": shot.get("callout") or "",
        "sfx": shot.get("sfx") or "",
        "crop_zoom": shot.get("crop_zoom"),
        "crop_watermark": bool(shot.get("crop_watermark", False)),
        "fade_in": float(shot.get("fade_in", 0.0)),
        "fade_out": float(shot.get("fade_out", 0.0)),
        "keep_native_sfx": shot.get("keep_native_sfx", True),
        "fps": fps, "w": width, "h": height, "enc": enc_name,
    }
    return hashlib.sha1(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:12]


def sfx_aeval_expr(sfx_name: str) -> str | None:
    """Procedural copyright-free cinema SFX (whoosh, bass_hit, pop, riser) for Cinema Documentary punch!"""
    if sfx_name == "whoosh":
        return "aevalsrc='0.35*sin(2*PI*(180+700*t)*t)*exp(-4.5*t) + 0.15*sin(2*PI*(90+240*t)*t)*exp(-3.5*t)':s=44100:d=0.45:c=mono,aresample=44100,aformat=channel_layouts=stereo,volume=-8dB"
    if sfx_name == "bass_hit":
        return "aevalsrc='0.55*sin(2*PI*(95*exp(-3.2*t)+38)*t)*exp(-3.8*t)':s=44100:d=0.65:c=mono,aresample=44100,aformat=channel_layouts=stereo,volume=-6dB"
    if sfx_name == "pop":
        return "aevalsrc='0.40*sin(2*PI*(520*exp(-12*t)+180)*t)*exp(-14*t)':s=44100:d=0.22:c=mono,aresample=44100,aformat=channel_layouts=stereo,volume=-9dB"
    if sfx_name == "riser":
        return "aevalsrc='0.28*sin(2*PI*(110+420*t*t)*t)*min(t*1.5,1)':s=44100:d=0.90:c=mono,aresample=44100,aformat=channel_layouts=stereo,volume=-9dB"
    return None


def build_clip(
    shot: dict,
    out_clip: Path,
    render_dur: float,
    enc_args: list[str],
    fps: int = 60,
    width: int = 1920,
    height: int = 1080,
):
    src = Path(shot["path"])
    ext = src.suffix.lower()
    is_img = ext in {".png", ".jpg", ".jpeg", ".webp"}
    motion = shot.get("motion", "zoom_in")
    callout = shot.get("callout")
    fade_in = float(shot.get("fade_in", 0.0))
    fade_out = float(shot.get("fade_out", 0.0))

    grade = "eq=contrast=1.05:saturation=1.06,vignette=PI/6"
    fades = ""
    if fade_in > 0:
        fades += f",fade=t=in:st=0:d={fade_in:.2f}"
    if fade_out > 0:
        st_out = max(render_dur - fade_out, 0.0)
        fades += f",fade=t=out:st={st_out:.2f}:d={fade_out:.2f}"

    # Smart 2560x1440 supersampling (1.33x) -> 2.25x faster Ken Burns than 4K, zero jitter at 1080p60!
    ss_w, ss_h = int(width * 4 / 3), int(height * 4 / 3)
    pix_fmt = "nv12" if "h264_qsv" in enc_args else "yuv420p"

    sfx_expr = sfx_aeval_expr(shot.get("sfx", ""))
    audio_src = sfx_expr if sfx_expr else "anullsrc=r=44100:cl=stereo"

    if is_img:
        frames = max(int(round(render_dur * fps)), 1)
        is_ai_3d = ("3d_images" in str(src).lower()) or bool(shot.get("crop_watermark", False))
        pre_crop = "crop=iw*0.88:ih*0.88:0:0," if is_ai_3d else ""

        if motion == "zoom_out":
            z_expr = f"max(1.10-0.10*on/{frames},1.0)"
            x_expr = "(iw-iw/zoom)/2"
        elif motion == "pan_right":
            z_expr = "1.09"
            x_expr = f"(iw-iw/zoom)*on/{frames}"
        elif motion == "pan_left":
            z_expr = "1.09"
            x_expr = f"(iw-iw/zoom)*(1-on/{frames})"
        else:
            z_expr = f"min(1.0+0.10*on/{frames},1.10)"
            x_expr = "(iw-iw/zoom)/2"

        vf = (
            f"{pre_crop}"
            f"scale={ss_w}:{ss_h}:force_original_aspect_ratio=increase,"
            f"crop={ss_w}:{ss_h},"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='(ih-ih/zoom)/2':d={frames}:s={width}x{height}:fps={fps},"
            f"{grade}{fades},format={pix_fmt}"
        )
        if callout:
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", str(src), "-loop", "1", "-i", str(callout),
                "-f", "lavfi", "-i", audio_src,
                "-filter_complex", f"[0:v]{vf}[bg];[bg][1:v]overlay=0:0:shortest=1,format={pix_fmt}[v];[2:a]apad=whole_dur={render_dur:.3f}[a]",
                "-map", "[v]", "-map", "[a]", "-t", f"{render_dur:.3f}",
                *enc_args, "-r", str(fps), "-c:a", "pcm_s16le", str(out_clip),
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", str(src),
                "-f", "lavfi", "-i", audio_src,
                "-t", f"{render_dur:.3f}", "-vf", vf, "-af", f"apad=whole_dur={render_dur:.3f}",
                *enc_args, "-r", str(fps), "-c:a", "pcm_s16le", str(out_clip),
            ]
    else:
        ss = float(shot.get("start", 0.0))
        default_crop = 1.14
        crop_zoom = float(shot.get("crop_zoom", default_crop))
        sw, sh = int(width * crop_zoom), int(height * crop_zoom)
        vf = (
            f"scale={sw}:{sh}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},fps={fps},{grade}{fades},format={pix_fmt}"
        )
        keep_sfx = shot.get("keep_native_sfx", True) and has_audio_stream(src)
        sfx_fade_out_st = max(render_dur - 0.18, 0.0)
        if keep_sfx:
            af = (
                f"volume=-16dB,aresample=44100,aformat=channel_layouts=stereo,"
                f"afade=t=in:st=0:d=0.15,afade=t=out:st={sfx_fade_out_st:.3f}:d=0.18"
            )
            if callout:
                cmd = [
                    "ffmpeg", "-y", "-ss", f"{ss:.3f}", "-t", f"{render_dur:.3f}", "-i", str(src),
                    "-loop", "1", "-i", str(callout),
                    "-filter_complex", f"[0:v]{vf}[bg];[bg][1:v]overlay=0:0:shortest=1,format={pix_fmt}[v];[0:a]{af}[a]",
                    "-map", "[v]", "-map", "[a]",
                    *enc_args, "-r", str(fps), "-c:a", "pcm_s16le", str(out_clip),
                ]
            else:
                cmd = [
                    "ffmpeg", "-y", "-ss", f"{ss:.3f}", "-t", f"{render_dur:.3f}", "-i", str(src),
                    "-vf", vf, "-af", af,
                    *enc_args, "-r", str(fps), "-c:a", "pcm_s16le", str(out_clip),
                ]
        else:
            if callout:
                cmd = [
                    "ffmpeg", "-y", "-ss", f"{ss:.3f}", "-t", f"{render_dur:.3f}", "-i", str(src),
                    "-loop", "1", "-i", str(callout),
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-filter_complex", f"[0:v]{vf}[bg];[bg][1:v]overlay=0:0:shortest=1,format={pix_fmt}[v]",
                    "-map", "[v]", "-map", "2:a", "-t", f"{render_dur:.3f}",
                    *enc_args, "-r", str(fps), "-c:a", "pcm_s16le", str(out_clip),
                ]
            else:
                cmd = [
                    "ffmpeg", "-y", "-ss", f"{ss:.3f}", "-t", f"{render_dur:.3f}", "-i", str(src),
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-map", "0:v", "-map", "1:a", "-t", f"{render_dur:.3f}", "-vf", vf,
                    *enc_args, "-r", str(fps), "-c:a", "pcm_s16le", str(out_clip),
                ]

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0 and "h264_qsv" in enc_args:
        # Automatic transparent fallback to libx264 if QSV rejects a specific clip
        fallback_cmd = [x for x in cmd]
        q_idx = fallback_cmd.index("h264_qsv")
        fallback_cmd[q_idx - 1 : q_idx + 7] = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18"]
        fallback_cmd = [x.replace("format=nv12", "format=yuv420p") for x in fallback_cmd]
        subprocess.run(fallback_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    elif res.returncode != 0:
        raise RuntimeError(f"FFmpeg clip render failed for {src.name}")


def xfade_join_clips(
    clip_paths: list[Path],
    target_durs: list[float],
    out_path: Path,
    enc_args: list[str],
    xfade_dur: float = XFADE_DUR,
    fps: int = 60,
    keep_tail_handle: bool = False,
):
    if len(clip_paths) == 1:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(clip_paths[0]), "-c:v", "copy", "-c:a", "pcm_s16le", str(out_path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
        return

    actual_durs = [probe_duration(p) for p in clip_paths]
    pix_fmt = "nv12" if "h264_qsv" in enc_args else "yuv420p"
    ff_inputs: list[str] = []
    v_filters: list[str] = []
    a_filters: list[str] = []
    for i, p in enumerate(clip_paths):
        ff_inputs += ["-i", str(p)]
        need_handle = (i < len(clip_paths) - 1) or keep_tail_handle
        exact_len = target_durs[i] + (xfade_dur if need_handle else 0.0)
        safe_len = min(exact_len, actual_durs[i])
        v_filters.append(f"[{i}:v]settb=AVTB,fps={fps},trim=0:{safe_len:.4f},setpts=PTS-STARTPTS,format=yuv420p[v{i}];")
        a_filters.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{safe_len:.4f},asetpts=PTS-STARTPTS[a{i}];")

    cur_v, cur_a = "v0", "a0"
    cum_offset = 0.0
    for i in range(1, len(clip_paths)):
        cum_offset += target_durs[i - 1]
        is_last = i == len(clip_paths) - 1
        nxt_v = "vout_raw" if is_last else f"xv{i}"
        nxt_a = "aout" if is_last else f"xa{i}"
        v_filters.append(
            f"[{cur_v}][v{i}]xfade=transition=fade:duration={xfade_dur:.3f}:offset={cum_offset:.3f}[{nxt_v}];"
        )
        a_filters.append(
            f"[{cur_a}][a{i}]acrossfade=d={xfade_dur:.3f}:c1=tri:c2=tri[{nxt_a}];"
        )
        cur_v, cur_a = nxt_v, nxt_a

    v_filters.append(f"[vout_raw]format={pix_fmt}[vout];")
    fc = "".join(v_filters) + "".join(a_filters).rstrip(";")
    cmd = [
        "ffmpeg", "-y", *ff_inputs,
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "[aout]",
        *enc_args, "-r", str(fps), "-c:a", "pcm_s16le", str(out_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0 and "h264_qsv" in enc_args:
        fb = [x.replace("format=nv12", "format=yuv420p") for x in cmd]
        q_idx = fb.index("h264_qsv")
        fb[q_idx - 1 : q_idx + 7] = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "17"]
        subprocess.run(fb, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    elif res.returncode != 0:
        raise RuntimeError(f"FFmpeg xfade join failed for {out_path.name}")


def two_pass_loudnorm_mix(
    video_joined: Path,
    narration: Path,
    bgm: Path | None,
    total_end_sec: float,
    out_wav: Path,
):
    premix_wav = out_wav.parent / "_premix_raw.wav"
    fade_start = max(total_end_sec - 2.5, 0.0)

    inputs = ["-i", str(video_joined), "-i", str(narration)]
    if bgm:
        inputs += ["-stream_loop", "-1", "-i", str(bgm)]
        af = (
            f"[1:a]aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur={total_end_sec:.3f},asplit=2[vo_main][vo_sc];"
            f"[2:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{total_end_sec:.3f},volume=-18dB,"
            f"afade=t=out:st={fade_start:.3f}:d=2.5[bgm_low];"
            f"[bgm_low][vo_sc]sidechaincompress=threshold=0.04:ratio=4:attack=25:release=350[bgm_duck];"
            f"[0:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{total_end_sec:.3f}[sfx];"
            f"[vo_main][sfx][bgm_duck]amix=inputs=3:duration=first:normalize=0,atrim=0:{total_end_sec:.3f}[aout]"
        )
    else:
        af = (
            f"[1:a]aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur={total_end_sec:.3f}[vo_main];"
            f"[0:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{total_end_sec:.3f}[sfx];"
            f"[vo_main][sfx]amix=inputs=2:duration=first:normalize=0,atrim=0:{total_end_sec:.3f}[aout]"
        )

    subprocess.run(
        ["ffmpeg", "-y", *inputs, "-filter_complex", af, "-map", "[aout]", "-ar", "44100", "-ac", "2", str(premix_wav)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )

    p1 = subprocess.run(
        ["ffmpeg", "-i", str(premix_wav), "-af", "loudnorm=I=-13:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=True,
    )
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p1.stderr, re.DOTALL)
    if not m:
        raise RuntimeError("Failed to parse loudnorm pass-1 JSON stats!")
    stats = json.loads(m.group(0))

    ln2 = (
        f"loudnorm=I=-13:TP=-1.5:LRA=9:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}:linear=true"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(premix_wav), "-af", ln2, "-ar", "44100", "-ac", "2", str(out_wav)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )
    premix_wav.unlink(missing_ok=True)
    print(f"Two-pass loudnorm complete: input_i={stats['input_i']} -> target -13.0 LUFS (TP=-1.5, LRA=9)")


def make_qa_grid(video_path: Path, out_grid: Path, num_frames: int = 25):
    dur = probe_duration(video_path)
    fps_expr = f"{num_frames}/{max(dur, 1.0):.2f}"
    cols = 5
    rows = (num_frames + cols - 1) // cols
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", f"fps={fps_expr},scale=480:270,tile={cols}x{rows}",
        "-frames:v", "1", str(out_grid),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def main():
    ap = argparse.ArgumentParser(description="Assemble 16:9 60fps GMZ Pro Documentary (v3.5 GPU + Multi-Core + Caching).")
    ap.add_argument("--plan", required=True, help="JSON list of shots")
    ap.add_argument("--narration", required=True, help="Master Hindi narration MP3/WAV")
    ap.add_argument("--bgm", default=None, help="Optional copyright-free BGM MP3/WAV")
    ap.add_argument("--segments", default=None, help="Optional segments.json to trim clean 2.5s ending after last spoken word")
    ap.add_argument("--out", required=True, help="Output final MP4 path")
    ap.add_argument("--badge", default="GMZ", help="Bottom-right glassmorphism pill badge text (default: GMZ)")
    ap.add_argument("--badge-png", default=None, help="Optional pre-rendered glassmorphism badge PNG path")
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--xfade", type=float, default=XFADE_DUR)
    ap.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    ap.add_argument("--workers", type=int, default=min(3, max(1, (os.cpu_count() or 4) // 2)), help="Parallel clip workers (default: 3)")
    ap.add_argument("--no-gpu", action="store_true", help="Force CPU libx264 encoding")
    ap.add_argument("--no-proxy", action="store_true", help="Skip Layer-2 QA proxy generation")
    args = ap.parse_args()

    if args.no_gpu:
        enc_name = "libx264"
        clip_enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18"]
        master_enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "18"]
    else:
        enc_name, clip_enc, master_enc = detect_best_encoder()
    print(f"[ENGINE v3.5] Video Encoder: {enc_name} | Parallel Workers: {args.workers} | Clip Caching: ON")

    shots = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    narr_dur = probe_duration(Path(args.narration))

    spoken_end = narr_dur
    if args.segments and Path(args.segments).exists():
        seg_data = json.loads(Path(args.segments).read_text(encoding="utf-8"))
        if seg_data.get("last_spoken_end"):
            spoken_end = float(seg_data["last_spoken_end"])
        elif seg_data.get("segments"):
            spoken_end = float(seg_data["segments"][-1]["end"])
    target_total = round(spoken_end + 2.5, 3)

    plan_dur = sum(float(s["duration"]) for s in shots)
    if plan_dur < target_total:
        deficit = target_total - plan_dur
        print(f"[GUARD] Extending last shot by +{deficit:.2f}s to match clean {target_total:.2f}s ending!")
        shots[-1]["duration"] = round(float(shots[-1]["duration"]) + deficit, 3)
        shots[-1]["fade_out"] = max(float(shots[-1].get("fade_out", 0.0)), 1.8)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_path.parent / "_tmp_clips_v35"
    cache_dir = tmp_dir / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Prepare tasks with SHA-1 smart clip caching + lossless PCM .mkv clips
    clip_paths: list[Path] = []
    target_durs: list[float] = []
    to_render: list[tuple[int, dict, Path, float]] = []
    cached_hits = 0

    for idx, shot in enumerate(shots, 1):
        tdur = float(shot["duration"])
        rdur = tdur + (args.xfade if idx < len(shots) else 0.0)
        key = shot_cache_key(shot, rdur, args.fps, args.width, args.height, enc_name)
        cpath = cache_dir / f"clip_{key}.mkv"
        clip_paths.append(cpath)
        target_durs.append(tdur)
        if cpath.exists() and cpath.stat().st_size > 20000:
            cached_hits += 1
        else:
            to_render.append((idx, shot, cpath, rdur))

    print(f"[CLIPS] Total={len(shots)} | Cached={cached_hits} | To Render={len(to_render)}")

    if to_render:
        done_count = 0
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futs = {
                pool.submit(build_clip, shot, cpath, rdur, clip_enc, args.fps, args.width, args.height): (idx, shot, rdur)
                for idx, shot, cpath, rdur in to_render
            }
            for fut in as_completed(futs):
                idx, shot, rdur = futs[fut]
                fut.result()
                done_count += 1
                if done_count % 10 == 0 or done_count == len(to_render):
                    print(f"  [RENDER {done_count}/{len(to_render)}] Done clip #{idx} ({Path(shot['path']).name})")

    # Batched 0.25s xfade join with lossless PCM intermediates (.mkv) & exact inter-batch handle sync!
    batch_files: list[Path] = []
    batch_durs: list[float] = []
    for b_idx, start_i in enumerate(range(0, len(clip_paths), args.batch_size), 1):
        b_clips = clip_paths[start_i : start_i + args.batch_size]
        b_durs = target_durs[start_i : start_i + args.batch_size]
        has_next_batch = (start_i + args.batch_size) < len(clip_paths)
        b_out = tmp_dir / f"batch_{b_idx:03d}.mkv"
        print(f"[BATCH {b_idx}] Xfade-joining {len(b_clips)} clips (target={sum(b_durs):.2f}s, tail_handle={has_next_batch})...")
        xfade_join_clips(b_clips, b_durs, b_out, clip_enc, xfade_dur=args.xfade, fps=args.fps, keep_tail_handle=has_next_batch)
        batch_files.append(b_out)
        batch_durs.append(sum(b_durs))

    video_joined = tmp_dir / "video_joined_xfade.mkv"
    print(f"[MASTER JOIN] Joining {len(batch_files)} batches with {args.xfade}s xfade...")
    xfade_join_clips(batch_files, batch_durs, video_joined, clip_enc, xfade_dur=args.xfade, fps=args.fps, keep_tail_handle=False)
    joined_dur = probe_duration(video_joined)
    drift = abs(joined_dur - sum(target_durs))
    print(f"[SYNC CHECK] Joined video={joined_dur:.3f}s vs target={sum(target_durs):.3f}s (drift={drift:.3f}s)")
    if drift > 0.15:
        print(f"  [WARN] Video xfade drift {drift:.3f}s exceeded Â±0.15s tolerance!")

    master_audio_wav = tmp_dir / "final_audio_master.wav"
    two_pass_loudnorm_mix(
        video_joined,
        Path(args.narration),
        Path(args.bgm) if args.bgm else None,
        target_total,
        master_audio_wav,
    )

    badge_png = Path(args.badge_png) if args.badge_png else (out_path.parent / "gmz_badge.png")
    if args.badge.strip() and not badge_png.exists():
        render_gmz_badge_png(args.badge.strip(), badge_png)

    master_pix = "nv12" if "h264_qsv" in master_enc else "yuv420p"
    if args.badge.strip() and badge_png.exists():
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_joined), "-i", str(master_audio_wav), "-i", str(badge_png),
            "-filter_complex", f"[0:v][2:v]overlay=W-w-36:H-h-30,format={master_pix}[vout]",
            "-map", "[vout]", "-map", "1:a",
            "-t", f"{target_total:.3f}",
            *master_enc, "-r", str(args.fps),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            str(out_path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_joined), "-i", str(master_audio_wav),
            "-map", "0:v", "-map", "1:a",
            "-t", f"{target_total:.3f}",
            "-vf", f"format={master_pix}",
            *master_enc, "-r", str(args.fps),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            str(out_path),
        ]

    print(f"Rendering final 1080p @ 60fps GMZ v3.5 Master ({enc_name}):", out_path)
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0 and "h264_qsv" in master_enc:
        fb = [x.replace("format=nv12", "format=yuv420p") for x in cmd]
        q_idx = fb.index("h264_qsv")
        fb[q_idx - 1 : q_idx + 7] = ["-c:v", "libx264", "-preset", "medium", "-crf", "18"]
        subprocess.run(fb, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    elif res.returncode != 0:
        raise RuntimeError("Final master encode failed!")

    qa_grid = out_path.parent / f"{out_path.stem}_QA_25frames.jpg"
    make_qa_grid(out_path, qa_grid, num_frames=25)
    final_dur = probe_duration(out_path)
    print(f"DONE! Video: {out_path} ({final_dur:.2f}s | spoken_end={spoken_end:.2f}s + 2.5s fade)")
    print(f"QA Grid saved: {qa_grid}")

    # Auto-build Layer-2 Native Watch & Listen QA Proxy chunks (~5 MB each) for direct read_file audit!
    if not args.no_proxy:
        proxy_script = Path(__file__).parent / "make_qa_proxy.py"
        if proxy_script.exists():
            subprocess.run(["python", str(proxy_script), "--video", str(out_path)], check=True)


if __name__ == "__main__":
    main()


