"""
evaluate.py
===========
Generates full evaluation metrics for a trained model:
  - Accuracy, Precision, Recall, F1 Score
  - Confusion Matrix (saved as PNG)
  - Training curves (accuracy & loss plots)
  - Classification report (saved as text)

Usage:
    python ml/evaluate.py --model mobilenet
    python ml/evaluate.py --model custom_cnn
"""

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
)
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "dataset" / "processed"
MODELS_DIR    = BASE_DIR / "models"
OUTPUTS_DIR   = BASE_DIR / "outputs"
PLOTS_DIR     = OUTPUTS_DIR / "plots"
REPORTS_DIR   = OUTPUTS_DIR / "reports"
CLASS_NAMES   = BASE_DIR / "ml" / "class_names.json"

PLOTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

IMG_SIZE   = (224, 224)
BATCH_SIZE = 32


def load_model_and_class_names(model_type: str) -> tuple:
    """Load model and class names based on model type."""
    model_files = {
        "mobilenet":   "crop_disease_mobilenet.h5",
        "custom_cnn":  "crop_disease_custom_cnn.h5",
    }
    model_path = MODELS_DIR / model_files[model_type]
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}\nRun training first.")

    model = tf.keras.models.load_model(str(model_path))
    with open(CLASS_NAMES) as f:
        class_names = json.load(f)
    log.info(f"Loaded model: {model_path.name}")
    return model, class_names


def build_test_generator(model_type: str) -> tf.keras.preprocessing.image.DirectoryIterator:
    """Build test data generator with appropriate preprocessing."""
    if model_type == "mobilenet":
        gen = ImageDataGenerator(preprocessing_function=mobilenet_preprocess)
    else:
        gen = ImageDataGenerator(rescale=1.0 / 255)

    return gen.flow_from_directory(
        str(PROCESSED_DIR / "test"),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False,
    )


def plot_training_curves(history_path: Path, model_name: str) -> None:
    """Plot accuracy and loss training curves from saved history JSON."""
    if not history_path.exists():
        log.warning(f"History file not found: {history_path}")
        return

    with open(history_path) as f:
        history = json.load(f)

    epochs = range(1, len(history["accuracy"]) + 1)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"{model_name} Training Curves", fontsize=16, fontweight="bold")

    # Accuracy plot
    axes[0].plot(epochs, history["accuracy"],      "b-o", label="Train Accuracy", linewidth=2)
    axes[0].plot(epochs, history["val_accuracy"],  "r-o", label="Val Accuracy",   linewidth=2)
    axes[0].set_title("Accuracy")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Accuracy")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Loss plot
    axes[1].plot(epochs, history["loss"],     "b-o", label="Train Loss", linewidth=2)
    axes[1].plot(epochs, history["val_loss"], "r-o", label="Val Loss",   linewidth=2)
    axes[1].set_title("Loss")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Loss")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = PLOTS_DIR / f"{model_name}_training_curves.png"
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Training curves saved → {save_path}")


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list,
    model_name: str,
) -> None:
    """Generate and save confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)  # Normalize per row

    # Limit to 20 classes max for readability
    display_classes = class_names[:20]
    cm_display = cm_norm[:20, :20]

    fig, ax = plt.subplots(figsize=(16, 14))
    sns.heatmap(
        cm_display,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        xticklabels=display_classes,
        yticklabels=display_classes,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title(f"{model_name} Confusion Matrix (Normalized)\nFirst 20 classes", fontsize=14)
    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_ylabel("True Label", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()

    save_path = PLOTS_DIR / f"{model_name}_confusion_matrix.png"
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Confusion matrix saved → {save_path}")


def evaluate(model_type: str) -> None:
    log.info("=" * 60)
    log.info(f"  Evaluating {model_type.upper()} model")
    log.info("=" * 60)

    model, class_names = load_model_and_class_names(model_type)
    test_gen = build_test_generator(model_type)

    # ── Run Predictions ───────────────────────────────────────────────────────
    log.info("Running inference on test set ...")
    y_pred_probs = model.predict(test_gen, verbose=1)
    y_pred = np.argmax(y_pred_probs, axis=1)
    y_true = test_gen.classes

    # ── Metrics ───────────────────────────────────────────────────────────────
    acc  = accuracy_score(y_true, y_pred)
    f1   = f1_score(y_true, y_pred, average="weighted")
    report = classification_report(y_true, y_pred, target_names=class_names)

    log.info(f"\n📊 Accuracy : {acc:.4f}")
    log.info(f"📊 F1 Score : {f1:.4f}")
    log.info(f"\nClassification Report:\n{report}")

    # ── Save Text Report ──────────────────────────────────────────────────────
    report_path = REPORTS_DIR / f"{model_type}_evaluation_report.txt"
    with open(report_path, "w") as f:
        f.write(f"Model: {model_type}\n")
        f.write(f"Accuracy : {acc:.4f}\n")
        f.write(f"F1 Score : {f1:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(report)
    log.info(f"Report saved → {report_path}")

    # ── Plots ─────────────────────────────────────────────────────────────────
    history_path = MODELS_DIR / "training_history" / f"{model_type}_history.json"
    plot_training_curves(history_path, model_type)
    plot_confusion_matrix(y_true, y_pred, class_names, model_type)

    log.info("\n✅ Evaluation complete!")
    log.info(f"   Plots saved to: {PLOTS_DIR}")
    log.info(f"   Report saved to: {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a crop disease model")
    parser.add_argument(
        "--model",
        type=str,
        default="mobilenet",
        choices=["mobilenet", "custom_cnn"],
        help="Which model to evaluate",
    )
    args = parser.parse_args()
    evaluate(args.model)
