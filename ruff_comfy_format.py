from __future__ import annotations

import argparse
import dataclasses
import subprocess


@dataclasses.dataclass(frozen=True)
class TestResult:
    width: int
    added: int
    deleted: int
    changed_files: int
    files: dict[str, tuple[int, int]]

    @property
    def total_delta(self):
        return self.added + self.deleted


def check_width(target, width: int) -> TestResult:
    subprocess.check_call(["git", "restore", target])
    subprocess.check_call(["ruff", "format", "-q", f"--line-length={width}", target])
    files = {}
    for line in subprocess.check_output(
        ["git", "diff", "--numstat", target],
        text=True,
    ).splitlines():
        line = line.strip()
        if not line:
            continue
        added, deleted, file = line.split(None)
        files[file] = (int(added), int(deleted))
    return TestResult(
        width=width,
        added=sum(added for added, _ in files.values()),
        deleted=sum(deleted for _, deleted in files.values()),
        changed_files=len(files),
        files=files,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--min-width", type=int, default=72)
    ap.add_argument("--max-width", type=int, default=120)
    args = ap.parse_args()

    widths = range(args.min_width, args.max_width + 1)
    target = args.target

    if subprocess.call(["git", "diff", "--quiet", "--exit-code", target]) != 0:
        ap.error("Target is not clean, refusing to work on it.")

    result_map = {}

    try:
        for width in widths:
            if not (width % 2 == 0 or width % 5 == 0):
                continue
            result_map[width] = check_width(target, width)
    finally:
        subprocess.check_call(["git", "restore", target])
    results = sorted(result_map.values(), key=lambda r: r.total_delta)
    print("Rank | Width | Total Delta")
    for i, result in enumerate(results, 1):
        print(f"{i:4d} | {result.width:5d} | {result.total_delta:11d}")


if __name__ == "__main__":
    main()
