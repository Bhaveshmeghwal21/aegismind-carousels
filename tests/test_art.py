from PIL import ImageChops, ImageStat

from carousel.art import make_art

TEXT_WHITE = 240  # text is pure white; the art must never get this bright


def test_art_is_a_1080x1350_greyscale_picture():
    img = make_art(1)
    assert img.size == (1080, 1350)
    assert img.mode == "L"


def test_art_is_deterministic_per_seed_and_varies_between_seeds():
    assert ImageChops.difference(make_art(7), make_art(7)).getbbox() is None
    assert ImageChops.difference(make_art(7), make_art(8)).getbbox() is not None


def test_art_is_dark_but_has_a_real_tonal_range():
    img = make_art(3)
    assert ImageStat.Stat(img).mean[0] < 80
    assert sum(1 for count in img.histogram() if count) >= 60


def test_art_stays_dimmer_than_the_text():
    assert make_art(5).getextrema()[1] < TEXT_WHITE
