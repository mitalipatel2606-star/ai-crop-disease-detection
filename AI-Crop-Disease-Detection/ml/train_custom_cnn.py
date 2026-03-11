"""
train_custom_cnn.py
===================
Baseline custom CNN built from scratch for plant disease classification.

Architecture:
  3× [Conv2D → BatchNorm → MaxPool → Dropout] blocks
  Flatten → Dense(512) → Dropout → Dense(num_classes, softmax)

Usage:
    python ml/train_custom_cnn.py

Outputs:
  models/crop_disease_custom_cnn.h5
  models/training_history/custom_cnn_history.json
"""

import json
import logging
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau,
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paths & Config ────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "dataset" / "processed"
MODELS_DIR    = BASE_DIR / "models"
HISTORY_DIR   = MODELS_DIR / "training_history"
CLASS_NAMES   = BASE_DIR / "ml" / "class_names.json"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

# ── Hyper-parameters ──────────────────────────────────────────────────────────
IMG_SIZE   = (224, 224)
BATCH_SIZE = 32
EPOCHS     = 20
LR         = 1e-3


def load_class_names() -> list:
    with open(CLASS_NAMES) as f:
        return json.load(f)


def build_data_generators() -> tuple:
    """
    Normalise pixels to [0, 1] for custom CNN.
    """
    train_gen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=30,
        zoom_range=0.2,
        horizontal_flip=True,
        brightness_range=[0.7, 1.3],
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
    )
    val_gen = ImageDataGenerator(rescale=1.0 / 255)

    train_flow = train_gen.flow_from_directory(
        str(PROCESSED_DIR / "train"),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=True,
    )
    val_flow = val_gen.flow_from_directory(
        str(PROCESSED_DIR / "val"),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False,
    )
    return train_flow, val_flow


def build_custom_cnn(num_classes: int) -> Model:
    """
    Build a custom CNN architecture from scratch.

    Block structure (×3):
      Conv2D(filters, 3×3, same) → BatchNorm → ReLU
      Conv2D(filters, 3×3, same) → BatchNorm → ReLU
      MaxPool(2×2) → Dropout

    Head:
      GlobalAveragePooling → Dense(512) → Dropout → Dense(num_classes, softmax)
    """
    inputs = tf.keras.Input(shape=(*IMG_SIZE, 3), name="input_image")

    # ── Block 1 (32 filters) ──────────────────────────────────────────────────
    x = layers.Conv2D(32, (3, 3), padding="same", activation="relu")(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(32, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    # ── Block 2 (64 filters) ──────────────────────────────────────────────────
    x = layers.Conv2D(64, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(64, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    # ── Block 3 (128 filters) ─────────────────────────────────────────────────
    x = layers.Conv2D(128, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(128, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)

    # ── Block 4 (256 filters) ─────────────────────────────────────────────────
    x = layers.Conv2D(256, (3, 3), padding="same", activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.3)(x)

    # ── Head ──────────────────────────────────────────────────────────────────
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(512, activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    model = Model(inputs, outputs, name="CustomCNN_CropDisease")
    log.info(f"Custom CNN built: {model.count_params():,} total params")
    return model


def train() -> None:
    log.info("=" * 60)
    log.info("  Custom CNN Training Pipeline")
    log.info("=" * 60)

    class_names = load_class_names()
    num_classes = len(class_names)
    log.info(f"Number of classes: {num_classes}")

    train_flow, val_flow = build_data_generators()
    model = build_custom_cnn(num_classes)

    model_path = str(MODELS_DIR / "crop_disease_custom_cnn.h5")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(LR),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary(print_fn=log.info)

    callbacks = [
        EarlyStopping(
            monitor="val_accuracy",
            patience=6,
            restore_best_weights=True,
            verbose=1,
        ),
        ModelCheckpoint(
            filepath=model_path,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.3,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    history = model.fit(
        train_flow,
        epochs=EPOCHS,
        validation_data=val_flow,
        callbacks=callbacks,
    )

    # ── Save history ──────────────────────────────────────────────────────────
    history_path = HISTORY_DIR / "custom_cnn_history.json"
    with open(history_path, "w") as f:
        json.dump(history.history, f, indent=2)
    log.info(f"Training history saved → {history_path}")

    log.info("\n✅ Custom CNN training complete!")
    log.info(f"   Best model saved → {model_path}")


if __name__ == "__main__":
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        tf.config.experimental.set_memory_growth(gpus[0], True)
    train()
