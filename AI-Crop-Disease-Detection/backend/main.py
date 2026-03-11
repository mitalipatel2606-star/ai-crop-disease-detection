"""
main.py
=======
FastAPI application entry point for the AI Crop Disease Detection API.

Endpoints:
  POST /predict    — Upload a leaf image → get disease prediction + GradCAM
  GET  /diseases   — Browse the full disease knowledge base
  GET  /history    — Retrieve prediction history
  GET  /health     — Health check / readiness probe

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from model_loader import model_loader
from predict import run_inference
from gradcam_service import generate_gradcam_base64
from recommendation import get_recommendation, get_all_diseases, load_disease_database
from history import init_db, get_db, save_prediction, get_prediction_history
from schemas import (
    PredictionResponse,
    HealthResponse,
    DiseasesResponse,
    HistoryResponse,
    HistoryEntry,
)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Allowed image MIME types ──────────────────────────────────────────────────
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# ── Lifespan: run startup/shutdown logic ──────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model and DB once on startup; clean up on shutdown."""
    log.info("🚀 Starting AI Crop Disease Detection API ...")

    # Load trained model
    model_path = os.getenv("MODEL_PATH", None)
    model_loader.load(model_path)

    # Initialise SQLite database
    init_db()

    # Load disease database
    load_disease_database()

    log.info("✅ All dependencies loaded. API is ready.")
    yield
    log.info("Shutting down API.")


# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Crop Disease Detection API",
    description=(
        "Deep learning–powered crop disease detection from leaf images. "
        "Returns predicted disease, confidence, treatment recommendations, and Grad-CAM heatmap."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — allow React frontend ───────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # In production, replace "*" with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.
    Returns model status and metadata.
    """
    return HealthResponse(
        status="healthy" if model_loader.is_loaded else "model_not_loaded",
        model_loaded=model_loader.is_loaded,
        model_name=model_loader.get_model_name(),
        num_classes=model_loader.num_classes,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(
    file: UploadFile = File(..., description="Leaf image file (JPEG/PNG, max 10MB)"),
    db: Session = Depends(get_db),
):
    """
    **Predict plant disease from a leaf image.**

    - Upload a JPEG or PNG image of a plant leaf.
    - Returns the predicted disease, confidence score, top-5 alternatives,
      treatment recommendations, and a Grad-CAM heatmap (base64).
    """
    # ── Validate file type ────────────────────────────────────────────────────
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Use JPEG or PNG.",
        )

    # ── Read file bytes ───────────────────────────────────────────────────────
    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB.",
        )

    # ── Run inference ─────────────────────────────────────────────────────────
    try:
        result = run_inference(image_bytes)
    except Exception as e:
        log.error(f"Inference failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

    disease    = result["disease"]
    confidence = result["confidence"]
    class_idx  = result["class_index"]
    img_array  = result["img_array"]

    # ── Grad-CAM ──────────────────────────────────────────────────────────────
    heatmap_b64 = generate_gradcam_base64(img_array, class_idx)

    # ── Recommendation ────────────────────────────────────────────────────────
    recommendation = get_recommendation(disease)

    # ── Save to history ───────────────────────────────────────────────────────
    save_prediction(db, filename=file.filename or "unknown.jpg", disease=disease, confidence=confidence)

    return PredictionResponse(
        disease=disease,
        confidence=confidence,
        top_predictions=result["top_predictions"],
        recommendation=recommendation,
        heatmap_base64=heatmap_b64,
        warning=result.get("warning"),
        model_version=model_loader.get_model_name(),
    )


@app.get("/diseases", response_model=DiseasesResponse, tags=["Knowledge Base"])
async def list_diseases():
    """
    **Browse the full disease knowledge base.**

    Returns all 38 plant disease entries with descriptions, treatments, and preventive measures.
    """
    diseases = get_all_diseases()
    return DiseasesResponse(count=len(diseases), diseases=diseases)


@app.get("/history", response_model=HistoryResponse, tags=["History"])
async def prediction_history(
    limit:  int = Query(default=20, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
):
    """
    **Retrieve prediction history.**

    Returns recent predictions in reverse chronological order.
    """
    records = get_prediction_history(db, limit=limit, offset=offset)
    entries = [
        HistoryEntry(
            id=r.id,
            filename=r.filename,
            disease=r.disease,
            confidence=r.confidence,
            timestamp=r.timestamp,
        )
        for r in records
    ]
    return HistoryResponse(count=len(entries), history=entries)


# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
