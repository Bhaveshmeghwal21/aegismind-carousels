import dataclasses

from PIL import Image, ImageChops, ImageStat

from carousel.grade import grade_art
from carousel.library import load_library

TEXT_WHITE = 240  # text is pure white; graded art must stay clearly dimmer


def piece(art_dir, name="a1", **changes):
    return dataclasses.replace(load_library(art_dir)[name], **changes)


def test_graded_art_is_a_1080x1350_greyscale_picture(art_dir):
    img = grade_art(piece(art_dir), art_dir, seed=1)
    assert img.size == (1080, 1350) and img.mode == "RGB"
    r, g, b = img.split()
    assert ImageChops.difference(r, g).getbbox() is None
    assert ImageChops.difference(g, b).getbbox() is None


def test_graded_art_sinks_into_black_at_the_bottom(art_dir):
    img = grade_art(piece(art_dir), art_dir, seed=1).convert("L")
    assert ImageStat.Stat(img.crop((0, 1250, 1080, 1350))).mean[0] < 25


def test_graded_art_is_never_as_bright_as_the_text(art_dir):
    assert grade_art(piece(art_dir), art_dir, seed=1).convert("L").getextrema()[1] < TEXT_WHITE


def test_grading_is_deterministic_per_seed(art_dir):
    a = grade_art(piece(art_dir), art_dir, seed=3)
    assert ImageChops.difference(a, grade_art(piece(art_dir), art_dir, seed=3)).getbbox() is None
    assert ImageChops.difference(a, grade_art(piece(art_dir), art_dir, seed=4)).getbbox() is not None


def test_focus_moves_the_crop(art_dir):
    left = grade_art(piece(art_dir, focus=(0.1, 0.1)), art_dir, seed=1)
    right = grade_art(piece(art_dir, focus=(0.9, 0.9)), art_dir, seed=1)
    assert ImageChops.difference(left, right).getbbox() is not None


def test_vignette_sinks_the_edges_but_keeps_the_subject(art_dir):
    plain = grade_art(piece(art_dir), art_dir, seed=1).convert("L")
    dark = grade_art(piece(art_dir, vignette=(540, 500, 250, 330, 0.0)), art_dir, seed=1).convert("L")
    corner = (0, 0, 120, 120)
    centre = (480, 440, 600, 560)
    assert ImageStat.Stat(dark.crop(corner)).mean[0] < 0.25 * ImageStat.Stat(plain.crop(corner)).mean[0]
    assert ImageStat.Stat(dark.crop(centre)).mean[0] > 0.8 * ImageStat.Stat(plain.crop(centre)).mean[0]


def test_crop_trims_a_paper_margin(art_dir):
    framed = Image.new("L", (600, 800), 255)
    framed.paste(Image.new("L", (440, 640), 90), (80, 80))
    framed.save(art_dir / "framed.jpg", quality=95)
    uncropped = grade_art(piece(art_dir, file="framed.jpg", focus=(0.5, 0.5)), art_dir, seed=1).convert("L")
    cropped = grade_art(
        piece(art_dir, file="framed.jpg", focus=(0.5, 0.5), crop=(0.2, 0.15, 0.8, 0.85)), art_dir, seed=1
    ).convert("L")
    top_strip = (0, 0, 1080, 60)
    assert ImageStat.Stat(uncropped.crop(top_strip)).mean[0] > ImageStat.Stat(cropped.crop(top_strip)).mean[0] + 40
