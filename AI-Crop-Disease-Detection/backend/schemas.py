"""
schemas.py
==========
Pydantic request/response schemas for the FastAPI application.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# ── Disease Recommendation Schema ─────────────────────────────────────────────
class DiseaseRecommendation(BaseModel):
    description:      str
    pesticide:        str
    organic_solution: str
    prevention:       List[str]


# ── Prediction Response ───────────────────────────────────────────────────────
class PredictionResponse(BaseModel):
    disease:         str           = Field(..., description="Predicted disease class name")
    confidence:      float         = Field(..., ge=0.0, le=1.0, description="Model confidence [0–1]")
    top_predictions: List[dict]    = Field(..., description="Top-5 predictions with probabilities")
    recommendation:  DiseaseRecommendation
    heatmap_base64:  Optional[str] = Field(None, description="Base64-encoded Grad-CAM PNG")
    warning:         Optional[str] = Field(None, description="Low-confidence warning message")
    model_version:   str           = Field("mobilenet_v2", description="Model used for inference")
    timestamp:       datetime      = Field(default_factory=datetime.utcnow)


# ── Disease List Response ─────────────────────────────────────────────────────
class DiseaseEntry(BaseModel):
    name:            str
    description:     str
    pesticide:       str
    organic_solution: str
    prevention:      List[str]


class DiseasesResponse(BaseModel):
    count:    int
    diseases: List[DiseaseEntry]


# ── Health Check Response ─────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status:        str
    model_loaded:  bool
    model_name:    str
    num_classes:   int
    version:       str = "1.0.0"


# ── Prediction History ────────────────────────────────────────────────────────
class HistoryEntry(BaseModel):
    id:         int
    filename:   str
    disease:    str
    confidence: float
    timestamp:  datetime

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    count:   int
    history: List[HistoryEntry]
