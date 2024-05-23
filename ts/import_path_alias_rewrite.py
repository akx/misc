import argparse
import dataclasses
import difflib
import pathlib
import re
from functools import partial

from_comp_re = re.compile(r" from '(.+)';$", re.MULTILINE)


@dataclasses.dataclass(frozen=True)
class Context:
    root_path: pathlib.Path
    accepted_segments: list[str]

    def is_acceptable(self, at_path: str):
        if not self.accepted_segments:
            return True
        return any(seg in at_path for seg in self.accepted_segments)


def handle_from(m: re.Match, *, path: pathlib.Path, context: Context):
    mod = m.group(1)
    if ".." not in mod:
        return m.group(0)
    try:
        mod_rel_path = (path.parent / mod).resolve().relative_to(context.root_path)
    except ValueError as ve:
        print(f"Error in {path}: {ve}")
        return m.group(0)
    at_path = f"@/{mod_rel_path}"
    if len(at_path) < len(mod) and context.is_acceptable(at_path):
        return f" from '{at_path}';"
    return m.group(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument(
        "-a",
        "--accepted-segment",
        dest="accepted_segments",
        action="append",
    )
    ap.add_argument("-w", "--write", action="store_true")
    args = ap.parse_args()
    context = Context(
        root_path=pathlib.Path(args.root).resolve(),
        accepted_segments=args.accepted_segments or [],
    )
    root_path = pathlib.Path(args.root).resolve()
    write = bool(args.write)

    for file in root_path.rglob("**/*.ts*"):
        # print(file)
        content = file.read_text()
        new_content = re.sub(
            from_comp_re,
            partial(handle_from, path=file, context=context),
            content,
        )
        if content != new_content:
            for line in difflib.unified_diff(
                content.splitlines(),
                new_content.splitlines(),
            ):
                print(line)
            if write:
                file.write_text(new_content)


if __name__ == "__main__":
    main()
