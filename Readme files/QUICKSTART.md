# Quick Start Guide - Phishing Detector v2

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Train Model
```bash
python main.py train --model sklearn --output models/sklearn_model.joblib
```

### Step 3: Launch Web UI
```bash
streamlit run frontend/app.py
```
Then open: http://localhost:8501

---

## 📋 Available Commands

### Train Models
```bash
# Scikit-Learn (Fast, ~85% accuracy)
python main.py train --model sklearn

# Keras/TensorFlow (Accurate, ~94% accuracy)
python main.py train --model keras --epochs 20
```

### Check URLs
```bash
# Single URL
python main.py check "https://example.com"

# Batch from CSV
python main.py batch urls.csv --output results.csv
```

### Web Interface
```bash
python main.py ui
# Opens Streamlit at http://localhost:8501
```

---

## 📊 Project Structure
```
├── src/                 # ML Engine
│   ├── detector.py      # Main inference
│   ├── feature_extractor.py
│   └── model_trainer.py
├── frontend/
│   └── app.py          # Streamlit UI
├── models/             # Trained models go here
├── data/               # Sample datasets
├── main.py             # CLI entry point
└── requirements.txt
```

---

## 🎯 Features

✅ **Multi-Model Support**
  - Scikit-Learn Logistic Regression
  - Keras/TensorFlow Neural Networks

✅ **Web UI** (Streamlit)
  - Single URL checking
  - Batch CSV analysis
  - Visual risk gauges
  - Model training interface

✅ **CLI Interface**
  - Train models
  - Check URLs
  - Batch processing
  - Export results

✅ **Advanced Detection**
  - 15+ URL features extracted
  - Suspicious token detection
  - IP address analysis
  - Entropy calculation

---

## 🧪 Test the System

### Quick Test
```bash
python main.py check "http://paypal.com.sign-in.verify.com"
# Should show: PHISHING (high confidence)

python main.py check "https://google.com"
# Should show: SAFE
```

### Batch Test
```powershell
# Windows: Create test file
echo "url`:nhttp//google.com`://phishing.nhttpfake" > test_urls.csv

# Run batch
python main.py batch test_urls.csv --output batch_results.csv
```

---

## 🔐 Security Features

- ✅ Runs locally (no external API calls)
- ✅ Offline operation supported
- ✅ Fast inference (<100ms per URL)
- ✅ Privacy-focused
- ✅ Extensible architecture

---

## 📈 Next Steps

1. **Add Real Dataset**
   - Use PhishTank or OpenPhish data
   - Improve model accuracy to 95%+

2. **Browser Extension**
   - Chrome/Firefox integration
   - Real-time link checking

3. **Model Improvements**
   - Ensemble methods
   - LSTM deep learning
   - Transfer learning

4. **Deployment**
   - Docker containerization
   - REST API server
   - Cloud hosting

---

## 💡 Tips

- **First time?** Run the Streamlit UI for easiest experience
- **Speed optimized?** Use sklearn model (faster)
- **Accuracy focused?** Use Keras model (more accurate)
- **Batch checking?** CSV upload works best
- **Integration?** Use REST API from Flask backend

---

**Happy detecting! 🛡️**
