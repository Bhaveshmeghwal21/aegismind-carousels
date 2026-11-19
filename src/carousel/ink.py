"""The ink layout: a white page, the quote in a heavy serif on top, the thinker and the work under it,
and an original black-and-white ink illustration filling the rest of the 1080x1350 post.

Only pure black, white and the illustration's own greys are used. The illustration's paper is pushed to
pure white so it melts into the page."""

import re
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .caption import display_quote
from .errors import TextOverflowError
from .library import ArtPiece
from .render import FONT_PATH, MAX_WIDTH, SIZE, _balanced_wrap, _check_glyphs

BLACK, WHITE = 0, 255
CENTER = SIZE[0] // 2
TOP = 74  # white space above the first line
GAP = 30  # white space between the text and the illustration
MIN_ART_HEIGHT = 640  # the illustration never gets squeezed below this
QUOTE_START, QUOTE_MIN, QUOTE_PITCH = 76, 44, 1.14
QUOTE_WEIGHT, AUTHOR_WEIGHT, SOURCE_WEIGHT = 700, 650, 500
AUTHOR_RATIO, SOURCE_RATIO = 0.74, 0.62
PAPER_FROM = 238  # anything lighter than this in the illustration becomes pure white
FADE_TOP = 48  # the illustration's top edge fades into the page over this many pixels


@lru_cache(maxsize=None)
def _font(size: int, weight: int) -> ImageFont.FreeTypeFont:
    # BASIC layout: same glyph placement on every machine, whether or not Raqm is installed
    font = ImageFont.truetype(str(FONT_PATH), size, layout_engine=ImageFont.Layout.BASIC)
    font.set_variation_by_axes([weight])
    return font


def short_source(source: str) -> str:
    """The work and section for the page: no translator, no trailing year in brackets."""
    text = re.split(r",?\s+tr\.\s", source.strip())[0]
    return re.sub(r"\s*\(\d{3,4}\)\s*$", "", text).strip()


def load_ink_art(piece: ArtPiece, art_dir: Path) -> Image.Image:
    """The illustration as a greyscale picture with a pure-white paper."""
    with Image.open(Path(art_dir) / piece.file) as source:
        img = ImageOps.grayscale(source)
    img = ImageOps.autocontrast(img, cutoff=0.3)
    return img.point(lambda v: WHITE if v >= PAPER_FROM else int(v * WHITE / PAPER_FROM))


def _cover(img: Image.Image, width: int, height: int, focus: tuple[float, float]) -> Image.Image:
    scale = max(width / img.width, height / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = int(min(max(focus[0] * img.width - width / 2, 0), img.width - width))
    top = int(min(max(focus[1] * img.height - height / 2, 0), img.height - height))
    return img.crop((left, top, left + width, top + height))


def _layout(quote: str, author: str, source: str, draw: ImageDraw.ImageDraw):
    """Largest quote size whose text block leaves the illustration at least MIN_ART_HEIGHT.
    Returns (quote font, quote lines, quote pitch, author font, author pitch, source font, source pitch)."""
    room = SIZE[1] - MIN_ART_HEIGHT - TOP - GAP
    for size in range(QUOTE_START, QUOTE_MIN - 1, -2):
        font = _font(size, QUOTE_WEIGHT)
        lines = _balanced_wrap(quote, font, draw)
        if lines is None:
            continue
        pitch = int(size * QUOTE_PITCH)
        author_size, source_size = round(size * AUTHOR_RATIO), round(size * SOURCE_RATIO)
        author_font, source_font = _font(author_size, AUTHOR_WEIGHT), _font(source_size, SOURCE_WEIGHT)
        author_pitch, source_pitch = int(author_size * 1.25), int(source_size * 1.25)
        if draw.textlength(f"— {author}", font=author_font) > MAX_WIDTH:
            raise TextOverflowError(f"author name too long: {author!r}")
        height = pitch * len(lines) + int(size * 0.35) + author_pitch + (source_pitch if source else 0)
        if height <= room:
            return font, lines, pitch, author_font, author_pitch, source_font, source_pitch
    raise TextOverflowError(f"text does not fit at {QUOTE_MIN}px: {quote[:40]!r}...")


def render_ink_image(quote: str, author: str, source: str, art: Image.Image, focus: tuple[float, float] = (0.5, 0.45)) -> Image.Image:
    """One 1080x1350 post: quote, thinker and work on white, the illustration below."""
    shown, byline, work = display_quote(quote), f"— {author}", short_source(source)
    for text in (shown, byline, work):
        _check_glyphs(text)

    page = Image.new("L", SIZE, WHITE)
    draw = ImageDraw.Draw(page)
    font, lines, pitch, author_font, author_pitch, source_font, source_pitch = _layout(shown, author, work, draw)

    y = TOP + round(font.size * 0.9)  # first baseline
    for line in lines:
        draw.text((CENTER, y), line, font=font, fill=BLACK, anchor="ms")
        y += pitch
    y += int(font.size * 0.35) - pitch + author_pitch
    draw.text((CENTER, y), byline, font=author_font, fill=BLACK, anchor="ms")
    if work:
        y += source_pitch
        draw.text((CENTER, y), work, font=source_font, fill=BLACK, anchor="ms")

    art_top = y + GAP
    picture = _cover(art, SIZE[0], SIZE[1] - art_top, focus)
    fade = Image.new("L", picture.size, 255)
    fade_draw = ImageDraw.Draw(fade)
    for row in range(FADE_TOP):
        fade_draw.line([0, row, picture.width, row], fill=int(255 * row / FADE_TOP))
    page.paste(Image.composite(picture, Image.new("L", picture.size, WHITE), fade), (0, art_top))
    return page.convert("RGB")
