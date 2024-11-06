"""
Merge multiple images into a single image, arranging them in a grid according to the specified number of rows and columns,
saving each merged image to a file with a template name that includes the index of the merged image.
"""

import argparse
import json

import tqdm
from PIL import Image


def chunk(objs, n):
    acc = []
    for obj in objs:
        acc.append(obj)
        if len(acc) == n:
            yield tuple(acc)
            acc = []
    if acc:
        yield tuple(acc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--columns", "-c", type=int, required=True)
    parser.add_argument("--rows", "-r", type=int, required=True)
    parser.add_argument("--output-template", "-o", required=True)
    parser.add_argument("--output-start-index", default=1, type=int)
    parser.add_argument("--save-options", default={}, type=json.loads)
    args = parser.parse_args()
    n_per_page = args.columns * args.rows
    if "%" not in args.output_template:
        args.error("output template must contain %")

    for nup_index, filenames in tqdm.tqdm(
        enumerate(chunk(args.files, n_per_page), start=args.output_start_index),
        total=len(args.files) // n_per_page,
    ):
        out_name = args.output_template % nup_index
        images = [Image.open(filename) for filename in filenames]
        largest_width = max(image.width for image in images)
        largest_height = max(image.height for image in images)
        width = largest_width * args.columns
        height = largest_height * args.rows
        new_image = Image.new("RGB", (width, height))
        for i, image in enumerate(images):
            r, c = divmod(i, args.columns)
            x = c * largest_width
            y = r * largest_height
            print(f"{out_name} image {i+1}/{len(images)}: Placing at {x}, {y}")
            # TODO: center within cell
            assert x < width - 1
            assert y < height - 1
            new_image.paste(image, (x, y))
        new_image.save(out_name, **args.save_options)


if __name__ == "__main__":
    main()
