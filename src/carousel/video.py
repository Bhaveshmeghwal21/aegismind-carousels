"""Turn the finished post image into a plain Reel: the image held still, nothing else.

Instagram only attaches music to Reels, and a Reel must be a video file, so this is the smallest
possible video: the unchanged 1080x1350 post centred on a 1080x1920 black frame, with a silent audio track."""

import shutil
import subprocess
from pathlib import Path

REEL_SIZE = (1080, 1920)
IMAGE_TOP = 100  # bar above the image; the bigger bar below keeps the quote clear of Reels' caption overlay
IMAGE_HEIGHT = 1350
FRAME_RATE = 30


def find_ffmpeg() -> str:
    """ffmpeg on the PATH, else the copy bundled with the imageio-ffmpeg package."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
    except ImportError as err:
        raise RuntimeError("ffmpeg not found: install ffmpeg, or run: pip install imageio-ffmpeg") from err
    return imageio_ffmpeg.get_ffmpeg_exe()


def make_reel(
    image_path: Path, out_path: Path, seconds: int, audio: Path | None = None, audio_start: float = 0.0, light: bool = False
) -> Path:
    """Write an H.264 MP4 of `seconds` seconds with `audio` (from audio_start, faded in and out), or silent.
    `light` puts a white bar above the image and a black one below it (for the white ink layout) instead of two black bars.
    Nothing is left behind if ffmpeg fails."""
    image_path, out_path = Path(image_path), Path(out_path)
    if not image_path.exists():
        raise FileNotFoundError(image_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    partial = out_path.with_name(out_path.stem + ".partial.mp4")
    width, height = REEL_SIZE
    if light:
        below = IMAGE_TOP + IMAGE_HEIGHT
        frame = f"pad={width}:{height}:0:{IMAGE_TOP}:white,drawbox=x=0:y={below}:w={width}:h={height - below}:color=black:t=fill,format=yuv420p"
    else:
        frame = f"pad={width}:{height}:0:{IMAGE_TOP}:black,format=yuv420p"
    if audio:
        sound = [
            "-ss", f"{audio_start:.2f}", "-i", str(audio),
            "-af", f"afade=t=in:d=0.3,afade=t=out:st={max(seconds - 1.2, 0):.2f}:d=1.2,apad",
        ]
    else:
        sound = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    command = [
        find_ffmpeg(), "-v", "error", "-y",
        "-loop", "1", "-framerate", str(FRAME_RATE), "-i", str(image_path),
        *sound,
        "-t", str(seconds),
        "-vf", frame,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FRAME_RATE),
        "-c:a", "aac", "-b:a", "64k",
        "-movflags", "+faststart",
        str(partial),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True)
        partial.replace(out_path)
    finally:
        partial.unlink(missing_ok=True)
    return out_path
