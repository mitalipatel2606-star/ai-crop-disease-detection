"""
preprocess.py
=============
Preprocesses the raw PlantVillage dataset:
  - Resizes images to 224×224
  - Applies data augmentation for training set
  - Splits into train / validation / test
  - Saves split data into dataset/processed/

Usage:
    python ml/preprocess.py
"""

import os
import shutil
import random
import logging
import json
from pathlib import Path
from PIL import Image, ImageEnhance
import numpy as np
from tqdm import tqdm

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent
RAW_DIR       = BASE_DIR / "dataset" / "raw"
PROCESSED_DIR = BASE_DIR / "dataset" / "processed"
IMG_SIZE      = (224, 224)

SPLIT_RATIOS  = {"train": 0.70, "val": 0.15, "test": 0.15}
RANDOM_SEED   = 42


# ── Helpers ───────────────────────────────────────────────────────────────────

def find_dataset_root(raw_dir: Path) -> Path:
    """
    Navigate into raw/ to find the folder containing class subfolders.
    """
    for item in raw_dir.iterdir():
        if item.is_dir():
            subdirs = [x for x in item.iterdir() if x.is_dir()]
            if len(subdirs) > 5:
                return item
            # One more level deep
            for sub in subdirs:
                subsubdirs = [x for x in sub.iterdir() if x.is_dir()]
                if len(subsubdirs) > 5:
                    return sub
    return raw_dir  # fallback


def resize_image(src: Path, dst: Path, size: tuple = IMG_SIZE) -> None:
    """
    Open, resize (LANCZOS), and save an image as JPEG.
    """
    with Image.open(src).convert("RGB") as img:
        img = img.resize(size, Image.LANCZOS)
        dst.parent.mkdir(parents=True, exist_ok=True)
        img.save(dst, "JPEG", quality=95)


def augment_and_save(src: Path, dst_dir: Path, class_name: str, idx: int) -> None:
    """
    Apply random augmentations and save augmented copies to dst_dir.
    Augmentations: rotation, horizontal flip, brightness, zoom.
    """
    with Image.open(src).convert("RGB") as img:
        img = img.resize(IMG_SIZE, Image.LANCZOS)

        # 1. Horizontal flip
        flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
        out = dst_dir / f"aug_flip_{idx}.jpg"
        flipped.save(out, "JPEG", quality=95)

        # 2. Random rotation (-30 to 30 degrees)
        angle = random.uniform(-30, 30)
        rotated = img.rotate(angle, fillcolor=(0, 0, 0))
        out = dst_dir / f"aug_rot_{idx}.jpg"
        rotated.save(out, "JPEG", quality=95)

        # 3. Brightness adjustment (0.7 – 1.4)
        factor = random.uniform(0.7, 1.4)
        bright = ImageEnhance.Brightness(img).enhance(factor)
        out = dst_dir / f"aug_bright_{idx}.jpg"
        bright.save(out, "JPEG", quality=95)

        # 4. Centre zoom (crop 80% then resize back)
        w, h = img.size
        left  = int(0.1 * w)
        top   = int(0.1 * h)
        right = int(0.9 * w)
        bot   = int(0.9 * h)
        zoomed = img.crop((left, top, right, bot)).resize(IMG_SIZE, Image.LANCZOS)
        out = dst_dir / f"aug_zoom_{idx}.jpg"
        zoomed.save(out, "JPEG", quality=95)


def split_files(file_list: list, ratios: dict, seed: int = RANDOM_SEED) -> dict:
    """
    Randomly split file list into train/val/test according to ratios.
    Returns a dict: {"train": [...], "val": [...], "test": [...]}
    """
    random.seed(seed)
    random.shuffle(file_list)
    n = len(file_list)
    n_train = int(n * ratios["train"])
    n_val   = int(n * ratios["val"])
    return {
        "train": file_list[:n_train],
        "val":   file_list[n_train:n_train + n_val],
        "test":  file_list[n_train + n_val:],
    }


# ── Main Processing Pipeline ──────────────────────────────────────────────────

def process_dataset(augment: bool = True) -> None:
    dataset_root = find_dataset_root(RAW_DIR)
    class_dirs   = sorted([d for d in dataset_root.iterdir() if d.is_dir()])

    if not class_dirs:
        raise FileNotFoundError(
            f"No class folders found in {dataset_root}\n"
            "Run: python ml/download_dataset.py first."
        )

    log.info(f"Found {len(class_dirs)} classes in {dataset_root}")
    CLASS_NAMES = [d.name for d in class_dirs]

    # Save updated class names
    cn_path = BASE_DIR / "ml" / "class_names.json"
    with open(cn_path, "w") as f:
        json.dump(CLASS_NAMES, f, indent=2)
    log.info(f"Class names saved → {cn_path}")

    stats = {"train": 0, "val": 0, "test": 0}

    for class_dir in tqdm(class_dirs, desc="Processing classes"):
        class_name = class_dir.name
        images = list(class_dir.glob("*.jpg")) + \
                 list(class_dir.glob("*.JPG")) + \
                 list(class_dir.glob("*.jpeg")) + \
                 list(class_dir.glob("*.png"))

        if not images:
            log.warning(f"  No images found in {class_name}, skipping.")
            continue

        splits = split_files(images, SPLIT_RATIOS)

        for split, files in splits.items():
            out_dir = PROCESSED_DIR / split / class_name
            out_dir.mkdir(parents=True, exist_ok=True)

            for i, img_path in enumerate(files):
                dst = out_dir / f"{i:05d}.jpg"
                resize_image(img_path, dst)
                stats[split] += 1

                # Augment only training set
                if split == "train" and augment:
                    augment_and_save(img_path, out_dir, class_name, i)
                    stats["train"] += 4  # 4 augmented copies

    log.info("\n✅ Preprocessing complete!")
    log.info(f"   Train images : {stats['train']:,}")
    log.info(f"   Val images   : {stats['val']:,}")
    log.info(f"   Test images  : {stats['test']:,}")
    log.info(f"\nSaved to: {PROCESSED_DIR}")
    log.info("Next step: python ml/train_mobilenet.py")


if __name__ == "__main__":
    process_dataset(augment=True)
