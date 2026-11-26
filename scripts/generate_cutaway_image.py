"""
Daily Learn 3.0 Style — 16:9 3D Cutaway, Metaphor & Thumbnail Art Generator
Uses nano-banana-pro-preview (fallback: gemini-3.1-flash-image) via Google AI Studio key.
Generates crisp, text-free 16:9 photorealistic 3D engineering cutaways and visual metaphors.
"""

import argparse
import json
import os
import time
from pathlib import Path
from google import genai
from google.genai import types

PRIMARY_IMG_MODEL = "nano-banana-pro-preview"
FALLBACK_IMG_MODEL = "gemini-3.1-flash-image"


def load_api_key(env_path: str | None = None) -> str:
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"].strip()
    candidates = [Path(env_path)] if env_path else [Path.cwd() / ".env", Path(r"f:\Daily Learn 3.0\.env")]
    for p in candidates:
        if p and p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("GEMINI_API_KEY not found in environment or .env file!")


def generate_one(client: genai.Client, prompt: str, out_path: Path):
    full_prompt = (
        f"{prompt.strip()}. "
        "Ultra-detailed photorealistic cinema documentary 16:9 widescreen composition, "
        "dramatic rim lighting, hyper-realistic textures, NO garbled text, NO watermarks."
    )
    for model in (PRIMARY_IMG_MODEL, FALLBACK_IMG_MODEL):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
            )
            for part in resp.candidates[0].content.parts:
                if getattr(part, "inline_data", None) and part.inline_data.data:
                    out_path.write_bytes(part.inline_data.data)
                    return model
        except Exception as e:
            print(f"  [WARN] {model} failed ({str(e)[:120]}), trying fallback...")
            time.sleep(2)
    raise RuntimeError(f"Failed to generate image for {out_path.name}")


def main():
    ap = argparse.ArgumentParser(description="Batch generate 16:9 AI cutaway & metaphor visuals.")
    ap.add_argument("--prompts-json", required=True, help="JSON list: [{'id': 'shot_01', 'prompt': '...'}]")
    ap.add_argument("--out-dir", required=True, help="Output folder for generated PNGs")
    ap.add_argument("--delay", type=float, default=4.0, help="Delay between requests (seconds)")
    ap.add_argument("--env", default=None, help="Optional .env path")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    items = json.loads(Path(args.prompts_json).read_text(encoding="utf-8"))
    client = genai.Client(api_key=load_api_key(args.env))

    for idx, item in enumerate(items, 1):
        out_path = out_dir / f"{item['id']}.png"
        if out_path.exists() and out_path.stat().st_size > 10000:
            print(f"[{idx}/{len(items)}] Skipping existing {out_path.name}")
            continue
        print(f"[{idx}/{len(items)}] Generating {out_path.name}...")
        used = generate_one(client, item["prompt"], out_path)
        print(f"  -> Saved ({used}): {out_path}")
        if idx < len(items):
            time.sleep(args.delay)


if __name__ == "__main__":
    main()
