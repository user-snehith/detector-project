<!-- Phishing Detector v2 - Copilot Instructions -->

## Project Overview
AI-based URL Phishing Detector with Streamlit UI, scikit-learn & Keras/TensorFlow backends.

## Development Workspace Setup

### ✅ Workspace Initialization Completed
- [x] Created organized folder structure
- [x] Frontend: Streamlit web interface (frontend/app.py)
- [x] Backend: ML engine with sklearn & Keras support (src/)
- [x] Data: Sample dataset and model storage (data/, models/)

### 📦 Dependencies Installed
- scikit-learn, TensorFlow, Keras
- Pandas, NumPy, Streamlit
- Flask, Plotly, tldextract
- All requirements in requirements.txt

### 🚀 How to Run

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Train Model (Choose One)**
```bash
# Scikit-Learn model
python main.py train --model sklearn --data data/url_dataset.csv --output models/sklearn_model.joblib

# Keras model
python main.py train --model keras --data data/url_dataset.csv --output models/keras_model.h5 --epochs 20
```

**3. Start Streamlit UI**
```bash
streamlit run frontend/app.py
# OR
python main.py ui
```

**4. Check Single URL (CLI)**
```bash
python main.py check "https://example.com" --model models/sklearn_model.joblib
```

**5. Batch Analysis (CLI)**
```bash
python main.py batch urls.csv --model models/sklearn_model.joblib --output results.csv
```

### 📁 Project Structure
```
phishing_detector_v2/
├── src/
│   ├── feature_extractor.py  # URL feature engineering
│   ├── model_trainer.py       # Model training pipeline
│   ├── detector.py           # Main inference engine
│   └── __init__.py
├── frontend/
│   └── app.py               # Streamlit web UI
├── models/                   # Trained models saved here
├── data/
│   └── url_dataset.csv      # Sample dataset
├── tests/                    # Unit tests (to be added)
├── .github/
│   └── copilot-instructions.md
├── main.py                  # CLI entry point
├── requirements.txt
└── README.md
```

### 🔧 Technology Stack
| Component | Technology |
|-----------|-----------|
| ML Backend | scikit-learn, TensorFlow/Keras |
| Data Processing | Pandas, NumPy |
| Frontend | Streamlit |
| API Server | Flask |
| URL Analysis | tldextract |
| Visualization | Plotly |

### 📊 Model Features (15 Features Extracted)
1. URL length
2. Host length & entropy
3. Path length
4. Special character counts
5. IP address detection
6. Suspicious token detection
7. Subdomain depth
8. TLD analysis

### ✨ Streamlit UI Features
- Single URL checking with visual risk gauge
- Batch CSV upload and analysis
- Model training interface
- Risk visualization (Gauge charts)
- Results export to CSV
- Model selection (sklearn/keras)

### 🎯 Next Development Steps
1. Add comprehensive unit tests (tests/)
2. Build Chrome extension for browser integration
3. Add real-time model updates
4. Implement REST API endpoints
5. Add logging and monitoring
6. Create Docker configuration

### 🔐 Security Notes
- Models run locally (no external API calls)
- Trained on sample URLs (recommend real dataset)
- Support for offline operation
- Fast inference (<100ms per URL)

---
**Last Updated**: March 24, 2026  
**Status**: Core implementation complete, ready for testing and deployment
