import zlib
from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from .caption import build_caption, display_quote
from .errors import TextOverflowError, UnsupportedGlyphError
from .grade import grade_art, ramp
from .library import DEFAULT_ART_DIR, load_library, pick_art
from .models import Idea
from .music import DEFAULT_MUSIC_DIR, load_music, pick_music
from .video import make_reel

SIZE = (1080, 1350)
MARGIN = 70
MAX_WIDTH = SIZE[0] - 2 * MARGIN
CENTER = SIZE[0] // 2
HANDLE = "@theaegismind"

FONT_PATH = Path(__file__).resolve().parents[2] / "assets" / "fonts" / "EBGaramond-Variable.ttf"
WEIGHT = 500

BLACK, WHITE = (0, 0, 0), (255, 255, 255)
SOFT, DIM = (205, 205, 205), (140, 140, 140)

QUOTE_START, QUOTE_MIN, QUOTE_PITCH = 66, 40, 1.3
QUOTE_LAST_BASELINE = 1090
QUOTE_MAX_HEIGHT = 520
AUTHOR_SIZE, AUTHOR_BASELINE = 34, 1185
HANDLE_SIZE, HANDLE_BASELINE = 28, SIZE[1] - 60


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


def fit_quote(text: str, max_height: int, draw: ImageDraw.ImageDraw) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    """Largest font size (stepping down from QUOTE_START) whose balanced wrap fits max_height."""
    for size in range(QUOTE_START, QUOTE_MIN - 1, -2):
        font = _font(size)
        lines = _balanced_wrap(text, font, draw)
        if lines is None:
            continue
        pitch = int(size * QUOTE_PITCH)
        if pitch * len(lines) <= max_height:
            return font, lines, pitch
    raise TextOverflowError(f"text does not fit at {QUOTE_MIN}px: {text[:40]!r}...")


def render_image(quote: str, author: str, art: Image.Image) -> Image.Image:
    """One 1080x1350 post: the art, the quote in white serif, the thinker's name, the account handle."""
    shown, byline = display_quote(quote), f"— {author}"
    _check_glyphs(shown)
    _check_glyphs(byline)

    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    font, lines, pitch = fit_quote(shown, QUOTE_MAX_HEIGHT, probe)
    if probe.textlength(byline, font=_font(AUTHOR_SIZE)) > MAX_WIDTH:
        raise TextOverflowError(f"author name too long: {author!r}")
    first_baseline = QUOTE_LAST_BASELINE - pitch * (len(lines) - 1)

    # a scrim behind the text keeps it readable whatever the art is doing there
    scrim = ramp([(0, 1.0), (first_baseline - 230, 1.0), (first_baseline - 60, 0.45), (SIZE[1], 0.45)])
    img = Image.composite(art.convert("RGB"), Image.new("RGB", SIZE, BLACK), scrim)

    draw = ImageDraw.Draw(img)
    baseline = first_baseline
    for line in lines:
        draw.text((CENTER, baseline), line, font=font, fill=WHITE, anchor="ms")
        baseline += pitch
    draw.text((CENTER, AUTHOR_BASELINE), byline, font=_font(AUTHOR_SIZE), fill=SOFT, anchor="ms")
    draw.text((CENTER, HANDLE_BASELINE), HANDLE, font=_font(HANDLE_SIZE), fill=DIM, anchor="ms")
    return img


def render_post(
    idea: Idea,
    out_dir: Path,
    art_dir: Path = DEFAULT_ART_DIR,
    music_dir: Path = DEFAULT_MUSIC_DIR,
    reel_seconds: int = 0,
) -> list[Path]:
    """Write out_dir/post.png and out_dir/caption.txt. With reel_seconds, also out_dir/reel.mp4: the
    post held still with a public-domain recording under it, which the caption then credits.
    The art, grain and default music are chosen by the date, so a rerun gives identical files.
    A bad lookup, glyph or fit raises before anything is written."""
    library = load_library(art_dir)
    piece = pick_art(library, idea.date, idea.image or None)
    track = pick_music(load_music(music_dir), idea.date, idea.music or None) if reel_seconds else None
    art = grade_art(piece, art_dir, seed=zlib.crc32(idea.date.encode()))
    img = render_image(idea.quote, idea.author, art)
    caption = build_caption(idea, piece, track)

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "post.png"
    img.save(path, optimize=True)
    (out_dir / "caption.txt").write_text(caption + "\n", encoding="utf-8")
    paths = [path]
    if track:
        paths.append(make_reel(path, out_dir / "reel.mp4", reel_seconds, Path(music_dir) / track.file, track.start))
    return paths
