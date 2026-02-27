import argparse
import csv
import logging
import time
from pathlib import Path

import pdfplumber


LOGGER = logging.getLogger("pdfplumber-parser")


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


def resolve_output_dir(input_dir: Path, output_dir: Path) -> Path:
    dataset_name = input_dir.resolve().name
    if output_dir.resolve().name == dataset_name:
        return output_dir
    return output_dir / dataset_name


def table_to_markdown(table: list[list[str]]) -> str:
    if not table:
        return ""
    max_cols = max(len(row) for row in table)
    normalized = []
    for row in table:
        padded = row + [""] * (max_cols - len(row))
        normalized.append([("" if cell is None else str(cell)).replace("\n", " ").strip() for cell in padded])
    header = normalized[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * len(header)) + " |",
    ]
    for row in normalized[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


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
        "# pdfplumber Benchmark Results",
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


def run(input_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {input_dir}")

    rows: list[dict] = []
    total_files = len(pdf_files)
    LOGGER.info("Start pdfplumber run: %d files", total_files)
    for idx, pdf_path in enumerate(pdf_files, start=1):
        LOGGER.info("Processing %s | %s", progress_label(idx, total_files), pdf_path.name)
        start = time.perf_counter()
        try:
            text_parts = []
            table_count = 0
            valid_table_count = 0
            image_count = 0
            per_pdf_root = output_dir / pdf_path.stem
            per_pdf_text_dir = per_pdf_root / "texts"
            per_pdf_table_dir = per_pdf_root / "tables"
            per_pdf_image_dir = per_pdf_root / "images"
            per_pdf_text_dir.mkdir(parents=True, exist_ok=True)
            per_pdf_table_dir.mkdir(parents=True, exist_ok=True)
            per_pdf_image_dir.mkdir(parents=True, exist_ok=True)

            with pdfplumber.open(pdf_path) as pdf:
                for page_idx, page in enumerate(pdf.pages, start=1):
                    text_parts.append(page.extract_text() or "")
                    image_count += len(page.images or [])

                    tables = page.extract_tables() or []
                    for table_idx, table in enumerate(tables, start=1):
                        table_count += 1
                        markdown = table_to_markdown(table)
                        if table and len(table) >= 2 and max((len(r) for r in table if r), default=0) >= 2:
                            valid_table_count += 1
                        out_table = per_pdf_table_dir / f"{pdf_path.stem}_p{page_idx}_t{table_idx}.md"
                        out_table.write_text(markdown, encoding="utf-8")

                page_count = len(pdf.pages)

            text = "\n".join(text_parts)
            (per_pdf_text_dir / f"{pdf_path.stem}.txt").write_text(text, encoding="utf-8")
            structure_pct = (valid_table_count / table_count * 100.0) if table_count else 0.0
            elapsed = time.perf_counter() - start
            LOGGER.info("Done %s | %s | %.3fs", progress_label(idx, total_files), pdf_path.name, elapsed)

            rows.append(
                {
                    "pdf_file": pdf_path.name,
                    "library": "pdfplumber",
                    "page_count": page_count,
                    "extract_time_sec": elapsed,
                    "text_chars": len(text),
                    "text_coverage_pct": 0.0,
                    "text_consensus_pct": 0.0,
                    "table_count": table_count,
                    "table_structure_pct": structure_pct,
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
                    "library": "pdfplumber",
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
    parser = argparse.ArgumentParser(description="pdfplumber extraction benchmark")
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs") / "pdfplumber")
    args = parser.parse_args()

    args.output_dir = resolve_output_dir(args.input_dir, args.output_dir)

    setup_logging(args.output_dir)
    run(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
