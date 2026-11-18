from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from .errors import TextOverflowError, UnsupportedGlyphError
from .models import Idea
from .palette import BLACK, RED, WHITE

SIZE = (1080, 1350)
MARGIN = 60
MAX_WIDTH = SIZE[0] - 2 * MARGIN
HANDLE = "@theaegismind"

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"
HEADLINE_FONT = FONT_DIR / "Anton-Regular.ttf"
BODY_FONT = FONT_DIR / "Inter-Variable.ttf"

FOOTER_SIZE = 28
FOOTER_BASELINE = SIZE[1] - MARGIN
BODY_BOTTOM = FOOTER_BASELINE - 80  # keep body text clear of the footer


@lru_cache(maxsize=None)
def _cmap(path: Path) -> frozenset[int]:
    return frozenset(TTFont(path).getBestCmap())


def _check_glyphs(text: str, font_path: Path) -> None:
    cmap = _cmap(font_path)
    for ch in text:
        if ord(ch) not in cmap:
            raise UnsupportedGlyphError(f"{ch!r} (U+{ord(ch):04X}) is not in {font_path.name}")


def _wrap(text: str, font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw) -> list[str] | None:
    """Greedy word wrap to MAX_WIDTH. None if a single word is wider than a line."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        if draw.textlength(word, font=font) > MAX_WIDTH:
            return None
        trial = f"{current} {word}".strip()
        if current and draw.textlength(trial, font=font) > MAX_WIDTH:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def _fit(
    text: str,
    font_path: Path,
    start: int,
    minimum: int,
    max_height: int,
    pitch_factor: float,
    draw: ImageDraw.ImageDraw,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    """Largest font size (stepping down) whose wrapped text fits max_height."""
    for size in range(start, minimum - 1, -2):
        font = ImageFont.truetype(str(font_path), size)
        lines = _wrap(text, font, draw)
        if lines is None:
            continue
        pitch = int(size * pitch_factor)
        if pitch * len(lines) <= max_height:
            return font, lines, pitch
    raise TextOverflowError(f"text does not fit at {minimum}px: {text[:40]!r}...")


def _footer(draw: ImageDraw.ImageDraw, index: int, total: int) -> None:
    font = ImageFont.truetype(str(BODY_FONT), FOOTER_SIZE)
    draw.text((MARGIN, FOOTER_BASELINE), f"{index}/{total}", font=font, fill=WHITE, anchor="ls")
    draw.text((SIZE[0] - MARGIN, FOOTER_BASELINE), HANDLE, font=font, fill=WHITE, anchor="rs")


def _draw_headline_block(draw: ImageDraw.ImageDraw, text: str, start: int) -> None:
    """Red bar above a large white headline, centred vertically (hook and closing slides)."""
    text = text.upper()
    _check_glyphs(text, HEADLINE_FONT)
    bar_h, gap = 14, 56
    area_top, area_bottom = MARGIN, BODY_BOTTOM
    font, lines, pitch = _fit(
        text, HEADLINE_FONT, start, 70, area_bottom - area_top - bar_h - gap, 1.12, draw
    )
    cap_h = -font.getbbox("H", anchor="ls")[1]
    text_h = cap_h + pitch * (len(lines) - 1)
    block_h = bar_h + gap + text_h
    top = area_top + (area_bottom - area_top - block_h) // 2
    draw.rectangle((MARGIN, top, MARGIN + 140, top + bar_h - 1), fill=RED)
    baseline = top + bar_h + gap + cap_h
    for line in lines:
        draw.text((MARGIN, baseline), line, font=font, fill=WHITE, anchor="ls")
        baseline += pitch


def _draw_idea_block(draw: ImageDraw.ImageDraw, title: str, body: str) -> None:
    title = title.upper()
    _check_glyphs(title, HEADLINE_FONT)
    _check_glyphs(body, BODY_FONT)
    top = MARGIN + 60
    t_font, t_lines, t_pitch = _fit(title, HEADLINE_FONT, 120, 52, 400, 1.12, draw)
    cap_h = -t_font.getbbox("H", anchor="ls")[1]
    baseline = top + cap_h
    for line in t_lines:
        draw.text((MARGIN, baseline), line, font=t_font, fill=RED, anchor="ls")
        baseline += t_pitch
    if not body.strip():
        return
    body_top = baseline - t_pitch + 56
    b_font, b_lines, b_pitch = _fit(body, BODY_FONT, 66, 30, BODY_BOTTOM - body_top, 1.4, draw)
    y = body_top
    for line in b_lines:
        draw.text((MARGIN, y), line, font=b_font, fill=WHITE, anchor="la")
        y += b_pitch


def render_slide(kind: str, title: str, body: str, index: int, total: int) -> Image.Image:
    """Render one 1080x1350 slide. kind is "hook", "idea" or "closing"."""
    img = Image.new("RGB", SIZE, BLACK)
    draw = ImageDraw.Draw(img)
    if kind in ("hook", "closing"):
        _draw_headline_block(draw, title, 170)
    elif kind == "idea":
        _draw_idea_block(draw, title, body)
    else:
        raise ValueError(f"unknown slide kind: {kind!r}")
    _footer(draw, index, total)
    return img


def render_carousel(idea: Idea, out_dir: Path, closing_line: str) -> list[Path]:
    """Write slide-1.png .. slide-N.png (N = len(idea.slides) + 2). Nothing is written if any slide fails."""
    total = len(idea.slides) + 2
    images = [render_slide("hook", idea.hook, "", 1, total)]
    for i, slide in enumerate(idea.slides, start=2):
        images.append(render_slide("idea", slide.title, slide.body, i, total))
    images.append(render_slide("closing", closing_line, "", total, total))

    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for n, img in enumerate(images, start=1):
        path = out_dir / f"slide-{n}.png"
        img.save(path, optimize=True)
        paths.append(path)
    return paths
