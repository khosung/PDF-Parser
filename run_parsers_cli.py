import argparse
import logging
import subprocess
import sys
from pathlib import Path


LOGGER = logging.getLogger("run-parsers-cli")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler()],
    )


def discover_parser_scripts(parser_dir: Path) -> list[Path]:
    scripts = []
    for script in sorted(parser_dir.rglob("*.py")):
        if script.name.startswith("_"):
            continue
        if script.name == "__init__.py":
            continue
        scripts.append(script)
    return scripts


def run_script(python_exec: str, script: Path, input_dir: Path, output_root: Path) -> int:
    parser_name = script.stem.replace("_parser", "")
    dataset_name = input_dir.resolve().name
    output_dir = output_root / parser_name / dataset_name
    cmd = [
        python_exec,
        str(script),
        "--input-dir",
        str(input_dir),
        "--output-dir",
        str(output_dir),
    ]
    LOGGER.info("Running parser: %s (dataset=%s)", parser_name, dataset_name)
    LOGGER.info("Command: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        LOGGER.info("[%s][stdout]\n%s", parser_name, result.stdout)
    if result.stderr:
        LOGGER.warning("[%s][stderr]\n%s", parser_name, result.stderr)
    if result.returncode != 0:
        LOGGER.error("Parser failed: %s (code=%s)", parser_name, result.returncode)
    else:
        LOGGER.info("Parser finished: %s", parser_name)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all parser scripts under a directory.")
    parser.add_argument("--parsers-dir", type=Path, default=Path("parser"), help="Directory containing parser python scripts")
    parser.add_argument("--input-dir", type=Path, default=Path("dataset"), help="Directory containing input PDFs")
    parser.add_argument("--output-root", type=Path, default=Path("outputs"), help="Root output directory")
    parser.add_argument("--python", type=str, default=sys.executable, help="Python executable path")
    parser.add_argument("--fail-fast", action="store_true", help="Stop immediately if one parser fails")
    args = parser.parse_args()

    setup_logging()

    if not args.parsers_dir.exists():
        raise FileNotFoundError(f"parser directory not found: {args.parsers_dir}")
    if not args.input_dir.exists():
        raise FileNotFoundError(f"input-dir not found: {args.input_dir}")

    scripts = discover_parser_scripts(args.parsers_dir)
    if not scripts:
        raise FileNotFoundError(f"No python parser scripts found under: {args.parsers_dir}")

    args.output_root.mkdir(parents=True, exist_ok=True)

    failed = []
    for script in scripts:
        code = run_script(args.python, script, args.input_dir, args.output_root)
        if code != 0:
            failed.append(script.name)
            if args.fail_fast:
                break

    if failed:
        raise SystemExit(f"Failed parsers: {', '.join(failed)}")

    LOGGER.info("All parsers executed successfully.")


if __name__ == "__main__":
    main()
