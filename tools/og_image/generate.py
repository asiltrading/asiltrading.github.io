#!/usr/bin/env python3
"""
Generate per-part Open Graph images for the parts catalogue.

Usage:
  python3 tools/og_image/generate.py                  # generate any missing
  python3 tools/og_image/generate.py --force          # regenerate all
  python3 tools/og_image/generate.py _parts/foo.md    # one file

Reads front matter from each _parts/*.md, renders a 1200x630 PNG that
mirrors the home og-image branding, and writes it to
assets/img/og/<slug>.png. The slug matches the file basename, which is
also what Jekyll uses for the permalink (/parts/:slug/).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PARTS_DIR = ROOT / "_parts"
OUT_DIR = ROOT / "assets" / "img" / "og"
LOGO_PATH = ROOT / "assets" / "img" / "logo.png"
FONT_DIR = Path(__file__).resolve().parent / "fonts"

W, H = 1200, 630

# Brand palette (sampled from the home og-image)
BG_TOP = (10, 18, 38)
BG_BOTTOM = (4, 10, 22)
GRID = (255, 255, 255, 10)
CYAN = (45, 196, 245)
WHITE = (255, 255, 255)
CHIP_FILL = (18, 30, 56)
CHIP_BORDER = (60, 90, 130)
CHIP_TEXT = (220, 232, 245)


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def parse_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip().splitlines()
    data: dict = {}
    for line in block:
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip('"').strip("'")
        data[key.strip()] = value
    return data


def make_background() -> Image.Image:
    img = Image.new("RGB", (W, H), BG_BOTTOM)
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        r = int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t)
        for x in range(W):
            px[x, y] = (r, g, b)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    step = 40
    for x in range(0, W, step):
        draw.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, step):
        draw.line([(0, y), (W, y)], fill=GRID, width=1)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img


def draw_rounded_rect(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def wrap_to_width(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        w = draw.textlength(candidate, font=font)
        if w <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_title(text: str, max_width: int, max_lines: int, draw: ImageDraw.ImageDraw, start: int = 72, min_size: int = 44) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    size = start
    while size >= min_size:
        font = load_font("Montserrat-Bold.ttf", size)
        lines = wrap_to_width(text, font, max_width, draw)
        if len(lines) <= max_lines and all(draw.textlength(ln, font=font) <= max_width for ln in lines):
            return font, lines
        size -= 2
    font = load_font("Montserrat-Bold.ttf", min_size)
    lines = wrap_to_width(text, font, max_width, draw)
    return font, lines[:max_lines]


def render(part: dict, out_path: Path) -> None:
    title = part.get("title", "").strip() or "Marine Spare Parts"
    manufacturer = part.get("manufacturer", "").strip()
    model = part.get("model", "").strip()
    category = part.get("category", "").strip()

    img = make_background()
    draw = ImageDraw.Draw(img, "RGBA")

    # Left vertical accent
    draw.rectangle([(60, 60), (64, H - 60)], fill=CYAN)

    # Brand wordmark + underline
    brand_font = load_font("Montserrat-Bold.ttf", 36)
    brand_text = "ASIL TRADING"
    bx, by = 100, 70
    draw.text((bx, by), brand_text, font=brand_font, fill=WHITE)
    bw = draw.textlength(brand_text, font=brand_font)
    draw.rectangle([(bx, by + 48), (bx + bw, by + 51)], fill=CYAN)

    # Manufacturer eyebrow (cyan, small caps)
    eyebrow_font = load_font("Montserrat-SemiBold.ttf", 26)
    eyebrow_y = 170
    if manufacturer:
        draw.text((100, eyebrow_y), manufacturer.upper(), font=eyebrow_font, fill=CYAN)
        title_y = eyebrow_y + 46
    else:
        title_y = eyebrow_y

    # Main title — prefer model as the prominent text if available, else full title.
    headline = model if model else title
    if manufacturer and model and title.lower() != f"{manufacturer} {model}".lower():
        # If the title carries extra qualifier (e.g. "Hyundai MAN B&W 6S50MC-C"), keep full title.
        headline = title.replace(manufacturer, "").strip() or title

    max_text_width = 720  # leave room for the logo on the right
    title_font, lines = fit_title(headline, max_text_width, max_lines=2, draw=draw)
    line_h = title_font.size + 8
    for i, ln in enumerate(lines):
        draw.text((100, title_y + i * line_h), ln, font=title_font, fill=WHITE)

    sub_y = title_y + len(lines) * line_h + 14

    # Sub-line
    sub_font = load_font("Montserrat-Medium.ttf", 28)
    sub_text = "Spare Parts Catalogue"
    draw.text((100, sub_y), sub_text, font=sub_font, fill=(200, 215, 235))

    # Category chip
    if category:
        chip_font = load_font("Montserrat-SemiBold.ttf", 22)
        chip_padding_x, chip_padding_y = 22, 12
        chip_text = category.upper()
        tw = draw.textlength(chip_text, font=chip_font)
        ascent, descent = chip_font.getmetrics()
        th = ascent + descent
        chip_y = sub_y + 60
        chip_box = (100, chip_y, 100 + int(tw) + chip_padding_x * 2, chip_y + th + chip_padding_y * 2)
        draw_rounded_rect(draw, chip_box, radius=10, fill=CHIP_FILL, outline=CHIP_BORDER, width=2)
        draw.text((chip_box[0] + chip_padding_x, chip_box[1] + chip_padding_y - 2), chip_text, font=chip_font, fill=CHIP_TEXT)

    # Logo on the right
    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGBA")
        target_h = 420
        ratio = target_h / logo.height
        target_w = int(logo.width * ratio)
        logo = logo.resize((target_w, target_h), Image.LANCZOS)
        lx = W - target_w - 60
        ly = (H - target_h) // 2
        img.paste(logo, (lx, ly), logo)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="Specific _parts/*.md files. Default: all.")
    parser.add_argument("--force", action="store_true", help="Regenerate even if the output already exists.")
    args = parser.parse_args()

    paths = [Path(p) for p in args.files] if args.files else sorted(PARTS_DIR.glob("*.md"))
    if not paths:
        print("No part files found.", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = skipped = 0
    for path in paths:
        slug = path.stem
        out = OUT_DIR / f"{slug}.png"
        if out.exists() and not args.force:
            skipped += 1
            continue
        fm = parse_front_matter(path)
        if not fm:
            print(f"skip (no front matter): {path}")
            continue
        render(fm, out)
        generated += 1
        print(f"  wrote {out.relative_to(ROOT)}")

    print(f"\nDone. generated={generated} skipped={skipped} total={len(paths)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
