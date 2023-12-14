import argparse
import os
import pathlib
import shutil

import tqdm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--source", required=True)
    ap.add_argument("-d", "--destination", required=True)
    args = ap.parse_args()

    source = pathlib.Path(args.source)
    destination = pathlib.Path(args.destination)

    for src_path in tqdm.tqdm(list(source.glob("**/*"))):
        if not src_path.is_file():
            continue
        dest_path = destination / src_path.relative_to(source)
        try:
            dest_stat = dest_path.stat()
        except FileNotFoundError:
            print("Copying", dest_path)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src_path, dest_path)
            continue
        else:
            src_stat = src_path.stat()
            if dest_stat.st_size == src_stat.st_size:
                os.utime(dest_path, ns=(src_stat.st_atime_ns, src_stat.st_mtime_ns))
                src_path.unlink()
                print("Unlinked", src_path)
                continue

        #
        # if not dest_path.exists():
        #     print(f"Copying {path} to {dest_path}")
        #     shutil.copy(path, dest_path)
        #


if __name__ == "__main__":
    main()
