import argparse
import importlib.util
import logging
import sys
from pathlib import Path


LOGGER = logging.getLogger("run-parsers-cli")

PARSERS = ["pdfminer", "pdfplumber", "pymupdf", "pypdf"]


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler()],
    )


def load_parser(parser_dir: Path, name: str):
    script = parser_dir / f"{name}_parser.py"
    if not script.exists():
        raise FileNotFoundError(f"Parser script not found: {script}")
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all PDF parsers and save Markdown output to ./res/")
    parser.add_argument("input", type=Path, help="PDF file or directory of PDFs")
    parser.add_argument("--parsers-dir", type=Path, default=Path("parser"), help="Directory containing parser scripts")
    parser.add_argument("--output-root", type=Path, default=Path("res"), help="Root output directory (default: ./res)")
    args = parser.parse_args()

    setup_logging()

    input_path: Path = args.input.resolve()
    if input_path.is_file():
        pdf_files = [input_path]
    elif input_path.is_dir():
        pdf_files = sorted(input_path.glob("*.pdf"))
    else:
        raise FileNotFoundError(f"Input not found: {input_path}")

    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found: {input_path}")

    LOGGER.info("Found %d PDF file(s): %s", len(pdf_files), [p.name for p in pdf_files])

    failed = []
    for name in PARSERS:
        output_dir = args.output_root / name
        output_dir.mkdir(parents=True, exist_ok=True)
        LOGGER.info("=" * 60)
        LOGGER.info("Running parser: %s  →  %s", name, output_dir)
        try:
            module = load_parser(args.parsers_dir, name)
            module.run(pdf_files, output_dir)
            LOGGER.info("Parser finished: %s", name)
        except Exception as e:
            LOGGER.error("Parser failed: %s — %s", name, e)
            failed.append(name)

    LOGGER.info("=" * 60)
    if failed:
        LOGGER.error("Failed parsers: %s", ", ".join(failed))
        sys.exit(1)
    else:
        LOGGER.info("All parsers completed successfully.")
        LOGGER.info("Output saved to: %s", args.output_root.resolve())


if __name__ == "__main__":
    main()

