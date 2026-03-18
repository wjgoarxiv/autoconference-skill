"""
Generate autoconference cover image (2560x1024).
Warm charcoal canvas, amber/gold + teal blobs, bold monospace title, rounded corners.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 2560, 1024
CORNER_RADIUS = 80

# 1. Base canvas
base = Image.new("RGBA", (W, H), (13, 13, 10, 255))

# 2. Color blobs
def make_blob(size, color_rgba, cx, cy, rx, ry):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color_rgba)
    return layer

blobs = [
    (180, 120,   0, 200,  700, 480, 700, 400, 120),
    (220, 170,  20, 160, 1900, 180, 600, 350, 100),
    (  0, 120, 100, 180, 1280, 920, 900, 300,  90),
    (160, 140,  20, 120, 1400, 500, 500, 300,  80),
]

canvas = base.copy()
for r, g, b, a, cx, cy, rx, ry, blur in blobs:
    blob = make_blob((W, H), (r, g, b, a), cx, cy, rx, ry)
    blob = blob.filter(ImageFilter.GaussianBlur(radius=blur))
    canvas = Image.alpha_composite(canvas, blob)

canvas = canvas.filter(ImageFilter.GaussianBlur(radius=8))

# 3. Film grain
rng = np.random.default_rng(42)
noise = rng.integers(0, 255, (H, W), dtype=np.uint8)
grain_alpha = (noise * 0.22).astype(np.uint8)
grain_layer = np.stack([noise, noise, noise, grain_alpha], axis=-1).astype(np.uint8)
grain_img = Image.fromarray(grain_layer, "RGBA")
canvas = Image.alpha_composite(canvas, grain_img)

# 4. Fonts
TITLE_SIZE = 180
SUBTITLE_SIZE = 54

try:
    font_title = ImageFont.truetype("/Users/woojin/Library/Fonts/JetBrainsMonoNerdFont-Bold.ttf", TITLE_SIZE)
    font_subtitle = ImageFont.truetype("/Users/woojin/Library/Fonts/JetBrainsMonoNerdFont-Regular.ttf", SUBTITLE_SIZE)
except Exception:
    try:
        font_title = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", TITLE_SIZE, index=1)
        font_subtitle = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", SUBTITLE_SIZE, index=0)
    except Exception:
        font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", TITLE_SIZE)
        font_subtitle = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", SUBTITLE_SIZE)

TITLE_TEXT = "autoconference"
SUBTITLE_TEXT = "Researchers compete, collaborate, and synthesize."

# 5. Measure text — retry with smaller size if too wide
tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(tmp)
t_bbox = d.textbbox((0, 0), TITLE_TEXT, font=font_title)
t_w = t_bbox[2] - t_bbox[0]

if t_w > 2300:
    TITLE_SIZE = 160
    try:
        font_title = ImageFont.truetype("/Users/woojin/Library/Fonts/JetBrainsMonoNerdFont-Bold.ttf", TITLE_SIZE)
    except Exception:
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", TITLE_SIZE, index=1)
        except Exception:
            font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", TITLE_SIZE)
    t_bbox = d.textbbox((0, 0), TITLE_TEXT, font=font_title)
    t_w = t_bbox[2] - t_bbox[0]

t_h = t_bbox[3] - t_bbox[1]
s_bbox = d.textbbox((0, 0), SUBTITLE_TEXT, font=font_subtitle)
s_w = s_bbox[2] - s_bbox[0]
s_h = s_bbox[3] - s_bbox[1]

GAP = 60
total_h = t_h + GAP + s_h
block_top = (H - total_h) // 2 - 30
title_x = (W - t_w) // 2 - t_bbox[0]
title_y = block_top - t_bbox[1]
subtitle_x = (W - s_w) // 2 - s_bbox[0]
subtitle_y = title_y + t_h + GAP

# 6. Title with glow
def draw_text_layer(text, x, y, font, color):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((x, y), text, font=font, fill=color)
    return layer

glow_specs = [
    ((255, 180,  80,  60), 18),
    ((255, 210, 120,  90),  9),
    ((255, 235, 180, 120),  4),
]
for color, blur_r in glow_specs:
    glow = draw_text_layer(TITLE_TEXT, title_x, title_y, font_title, color)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_r))
    canvas = Image.alpha_composite(canvas, glow)

title_layer = draw_text_layer(TITLE_TEXT, title_x, title_y, font_title, (255, 255, 255, 245))
canvas = Image.alpha_composite(canvas, title_layer)

# 7. Subtitle
subtitle_layer = draw_text_layer(
    SUBTITLE_TEXT, subtitle_x, subtitle_y, font_subtitle, (192, 180, 150, 210)
)
canvas = Image.alpha_composite(canvas, subtitle_layer)

# 8. Rounded corner mask
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (W - 1, H - 1)], radius=CORNER_RADIUS, fill=255)
canvas.putalpha(mask)

# 9. Final polish blur
canvas = canvas.filter(ImageFilter.GaussianBlur(radius=1))

# 10. Save
out_path = str(Path(__file__).parent / "cover.png")
canvas.save(out_path, "PNG", dpi=(400, 400))
print(f"Saved: {out_path}")
print(f"Size: {canvas.size}")
print(f"Mode: {canvas.mode}")
