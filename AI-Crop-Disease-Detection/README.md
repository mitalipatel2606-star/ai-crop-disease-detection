# 🌿 CropGuard AI — Crop Disease Detection & Smart Recommendation System

<p align="center">
  <img src="https://img.shields.io/badge/TensorFlow-2.13-FF6F00?logo=tensorflow&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.103-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/MobileNetV2-Transfer%20Learning-22C55E" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" />
</p>

An end-to-end AI-powered system that detects plant diseases from leaf images and recommends targeted treatments. Built with **MobileNetV2 transfer learning**, **FastAPI**, and **React**, with **Grad-CAM** explainability.

---

## 📸 Features

| Feature | Description |
|---------|-------------|
| 🔬 Disease Detection | MobileNetV2 model trained on 54,000+ PlantVillage images |
| 📊 Confidence Scores | Top-5 predictions with probability scores |
| 🧠 Explainable AI | Grad-CAM heatmaps highlight infected leaf regions |
| 💊 Pesticide Recommendations | Specific chemical treatments per disease |
| 🌿 Organic Solutions | Eco-friendly alternatives (neem oil, copper sprays etc.) |
| 🛡️ Preventive Practices | Agronomic best practices to prevent future outbreaks |
| 📜 Prediction History | SQLite-backed history of all past scans |
| 🐳 Docker Ready | One-command deployment with Docker Compose |

---

## 🏗️ Project Structure

```
AI-Crop-Disease-Detection/
├── dataset/              # Raw & processed PlantVillage images
├── ml/
│   ├── download_dataset.py   # Auto-download from Kaggle
│   ├── preprocess.py         # Resize, augment, train/val/test split
│   ├── train_mobilenet.py    # Transfer learning (MobileNetV2)
│   ├── train_custom_cnn.py   # Baseline custom CNN
│   ├── evaluate.py           # Metrics, confusion matrix, plots
│   ├── gradcam.py            # Grad-CAM visualisation (CLI)
│   └── class_names.json      # 38-class label mapping
├── models/               # Saved .h5 model weights
├── backend/
│   ├── main.py               # FastAPI app
│   ├── model_loader.py       # Singleton model cache
│   ├── predict.py            # Inference pipeline
│   ├── gradcam_service.py    # Server-side Grad-CAM
│   ├── recommendation.py     # Knowledge base lookup
│   ├── history.py            # SQLite prediction history
│   ├── schemas.py            # Pydantic models
│   └── disease_database.json # 38 disease treatments
├── frontend/             # React 18 app
├── docker/               # Dockerfiles + docker-compose
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start (Local)

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) Kaggle API key for dataset download
- (Optional) Docker + Docker Compose

---

### Step 1 — Clone & Install

```bash
git clone https://github.com/yourusername/AI-Crop-Disease-Detection.git
cd AI-Crop-Disease-Detection

# Python environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### Step 2 — Download Dataset

