"""
Safe Archive Utility for Experiment Results.

Automatically packages test generation and evaluation outputs into clean,
antivirus-safe .zip or .tar.gz archives.

Filters out:
- mutmut temporary mutation workspace and .mutmut-cache database (which frequently
  trigger heuristic antivirus / Chrome Safe Browsing false-positives)
- Python bytecode (__pycache__, *.pyc)
- Execution cache directories (.pytest_cache, .coverage)

Retains:
- All generated unit tests (test_*.py)
- All evaluation reports and metrics (*.json, *.csv, *.md, *.txt)
- Statistical summaries (statistical_summary.*, cross_context_summary.*)
"""

import os
import sys
import shutil
import zipfile
import tarfile
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Set, Tuple

logger = logging.getLogger(__name__)

# Directory names to exclude (sources of false positives and bloat)
EXCLUDE_DIR_NAMES: Set[str] = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    "mutants",         # mutmut scratch space containing mutated code that triggers AV heuristics
    ".mutmut-cache",   # sqlite database
    ".coverage",
    "htmlcov",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    ".ipynb_checkpoints",
}

# File extensions to exclude
EXCLUDE_EXTENSIONS: Set[str] = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".lock",
    ".tmp",
}

# Safe extensions that are guaranteed valid results
SAFE_EXTENSIONS: Set[str] = {
    ".json",
    ".csv",
    ".md",
    ".txt",
    ".py",
    ".svg",
    ".png",
    ".log",
}


def is_path_safe(file_path: Path, base_dir: Path) -> bool:
    """Check if a file should be included in the safe archive."""
    try:
        rel_parts = file_path.relative_to(base_dir).parts
    except ValueError:
        rel_parts = file_path.parts

    # Check for excluded directories in the path
    for part in rel_parts:
        if part in EXCLUDE_DIR_NAMES:
            return False
        if part.startswith(".mutmut") or part == "mutants":
            return False

    # Check file extension
    ext = file_path.suffix.lower()
    if ext in EXCLUDE_EXTENSIONS:
        return False

    # Exclude hidden files
    if file_path.name.startswith(".") and file_path.name not in {".env.example"}:
        return False

    # Must have a known safe extension or be a recognized result file
    if ext in SAFE_EXTENSIONS or file_path.name in {"summary.txt", "mutmut_results.txt"}:
        return True

    return False


def collect_safe_files(source_dir: Path) -> List[Tuple[Path, str]]:
    """
    Collect all safe result files under source_dir.
    Returns list of (absolute_path, relative_archive_path).
    """
    source_dir = Path(source_dir).resolve()
    if not source_dir.exists():
        logger.warning(f"Source directory does not exist: {source_dir}")
        return []

    collected: List[Tuple[Path, str]] = []
    base_parent = source_dir.parent

    for root, dirs, files in os.walk(source_dir):
        # Prune excluded directories in-place so os.walk does not descend into them
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_NAMES and not d.startswith(".mutmut")]

        for f in files:
            full_path = Path(root) / f
            if is_path_safe(full_path, source_dir):
                # Archive relative to source_dir's parent so top folder name is preserved
                rel_path = full_path.relative_to(base_parent).as_posix()
                collected.append((full_path, rel_path))

    return collected


