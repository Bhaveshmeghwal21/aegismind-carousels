"""Original dark landscape art, drawn in code: a pale moon behind layered ridges and mist.

Greyscale only. Every random choice comes from `random.Random(seed)`, so a seed always gives
the same picture on every machine (Pillow's own noise generator is not seeded, so it is not used).
"""

import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

W, H = 1080, 1350
HORIZON = int(H * 0.66)
MOON = 205
MAX_TONE = 215  # text is pure white; the art must stay clearly dimmer than it
RIDGE_SHADES = (58, 40, 24, 10, 0)


def ramp(stops: list[tuple[int, float]]) -> Image.Image:
    """Full-size mask that changes only with height. stops = [(y, value 0..1), ...] in y order."""

    def value(y: int) -> float:
        if y <= stops[0][0]:
            return stops[0][1]
        for (y0, v0), (y1, v1) in zip(stops, stops[1:]):
            if y <= y1:
                return v0 + (v1 - v0) * (y - y0) / max(1, y1 - y0)
        return stops[-1][1]

    column = Image.new("L", (1, H))
    column.putdata([int(255 * value(y)) for y in range(H)])
    return column.resize((W, H))


def _cloud(rng: random.Random, cell: int, blur: int) -> Image.Image:
    """Soft blotchy noise, stretched to the full 0..255 range."""
    size = (W // cell, H // cell)
    raw = Image.frombytes("L", size, rng.randbytes(size[0] * size[1]))
    soft = raw.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))
    return ImageOps.autocontrast(soft, cutoff=2)


def _sky() -> Image.Image:
    sky = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(sky)
    for y in range(H):
        draw.line([(0, y), (W, y)], fill=int(6 + 74 * min(1.0, y / HORIZON) ** 1.7))
    return sky


def _moon(img: Image.Image, rng: random.Random) -> tuple[Image.Image, int]:
    """Add a glowing moon. Returns the image and the moon's centre height."""
    x = int(W * rng.uniform(0.3, 0.7))
    y = int(HORIZON - H * rng.uniform(0.11, 0.19))  # low enough to clear a two or three line hook
    r = rng.randint(120, 170)

    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([x - 2 * r, y - 2 * r, x + 2 * r, y + 2 * r], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(100)).point(lambda v: int(v * 0.55))
    img = Image.composite(Image.new("L", (W, H), MOON), img, glow)

    disc = Image.new("L", (W * 2, H * 2), 0)
    ImageDraw.Draw(disc).ellipse([(x - r) * 2, (y - r) * 2, (x + r) * 2, (y + r) * 2], fill=255)
    disc = disc.resize((W, H), Image.LANCZOS)
    patches = _cloud(rng, 14, 14).point(lambda v: max(0, min(255, int((v - 128) * 1.6 + 170))))
    surface = Image.composite(Image.new("L", (W, H), MOON), Image.new("L", (W, H), 125), patches)
    img.paste(surface, (0, 0), disc)

    mist = ramp([(0, 0.0), (y + int(r * 0.15), 0.0), (HORIZON, 0.78), (H, 0.78)])
    mist = ImageChops.multiply(mist, _cloud(rng, 8, 26))
    return Image.composite(Image.new("L", (W, H), 70), img, mist.point(lambda v: int(v * 0.8))), y


def _ridges(img: Image.Image, rng: random.Random) -> Image.Image:
    for i, shade in enumerate(RIDGE_SHADES):
        base = HORIZON - 20 + i * 62
        amps = [rng.uniform(40, 80) - i * 6, rng.uniform(14, 30), rng.uniform(5, 12)]
        freqs = [rng.uniform(0.0035, 0.007), rng.uniform(0.012, 0.02), rng.uniform(0.04, 0.07)]
        phases = [rng.uniform(0, 2 * math.pi) for _ in range(3)]
        points = []
        for x in range(0, W + 8, 6):
            height = sum(a * (0.5 + 0.5 * math.sin(x * f + p)) for a, f, p in zip(amps, freqs, phases))
            points.append((x, base - height))
        ridge = Image.new("L", (W, H), 0)
        ImageDraw.Draw(ridge).polygon(points + [(W, H), (0, H)], fill=255)
        img.paste(Image.new("L", (W, H), shade), (0, 0), ridge)

        band = Image.new("L", (W, H), 0)
        ImageDraw.Draw(band).rectangle([0, base - 10, W, base + 40], fill=int(110 - i * 16))
        band = ImageChops.multiply(band.filter(ImageFilter.GaussianBlur(34)), _cloud(rng, 8, 20))
        img = Image.composite(Image.new("L", (W, H), 120), img, band.point(lambda v: int(v * 0.55)))
    return img


def make_art(seed: int) -> Image.Image:
    """A 1080x1350 greyscale ("L") picture, never brighter than MAX_TONE."""
    rng = random.Random(seed)
    img, _ = _moon(_sky(), rng)
    img = _ridges(img, rng)
    grain = Image.frombytes("L", (W, H), rng.randbytes(W * H)).point(lambda v: 128 + (v - 128) // 5)
    img = ImageChops.add(img, grain, scale=1.0, offset=-128)
    return img.point(lambda v: min(v, MAX_TONE))
