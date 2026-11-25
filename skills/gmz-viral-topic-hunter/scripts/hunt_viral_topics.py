"""
GMZ Viral Topic Hunter (yt-dlp Outlier + 3D Cinema Scorer)
Scans public YouTube /videos (and optional /shorts) feeds across benchmark Hindi & Global channels
WITHOUT requiring any API keys or logged-in cookies, calculates channel-median outlier multipliers,
and discovers fresh high-CTR documentary & Shorts topics ideal for 3D AI visual storytelling.
"""

import argparse
import concurrent.futures
import json
import re
import statistics
from pathlib import Path
import yt_dlp

HERE = Path(__file__).resolve().parent.parent
CONFIG = json.loads((HERE / "hooks_and_niches.json").read_text(encoding="utf-8"))


def classify_formula(title: str) -> str:
    best_n, best_name = 0, "Curiosity / Deep-Dive"
    for f in CONFIG["title_formulas"]:
        hits = sum(1 for pat in f["patterns"] if re.search(pat, title, re.IGNORECASE))
        if hits > best_n:
            best_n, best_name = hits, f["name"]
    return best_name


def score_3d_cinema(title: str) -> int:
    tl = title.lower()
    hits = sum(1 for kw in CONFIG["cinema_3d_keywords"] if kw in tl)
    return min(10, 4 + hits * 2) if hits > 0 else 3


def fetch_channel_videos(ch: dict, max_items: int, min_dur: int, include_shorts: bool) -> dict:
    url = ch["url"]
    if include_shorts and url.endswith("/videos"):
        url = url[:-7] + "/shorts"
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": max_items,
        "ignoreerrors": True,
    }
    videos = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info or "entries" not in info:
                return {"channel": ch["name"], "lang": ch["lang"], "videos": [], "error": "no_entries"}
            for e in info["entries"]:
                if not e:
                    continue
                views = int(e.get("view_count") or 0)
                dur = int(e.get("duration") or 0)
                if not include_shorts and dur > 0 and dur < min_dur:
                    continue
                vid_id = e.get("id") or ""
                v_url = e.get("url") or (f"https://www.youtube.com/watch?v={vid_id}" if vid_id else "")
                videos.append({
                    "id": vid_id,
                    "title": e.get("title") or "",
                    "views": views,
                    "duration": dur,
                    "url": v_url,
                    "channel": ch["name"],
                    "lang": ch["lang"],
                    "note": ch.get("note", ""),
                })
    except Exception as ex:
        return {"channel": ch["name"], "lang": ch["lang"], "videos": [], "error": str(ex)[:120]}
    return {"channel": ch["name"], "lang": ch["lang"], "videos": videos, "error": None}


