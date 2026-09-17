#!/usr/bin/env python3
"""
Separate real layout offsets from rasterisation noise.

For each named region, compare the reference (Figma export) against the
implementation screenshot at the region's own position AND at every integer
shift within ±radius, and report the shift that minimises the mean absolute
difference. A region whose best shift is (0,0) with a low residual is
anti-aliasing; a region whose best shift is (+1,0) or (0,-2) with a much lower
residual than at (0,0) is a real offset of that many pixels — go fix it.

    python shift_search.py --image-a figma/s19.png --image-b dev/s19.png \
        --regions '{"headline":[509,198,1003,280],"card":[500,362,1012,456]}' \
        [--scale 2] [--radius 4]

--scale multiplies the region boxes (given in CSS px) so the same region file
works for 1x and 2x captures. Pure Pillow, no numpy.
"""
import argparse, json
from PIL import Image, ImageChops, ImageStat

def mean_diff(a, b):
    return ImageStat.Stat(ImageChops.difference(a, b)).mean[0]

def best_shift(a, b, box, radius):
    x0, y0, x1, y1 = box
    ref = a.crop(box)
    best = None
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            d = mean_diff(ref, b.crop((x0 + dx, y0 + dy, x1 + dx, y1 + dy)))
            if best is None or d < best[0]:
                best = (d, dx, dy)
    return mean_diff(ref, b.crop(box)), best

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--image-a", required=True, help="reference (Figma export)")
    p.add_argument("--image-b", required=True, help="implementation screenshot, same size")
    p.add_argument("--regions", required=True, help='JSON {name:[x0,y0,x1,y1]} or @file.json')
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--radius", type=int, default=3)
    p.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = p.parse_args()
    regions = json.load(open(args.regions[1:])) if args.regions.startswith("@") else json.loads(args.regions)
    a = Image.open(args.image_a).convert("L"); b = Image.open(args.image_b).convert("L")
    assert a.size == b.size, f"size mismatch {a.size} vs {b.size} — capture at the export's scale"
    out = {}
    for name, box in regions.items():
        box = tuple(int(round(v * args.scale)) for v in box)
        d0, (d, dx, dy) = best_shift(a, b, box, args.radius)
        out[name] = {"diff_at_0": round(d0, 2), "best_diff": round(d, 2), "dx": dx, "dy": dy}
        if not args.json:
            verdict = "aligned" if (dx, dy) == (0, 0) else f"implementation is offset {dx:+d},{dy:+d}px (device px at this scale)"
            print(f"{name:16s} diff@0={d0:6.2f}  best={d:6.2f} at dx={dx:+d} dy={dy:+d}   {verdict}")
    if args.json:
        print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
