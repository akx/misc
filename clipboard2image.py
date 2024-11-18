# /// script
# dependencies = [
#     "numpy",
#     "pillow",
#     "rich",
# ]
# ///

import argparse
import io
import pathlib
import subprocess
import tempfile
import time

from PIL import ImageGrab, Image
from rich.progress import Progress


def calculate_psnr(img1, img2, max_value=255):
    """ "Calculating peak signal-to-noise ratio (PSNR) between two images."""
    import numpy as np

    mse = np.mean(
        (np.array(img1, dtype=np.float32) - np.array(img2, dtype=np.float32)) ** 2,
    )
    if mse == 0:
        return 100
    return 20 * np.log10(max_value / (np.sqrt(mse)))


def encode_to_target_psnr(
    progress: Progress,
    im: Image,
    target_psnr: float,
    format: str,
    max_steps: int = 10,
):
    """Encode an image to a target PSNR."""
    if format != "jpeg":
        raise ValueError(f"Unsupported format: {format}")
    psnr_task = progress.add_task("Encoding to target PSNR...", total=max_steps)

    min_quality = 5
    max_quality = 99
    bio = None
    try:
        for step in range(max_steps):
            quality = (min_quality + max_quality) // 2
            bio = io.BytesIO()
            im.save(bio, format="jpeg", quality=quality, optimize=True)
            bio.seek(0)
            with Image.open(bio) as im2:
                psnr = calculate_psnr(im, im2)
            progress.update(
                psnr_task,
                advance=1,
                description=f"Encoding to target PSNR {target_psnr}... {quality=}, {psnr=:.2f}",
            )
            if abs(psnr - target_psnr) < 2:
                break
            if psnr < target_psnr:
                min_quality = quality
            else:
                max_quality = quality
            if max_quality - min_quality <= 1:
                break
        bio.seek(0)
        return bio.getvalue()

    finally:
        progress.update(psnr_task, completed=1)


def do_the_thing(*, progress: Progress, format: str):
    main_task = progress.add_task("Converting...", total=5)
    progress.update(main_task, description="Grabbing clipboard...", advance=1)
    im = ImageGrab.grabclipboard()
    if not im:
        raise ValueError("No image found in clipboard")
    outname = pathlib.Path.home() / "Desktop" / f"cb-{int(time.time())}.{format}"
    with tempfile.NamedTemporaryFile(suffix=".ppm") as f:
        if format == "webp":
            progress.update(
                main_task,
                description=f"Saving {im.size} ({im.format}) to temp file...",
                advance=1,
            )
            im.save(f.name)
            progress.update(
                main_task,
                description="Converting to webp...",
                advance=1,
            )
            subprocess.run(["cwebp", "-q", "95", "-mt", f.name, "-o", str(outname)])
        elif format == "jpeg":
            jpeg_bytes = encode_to_target_psnr(
                progress,
                im,
                target_psnr=45,
                format="jpeg",
            )
            progress.update(
                main_task,
                description="Writing to output file...",
                advance=1,
            )
            outname.write_bytes(jpeg_bytes)
        elif format == "png":
            progress.update(
                main_task,
                description="Saving to output file...",
                advance=1,
            )
            im.save(outname, format="png", optimize=True, compress_level=9)
        else:
            raise ValueError(f"Unknown format: {format}")
    progress.update(main_task, description="Opening output file...", advance=1)
    subprocess.run(["open", "-R", str(outname)])
    progress.update(main_task, description="Done", completed=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--format", choices=("webp", "jpeg", "png"), default="webp")
    args = ap.parse_args()
    with Progress() as progress:
        do_the_thing(progress=progress, format=args.format)


if __name__ == "__main__":
    main()
