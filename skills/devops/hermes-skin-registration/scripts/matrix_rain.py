#!/usr/bin/env python3
"""Render a looping Matrix-rain GIF for terminal background images.

Usage: python3 matrix_rain.py [output.gif]   (default: matrix-rain-blue.gif)
Edit palette constants at top for hue variants (blue default; green = classic Matrix).
Requires Pillow. Verify the result by extracting a frame and viewing it
(vision_analyze) before delivering to the user.
"""
import random
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 960, 540
CELL = 16                       # glyph cell size
COLS = W // CELL
FRAMES = 40
FPS_DELAY = 70                  # ms per frame
OUT = sys.argv[1] if len(sys.argv) > 1 else "matrix-rain-blue.gif"

# Swap to BG=(0,6,0), HEAD=(200,255,200), SUB=(60,200,60), TAIL=(0,60,20) for green
BG = (0, 0, 6)
HEAD = (190, 235, 255)
SUB = (90, 170, 255)
TAIL = (20, 90, 255)

CHARS = "アカサタナハマヤラワイキシチニヒミリギ0123456789ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ"

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            continue
    return ImageFont.load_default()

FNT = font(CELL - 2)

class Column:
    def __init__(self):
        self.reset(True)
    def reset(self, init=False):
        self.y = random.uniform(-H, 0) if init else random.uniform(-200, -20)
        self.speed = random.choice((CELL, CELL, int(CELL * 1.5)))
        self.len = random.randint(6, 22)
        self.stream = [random.choice(CHARS) for _ in range(60)]
    def step(self):
        self.y += self.speed
        if self.y - self.len * CELL > H:
            self.reset()

cols = [Column() for _ in range(COLS)]
img = Image.new("RGB", (W, H), BG)
frames = []

for f in range(FRAMES):
    d = ImageDraw.Draw(img)
    # NOTE: box must be a sequence — rectangle(0,0,W,H,fill=...) raises TypeError
    d.rectangle([0, 0, W - 1, H - 1], fill=BG)
    for x, c in enumerate(cols):
        c.step()
        head = int(c.y)
        for i in range(c.len):
            yy = head - i * CELL
            if yy < -CELL or yy > H:
                continue
            ch = c.stream[(i + f) % len(c.stream)]
            if i == 0:
                col = HEAD
            elif i == 1:
                col = SUB
            else:
                fade = max(0.08, 1.0 - i / c.len)
                col = tuple(int(v * fade) for v in TAIL)
            d.text((x * CELL, yy), ch, font=FNT, fill=col)
    frames.append(img.copy())

frames[0].save(OUT, save_all=True, append_images=frames[1:],
               duration=FPS_DELAY, loop=0, optimize=True)
print("wrote", OUT)
