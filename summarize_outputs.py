import argparse
import csv
import logging
import re
from pathlib import Path


LOGGER = logging.getLogger("summarize-outputs")


def progress_label(current: int, total: int) -> str:
    if total <= 0:
        return "0/0 (0.0%)"
    return f"{current}/{total} ({(current / total) * 100.0:.1f}%)"


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler()],
    )


def normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def similarity(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    max_chars = 50000
    max_tokens = 5000
    token_pattern = r"[\w가-힣]+"

    ta = re.findall(token_pattern, normalize_text(a)[:max_chars])[:max_tokens]
    tb = re.findall(token_pattern, normalize_text(b)[:max_chars])[:max_tokens]

    set_a = set(ta)
    set_b = set(tb)
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0

    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def discover_parser_outputs(outputs_root: Path) -> list[Path]:
    result_dirs = []
    for csv_path in sorted(outputs_root.rglob("benchmark_results.csv")):
        candidate = csv_path.parent
        if candidate.name == "summary":
            continue
        result_dirs.append(candidate)
    return result_dirs


def read_rows(result_dir: Path, outputs_root: Path) -> list[dict]:
    rows = []
    csv_path = result_dir / "benchmark_results.csv"

    rel_parts = result_dir.relative_to(outputs_root).parts
    if len(rel_parts) >= 2:
        parser_name = rel_parts[0]
        dataset_name = rel_parts[1]
    elif len(rel_parts) == 1:
        parser_name = rel_parts[0]
        dataset_name = "default"
    else:
        parser_name = "unknown"
        dataset_name = "default"

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["parser_name"] = parser_name
            row["dataset_name"] = dataset_name
            rows.append(row)
    return rows


def read_text(outputs_root: Path, parser_name: str, dataset_name: str, pdf_file: str) -> str:
    stem = Path(pdf_file).stem
    primary = outputs_root / parser_name / dataset_name / stem / "texts" / f"{stem}.txt"
    fallback_1 = outputs_root / parser_name / dataset_name / "texts" / f"{stem}.txt"
    fallback_2 = outputs_root / parser_name / stem / "texts" / f"{stem}.txt"
    fallback_3 = outputs_root / parser_name / "texts" / f"{stem}.txt"

    if primary.exists():
        return primary.read_text(encoding="utf-8", errors="ignore")
    if fallback_1.exists():
        return fallback_1.read_text(encoding="utf-8", errors="ignore")
    if fallback_2.exists():
        return fallback_2.read_text(encoding="utf-8", errors="ignore")
    if fallback_3.exists():
        return fallback_3.read_text(encoding="utf-8", errors="ignore")
    return ""


def to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def to_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def recompute_scores(rows: list[dict], outputs_root: Path) -> None:
    by_pdf: dict[str, list[dict]] = {}
    for row in rows:
        by_pdf.setdefault(row.get("pdf_file", ""), []).append(row)

    total_pdfs = len(by_pdf)
    for pdf_idx, (pdf_file, pdf_rows) in enumerate(by_pdf.items(), start=1):
        LOGGER.info("Scoring %s | %s", progress_label(pdf_idx, total_pdfs), pdf_file)
        max_chars = max((to_int(r.get("text_chars", "0")) for r in pdf_rows), default=0)
        texts_by_parser: dict[str, str] = {}
        for row in pdf_rows:
            parser_name = row.get("parser_name", row.get("library", ""))
            dataset_name = row.get("dataset_name", "default")
            key = f"{parser_name}::{dataset_name}"
            texts_by_parser[key] = read_text(outputs_root, parser_name, dataset_name, pdf_file)

        total_rows = len(pdf_rows)
        for row_idx, row in enumerate(pdf_rows, start=1):
            status = row.get("status", "")
            parser_name = row.get("parser_name", row.get("library", ""))
            dataset_name = row.get("dataset_name", "default")
            current_key = f"{parser_name}::{dataset_name}"
            text_chars = to_int(row.get("text_chars", "0"))

            coverage = (text_chars / max_chars * 100.0) if max_chars > 0 else 0.0
            row["text_coverage_pct"] = f"{coverage:.6f}"

            if status != "ok":
                row["text_consensus_pct"] = "0.000000"
                continue

            current_text = texts_by_parser.get(current_key, "")
            peer_scores = []
            for peer_key, peer_text in texts_by_parser.items():
                if peer_key == current_key:
                    continue
                if not peer_text and not current_text:
                    continue
                peer_scores.append(similarity(current_text, peer_text))

            consensus = (sum(peer_scores) / len(peer_scores) * 100.0) if peer_scores else 0.0
            row["text_consensus_pct"] = f"{consensus:.6f}"

            LOGGER.info(
                "Scoring detail %s | %s | %s",
                progress_label(row_idx, total_rows),
                pdf_file,
                current_key,
            )


def write_combined_reports(rows: list[dict], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "combined_benchmark_results.csv"
    md_path = output_dir / "combined_benchmark_results.md"

    fields = [
        "pdf_file",
        "library",
        "parser_name",
        "dataset_name",
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
        for row in rows:
            record = {key: row.get(key, "") for key in fields}
            writer.writerow(record)

    lines = [
        "# Combined PDF Extraction Benchmark",
        "",
        "| " + " | ".join(fields[:-1]) + " |",
        "| " + " | ".join(["---"] * (len(fields) - 1)) + " |",
    ]
    for row in rows:
        vals = []
        for key in fields[:-1]:
            val = row.get(key, "")
            if key in {"extract_time_sec", "text_coverage_pct", "text_consensus_pct", "table_structure_pct"}:
                vals.append(f"{to_float(str(val)):.3f}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize benchmark outputs by walking outputs/parser_name directories")
    parser.add_argument("--input-dir", type=Path, default=Path("outputs"), help="Root outputs directory")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs") / "summary", help="Directory to write combined reports")
    args = parser.parse_args()

    setup_logging()
    if not args.input_dir.exists():
        raise FileNotFoundError(f"Input outputs directory not found: {args.input_dir}")

    parser_dirs = discover_parser_outputs(args.input_dir)
    if not parser_dirs:
        raise FileNotFoundError(f"No parser result directories found under: {args.input_dir}")

    all_rows = []
    total_parsers = len(parser_dirs)
    for parser_idx, parser_dir in enumerate(parser_dirs, start=1):
        LOGGER.info("Reading %s | %s", progress_label(parser_idx, total_parsers), parser_dir)
        all_rows.extend(read_rows(parser_dir, args.input_dir))

    recompute_scores(all_rows, args.input_dir)
    csv_path, md_path = write_combined_reports(all_rows, args.output_dir)
    LOGGER.info("Combined CSV: %s", csv_path)
    LOGGER.info("Combined MD: %s", md_path)


if __name__ == "__main__":
    main()
