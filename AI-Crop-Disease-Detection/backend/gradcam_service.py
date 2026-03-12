"""
gradcam_service.py
==================
FastAPI-compatible Grad-CAM service.
Takes a numpy image array and model, returns a base64-encoded PNG heatmap overlay.
"""

import io
import base64
import logging
from typing import Optional

import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from model_loader import model_loader

log = logging.getLogger(__name__)

IMG_SIZE = (224, 224)


def _get_gradcam_heatmap(
    img_array: np.ndarray,
    class_idx: int,
) -> np.ndarray:
    """
    Compute Grad-CAM heatmap for the given class index.

    Args:
        img_array: Raw float32 image, shape (224, 224, 3), values in [0, 255].
        class_idx: Target class index for gradient computation.

    Returns:
        heatmap: Shape (h, w) normalised to [0, 1].
    """
    model = model_loader.model

    # Find MobileNetV2 base model and its last Conv2D layer
    base_model = None
    last_conv_name = None
    
    # 1. Find the base model (mobilenetv2_1.00_224)
    for layer in model.layers:
        if hasattr(layer, "layers"):
            base_model = layer
            break
            
    if base_model is None:
        log.warning("No base model found; GradCAM skipped.")
        return np.zeros(IMG_SIZE)
        
    # 2. Find the last Conv2D in the base model
    for layer in reversed(base_model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            last_conv_name = layer.name
            break

    if last_conv_name is None:
        log.warning("No Conv2D layer found; GradCAM skipped.")
        return np.zeros(IMG_SIZE)

    # 3. Build grad model (Must extract from base model, not main model)
    last_conv_layer = base_model.get_layer(last_conv_name)
    grad_model = tf.keras.Model(
        inputs=model.inputs,
        outputs=[last_conv_layer.output, model.output],
    )

    # Preprocess for MobileNetV2
    img_input = preprocess_input(
        np.expand_dims(img_array.copy(), axis=0)
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_input)
        class_channel = predictions[:, class_idx]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()


def _overlay_heatmap(
    heatmap: np.ndarray,
    original_rgb: np.ndarray,
    alpha: float = 0.4,
) -> np.ndarray:
    """
    Overlay a jet-colormap heatmap on the original image.

    Args:
        heatmap:      Shape (h, w), values in [0, 1].
        original_rgb: Shape (224, 224, 3), uint8 RGB.
        alpha:        Heatmap opacity.

    Returns:
        Overlaid RGB image, shape (224, 224, 3), uint8.
    """
    # Resize heatmap to image size
    heatmap_resized = cv2.resize(heatmap, IMG_SIZE)

    # Apply jet colormap
    colormap = cm.get_cmap("jet")
    heatmap_colored = colormap(heatmap_resized)[:, :, :3]         # RGBA → RGB
    heatmap_colored = (heatmap_colored * 255).astype(np.uint8)    # Scale to 255

    # Convert original to uint8 if needed
    orig = original_rgb.astype(np.uint8) if original_rgb.dtype != np.uint8 else original_rgb

    # Blend
    overlay = cv2.addWeighted(orig, 1 - alpha, heatmap_colored, alpha, 0)
    return overlay


def _ndarray_to_base64_png(img_rgb: np.ndarray) -> str:
    """
    Encode a uint8 RGB numpy array as a base64 PNG string.
    """
    pil_img = tf.keras.utils.array_to_img(img_rgb)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def generate_gradcam_base64(
    img_array: np.ndarray,
    class_idx: int,
) -> Optional[str]:
    """
    Full Grad-CAM pipeline → base64-encoded overlay PNG.

    Args:
        img_array:  Raw image array (224, 224, 3) float32, values in [0, 255].
        class_idx:  Predicted class index.

    Returns:
        Base64 string of the Grad-CAM overlay PNG, or None on failure.
    """
    try:
        heatmap = _get_gradcam_heatmap(img_array, class_idx)
        overlay = _overlay_heatmap(heatmap, img_array)
        b64 = _ndarray_to_base64_png(overlay)
        log.info("Grad-CAM generated successfully.")
        return b64
    except Exception as e:
        log.error(f"Grad-CAM generation failed: {e}", exc_info=True)
        return None
