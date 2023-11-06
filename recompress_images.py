"""
This script _lossily_ recompresses and possibly resizes
a directory tree full of JPEG files into another tree.

It depends on graphicsmagick, jpeg-archive and jpegoptim.
If you're using macOS, you can find these in Homebrew.
"""

import argparse
import functools
import json
import os
import shutil
import subprocess
import multiprocessing.dummy as mp
import time
from PIL import Image

import tqdm


def process_image(args, relpath):
    input_path = os.path.join(args.input_directory, relpath)
    output_path = os.path.join(args.output_directory, relpath)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    orig_size = os.stat(input_path).st_size
    resized = False

    if not os.path.exists(output_path):
        with Image.open(input_path) as img:
            width, height = img.size

        if width > args.max_size or height > args.max_size:
            subprocess.check_call(
                [
                    "gm",
                    "convert",
                    "-resize",
                    "%dx%d>" % (args.max_size, args.max_size),
                    input_path,
                    output_path,
                ],
            )
            resized = True
        else:
            shutil.copy(input_path, output_path)
            resized = False

        subprocess.check_call(
            [
                "jpeg-recompress",
                "--quiet",
                output_path,
                output_path,
            ],
        )
        subprocess.check_call(
            [
                "jpegoptim",
                "--strip-all",
                # '--max=90',
                "--quiet",
                output_path,
            ],
        )

    new_size = os.stat(output_path).st_size

    if new_size == 0:
        print("Catastrophic recompression error with %s, just copying :(" % relpath)
        shutil.copy(input_path, output_path)
        resized = False

    return {
        "name": relpath,
        "resized": resized,
        "orig_size": orig_size,
        "new_size": new_size,
        "ratio": (new_size / orig_size),
    }


def get_images(input_directory):
    files = []
    image_formats = {".jpg", ".jpeg", ".png"}
    for dirname, dirnames, filenames in os.walk(input_directory):
        for f in filenames:
            f = os.path.join(dirname, f)
            ext = os.path.splitext(f)[-1].lower()
            if ext not in image_formats:
                continue
            files.append(os.path.relpath(f, input_directory))
    files.sort()
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_directory")
    ap.add_argument("output_directory")
    ap.add_argument("--max-size", default=2000, type=int)
    ap.add_argument("--log-file", default=None)
    args = ap.parse_args()
    args.log_file = args.log_file or "recompress-log-%s.jsonl" % time.time()
    files = get_images(args.input_directory)
    pool = mp.Pool()

    with open(args.log_file, "w") as logfp:
        print("Logging to:", logfp.name)
        mapper = pool.imap_unordered(
            functools.partial(process_image, args),
            files,
            chunksize=32,
        )
        for result in tqdm.tqdm(mapper, total=len(files)):
            logfp.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    main()
