"""
predict.py
==========
Image preprocessing and model inference for a single uploaded image.
Returns top-5 predictions with disease name and confidence scores.
"""

import io
import logging
from typing import List, Dict, Any

import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from model_loader import model_loader

log = logging.getLogger(__name__)

# Model expects 224×224 RGB images
IMG_SIZE = (224, 224)

# Confidence threshold below which a warning is issued
LOW_CONFIDENCE_THRESHOLD = 0.50


def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Load image bytes → resize to 224×224 → return float32 array.

    Args:
        image_bytes: Raw bytes from the uploaded file.

    Returns:
        numpy array of shape (224, 224, 3), dtype float32.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize(IMG_SIZE, Image.LANCZOS)
    return np.array(image, dtype=np.float32)


def preprocess_for_mobilenet(img_array: np.ndarray) -> np.ndarray:
    """
    Apply MobileNetV2 preprocessing (pixel values scaled to [-1, 1])
    and add batch dimension.

    Args:
        img_array: Shape (224, 224, 3)

    Returns:
        Shape (1, 224, 224, 3) ready for model.predict()
    """
    img = np.expand_dims(img_array, axis=0)       # (1, 224, 224, 3)
    img = preprocess_input(img)                    # Scale to [-1, 1]
    return img


def run_inference(image_bytes: bytes) -> Dict[str, Any]:
    """
    Full inference pipeline for an uploaded image.

    Steps:
      1. Decode + resize image
      2. Preprocess (MobileNetV2 scale)
      3. Run model.predict()
      4. Extract top-5 predictions
      5. Build response dict

    Args:
        image_bytes: Raw bytes from HTTP upload.

    Returns:
        {
          "disease": str,
          "confidence": float,
          "top_predictions": [...],
          "warning": str | None,
          "img_array": ndarray (224,224,3) — for GradCAM
        }
    """
    model = model_loader.model
    class_names = model_loader.class_names

    # 1. Load image
    img_array = load_image_from_bytes(image_bytes)

    # 2. Preprocess
    img_input = preprocess_for_mobilenet(img_array)

    # 3. Predict
    log.info("Running model inference ...")
    predictions = model.predict(img_input, verbose=0)[0]  # Shape: (num_classes,)

    # 4. Top-5 predictions
    top5_indices = np.argsort(predictions)[::-1][:5]
    top5 = [
        {
            "class":      class_names[i],
            "confidence": round(float(predictions[i]), 4),
        }
        for i in top5_indices
    ]

    best_idx  = top5_indices[0]
    best_name = class_names[best_idx]
    best_conf = float(predictions[best_idx])

    # 5. Low-confidence warning
    warning = None
    if best_conf < LOW_CONFIDENCE_THRESHOLD:
        warning = (
            f"Low confidence ({best_conf:.0%}). "
            "Please upload a clearer, well-lit image of the leaf."
        )

    log.info(f"Prediction: {best_name} ({best_conf:.2%})")

    return {
        "disease":         best_name,
        "confidence":      round(best_conf, 4),
        "top_predictions": top5,
        "warning":         warning,
        "img_array":       img_array,   # (224, 224, 3) float32 for Grad-CAM
        "class_index":     int(best_idx),
    }
