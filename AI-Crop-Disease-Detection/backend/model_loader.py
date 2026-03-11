"""
model_loader.py
===============
Singleton pattern to load and cache the trained Keras model.
Avoids reloading the model on every request.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import tensorflow as tf
import numpy as np

log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent.parent
MODELS_DIR   = BASE_DIR / "models"
ML_DIR       = BASE_DIR / "ml"

# Default model file (MobileNetV2)
DEFAULT_MODEL = MODELS_DIR / "crop_disease_mobilenet.h5"
CLASS_NAMES_PATH = ML_DIR / "class_names.json"


class ModelLoader:
    """
    Thread-safe singleton for loading and caching the Keras model.
    """

    _instance: Optional["ModelLoader"] = None
    _model: Optional[tf.keras.Model] = None
    _class_names: Optional[list] = None

    def __new__(cls) -> "ModelLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, model_path: Optional[str] = None) -> None:
        """
        Load the Keras model and class names from disk.
        Skips if already loaded (singleton behaviour).
        """
        if self._model is not None:
            log.info("Model already loaded — skipping reload.")
            return

        mp = Path(model_path) if model_path else DEFAULT_MODEL

        if not mp.exists():
            raise FileNotFoundError(
                f"Model file not found: {mp}\n"
                "Train the model first: python ml/train_mobilenet.py"
            )

        log.info(f"Loading model from {mp} ...")
        self._model = tf.keras.models.load_model(str(mp))
        log.info(f"✅ Model loaded. Input shape: {self._model.input_shape}")

        # Load class names
        if not CLASS_NAMES_PATH.exists():
            raise FileNotFoundError(f"class_names.json not found at {CLASS_NAMES_PATH}")
        with open(CLASS_NAMES_PATH) as f:
            self._class_names = json.load(f)
        log.info(f"✅ {len(self._class_names)} class names loaded.")

    @property
    def model(self) -> tf.keras.Model:
        if self._model is None:
            raise RuntimeError("Model not loaded. Call ModelLoader().load() first.")
        return self._model

    @property
    def class_names(self) -> list:
        if self._class_names is None:
            raise RuntimeError("Class names not loaded.")
        return self._class_names

    @property
    def num_classes(self) -> int:
        return len(self._class_names) if self._class_names else 0

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def get_model_name(self) -> str:
        if self._model:
            return self._model.name
        return "not_loaded"


# ── Global singleton instance ─────────────────────────────────────────────────
model_loader = ModelLoader()
