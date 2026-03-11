"""
train_mobilenet.py
==================
Transfer learning pipeline using MobileNetV2 pre-trained on ImageNet.

Pipeline:
  Phase 1 — Freeze base model, train only top layers (5 epochs)
  Phase 2 — Unfreeze top 30 layers, fine-tune with lower LR (10–15 epochs)

Usage:
    python ml/train_mobilenet.py

Outputs:
  models/crop_disease_mobilenet.h5
  models/training_history/mobilenet_history.json
"""

import os
import json
import logging
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ModelCheckpoint,
    ReduceLROnPlateau,
    TensorBoard,
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
IMG_SIZE    = (224, 224)
BATCH_SIZE  = 32
PHASE1_EPOCHS = 5
PHASE2_EPOCHS = 15
LEARNING_RATE = 1e-3
FINE_TUNE_LR  = 1e-5


def load_class_names() -> list:
    with open(CLASS_NAMES) as f:
        return json.load(f)


def build_data_generators() -> tuple:
    """
    Create training and validation ImageDataGenerators.
    MobileNetV2 expects pixels in [-1, 1] range (preprocess_input).
    """
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    train_gen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=30,
        zoom_range=0.2,
        horizontal_flip=True,
        brightness_range=[0.7, 1.3],
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
    )
    val_gen = ImageDataGenerator(preprocessing_function=preprocess_input)

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


def build_model(num_classes: int) -> Model:
    """
    Build MobileNetV2 transfer-learning model.
    """
    # Base model without top classifier
    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(*IMG_SIZE, 3),
    )
    base_model.trainable = False  # Freeze for Phase 1

    # Custom top layers
    inputs  = tf.keras.Input(shape=(*IMG_SIZE, 3))
    x       = base_model(inputs, training=False)
    x       = layers.GlobalAveragePooling2D()(x)
    x       = layers.Dense(256, activation="relu")(x)
    x       = layers.BatchNormalization()(x)
    x       = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = Model(inputs, outputs, name="MobileNetV2_CropDisease")
    log.info(f"Model built: {model.count_params():,} total params")
    return model, base_model


def get_callbacks(phase: int, model_path: str) -> list:
    return [
        EarlyStopping(
            monitor="val_accuracy",
            patience=5,
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
        TensorBoard(
            log_dir=str(BASE_DIR / "outputs" / "logs" / f"mobilenet_phase{phase}"),
            histogram_freq=0,
        ),
    ]


def save_history(history_dict: dict, name: str) -> None:
    path = HISTORY_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(history_dict, f, indent=2)
    log.info(f"Training history saved → {path}")


def train() -> None:
    log.info("=" * 60)
    log.info("  MobileNetV2 Training Pipeline")
    log.info("=" * 60)

    class_names = load_class_names()
    num_classes = len(class_names)
    log.info(f"Number of classes: {num_classes}")

    # ── Data ──────────────────────────────────────────────────────────────────
    train_flow, val_flow = build_data_generators()
    log.info(f"Train batches: {len(train_flow)} | Val batches: {len(val_flow)}")

    # ── Build Model ───────────────────────────────────────────────────────────
    model, base_model = build_model(num_classes)
    model_path = str(MODELS_DIR / "crop_disease_mobilenet.h5")

    # ==========================================================================
    # PHASE 1: Train only top layers with frozen base
    # ==========================================================================
    log.info("\n🟡 Phase 1: Training top layers (base frozen) ...")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    history1 = model.fit(
        train_flow,
        epochs=PHASE1_EPOCHS,
        validation_data=val_flow,
        callbacks=get_callbacks(1, model_path),
    )

    # ==========================================================================
    # PHASE 2: Unfreeze top 30 layers of base and fine-tune
    # ==========================================================================
    log.info("\n🟢 Phase 2: Fine-tuning (unfreeze top 30 base layers) ...")
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(FINE_TUNE_LR),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    history2 = model.fit(
        train_flow,
        epochs=PHASE2_EPOCHS,
        validation_data=val_flow,
        callbacks=get_callbacks(2, model_path),
    )

    # ── Save Combined History ─────────────────────────────────────────────────
    combined = {}
    for k in history1.history:
        combined[k] = history1.history[k] + history2.history.get(k, [])
    save_history(combined, "mobilenet_history")

    log.info("\n✅ Training complete!")
    log.info(f"   Best model saved → {model_path}")
    log.info("   Next step: python ml/evaluate.py")


if __name__ == "__main__":
    # Use GPU if available
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        log.info(f"GPU detected: {gpus}")
        tf.config.experimental.set_memory_growth(gpus[0], True)
    else:
        log.info("No GPU detected, training on CPU.")

    train()
