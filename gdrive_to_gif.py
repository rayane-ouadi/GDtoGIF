"""
Google Drive Video to GIF Converter
Converts a Google Drive video link into a 5-second GIF at 720p resolution.

Requirements:
    pip install yt-dlp

    Also install ffmpeg:
      Windows : winget install ffmpeg
      macOS   : brew install ffmpeg
      Linux   : sudo apt install ffmpeg

Usage:
    python gdrive_to_gif.py
"""

import os
import re
import sys
import subprocess
import tempfile
from pathlib import Path


# ── Configuration ─────────────────────────────────────────────────────────────
GIF_DURATION_SECONDS = 5    # How many seconds to capture
GIF_WIDTH  = 1280           # 720p width
GIF_HEIGHT = 720            # 720p height
GIF_FPS    = 15             # Frames per second (lower = smaller file)
START_TIME = 0              # Start offset in seconds (0 = from the very beginning)
OUTPUT_DIR = Path.home() / "Downloads"
# ──────────────────────────────────────────────────────────────────────────────


def extract_file_id(url: str) -> str:
    """Pull the Google Drive file ID out of any common share-link format."""
    patterns = [
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"open\?id=([a-zA-Z0-9_-]+)",
        r"[?&]id=([a-zA-Z0-9_-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    raise ValueError(
        "Could not find a file ID in that URL.\n"
        "Supported formats:\n"
        "  https://drive.google.com/file/d/FILE_ID/view?usp=sharing\n"
        "  https://drive.google.com/open?id=FILE_ID"
    )


def build_direct_url(file_id: str) -> str:
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def check_ffmpeg() -> None:
    try:
        subprocess.run(["ffmpeg", "-version"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        sys.exit(
            "ERROR: ffmpeg is not installed or not on your PATH.\n"
            "  Windows: winget install ffmpeg\n"
            "  macOS  : brew install ffmpeg\n"
            "  Linux  : sudo apt install ffmpeg"
        )


def download_video(url: str, dest: str) -> None:
    try:
        import yt_dlp
    except ImportError:
        sys.exit("ERROR: yt-dlp is not installed.\nRun: pip install yt-dlp")

    opts = {
        "outtmpl": dest,
        "quiet": False,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])


def convert_to_gif(video_path: str, gif_path: str) -> None:
    """Two-pass ffmpeg encode for a high-quality, palette-optimised GIF."""
    print(f"\nConverting: {GIF_DURATION_SECONDS}s  |  {GIF_WIDTH}x{GIF_HEIGHT}  |  {GIF_FPS} fps")

    vf_scale = (
        f"scale={GIF_WIDTH}:{GIF_HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={GIF_WIDTH}:{GIF_HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
        f"fps={GIF_FPS}"
    )

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as pf:
        palette = pf.name

    try:
        # Pass 1 – build colour palette
        subprocess.run([
            "ffmpeg", "-y",
            "-ss", str(START_TIME), "-t", str(GIF_DURATION_SECONDS),
            "-i", video_path,
            "-vf", f"{vf_scale},palettegen=max_colors=256:stats_mode=diff",
            palette,
        ], check=True)

        # Pass 2 – render GIF using the palette
        subprocess.run([
            "ffmpeg", "-y",
            "-ss", str(START_TIME), "-t", str(GIF_DURATION_SECONDS),
            "-i", video_path,
            "-i", palette,
            "-lavfi", f"{vf_scale} [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=5",
            gif_path,
        ], check=True)

    finally:
        if os.path.exists(palette):
            os.remove(palette)


def main() -> None:
    check_ffmpeg()

    print("=" * 55)
    print("  Google Drive Video  →  5-Second 720p GIF")
    print("=" * 55)

    url = input("\nPaste your Google Drive video URL:\n> ").strip()
    if not url:
        sys.exit("No URL entered – exiting.")

    file_id = extract_file_id(url)
    direct  = build_direct_url(file_id)
    print(f"\nFile ID : {file_id}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    gif_path = str(OUTPUT_DIR / f"gdrive_{file_id[:8]}.gif")

    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "source_video.mp4")
        print("\nDownloading video …")
        download_video(direct, raw)

        # yt-dlp may append an extension, find the real file
        candidates = list(Path(tmp).glob("source_video*"))
        if not candidates:
            sys.exit("Download failed – no video file found in temp directory.")
        raw = str(candidates[0])

        convert_to_gif(raw, gif_path)

    size_mb = os.path.getsize(gif_path) / 1_048_576
    print(f"\nDone!  GIF saved to : {gif_path}")
    print(f"       File size    : {size_mb:.1f} MB")


if __name__ == "__main__":
    main()