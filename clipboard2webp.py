# /// script
# dependencies = [
#     "pillow",
#     "rich",
# ]
# ///

import pathlib
import subprocess
import tempfile
import time
from PIL import ImageGrab
from rich.progress import Progress


def do_the_thing():
    yield "Grabbing clipboard..."
    im = ImageGrab.grabclipboard()
    if not im:
        raise ValueError("No image found in clipboard")
    outname = pathlib.Path.home() / "Desktop" / f"cb-{int(time.time())}.webp"
    with tempfile.NamedTemporaryFile(suffix=".ppm") as f:
        yield f"Saving {im.size} to temp file..."
        im.save(f.name)
        yield "Converting to webp..."
        subprocess.run(["cwebp", "-q", "95", "-mt", f.name, "-o", str(outname)])
    yield "Opening output file..."
    subprocess.run(["open", "-R", str(outname)])
    yield "Done!"


def main():
    with Progress() as progress:
        task = progress.add_task("Converting...", total=5)
        for msg in do_the_thing():
            progress.update(task, description=msg)
            progress.advance(task)


if __name__ == "__main__":
    main()
