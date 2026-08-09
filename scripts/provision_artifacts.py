import argparse
import os
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path


def download_archive(url: str, destination: Path) -> None:
    print(f"Downloading artifact archive from {url}...")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response:
        if response.status != 200:
            raise RuntimeError(f"Failed to download artifact archive: HTTP {response.status}")
        with destination.open("wb") as handle:
            handle.write(response.read())


def unpack_archive(archive_path: Path, dest_dir: Path) -> None:
    print(f"Extracting artifact archive {archive_path} to {dest_dir}...")
    if not archive_path.exists():
        raise FileNotFoundError(f"Artifact archive not found: {archive_path}")
    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path, mode="r:gz") as tar:
            tar.extractall(path=dest_dir)
    else:
        raise RuntimeError(f"Unsupported artifact archive format: {archive_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Provision recommended artifacts for CI and local testing.")
    parser.add_argument(
        "--archive",
        type=Path,
        default=None,
        help="Local archive path to use if ARTIFACT_ARCHIVE_URL is not set.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    archive_url = os.environ.get("ARTIFACT_ARCHIVE_URL")
    artifact_archive = args.archive or project_root / "artifacts.tar.gz"

    if archive_url:
        archive_path = project_root / "artifacts.tar.gz"
        download_archive(archive_url, archive_path)
    elif artifact_archive.exists():
        archive_path = artifact_archive
    else:
        print("ERROR: No artifact archive found.")
        print("Set the ARTIFACT_ARCHIVE_URL secret or place artifacts.tar.gz in the repository root.")
        return 1

    unpack_archive(archive_path, project_root)
    print("Artifacts provisioned successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
