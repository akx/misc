"""
This script takes a Ruff report JSON file, looks for `F401` issues
in `__init__.py` files, and generates `__all__` expressions for the
seemingly unused names.
"""

import argparse
import json
from collections import defaultdict


def process_files(things_by_file, write: bool) -> None:
    for filename, things in things_by_file.items():
        all_expression_bits = ["__all__ = [\n"]
        for thing in sorted(things):
            all_expression_bits.append(f"    {thing!r},\n".replace("'", '"'))
        all_expression_bits.append("]")
        all_expression = "".join(all_expression_bits)

        if write:
            with open(filename, "a") as f:
                f.write("\n\n")
                f.write(all_expression)
                f.write("\n")
        else:
            print("\n**", filename, "**")
            print()
            print(all_expression)
            print()


def read_f401_names(json_path: str):
    things_by_file = defaultdict(set)
    with open(json_path) as f:
        for issue in json.load(f):
            if issue["code"] != "F401":
                continue
            filename = issue["filename"]
            if not filename.endswith("__init__.py"):
                continue
            thing = issue["message"].lstrip("`").partition("`")[0]
            basename = thing.rpartition(".")[-1]
            things_by_file[filename].add(basename)
    return things_by_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json", help="Ruff report JSON")
    ap.add_argument("-w", "--write", action="store_true", help="Actually write")
    args = ap.parse_args()
    things_by_file = read_f401_names(args.json)
    process_files(things_by_file, write=args.write)


if __name__ == "__main__":
    main()
