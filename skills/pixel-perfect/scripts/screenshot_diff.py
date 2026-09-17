#!/usr/bin/env python3
"""
Pixel-diff two images (or two URLs, screenshotting them first) and produce a
match score plus a visual diff heatmap. Typical uses:

  - a baseline preview vs a proposed preview (regression check)
  - a proposed preview vs a Figma design export (design-fidelity check)

Usage (two existing images):
    python screenshot_diff.py --image-a a.png --image-b b.png --out-dir <dir>

Usage (two URLs — screenshots them with Playwright first):
    python screenshot_diff.py --url-a http://localhost:4100 --url-b http://localhost:4101 --out-dir <dir>

Requires Pillow, and Playwright for the --url mode. Neither needs to be a
dependency of the target repo being reviewed — this is tooling for the review
process, running in the agent's own working environment. If missing, install
them there: `pip install pillow` and, for --url mode,
`pip install playwright && playwright install chromium`.

Prints a JSON result to stdout, e.g.:
    {
      "match_pct": 98.7,
      "dimensions_match": true,
      "image_a_size": [1440, 900],
      "image_b_size": [1440, 900],
      "diff_bbox": [12, 340, 210, 410],
      "diff_image": "<path>",
      "note": null
    }
"""
import argparse
import json
import os
import sys

# Per-channel absolute difference below this is treated as harmless noise
# (anti-aliasing, compression artifacts) rather than a real mismatch.
DIFF_THRESHOLD = 15


def screenshot_url(url: str, out_path: str, viewport=(1440, 900)) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
        page.goto(url, wait_until="networkidle", timeout=15000)
        page.screenshot(path=out_path, full_page=True)
        browser.close()


def diff_images(path_a: str, path_b: str, out_dir: str) -> dict:
    from PIL import Image, ImageChops

    orig_a = Image.open(path_a).convert("RGB")
    orig_b = Image.open(path_b).convert("RGB")
    img_a, img_b = orig_a, orig_b

    dimensions_match = orig_a.size == orig_b.size
    note = None

    if not dimensions_match:
        # A size mismatch is often a real finding on its own (missing content,
        # wrong viewport) — pad to the union size so the rest of the pixels
        # can still be compared, but surface the mismatch explicitly.
        w = max(orig_a.size[0], orig_b.size[0])
        h = max(orig_a.size[1], orig_b.size[1])
        canvas_a = Image.new("RGB", (w, h), "white")
        canvas_a.paste(orig_a, (0, 0))
        canvas_b = Image.new("RGB", (w, h), "white")
        canvas_b.paste(orig_b, (0, 0))
        img_a, img_b = canvas_a, canvas_b
        note = (
            f"Image dimensions differ (A={orig_a.size}, B={orig_b.size}) — "
            "padded to compare the overlap, but treat the size mismatch itself as a finding."
        )

    diff = ImageChops.difference(img_a, img_b)
    bbox = diff.getbbox()

    # Heatmap: grayscale of image A with differing regions painted in red.
    # Counts the changed-pixel total in the same pass to avoid a second
    # full-image scan (and Pillow's deprecated Image.getdata()).
    heatmap = img_a.convert("L").convert("RGB")
    heat_pixels = heatmap.load()
    diff_pixels = diff.load()
    w, h = heatmap.size
    changed = 0
    for y in range(h):
        for x in range(w):
            if max(diff_pixels[x, y]) > DIFF_THRESHOLD:
                heat_pixels[x, y] = (255, 0, 64)
                changed += 1

    total = w * h
    match_pct = round(100 * (1 - changed / total), 2) if total else 100.0

    os.makedirs(out_dir, exist_ok=True)
    diff_path = os.path.join(out_dir, "screenshot_diff_heatmap.png")
    heatmap.save(diff_path)

    return {
        "match_pct": match_pct,
        "dimensions_match": dimensions_match,
        "image_a_size": list(orig_a.size),
        "image_b_size": list(orig_b.size),
        "diff_bbox": list(bbox) if bbox else None,
        "diff_image": diff_path,
        "note": note,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--image-a")
    ap.add_argument("--image-b")
    ap.add_argument("--url-a")
    ap.add_argument("--url-b")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--out-json", default=None, help="Optional path to also write the JSON result to")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    if args.url_a and args.url_b:
        path_a = os.path.join(args.out_dir, "shot_a.png")
        path_b = os.path.join(args.out_dir, "shot_b.png")
        try:
            screenshot_url(args.url_a, path_a)
            screenshot_url(args.url_b, path_b)
        except ImportError:
            print(json.dumps({
                "error": "Playwright not installed. Run: pip install playwright && playwright install chromium"
            }))
            sys.exit(1)
    elif args.image_a and args.image_b:
        path_a, path_b = args.image_a, args.image_b
    else:
        print(json.dumps({"error": "Provide either --image-a/--image-b or --url-a/--url-b"}))
        sys.exit(1)

    try:
        result = diff_images(path_a, path_b, args.out_dir)
    except ImportError:
        print(json.dumps({"error": "Pillow not installed. Run: pip install pillow"}))
        sys.exit(1)

    if args.out_json:
        with open(args.out_json, "w") as f:
            json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
