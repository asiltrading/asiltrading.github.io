#!/usr/bin/env python3
"""
Generate the site-wide OG image for the Russian site (assets/img/og-image-ru.png),
mirroring the layout/branding of the English assets/img/og-image.png.

Usage:
  python3 tools/og_image/generate_site_og.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LOGO_PATH = ROOT / "assets" / "img" / "logo.png"
FONT_DIR = Path(__file__).resolve().parent / "fonts"
OUT_PATH = ROOT / "assets" / "img" / "og-image-ru.png"

W, H = 1200, 630
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
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def draw_chip(draw, x, y, text, font, padding_x=20, padding_y=12):
    tw = draw.textlength(text, font=font)
    ascent, descent = font.getmetrics()
    th = ascent + descent
    box = (x, y, x + int(tw) + padding_x * 2, y + th + padding_y * 2)
    draw.rounded_rectangle(box, radius=10, fill=CHIP_FILL, outline=CHIP_BORDER, width=2)
    draw.text((box[0] + padding_x, box[1] + padding_y - 2), text, font=font, fill=CHIP_TEXT)
    return box[2] - box[0], box[3] - box[1]


def main():
    img = make_background()
    draw = ImageDraw.Draw(img, "RGBA")

    # Left vertical accent
    draw.rectangle([(60, 60), (64, H - 60)], fill=CYAN)

    # Brand wordmark + underline
    brand_font = load_font("Montserrat-Bold.ttf", 44)
    bx, by = 100, 60
    brand_text = "ASIL TRADING"
    draw.text((bx, by), brand_text, font=brand_font, fill=WHITE)
    bw = draw.textlength(brand_text, font=brand_font)
    draw.rectangle([(bx, by + 58), (bx + bw, by + 62)], fill=CYAN)

    # Headline (3 lines): white / cyan / white
    headline_font = load_font("Montserrat-Bold.ttf", 56)
    line_h = headline_font.size + 12
    headline_y = 160
    draw.text((100, headline_y),                "Морские, офшорные и",  font=headline_font, fill=WHITE)
    draw.text((100, headline_y + line_h),       "промышленные",          font=headline_font, fill=CYAN)
    draw.text((100, headline_y + 2 * line_h),   "запасные части",        font=headline_font, fill=WHITE)

    # Chips
    chip_font = load_font("Montserrat-SemiBold.ttf", 22)
    chips_row_1 = ["Двигатели", "Насосы", "Навигация"]
    chips_row_2 = ["Датчики", "Электрика", "Вспомогательное"]
    chip_y_1 = headline_y + 3 * line_h + 8
    gap = 14
    x = 100
    for text in chips_row_1:
        cw, ch = draw_chip(draw, x, chip_y_1, text, chip_font)
        x += cw + gap
    chip_y_2 = chip_y_1 + 60
    x = 100
    for text in chips_row_2:
        cw, ch = draw_chip(draw, x, chip_y_2, text, chip_font)
        x += cw + gap

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

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_PATH, "PNG", optimize=True)
    print(f"wrote {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
