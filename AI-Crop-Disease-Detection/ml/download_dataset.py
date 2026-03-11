"""
download_dataset.py
===================
Automatically downloads the PlantVillage dataset from Kaggle.

Usage:
    python ml/download_dataset.py

Prerequisites:
    1. Install kaggle: pip install kaggle
    2. Place your kaggle.json API key in ~/.kaggle/kaggle.json
       OR set KAGGLE_USERNAME and KAGGLE_KEY environment variables.

Dataset: https://www.kaggle.com/datasets/emmarex/plantdisease
"""

import os
import sys
import zipfile
import shutil
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# ── Load environment variables ────────────────────────────────────────────────
load_dotenv()

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset" / "raw"
KAGGLE_DS   = "emmarex/plantdisease"          # Kaggle dataset slug


def configure_kaggle_credentials() -> None:
    """
    Configure Kaggle credentials from env vars if kaggle.json is missing.
    """
    kaggle_dir  = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"

    if not kaggle_json.exists():
        username = os.getenv("KAGGLE_USERNAME")
        key      = os.getenv("KAGGLE_KEY")
        if not username or not key:
            raise EnvironmentError(
                "Kaggle credentials not found.\n"
                "Set KAGGLE_USERNAME and KAGGLE_KEY in your .env file,\n"
                "or place kaggle.json at ~/.kaggle/kaggle.json"
            )
        kaggle_dir.mkdir(parents=True, exist_ok=True)
        with open(kaggle_json, "w") as f:
            json.dump({"username": username, "key": key}, f)
        kaggle_json.chmod(0o600)
        log.info("Kaggle credentials written from environment variables.")
    else:
        log.info("Using existing kaggle.json credentials.")


def download_dataset() -> Path:
    """
    Download PlantVillage dataset from Kaggle and return the zip path.
    """
    import kaggle  # imported after credentials are configured

    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    log.info(f"Downloading dataset '{KAGGLE_DS}' to {DATASET_DIR} ...")

    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(
        KAGGLE_DS,
        path=str(DATASET_DIR),
        unzip=False,
    )
    zip_files = list(DATASET_DIR.glob("*.zip"))
    if not zip_files:
        raise FileNotFoundError("Download failed — no zip found in dataset/raw/")

    log.info(f"Downloaded: {zip_files[0].name}")
    return zip_files[0]


def extract_dataset(zip_path: Path) -> Path:
    """
    Extract downloaded zip to dataset/raw/ and return the extracted folder.
    """
    log.info(f"Extracting {zip_path.name} ...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(DATASET_DIR)

    zip_path.unlink()  # Remove zip after extraction
    log.info("Extraction complete. Zip file removed.")

    # Find the PlantVillage folder
    for folder in DATASET_DIR.iterdir():
        if folder.is_dir():
            return folder
    raise FileNotFoundError("Could not find extracted dataset folder.")


def verify_dataset(dataset_folder: Path) -> None:
    """
    Verify that dataset has expected structure and count classes.
    """
    class_dirs = [d for d in dataset_folder.iterdir() if d.is_dir()]
    total_images = sum(
        len(list(d.glob("*.jpg"))) + len(list(d.glob("*.JPG"))) + len(list(d.glob("*.png")))
        for d in class_dirs
    )
    log.info(f"✅ Dataset verified: {len(class_dirs)} classes, ~{total_images:,} images found.")

    # Save class names json
    class_names = sorted([d.name for d in class_dirs])
    class_names_path = BASE_DIR / "ml" / "class_names.json"
    with open(class_names_path, "w") as f:
        json.dump(class_names, f, indent=2)
    log.info(f"Class names saved → {class_names_path}")


def main() -> None:
    log.info("=" * 60)
    log.info("  PlantVillage Dataset Downloader")
    log.info("=" * 60)

    configure_kaggle_credentials()
    zip_path = download_dataset()
    dataset_folder = extract_dataset(zip_path)
    verify_dataset(dataset_folder)

    log.info("")
    log.info("🎉 Dataset ready. Next step:")
    log.info("   python ml/preprocess.py")
    log.info("")


if __name__ == "__main__":
    main()
