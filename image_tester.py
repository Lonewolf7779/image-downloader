import argparse
import json
from PIL import Image, ImageChops
import numpy as np
import sys

def analyze_image(path):
    img = Image.open(path)
    info = {
        "path": path,
        "format": img.format,
        "mode": img.mode,
        "size": img.size,  # (width, height)
    }
    arr = np.asarray(img.convert("RGBA"), dtype=np.float32)  # stable shape
    # per-channel mean/std (RGBA)
    means = arr.mean(axis=(0,1)).tolist()
    stds = arr.std(axis=(0,1)).tolist()
    info.update({
        "means": means,
        "stds": stds,
        "pixels": int(arr.shape[0] * arr.shape[1])
    })
    return info

def mse(a, b):
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    return np.mean((a - b) ** 2)

def compare_images(path1, path2):
    a = Image.open(path1).convert("RGBA")
    b = Image.open(path2).convert("RGBA")
    if a.size != b.size:
        # resize smaller to larger while keeping aspect by simple resize to match sizes
        b = b.resize(a.size)
    arr_a = np.asarray(a, dtype=np.float32)
    arr_b = np.asarray(b, dtype=np.float32)
    e = mse(arr_a, arr_b)
    # compute percent different pixels using absolute difference threshold
    diff = np.abs(arr_a - arr_b).mean(axis=2)  # average per-pixel across channels
    diff_pixels = (diff > 1.0).sum()
    total = diff.size
    percent_diff = float(diff_pixels) / float(total) * 100.0
    # simple image difference summary using PIL
    diff_img = ImageChops.difference(a, b)
    bbox = diff_img.getbbox()
    return {
        "path1": path1,
        "path2": path2,
        "mse": float(e),
        "percent_pixels_different": percent_diff,
        "has_any_diff": bbox is not None
    }

def main(argv):
    p = argparse.ArgumentParser(prog="image_tester", description="Analyze and compare images")
    sub = p.add_subparsers(dest="cmd", required=True)
    sa = sub.add_parser("analyze", help="Analyze an image")
    sa.add_argument("image")
    sc = sub.add_parser("compare", help="Compare two images")
    sc.add_argument("image1")
    sc.add_argument("image2")
    args = p.parse_args(argv)
    if args.cmd == "analyze":
        out = analyze_image(args.image)
        print(json.dumps(out, indent=2))
    elif args.cmd == "compare":
        out = compare_images(args.image1, args.image2)
        print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main(sys.argv[1:])
