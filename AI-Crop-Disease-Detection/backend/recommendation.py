"""
recommendation.py
=================
Retrieves disease treatment recommendations from the disease knowledge base (JSON).
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from schemas import DiseaseRecommendation, DiseaseEntry

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH  = BASE_DIR / "disease_database.json"

# ── Load DB once at module import ─────────────────────────────────────────────
_disease_db: Dict[str, Any] = {}


def load_disease_database() -> None:
    """Load the JSON knowledge base into memory."""
    global _disease_db
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Disease database not found: {DB_PATH}")
    with open(DB_PATH, encoding="utf-8") as f:
        _disease_db = json.load(f)
    log.info(f"✅ Disease database loaded: {len(_disease_db)} entries.")


def get_recommendation(disease_name: str) -> DiseaseRecommendation:
    """
    Fetch the treatment recommendation for a given disease class name.
    Falls back to a generic response if the disease is not found in the DB.

    Args:
        disease_name: PlantVillage class label, e.g. "Tomato___Early_blight"

    Returns:
        DiseaseRecommendation with description, pesticide, organic_solution, prevention.
    """
    if not _disease_db:
        load_disease_database()

    # Direct lookup
    entry = _disease_db.get(disease_name)

    # Fuzzy fallback: match by disease name fragment
    if entry is None:
        for key, val in _disease_db.items():
            if disease_name.lower() in key.lower() or key.lower() in disease_name.lower():
                entry = val
                break

    if entry is None:
        log.warning(f"Disease '{disease_name}' not found in database. Using generic response.")
        return DiseaseRecommendation(
            description=(
                f"No specific information available for '{disease_name}'. "
                "Consult your local agricultural extension office."
            ),
            pesticide="Consult a local agronomist for specific pesticide recommendations.",
            organic_solution="Neem oil spray, copper-based fungicide, and crop rotation are generally effective.",
            prevention=[
                "Regular field scouting",
                "Good sanitation practices",
                "Crop rotation",
                "Use of certified disease-free planting material",
            ],
        )

    return DiseaseRecommendation(
        description=entry.get("description", ""),
        pesticide=entry.get("pesticide", ""),
        organic_solution=entry.get("organic_solution", ""),
        prevention=entry.get("prevention", []),
    )


def get_all_diseases() -> List[DiseaseEntry]:
    """
    Return all disease entries in the knowledge base as a list.
    """
    if not _disease_db:
        load_disease_database()

    diseases = []
    for name, data in _disease_db.items():
        diseases.append(
            DiseaseEntry(
                name=name,
                description=data.get("description", ""),
                pesticide=data.get("pesticide", ""),
                organic_solution=data.get("organic_solution", ""),
                prevention=data.get("prevention", []),
            )
        )
    return sorted(diseases, key=lambda d: d.name)
