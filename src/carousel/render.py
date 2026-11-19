import zlib
from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from .art import make_art, ramp
from .errors import TextOverflowError, UnsupportedGlyphError
from .models import Idea

SIZE = (1080, 1350)
MARGIN = 70
MAX_WIDTH = SIZE[0] - 2 * MARGIN
CENTER = SIZE[0] // 2
HANDLE = "@theaegismind"

FONT_PATH = Path(__file__).resolve().parents[2] / "assets" / "fonts" / "EBGaramond-Variable.ttf"
WEIGHT = 500

BLACK, WHITE = (0, 0, 0), (255, 255, 255)
SOFT, DIM = (205, 205, 205), (140, 140, 140)

HOOK_START, HOOK_MIN, HOOK_PITCH = 68, 40, 1.3
LABEL_SIZE, LABEL_BASELINE = 28, 170
HOOK_FIRST_BASELINE = LABEL_BASELINE + 110
TEXT_BOTTOM = 820
HANDLE_SIZE, HANDLE_BASELINE = 28, SIZE[1] - 70


@lru_cache(maxsize=None)
def _cmap() -> frozenset[int]:
    return frozenset(TTFont(FONT_PATH).getBestCmap())


@lru_cache(maxsize=None)
def _font(size: int) -> ImageFont.FreeTypeFont:
    # BASIC layout: same glyph placement on every machine, whether or not Raqm is installed
    font = ImageFont.truetype(str(FONT_PATH), size, layout_engine=ImageFont.Layout.BASIC)
    font.set_variation_by_axes([WEIGHT])
    return font


def _check_glyphs(text: str) -> None:
    cmap = _cmap()
    for ch in text:
        if ord(ch) not in cmap:
            raise UnsupportedGlyphError(f"{ch!r} (U+{ord(ch):04X}) is not in {FONT_PATH.name}")


def _wrap(text: str, font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw, width: int) -> list[str] | None:
    """Greedy word wrap to `width`. None if a single word is wider than a line."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        if draw.textlength(word, font=font) > width:
            return None
        trial = f"{current} {word}".strip()
        if current and draw.textlength(trial, font=font) > width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def _balanced_wrap(text: str, font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw) -> list[str] | None:
    """Wrap to MAX_WIDTH, then narrow the lines as far as possible without adding a line,
    so the last line is never a lone straggler."""
    lines = _wrap(text, font, draw, MAX_WIDTH)
    if lines is None or len(lines) < 2:
        return lines
    low, high = 0, MAX_WIDTH
    while low < high:
        mid = (low + high) // 2
        trial = _wrap(text, font, draw, mid)
        if trial is not None and len(trial) <= len(lines):
            high = mid
        else:
            low = mid + 1
    return _wrap(text, font, draw, high)


def fit_hook(text: str, max_height: int, draw: ImageDraw.ImageDraw) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    """Largest font size (stepping down from HOOK_START) whose balanced wrap fits max_height."""
    for size in range(HOOK_START, HOOK_MIN - 1, -2):
        font = _font(size)
        lines = _balanced_wrap(text, font, draw)
        if lines is None:
            continue
        pitch = int(size * HOOK_PITCH)
        if pitch * len(lines) <= max_height:
            return font, lines, pitch
    raise TextOverflowError(f"text does not fit at {HOOK_MIN}px: {text[:40]!r}...")


def render_image(hook: str, topic: str, seed: int) -> Image.Image:
    """One 1080x1350 post: dark art, a small topic label, the hook line, the account handle."""
    label = topic.upper()
    _check_glyphs(hook)
    _check_glyphs(label)

    art = make_art(seed).convert("RGB")
    fade_in = ramp([(0, 0.0), (330, 0.0), (720, 1.0), (SIZE[1], 1.0)])
    img = Image.composite(art, Image.new("RGB", SIZE, BLACK), fade_in)

    draw = ImageDraw.Draw(img)
    draw.text((CENTER, LABEL_BASELINE), label, font=_font(LABEL_SIZE), fill=SOFT, anchor="ms")
    font, lines, pitch = fit_hook(hook, TEXT_BOTTOM - HOOK_FIRST_BASELINE, draw)
    baseline = HOOK_FIRST_BASELINE
    for line in lines:
        draw.text((CENTER, baseline), line, font=font, fill=WHITE, anchor="ms")
        baseline += pitch
    draw.text((CENTER, HANDLE_BASELINE), HANDLE, font=_font(HANDLE_SIZE), fill=DIM, anchor="ms")
    return img


def render_post(idea: Idea, out_dir: Path) -> list[Path]:
    """Write out_dir/post.png for this idea. The picture is seeded by the date, so a rerun is identical."""
    img = render_image(idea.hook, idea.topic, seed=zlib.crc32(idea.date.encode()))
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "post.png"
    img.save(path, optimize=True)
    return [path]