def create_safe_results_archive(
    source_dir: Path,
    output_path: Optional[Path] = None,
    output_prefix: str = "results",
    archive_format: str = "zip",
    password: Optional[str] = None,
    verbose: bool = True,
) -> Optional[Path]:
    """
    Create a clean, virus-scan-safe archive of experiment results.

    Args:
        source_dir: Path to results directory (e.g. 'cli_results_v1')
        output_path: Explicit output file path (optional)
        output_prefix: Prefix for auto-generated archive name
        archive_format: 'zip', 'tar.gz', or 'both'
        password: Optional password to encrypt zip archive (uses system 'zip' CLI)
        verbose: Whether to log and print user-friendly summary

    Returns:
        Path to the generated archive (or primary archive if both).
    """
    source_dir = Path(source_dir).resolve()
    if not source_dir.exists():
        logger.warning(f"Cannot archive non-existent directory: {source_dir}")
        return None

    files_to_pack = collect_safe_files(source_dir)
    if not files_to_pack:
        logger.warning(f"No result files found in {source_dir} matching safe criteria.")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_prefix = output_prefix.replace("/", "_").replace(":", "_").replace(" ", "_")

    # Determine destination directory (current working directory by default)
    dest_dir = Path.cwd()

    created_archives: List[Path] = []

    # 1. Password-protected zip via system CLI if requested
    if password and archive_format in ("zip", "both") and shutil.which("zip"):
        zip_file = output_path or (dest_dir / f"{clean_prefix}_{timestamp}_protected.zip")
        try:
            cmd = ["zip", "-q", "-r", "-P", password, str(zip_file)]
            # Add relative paths from base_parent
            base_parent = source_dir.parent
            for full_p, rel_p in files_to_pack:
                cmd.append(rel_p)
            subprocess.run(cmd, cwd=str(base_parent), check=True, capture_output=True)
            created_archives.append(Path(zip_file))
        except Exception as e:
            logger.warning(f"System zip command failed with password ({e}). Falling back to standard zip.")

    # 2. Standard .zip archive
    if archive_format in ("zip", "both") and not created_archives:
        zip_file = output_path or (dest_dir / f"{clean_prefix}_{timestamp}.zip")
        zip_file = Path(zip_file)
        with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for full_p, rel_p in files_to_pack:
                zf.write(full_p, arcname=rel_p)
        created_archives.append(zip_file)

    # 3. .tar.gz archive (excellent bypass for Windows Defender / Chrome heuristics)
    if archive_format in ("tar.gz", "both"):
        tar_file = dest_dir / f"{clean_prefix}_{timestamp}.tar.gz"
        with tarfile.open(tar_file, "w:gz") as tf:
            for full_p, rel_p in files_to_pack:
                tf.add(full_p, arcname=rel_p)
        created_archives.append(tar_file)

    if not created_archives:
        return None

    primary_archive = created_archives[0]

    if verbose:
        size_kb = primary_archive.stat().st_size / 1024
        print("\n" + "=" * 70)
        print("📦 [SAFE ARCHIVE CREATED] Experiment results safely packaged:")
        for arc in created_archives:
            arc_size = arc.stat().st_size / 1024
            print(f"  • File: {arc.name} ({arc_size:.1f} KB)")
            print(f"    Path: {arc.resolve()}")
        print(f"  • Included: {len(files_to_pack)} clean files (reports, metrics, test code)")
        print(f"  • Filtered: Excluded mutants/, .mutmut-cache, __pycache__ (No AV flags)")
        if password:
            print(f"  • Password Protected: Yes (Password: {password})")

        # In-notebook Kaggle download link
        try:
            from IPython.display import FileLink, display
            print("\n📥 [Kaggle Direct Download] Click below to download in your browser:")
            display(FileLink(primary_archive.name))
        except Exception:
            pass
        print("=" * 70 + "\n")

    return primary_archive


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Safe Results Archive Packager for LLM Testing Experiments",
        epilog="""
Examples:
  # Package results directory into a clean, safe zip
  python archive_utils.py --dir cli_results_v1

  # Package into both .zip and .tar.gz
  python archive_utils.py --dir cli_results_v1 --format both

  # Password-protect zip to bypass strict corporate/browser download scanners
  python archive_utils.py --dir cli_results_v1 --password mypass
        """
    )
    parser.add_argument("--dir", default="cli_results_v1", help="Results directory to package (default: cli_results_v1)")
    parser.add_argument("--output", default=None, help="Explicit output archive filename")
    parser.add_argument("--prefix", default="results", help="Prefix for auto-generated archive name")
    parser.add_argument("--format", choices=["zip", "tar.gz", "both"], default="zip", help="Archive format")
    parser.add_argument("--password", default=None, help="Optional password encryption for zip archive")

    cli_args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    res = create_safe_results_archive(
        source_dir=Path(cli_args.dir),
        output_path=Path(cli_args.output) if cli_args.output else None,
        output_prefix=cli_args.prefix,
        archive_format=cli_args.format,
        password=cli_args.password,
        verbose=True,
    )
    if not res:
        sys.exit(1)
