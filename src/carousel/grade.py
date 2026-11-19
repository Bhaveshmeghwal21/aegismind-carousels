"""Turn an art piece into a dark black-and-white 1080x1350 background."""

import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

from .library import ArtPiece

W, H = 1080, 1350
MAX_TONE = 235  # text is pure white; the art must stay clearly dimmer
SUBJECT_AT = (0.5, 0.40)  # where the art's focus point lands on the canvas, as fractions


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


def _cover(img: Image.Image, focus: tuple[float, float]) -> Image.Image:
    """Scale to fill the canvas, cropping around the focus point."""
    scale = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = int(min(max(focus[0] * img.width - SUBJECT_AT[0] * W, 0), img.width - W))
    top = int(min(max(focus[1] * img.height - SUBJECT_AT[1] * H, 0), img.height - H))
    return img.crop((left, top, left + W, top + H))


def grade_art(piece: ArtPiece, art_dir: Path, seed: int) -> Image.Image:
    """Greyscale, darkened, framed on the subject, sunk into black at the bottom, with film grain."""
    with Image.open(Path(art_dir) / piece.file) as source:
        img = ImageOps.grayscale(source)
    if piece.crop:
        left, top, right, bottom = piece.crop
        img = img.crop((int(left * img.width), int(top * img.height), int(right * img.width), int(bottom * img.height)))
    img = ImageOps.autocontrast(_cover(img, piece.focus), cutoff=1)
    img = img.point(lambda v: int(255 * (v / 255) ** piece.gamma))

    if piece.vignette:
        cx, cy, rx, ry, floor = piece.vignette
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(110)).point(lambda v: int(floor * 255 + (1 - floor) * v))
        img = ImageChops.multiply(img, mask)

    img = ImageChops.multiply(img, ramp([(0, 1.0), (760, 1.0), (1080, 0.12), (H, 0.0)]))
    grain = Image.frombytes("L", (W, H), random.Random(seed).randbytes(W * H)).point(lambda v: 128 + (v - 128) // 7)
    img = ImageChops.add(img, grain, 1.0, -128).point(lambda v: min(v, MAX_TONE))
    return img.convert("RGB")
