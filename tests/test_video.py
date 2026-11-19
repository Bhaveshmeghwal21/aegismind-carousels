import re
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from carousel.video import find_ffmpeg, make_reel


def probe(path: Path) -> str:
    """ffmpeg prints the stream details to stderr when given only an input."""
    return subprocess.run([find_ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr


@pytest.fixture
def post(tmp_path: Path) -> Path:
    path = tmp_path / "post.png"
    Image.new("RGB", (1080, 1350), (120, 120, 120)).save(path)
    return path


def test_find_ffmpeg_returns_a_working_program():
    result = subprocess.run([find_ffmpeg(), "-version"], capture_output=True, text=True)
    assert result.returncode == 0 and "ffmpeg version" in result.stdout


def test_reel_is_a_1080x1920_h264_video_of_the_requested_length(tmp_path: Path, post: Path):
    out = make_reel(post, tmp_path / "reel.mp4", seconds=2)
    info = probe(out)
    assert out == tmp_path / "reel.mp4"
    assert "Video: h264" in info and "1080x1920" in info
    assert re.search(r"Duration: 00:00:0[12]\.", info), info


def test_reel_has_a_silent_audio_track_so_every_player_accepts_it(tmp_path: Path, post: Path):
    assert "Audio: aac" in probe(make_reel(post, tmp_path / "reel.mp4", seconds=1))


def test_reel_holds_the_image_still_between_black_bars(tmp_path: Path, post: Path):
    out = make_reel(post, tmp_path / "reel.mp4", seconds=2)
    frame = tmp_path / "frame.png"
    subprocess.run(
        [find_ffmpeg(), "-v", "error", "-y", "-ss", "1", "-i", str(out), "-frames:v", "1", str(frame)], check=True
    )
    img = Image.open(frame).convert("L")
    assert img.getpixel((540, 20)) < 25  # black bar above the image
    assert 105 <= img.getpixel((540, 900)) <= 135  # the image itself, unchanged
    assert img.getpixel((540, 1850)) < 25  # black bar below it


def mean_volume(path: Path) -> float:
    log = subprocess.run(
        [find_ffmpeg(), "-hide_banner", "-i", str(path), "-vn", "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True,
        text=True,
    ).stderr
    return float(re.search(r"mean_volume: (-?[\d.]+) dB", log).group(1))


def test_reel_without_music_is_silent(tmp_path: Path, post: Path):
    assert mean_volume(make_reel(post, tmp_path / "reel.mp4", seconds=2)) < -70


def test_reel_plays_the_chosen_music_for_its_whole_length(tmp_path: Path, post: Path, music_dir: Path):
    out = make_reel(post, tmp_path / "reel.mp4", seconds=4, audio=music_dir / "tone-a.m4a", audio_start=0.5)
    info = probe(out)
    assert "Audio: aac" in info and "Video: h264" in info
    assert re.search(r"Duration: 00:00:0[34]\.", info), info
    assert mean_volume(out) > -40


def test_missing_image_raises_and_writes_nothing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        make_reel(tmp_path / "nope.png", tmp_path / "reel.mp4", seconds=1)
    assert not (tmp_path / "reel.mp4").exists()
