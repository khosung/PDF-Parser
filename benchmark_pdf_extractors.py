import argparse
import csv
import importlib.util
import logging
import re
import time
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Tuple


LOGGER = logging.getLogger("pdf-benchmark")


@dataclass
class BenchmarkRow:
    pdf_file: str
    library: str
    page_count: int
    extract_time_sec: float
    text_chars: int
    text_coverage_pct: float
    text_consensus_pct: float
    table_count: int
    table_structure_pct: float
    image_count: int
    status: str
    error_message: str


def setup_logging(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "benchmark.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler()],
    )


def is_installed(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def similarity(a: str, b: str) -> float:
    na, nb = normalize_text(a), normalize_text(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def table_to_markdown(table: List[List[str]]) -> str:
    if not table:
        return ""

    safe_rows = []
    max_cols = max(len(row) for row in table)
    for row in table:
        padded = list(row) + [""] * (max_cols - len(row))
        safe_rows.append([("" if cell is None else str(cell)).replace("\n", " ").strip() for cell in padded])

    header = safe_rows[0]
    sep = ["---"] * len(header)
    body = safe_rows[1:] if len(safe_rows) > 1 else []

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def extract_with_pymupdf(pdf_path: Path, output_dir: Path) -> Tuple[str, int, int, int, float]:
    import fitz

    t0 = time.perf_counter()
    text_parts: List[str] = []
    image_count = 0
    doc = fitz.open(pdf_path)
    image_dir = output_dir / "images" / "pymupdf" / pdf_path.stem
    image_dir.mkdir(parents=True, exist_ok=True)

    for page_index, page in enumerate(doc, start=1):
        text_parts.append(page.get_text("text") or "")
        for image_idx, image_info in enumerate(page.get_images(full=True), start=1):
            xref = image_info[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image.get("image")
            img_ext = base_image.get("ext", "png")
            if not img_bytes:
                continue
            image_count += 1
            img_file = image_dir / f"{pdf_path.stem}_p{page_index}_i{image_idx}.{img_ext}"
            img_file.write_bytes(img_bytes)

    page_count = doc.page_count
    doc.close()
    elapsed = time.perf_counter() - t0
    return "\n".join(text_parts), page_count, 0, image_count, elapsed


def extract_with_pdfplumber(pdf_path: Path, output_dir: Path) -> Tuple[str, int, int, int, float, float]:
    import pdfplumber

    t0 = time.perf_counter()
    text_parts: List[str] = []
    table_count = 0
    valid_table_count = 0
    image_count = 0
    table_dir = output_dir / "tables" / pdf_path.stem
    table_dir.mkdir(parents=True, exist_ok=True)

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            text_parts.append(page.extract_text() or "")
            image_count += len(page.images or [])

            tables = page.extract_tables() or []
            for table_idx, table in enumerate(tables, start=1):
                table_count += 1
                md = table_to_markdown(table)
                if md and len(table or []) >= 2 and max((len(r) for r in table if r), default=0) >= 2:
                    valid_table_count += 1
                table_file = table_dir / f"{pdf_path.stem}_p{page_idx}_t{table_idx}.md"
                table_file.write_text(md, encoding="utf-8")

        page_count = len(pdf.pages)

    elapsed = time.perf_counter() - t0
    structure_pct = (valid_table_count / table_count * 100.0) if table_count else 0.0
    return "\n".join(text_parts), page_count, table_count, image_count, elapsed, structure_pct


def extract_with_pdfminer(pdf_path: Path) -> Tuple[str, int, int, int, float]:
    from pdfminer.high_level import extract_text
    from pdfminer.pdfpage import PDFPage

    t0 = time.perf_counter()
    text = extract_text(str(pdf_path)) or ""
    with pdf_path.open("rb") as f:
        page_count = sum(1 for _ in PDFPage.get_pages(f))
    elapsed = time.perf_counter() - t0
    return text, page_count, 0, 0, elapsed


def extract_with_pypdf(pdf_path: Path, output_dir: Path) -> Tuple[str, int, int, int, float]:
    from pypdf import PdfReader

    t0 = time.perf_counter()
    text_parts: List[str] = []
    image_count = 0

    reader = PdfReader(str(pdf_path))
    image_dir = output_dir / "images" / "pypdf" / pdf_path.stem
    image_dir.mkdir(parents=True, exist_ok=True)

    for page_idx, page in enumerate(reader.pages, start=1):
        text_parts.append(page.extract_text() or "")

        page_images = getattr(page, "images", None)
        if page_images:
            for image_idx, image_file in enumerate(page_images, start=1):
                try:
                    image_count += 1
                    name = getattr(image_file, "name", f"img_{image_idx}.bin")
                    img_bytes = getattr(image_file, "data", b"")
                    if not img_bytes:
                        continue
                    out_file = image_dir / f"{pdf_path.stem}_p{page_idx}_i{image_idx}_{name}"
                    out_file.write_bytes(img_bytes)
                except Exception as image_err:
                    LOGGER.warning("pypdf image save failed: %s", image_err)

    elapsed = time.perf_counter() - t0
    return "\n".join(text_parts), len(reader.pages), 0, image_count, elapsed


def ensure_text_export(output_dir: Path, library: str, pdf_name: str, text: str) -> None:
    text_dir = output_dir / "texts" / library
    text_dir.mkdir(parents=True, exist_ok=True)
    out_file = text_dir / f"{pdf_name}.txt"
    out_file.write_text(text or "", encoding="utf-8")


def compute_proxy_scores(rows: List[BenchmarkRow], text_map: Dict[Tuple[str, str], str]) -> None:
    by_pdf: Dict[str, List[BenchmarkRow]] = {}
    for row in rows:
        by_pdf.setdefault(row.pdf_file, []).append(row)

    for pdf_file, pdf_rows in by_pdf.items():
        max_chars = max((r.text_chars for r in pdf_rows), default=0)
        for row in pdf_rows:
            row.text_coverage_pct = (row.text_chars / max_chars * 100.0) if max_chars > 0 else 0.0
            peers = [r for r in pdf_rows if r.library != row.library and r.status == "ok"]
            if not peers or row.status != "ok":
                row.text_consensus_pct = 0.0
                continue
            base_text = text_map.get((pdf_file, row.library), "")
            scores = []
            for peer in peers:
                peer_text = text_map.get((pdf_file, peer.library), "")
                scores.append(similarity(base_text, peer_text))
            row.text_consensus_pct = (sum(scores) / len(scores) * 100.0) if scores else 0.0


def write_csv(output_dir: Path, rows: List[BenchmarkRow]) -> Path:
    csv_path = output_dir / "benchmark_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = list(asdict(rows[0]).keys()) if rows else list(BenchmarkRow.__annotations__.keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    return csv_path


def write_markdown(output_dir: Path, rows: List[BenchmarkRow]) -> Path:
    md_path = output_dir / "benchmark_results.md"
    headers = [
        "pdf_file",
        "library",
        "extract_time_sec",
        "text_chars",
        "text_coverage_pct",
        "text_consensus_pct",
        "table_count",
        "table_structure_pct",
        "image_count",
        "status",
    ]

    lines = [
        "# PDF Extractor Benchmark Results",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    def fmt(v):
        if isinstance(v, float):
            return f"{v:.3f}"
        return str(v)

    for row in rows:
        data = asdict(row)
        lines.append("| " + " | ".join(fmt(data[h]) for h in headers) + " |")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def run_benchmark(input_dir: Path, output_dir: Path) -> List[BenchmarkRow]:
    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {input_dir}")

    extractors = {
        "pymupdf": {"module": "fitz"},
        "pdfplumber": {"module": "pdfplumber"},
        "pdfminer": {"module": "pdfminer"},
        "pypdf": {"module": "pypdf"},
    }

    rows: List[BenchmarkRow] = []
    text_map: Dict[Tuple[str, str], str] = {}

    for pdf_path in pdf_files:
        LOGGER.info("Processing PDF: %s", pdf_path.name)

        for library, meta in extractors.items():
            if not is_installed(meta["module"]):
                LOGGER.warning("Library not installed, skipping: %s", library)
                rows.append(
                    BenchmarkRow(
                        pdf_file=pdf_path.name,
                        library=library,
                        page_count=0,
                        extract_time_sec=0.0,
                        text_chars=0,
                        text_coverage_pct=0.0,
                        text_consensus_pct=0.0,
                        table_count=0,
                        table_structure_pct=0.0,
                        image_count=0,
                        status="skipped",
                        error_message="module_not_installed",
                    )
                )
                continue

            try:
                if library == "pymupdf":
                    text, page_count, table_count, image_count, elapsed = extract_with_pymupdf(pdf_path, output_dir)
                    structure_pct = 0.0
                elif library == "pdfplumber":
                    text, page_count, table_count, image_count, elapsed, structure_pct = extract_with_pdfplumber(pdf_path, output_dir)
                elif library == "pdfminer":
                    text, page_count, table_count, image_count, elapsed = extract_with_pdfminer(pdf_path)
                    structure_pct = 0.0
                elif library == "pypdf":
                    text, page_count, table_count, image_count, elapsed = extract_with_pypdf(pdf_path, output_dir)
                    structure_pct = 0.0
                else:
                    raise ValueError(f"Unknown library: {library}")

                ensure_text_export(output_dir, library, pdf_path.stem, text)
                text_map[(pdf_path.name, library)] = text

                rows.append(
                    BenchmarkRow(
                        pdf_file=pdf_path.name,
                        library=library,
                        page_count=page_count,
                        extract_time_sec=elapsed,
                        text_chars=len(text),
                        text_coverage_pct=0.0,
                        text_consensus_pct=0.0,
                        table_count=table_count,
                        table_structure_pct=structure_pct,
                        image_count=image_count,
                        status="ok",
                        error_message="",
                    )
                )
                LOGGER.info("Done: %s | %s | %.3fs", pdf_path.name, library, elapsed)

            except Exception as err:
                LOGGER.exception("Failed: %s | %s", pdf_path.name, library)
                rows.append(
                    BenchmarkRow(
                        pdf_file=pdf_path.name,
                        library=library,
                        page_count=0,
                        extract_time_sec=0.0,
                        text_chars=0,
                        text_coverage_pct=0.0,
                        text_consensus_pct=0.0,
                        table_count=0,
                        table_structure_pct=0.0,
                        image_count=0,
                        status="error",
                        error_message=str(err).replace("\n", " ")[:500],
                    )
                )

    compute_proxy_scores(rows, text_map)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark PDF extraction libraries.")
    parser.add_argument("--input-dir", type=Path, default=Path("dataset"), help="Directory containing PDF files.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Directory to store results.")
    args = parser.parse_args()

    setup_logging(args.output_dir)

    LOGGER.info("Starting benchmark...")
    LOGGER.info("Input directory: %s", args.input_dir.resolve())
    LOGGER.info("Output directory: %s", args.output_dir.resolve())

    rows = run_benchmark(args.input_dir, args.output_dir)
    csv_path = write_csv(args.output_dir, rows)
    md_path = write_markdown(args.output_dir, rows)

    LOGGER.info("Benchmark completed.")
    LOGGER.info("CSV report: %s", csv_path.resolve())
    LOGGER.info("Markdown report: %s", md_path.resolve())


if __name__ == "__main__":
    main()