> Requires a [Kaggle API key](https://www.kaggle.com/account). Place `kaggle.json` at `~/.kaggle/kaggle.json`

```bash
python ml/download_dataset.py
```

Or download manually from [Kaggle PlantVillage](https://www.kaggle.com/datasets/emmarex/plantdisease) and extract to `dataset/raw/`.

---

### Step 3 — Preprocess Data

```bash
python ml/preprocess.py
```

This resizes all images to 224×224, applies augmentation (rotation, flip, brightness, zoom), and splits into train/val/test.

---

### Step 4 — Train Models

**Option A — MobileNetV2 (Recommended, faster, higher accuracy)**
```bash
python ml/train_mobilenet.py
```

**Option B — Custom CNN (Baseline)**
```bash
python ml/train_custom_cnn.py
```

Models are saved to `models/`. Training takes ~30–60 min with GPU.

---

### Step 5 — Evaluate

```bash
python ml/evaluate.py --model mobilenet
# or
python ml/evaluate.py --model custom_cnn
```

Generates accuracy/loss plots and confusion matrix in `outputs/plots/`.

---

### Step 6 — Start Backend API

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API available at: **`http://localhost:8000`**  
Interactive docs: **`http://localhost:8000/docs`**

---

### Step 7 — Start Frontend

```bash
cd frontend
npm install
npm start
```

App available at: **`http://localhost:3000`**

---

## 🐳 Docker Deployment (One Command)

```bash
# Build and start both services
docker compose -f docker/docker-compose.yml up --build

# Frontend → http://localhost:3000
# Backend  → http://localhost:8000
```

> **Note:** Mount your trained model before starting Docker:
> ```bash
> # Ensure models/crop_disease_mobilenet.h5 exists
> docker compose -f docker/docker-compose.yml up --build
> ```

---

## 📡 API Reference

### `POST /predict`

Upload a leaf image and get disease prediction.

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/leaf.jpg"
```

**Response:**
```json
{
  "disease": "Tomato___Early_blight",
  "confidence": 0.9421,
  "top_predictions": [
    { "class": "Tomato___Early_blight", "confidence": 0.9421 },
    { "class": "Tomato___Target_Spot",  "confidence": 0.0312 }
  ],
  "recommendation": {
    "description": "Early blight is caused by Alternaria solani...",
    "pesticide": "Chlorothalonil, Mancozeb applied every 7–10 days",
    "organic_solution": "Neem oil spray every 7 days",
    "prevention": ["Mulch around plants", "Avoid overhead irrigation"]
  },
  "heatmap_base64": "<base64 PNG string>",
  "warning": null,
  "model_version": "MobileNetV2_CropDisease"
}
```

---

### `GET /diseases`

Browse the full disease knowledge base.

```bash
curl http://localhost:8000/diseases
```

---

### `GET /history`

Retrieve prediction history (paginated).

```bash
curl "http://localhost:8000/history?limit=20&offset=0"
```

---

### `GET /health`

Health check / readiness probe.

```bash
curl http://localhost:8000/health
```

---

## 🤖 Model Details

| Property | MobileNetV2 | Custom CNN |
|----------|-------------|------------|
| Architecture | Transfer learning | Built from scratch |
| Base | MobileNetV2 (ImageNet) | 4× Conv blocks |
| Training phases | 2 (freeze → fine-tune) | 1 |
| Input size | 224 × 224 | 224 × 224 |
| Output classes | 38 | 38 |
| Training epochs | 5 + 15 | 20 |
| Expected accuracy | ~96% | ~88% |
| Model size | ~14 MB | ~45 MB |

### Grad-CAM (Explainability)

Generate Grad-CAM for any image from the command line:

```bash
python ml/gradcam.py --image path/to/leaf.jpg --model mobilenet --output outputs/plots/my_gradcam.png
```

---

## 📊 Dataset

| Property | Value |
|----------|-------|
| Source | [PlantVillage (Kaggle)](https://www.kaggle.com/datasets/emmarex/plantdisease) |
| Total Images | ~54,300 |
| Classes | 38 (26 diseases + 12 healthy) |
| Crops | Tomato, Potato, Corn, Apple, Grape, Pepper, Peach, Cherry, Strawberry, Orange, Soybean, Squash, Blueberry, Raspberry |
| Image Size | 224 × 224 (after preprocessing) |
| Split | 70% train / 15% val / 15% test |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| ML Framework | TensorFlow 2.13 / Keras |
| Model | MobileNetV2 (ImageNet pre-trained) |
| Explainability | Grad-CAM |
| Backend | FastAPI + Pydantic |
| Data Validation | SQLAlchemy + SQLite |
| Frontend | React 18, React Router v6 |
| HTTP Client | Axios |
| File Upload | react-dropzone |
| Notifications | react-hot-toast |
| Containerisation | Docker + Docker Compose |

---

## 📁 Generated Outputs

```
outputs/
├── plots/
│   ├── mobilenet_training_curves.png     # Accuracy & loss curves
│   ├── mobilenet_confusion_matrix.png    # Normalised confusion matrix
│   └── gradcam_result.png               # Sample Grad-CAM
└── reports/
    └── mobilenet_evaluation_report.txt  # Full classification report
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🌾 Acknowledgements

- [PlantVillage Dataset](https://plantvillage.psu.edu/) — Penn State University
- [MobileNetV2](https://arxiv.org/abs/1801.04381) — Google Research
- [Grad-CAM](https://arxiv.org/abs/1610.02391) — Selvaraju et al.

---

*Built with ❤️ for sustainable precision agriculture.*
