"""
Takes a PDF file and a TSV specification file,
and separates the PDF file's pages into individual files,
each of which repeats the page as specified in the TSV file.
"""

import argparse
import asyncio
import csv
import dataclasses
import pathlib
import re
import shlex
import shutil
import tempfile

SEPARATED_PATTERN = "sep_%08d.pdf"


async def print_and_check_call(args):
    assert isinstance(args, list)
    cmd = shlex.join(args)
    print("=>", cmd)
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return proc.returncode


@dataclasses.dataclass
class PageSpec:
    page: int
    repeats: int
    title: str | None


def sanitize_title(param: str):
    return re.sub(r"\s+", " ", param.strip())


def read_page_specs(args):
    page_specs = []
    with open(args.spec_tsv_file) as f:
        for dt in csv.DictReader(f, delimiter="\t"):
            page_no = int(dt[args.page_no_column].lstrip("p"))
            repeats = int(dt[args.repeats_column])
            title = sanitize_title(dt.get(args.title_column, ""))
            page_specs.append(PageSpec(page=page_no, repeats=repeats, title=title))
    return page_specs


async def process_single_page_spec(
    *,
    page_spec: PageSpec,
    temp_path: pathlib.Path,
    output_path: pathlib.Path,
):
    if page_spec.title:
        filename = f"{page_spec.title}.pdf"
    else:
        filename = f"{page_spec.page:04d}.pdf"
    output_temp_path = temp_path / f"temp-{page_spec.page}.pdf"
    page_path = temp_path / (SEPARATED_PATTERN % page_spec.page)
    assert page_path.is_file(), f"Page file {page_path} not found"
    await print_and_check_call(
        [
            "pdfunite",
            *[str(page_path)] * page_spec.repeats,
            str(output_temp_path),
        ],
    )
    output_pdf_path = output_path / filename
    await print_and_check_call(
        [
            "gs",
            "-dBATCH",
            "-dDetectDuplicateImages=true",
            "-dNOPAUSE",
            # "-dPDFSETTINGS=/printer",
            "-q",
            "-sDEVICE=pdfwrite",
            "-o",
            str(output_pdf_path),
            str(output_temp_path),
        ],
    )
    output_temp_path.unlink()


async def do_process(
    *,
    input_pdf_file: pathlib.Path,
    page_specs: list[PageSpec],
    temp_path: pathlib.Path,
    output_path: pathlib.Path,
):
    await print_and_check_call(
        [
            "pdfseparate",
            str(input_pdf_file),
            str(temp_path / SEPARATED_PATTERN),
        ],
    )

    promises = [
        process_single_page_spec(
            page_spec=page_spec,
            temp_path=temp_path,
            output_path=output_path,
        )
        for page_spec in sorted(page_specs, key=lambda ps: ps.page)
    ]

    await asyncio.gather(*promises)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-file", required=True)
    ap.add_argument("--spec-tsv-file", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--page-no-column", default="page_no")
    ap.add_argument("--repeats-column", default="repeats")
    ap.add_argument("--title-column", default=None)
    args = ap.parse_args()

    page_specs = read_page_specs(args)

    temp_path = pathlib.Path(tempfile.mkdtemp())
    output_path = pathlib.Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        await do_process(
            input_pdf_file=pathlib.Path(args.pdf_file),
            page_specs=page_specs,
            temp_path=temp_path,
            output_path=output_path,
        )
    finally:
        shutil.rmtree(temp_path)


if __name__ == "__main__":
    asyncio.run(main())
