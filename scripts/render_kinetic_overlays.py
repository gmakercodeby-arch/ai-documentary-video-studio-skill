"""
GMZ Documentary Studio v5.0 â€” Cinema Documentary Style Kinetic Typography, HUD Pointer & Split-Screen Overlay Renderer
Replaces boring static blueprint slides with broadcast-grade transparent 1920x1080 PNG overlays
that composite directly ON TOP of moving Veo 3.1 / 3D cinema footage:
  - mode="impact"  : Giant bold Hindi/English impact text with cinema drop shadow & subtle glow (e.g. "à¤¸à¤¨à¥à¤¨à¤¾à¤Ÿà¤¾à¥¤", "500 FEET")
  - mode="hud"     : Thin glowing white/cyan technical HUD pointer line + floating label pointing at the subject
  - mode="split"   : Vertical glowing split-screen divider with bold Left vs Right headers ("1. PROBLEM" | "2. SOLUTION")
  - mode="cta"     : Sleek translucent gold glassmorphism 1-Click Website Outro CTA card
"""

import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def make_overlay_html(item: dict) -> str:
    mode = item.get("mode", "impact")
    title = item.get("title", "")
    subtitle = item.get("subtitle", "")
    accent = item.get("accent", "#FFD600")

    if mode == "impact":
        pos = item.get("position", "center")  # center | bottom | top
        align_css = (
            "align-items:center; justify-content:center;" if pos == "center"
            else ("align-items:flex-end; justify-content:center; padding-bottom:130px;" if pos == "bottom"
                  else "align-items:flex-start; justify-content:center; padding-top:90px;")
        )
        return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
          *{{margin:0;padding:0;box-sizing:border-box;}}
          body{{width:1920px;height:1080px;background:transparent;display:flex;{align_css}
               font-family:'Nirmala UI','Segoe UI','Noto Sans Devanagari',Arial,sans-serif;}}
          .wrap{{text-align:center;max-width:1600px;}}
          .main{{font-size:108px;font-weight:900;color:#FFFFFF;letter-spacing:2px;line-height:1.12;
                text-shadow:0 8px 32px rgba(0,0,0,0.95), 0 0 42px {accent}88, -3px -3px 0 #000, 3px -3px 0 #000, -3px 3px 0 #000, 3px 3px 0 #000;}}
          .sub{{margin-top:16px;font-size:38px;font-weight:800;color:{accent};letter-spacing:3px;text-transform:uppercase;
               text-shadow:0 4px 18px rgba(0,0,0,0.95);}}
        </style></head><body><div class="wrap"><div class="main">{title}</div>
        {f'<div class="sub">{subtitle}</div>' if subtitle else ''}</div></body></html>"""

    if mode == "hud":
        x = int(item.get("x", 180))
        y = int(item.get("y", 220))
        tx = int(item.get("target_x", 720))
        ty = int(item.get("target_y", 460))
        return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
          *{{margin:0;padding:0;box-sizing:border-box;}}
          body{{width:1920px;height:1080px;background:transparent;position:relative;
               font-family:'Segoe UI','Nirmala UI',Arial,sans-serif;}}
          .label{{position:absolute;left:{x}px;top:{y}px;padding:14px 24px;
                 background:rgba(6,12,22,0.78);backdrop-filter:blur(10px);
                 border-left:4px solid {accent};border-radius:8px;
                 box-shadow:0 12px 32px rgba(0,0,0,0.65);}}
          .t{{color:#FFFFFF;font-size:34px;font-weight:900;letter-spacing:2px;}}
          .s{{color:{accent};font-size:19px;font-weight:700;letter-spacing:1.5px;margin-top:4px;}}
        </style></head><body>
          <svg viewBox="0 0 1920 1080" style="position:absolute;inset:0;width:1920px;height:1080px;">
            <polyline points="{x+20},{y+92} {x+20},{ty} {tx},{ty}" fill="none" stroke="{accent}" stroke-width="3" stroke-dasharray="6,4"/>
            <circle cx="{tx}" cy="{ty}" r="10" fill="{accent}"/>
            <circle cx="{tx}" cy="{ty}" r="22" fill="none" stroke="{accent}" stroke-width="2" opacity="0.6"/>
          </svg>
          <div class="label"><div class="t">{title}</div>{f'<div class="s">{subtitle}</div>' if subtitle else ''}</div>
        </body></html>"""

    if mode == "split":
        left_t = item.get("left_title", "1. PROBLEM")
        left_s = item.get("left_sub", "")
        right_t = item.get("right_title", "2. SOLUTION")
        right_s = item.get("right_sub", "")
        return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
          *{{margin:0;padding:0;box-sizing:border-box;}}
          body{{width:1920px;height:1080px;background:transparent;position:relative;
               font-family:'Segoe UI','Nirmala UI',Arial,sans-serif;}}
          .div{{position:absolute;left:957px;top:0;width:6px;height:1080px;background:#FFD600;box-shadow:0 0 24px #FFD600;}}
          .box{{position:absolute;top:64px;width:820px;text-align:center;padding:18px 26px;
               background:rgba(5,10,18,0.82);border-bottom:4px solid #FFD600;border-radius:12px;}}
          .l{{left:70px;}} .r{{right:70px;}}
          .t{{font-size:44px;font-weight:900;color:#fff;letter-spacing:1.5px;text-shadow:0 3px 12px #000;}}
          .s{{font-size:22px;font-weight:700;color:#FFD600;margin-top:6px;}}
        </style></head><body>
          <div class="div"></div>
          <div class="box l"><div class="t">{left_t}</div><div class="s">{left_s}</div></div>
          <div class="box r"><div class="t">{right_t}</div><div class="s">{right_s}</div></div>
        </body></html>"""

    # Default: cta / lower-third glassmorphism
    badge = item.get("badge", "GMZ AI DOCUMENTARY STUDIO")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
      *{{margin:0;padding:0;box-sizing:border-box;}}
      body{{width:1920px;height:1080px;background:transparent;position:relative;
           font-family:'Segoe UI','Roboto',Arial,sans-serif;}}
      .card{{position:absolute;left:72px;bottom:86px;max-width:960px;padding:24px 36px;
            background:linear-gradient(135deg,rgba(8,14,26,0.90),rgba(14,26,44,0.80));
            backdrop-filter:blur(18px);border-left:6px solid {accent};border-bottom:2px solid {accent};
            border-radius:16px;box-shadow:0 18px 46px rgba(0,0,0,0.7),0 0 28px {accent}44;}}
      .badge{{display:inline-block;padding:5px 14px;margin-bottom:10px;background:{accent};color:#07101C;
             font-size:17px;font-weight:900;letter-spacing:2px;border-radius:6px;}}
      .title{{color:#FFF;font-size:42px;font-weight:900;line-height:1.15;}}
      .sub{{margin-top:8px;color:#D8E8F8;font-size:22px;font-weight:600;}}
    </style></head><body><div class="card"><div class="badge">{badge}</div><div class="title">{title}</div>
    <div class="sub">{subtitle}</div></div></body></html>"""


def main():
    ap = argparse.ArgumentParser(description="Render v5.0 Cinema Documentary style kinetic text, HUD pointers & split-screen overlays.")
    ap.add_argument("--specs-json", required=True, help="JSON list of overlay specs [{'file':'k01.png','mode':'impact','title':'...'}]")
    ap.add_argument("--out-dir", required=True, help="Output folder for transparent 1920x1080 PNGs")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    specs = json.loads(Path(args.specs_json).read_text(encoding="utf-8"))

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")
        except Exception:
            browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        for item in specs:
            out_p = out_dir / item["file"]
            page.set_content(make_overlay_html(item))
            page.screenshot(path=str(out_p), omit_background=True)
            print(f"  Rendered [{item.get('mode','impact')}] {out_p.name}")
        browser.close()
    print(f"DONE! Rendered {len(specs)} v5.0 kinetic overlays -> {out_dir}")


if __name__ == "__main__":
    main()

