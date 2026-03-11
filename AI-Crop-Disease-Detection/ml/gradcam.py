"""
gradcam.py
==========
Grad-CAM (Gradient-weighted Class Activation Mapping) implementation.

Given an image and a trained model, generates a heatmap that highlights
the regions of the leaf that influenced the prediction most.

Reference: Selvaraju et al., "Grad-CAM: Visual Explanations from Deep Networks
           via Gradient-based Localization" (ICCV 2017)

Usage:
    python ml/gradcam.py --image path/to/leaf.jpg --model mobilenet
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
from PIL import Image

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent.parent
MODELS_DIR  = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs" / "plots"
CLASS_NAMES_PATH = BASE_DIR / "ml" / "class_names.json"
img_size    = (224, 224)

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# ── Core Grad-CAM Functions ───────────────────────────────────────────────────

def preprocess_image(
    image_path: str,
    model_type: str = "mobilenet",
) -> np.ndarray:
    """
    Load and preprocess a single image for inference.
    Returns a batched array of shape (1, 224, 224, 3).
    """
    img = tf.keras.utils.load_img(image_path, target_size=img_size)
    img_array = tf.keras.utils.img_to_array(img)

    if model_type == "mobilenet":
        img_array = mobilenet_preprocess(img_array)
    else:
        img_array = img_array / 255.0  # Normalize to [0, 1]

    return np.expand_dims(img_array, axis=0)  # shape: (1, 224, 224, 3)


def get_last_conv_layer_name(model: tf.keras.Model) -> str:
    """
    Automatically find the last convolutional layer in the model.
    This is where Grad-CAM extracts feature maps.
    """
    for layer in reversed(model.layers):
        if isinstance(layer, (tf.keras.layers.Conv2D,)):
            return layer.name
        # Handle MobileNetV2 sub-model
        if hasattr(layer, "layers"):
            for sub in reversed(layer.layers):
                if isinstance(sub, tf.keras.layers.Conv2D):
                    return sub.name
    raise ValueError("No Conv2D layer found in model.")


def compute_gradcam(
    model: tf.keras.Model,
    img_array: np.ndarray,
    class_idx: int,
    last_conv_layer_name: Optional[str] = None,
) -> np.ndarray:
    """
    Compute Grad-CAM heatmap for the specified class index.

    Returns:
        heatmap (np.ndarray): Normalised heatmap of shape (h, w) in [0, 1].
    """
    if last_conv_layer_name is None:
        last_conv_layer_name = get_last_conv_layer_name(model)

    # Build a sub-model that outputs (conv_feature_maps, predictions)
    grad_model = tf.keras.Model(
        inputs=model.inputs,
        outputs=[
            model.get_layer(last_conv_layer_name).output,
            model.output,
        ],
    )

    # Compute gradients of the class score w.r.t. convolutional output
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        class_channel = predictions[:, class_idx]

    grads = tape.gradient(class_channel, conv_outputs)

    # Global average pooling of gradients → importance weights
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Weight feature maps by importance
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # Normalise heatmap to [0, 1]
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()


def overlay_heatmap(
    heatmap: np.ndarray,
    original_image_path: str,
    alpha: float = 0.4,
    colormap: str = "jet",
) -> np.ndarray:
    """
    Resize heatmap to original image size and overlay it using a colormap.

    Returns:
        superimposed (np.ndarray): BGR image with heatmap overlay, shape (224, 224, 3)
    """
    # Resize heatmap to image size
    heatmap_resized = cv2.resize(heatmap, img_size)

    # Apply color map (jet → red = high activation)
    colormap_fn = cm.get_cmap(colormap)
    heatmap_colored = colormap_fn(heatmap_resized)  # RGBA (224, 224, 4)
    heatmap_colored = (heatmap_colored[:, :, :3] * 255).astype(np.uint8)  # RGB

    # Load original image
    original = cv2.imread(original_image_path)
    original = cv2.resize(original, img_size)

    # Overlay
    superimposed = cv2.addWeighted(original, 1 - alpha, heatmap_colored, alpha, 0)
    return superimposed


def generate_gradcam(
    image_path: str,
    model: tf.keras.Model,
    class_names: list,
    model_type: str = "mobilenet",
    save_path: Optional[str] = None,
) -> dict:
    """
    End-to-end Grad-CAM pipeline for a single image.

    Returns:
        dict with keys: predicted_class, confidence, heatmap_array, overlay_image
    """
    img_array = preprocess_image(image_path, model_type)

    # Predict
    preds       = model.predict(img_array, verbose=0)
    class_idx   = int(np.argmax(preds[0]))
    confidence  = float(preds[0][class_idx])
    class_label = class_names[class_idx]

    log.info(f"Predicted: {class_label}  (confidence: {confidence:.2%})")

    # Compute Grad-CAM
    last_conv = get_last_conv_layer_name(model)
    heatmap   = compute_gradcam(model, img_array, class_idx, last_conv)
    overlay   = overlay_heatmap(heatmap, image_path)

    # Save result
    if save_path is None:
        save_path = str(OUTPUTS_DIR / "gradcam_result.png")

    _save_gradcam_figure(image_path, heatmap, overlay, class_label, confidence, save_path)

    return {
        "predicted_class": class_label,
        "class_index":     class_idx,
        "confidence":      confidence,
        "heatmap":         heatmap,
        "overlay_bgr":     overlay,
        "save_path":       save_path,
    }


def _save_gradcam_figure(
    original_path: str,
    heatmap: np.ndarray,
    overlay: np.ndarray,
    label: str,
    confidence: float,
    save_path: str,
) -> None:
    """Save a 3-panel figure: original | heatmap | overlay."""
    original = cv2.imread(original_path)
    original = cv2.resize(original, img_size)
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    overlay_rgb  = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        f"Grad-CAM | {label} ({confidence:.1%} confidence)",
        fontsize=14,
        fontweight="bold",
    )

    axes[0].imshow(original_rgb)
    axes[0].set_title("Original Image")
    axes[0].axis("off")

    axes[1].imshow(heatmap, cmap="jet")
    axes[1].set_title("Grad-CAM Heatmap")
    axes[1].axis("off")
    plt.colorbar(
        plt.cm.ScalarMappable(cmap="jet"),
        ax=axes[1],
        fraction=0.046,
        pad=0.04,
    )

    axes[2].imshow(overlay_rgb)
    axes[2].set_title("Overlay (Infected Region)")
    axes[2].axis("off")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Grad-CAM figure saved → {save_path}")


# ── CLI Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Grad-CAM for a leaf image")
    parser.add_argument("--image",  type=str, required=True, help="Path to leaf image")
    parser.add_argument("--model",  type=str, default="mobilenet",
                        choices=["mobilenet", "custom_cnn"])
    parser.add_argument("--output", type=str, default=None, help="Output PNG path")
    args = parser.parse_args()

    MODEL_FILES = {
        "mobilenet":  "crop_disease_mobilenet.h5",
        "custom_cnn": "crop_disease_custom_cnn.h5",
    }
    model_path = MODELS_DIR / MODEL_FILES[args.model]
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    model = tf.keras.models.load_model(str(model_path))
    with open(CLASS_NAMES_PATH) as f:
        class_names = json.load(f)

    results = generate_gradcam(
        image_path=args.image,
        model=model,
        class_names=class_names,
        model_type=args.model,
        save_path=args.output,
    )
    log.info(f"\n✅ Grad-CAM complete! Output: {results['save_path']}")