def main():
    ap = argparse.ArgumentParser(description="Hunt viral outlier YouTube documentary & Short topics via public yt-dlp feeds.")
    ap.add_argument("--group", choices=["all", "hindi", "global", "science", "business"], default="all", help="Channel group to scan")
    ap.add_argument("--max-per-channel", type=int, default=35, help="Recent videos per channel to sample (default 35)")
    ap.add_argument("--min-dur", type=int, default=240, help="Ignore clips shorter than N seconds on /videos (default 240s)")
    ap.add_argument("--min-mult", type=float, default=1.8, help="Minimum outlier multiple over channel median (default 1.8x)")
    ap.add_argument("--min-views", type=int, default=150000, help="Minimum absolute views so small-channel noise doesn't skew top ranks (default 150000)")
    ap.add_argument("--shorts", action="store_true", help="Scan /shorts tabs instead of long-form /videos")
    ap.add_argument("--workers", type=int, default=8, help="Parallel channel fetch workers")
    ap.add_argument("--out-dir", required=True, help="Directory to save viral_report.json & viral_report.md")
    args = ap.parse_args()

    all_lists = [
        CONFIG["channels"]["hindi_leaders"],
        CONFIG["channels"].get("hindi_business_casestudy", []),
        CONFIG["channels"]["global_engineering_goldmines"],
        CONFIG["channels"].get("global_business_casestudy", []),
    ]
    channels = []
    for lst in all_lists:
        for ch in lst:
            if args.group == "all":
                channels.append(ch)
            elif args.group == "hindi" and ch["lang"] == "hi":
                channels.append(ch)
            elif args.group == "global" and ch["lang"] == "en":
                channels.append(ch)
            elif args.group in ("science", "business") and ch.get("category") == args.group:
                channels.append(ch)

    print(f"Scanning {len(channels)} YouTube channels ({'SHORTS' if args.shorts else 'LONG-FORM'}) via yt-dlp...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(fetch_channel_videos, ch, args.max_per_channel, args.min_dur, args.shorts) for ch in channels]
        for fut in concurrent.futures.as_completed(futs):
            res = fut.result()
            n_v = len(res["videos"])
            status = f"ERR: {res['error']}" if res["error"] else f"{n_v} items"
            print(f"  [{res['lang'].upper()}] {res['channel']:<22} -> {status}")
            results.append(res)

    outliers = []
    channel_summaries = []
    for res in results:
        vids = [v for v in res["videos"] if v["views"] > 0]
        if len(vids) < 4:
            continue
        med = statistics.median(v["views"] for v in vids)
        if med <= 0:
            continue
        channel_summaries.append({"channel": res["channel"], "lang": res["lang"], "sampled": len(vids), "median_views": int(med)})
        for v in vids:
            if v["views"] < args.min_views:
                continue
            mult = v["views"] / med
            if mult >= args.min_mult:
                c_score = score_3d_cinema(v["title"])
                # Normalize tiny pivoting channels (median < 50K) so 500x ratios don't drown out established hits
                norm_mult = v["views"] / max(med, 50000)
                # Composite rank blends Normalized Outlier Multiple + 3D AI Cinema visual suitability
                gmz_score = round(norm_mult * (0.7 + 0.08 * c_score), 2)
                outliers.append({
                    "channel": v["channel"],
                    "lang": v["lang"],
                    "title": v["title"],
                    "views": v["views"],
                    "median_views": int(med),
                    "multiplier": round(mult, 2),
                    "cinema_3d_score": c_score,
                    "gmz_score": gmz_score,
                    "formula": classify_formula(v["title"]),
                    "duration_min": round(v["duration"] / 60.0, 1),
                    "url": v["url"],
                })

    outliers.sort(key=lambda x: (-x["gmz_score"], -x["views"]))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_json = out_dir / "viral_report.json"
    report_md = out_dir / "viral_report.md"

    report_json.write_text(json.dumps({
        "mode": "shorts" if args.shorts else "long_form",
        "channels_scanned": len(channel_summaries),
        "channel_medians": sorted(channel_summaries, key=lambda x: -x["median_views"]),
        "top_outliers": outliers[:100],
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [f"# GMZ Viral Topic Hunter Report ({'Shorts' if args.shorts else 'Long-Form Documentaries'})\n"]
    md.append(f"Scanned **{len(channel_summaries)} channels**, found **{len(outliers)} breakout outliers (>= {args.min_mult}x channel median)**.\n\n")
    md.append("## Top 40 Breakout Topics Ranked by GMZ Viral + 3D Visual Score\n")
    md.append("| Rank | Mult | Views vs Median | 3D Fit | Lang | Channel | Formula | Title |\n|---:|---:|---:|---:|:---:|---|---|---|\n")
    for idx, o in enumerate(outliers[:40], 1):
        v_str = f"{o['views']:,} vs {o['median_views']:,}"
        md.append(f"| {idx} | **{o['multiplier']:.1f}x** | {v_str} | {o['cinema_3d_score']}/10 | `{o['lang']}` | {o['channel']} | {o['formula']} | [{o['title'][:75]}]({o['url']}) |\n")

    md.append("\n## Channel Baseline Medians\n")
    for cs in sorted(channel_summaries, key=lambda x: -x["median_views"]):
        md.append(f"- **{cs['channel']}** (`{cs['lang']}`): `{cs['median_views']:,}` median views ({cs['sampled']} sampled)\n")

    report_md.write_text("".join(md), encoding="utf-8")
    print(f"\nDONE! Saved {len(outliers)} outliers -> {report_md} & {report_json}")


if __name__ == "__main__":
    main()
