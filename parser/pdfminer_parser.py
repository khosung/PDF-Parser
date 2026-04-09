import argparse
import csv
import logging
import time
from pathlib import Path

import fitz
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from pdfminer.pdfpage import PDFPage


LOGGER = logging.getLogger("pdfminer-parser")


def progress_label(current: int, total: int) -> str:
    if total <= 0:
        return "0/0 (0.0%)"
    return f"{current}/{total} ({(current / total) * 100.0:.1f}%)"


def setup_logging(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.FileHandler(output_dir / "run.log", encoding="utf-8"), logging.StreamHandler()],
    )


def write_reports(output_dir: Path, rows: list[dict]) -> None:
    csv_path = output_dir / "benchmark_results.csv"
    md_path = output_dir / "benchmark_results.md"
    fields = [
        "pdf_file",
        "library",
        "page_count",
        "extract_time_sec",
        "text_chars",
        "text_coverage_pct",
        "text_consensus_pct",
        "table_count",
        "table_structure_pct",
        "image_count",
        "status",
        "error_message",
    ]

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# pdfminer.six Benchmark Results",
        "",
        "| " + " | ".join(fields[:-1]) + " |",
        "| " + " | ".join(["---"] * (len(fields) - 1)) + " |",
    ]
    for row in rows:
        values = []
        for key in fields[:-1]:
            value = row[key]
            if isinstance(value, float):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def run(pdf_files: list[Path], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    total_files = len(pdf_files)
    LOGGER.info("Start pdfminer run: %d files", total_files)

    for idx, pdf_path in enumerate(pdf_files, start=1):
        LOGGER.info("Processing %s | %s", progress_label(idx, total_files), pdf_path.name)
        start = time.perf_counter()
        try:
            image_dir = output_dir / f"{pdf_path.stem}_images"
            image_dir.mkdir(parents=True, exist_ok=True)

            # Extract text per page using pdfminer
            page_layouts = list(extract_pages(str(pdf_path)))
            page_count = len(page_layouts)

            # Extract images using fitz (pdfminer has no image API)
            fitz_doc = fitz.open(pdf_path)
            page_image_refs: list[list[str]] = [[] for _ in range(page_count)]
            image_count = 0
            for page_idx in range(page_count):
                fitz_page = fitz_doc[page_idx]
                for image_info in fitz_page.get_images(full=True):
                    xref = image_info[0]
                    img_dict = fitz_doc.extract_image(xref)
                    img_bytes = img_dict.get("image", b"")
                    ext = img_dict.get("ext", "png")
                    if not img_bytes:
                        continue
                    image_count += 1
                    img_filename = f"{image_count:03d}.{ext}"
                    (image_dir / img_filename).write_bytes(img_bytes)
                    rel = f"{pdf_path.stem}_images/{img_filename}"
                    page_image_refs[page_idx].append(f"![Image {image_count}]({rel})")
            fitz_doc.close()

            md_parts: list[str] = []
            for page_idx, page_layout in enumerate(page_layouts, start=1):
                page_text = "".join(
                    el.get_text() for el in page_layout if isinstance(el, LTTextContainer)
                ).strip()
                page_lines: list[str] = [f"## Page {page_idx}", ""]
                if page_text:
                    page_lines.append(page_text)
                    page_lines.append("")
                page_lines.extend(page_image_refs[page_idx - 1])
                md_parts.append("\n".join(page_lines))

            md_text = "\n\n".join(md_parts)
            (output_dir / f"{pdf_path.stem}.md").write_text(md_text, encoding="utf-8")
            elapsed = time.perf_counter() - start
            LOGGER.info("Done %s | %s | %.3fs", progress_label(idx, total_files), pdf_path.name, elapsed)
            rows.append(
                {
                    "pdf_file": pdf_path.name,
                    "library": "pdfminer",
                    "page_count": page_count,
                    "extract_time_sec": elapsed,
                    "text_chars": len(md_text),
                    "text_coverage_pct": 0.0,
                    "text_consensus_pct": 0.0,
                    "table_count": 0,
                    "table_structure_pct": 0.0,
                    "image_count": image_count,
                    "status": "ok",
                    "error_message": "",
                }
            )
        except Exception as err:
            LOGGER.exception("Failed on %s", pdf_path.name)
            rows.append(
                {
                    "pdf_file": pdf_path.name,
                    "library": "pdfminer",
                    "page_count": 0,
                    "extract_time_sec": 0.0,
                    "text_chars": 0,
                    "text_coverage_pct": 0.0,
                    "text_consensus_pct": 0.0,
                    "table_count": 0,
                    "table_structure_pct": 0.0,
                    "image_count": 0,
                    "status": "error",
                    "error_message": str(err)[:500],
                }
            )

    write_reports(output_dir, rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="pdfminer PDF to Markdown converter")
    parser.add_argument("input", type=Path, help="PDF file or directory of PDFs")
    parser.add_argument("--output-dir", type=Path, default=Path("res") / "pdfminer")
    args = parser.parse_args()

    input_path: Path = args.input
    if input_path.is_file():
        pdf_files = [input_path]
    elif input_path.is_dir():
        pdf_files = sorted(input_path.glob("*.pdf"))
    else:
        raise FileNotFoundError(f"Input not found: {input_path}")

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found: {input_path}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(args.output_dir)
    run(pdf_files, args.output_dir)


if __name__ == "__main__":
    main()
