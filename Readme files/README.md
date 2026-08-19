# AI-Based URL Phishing Detector with Chrome Extension

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-orange.svg)](https://developer.chrome.com/docs/extensions/)

An intelligent phishing URL detection system with machine learning and real-time browser protection.

## ✨ Features

### 🔍 Advanced Detection
- **28+ URL Features**: Comprehensive analysis including length, entropy, character patterns
- **Homograph Detection**: Identifies lookalike domains (g00gle, amaz0n, rnicrosoft)
- **Machine Learning**: Scikit-learn and TensorFlow/Keras models
- **Real-time Analysis**: <100ms per URL check

### 🌐 Chrome Extension
- **Automatic Link Monitoring**: Intercepts all link clicks
- **Safe Browsing**: Shows warnings for suspicious URLs
- **Seamless Integration**: Works with Streamlit web interface
- **Privacy-First**: Local analysis, no external API calls

### 📊 Web Interface
- **Single URL Check**: Manual URL analysis
- **Batch Processing**: CSV upload for bulk analysis
- **Visual Results**: Charts and risk indicators
- **Model Training**: Train new ML models

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
# Clone and setup everything automatically
python setup_extension.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Train model (optional - uses pre-trained if available)
python main.py train --model sklearn

# Start web interface
streamlit run frontend/app.py

# Install Chrome extension (see below)
```

## 🛠️ Chrome Extension Installation

1. **Run Setup Script**:
   ```bash
   python setup_extension.py
   ```

2. **Manual Installation**:
   - Open Chrome → `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select `chrome_extension/` folder

3. **Verify Installation**:
   - Extension icon appears in toolbar
   - Click icon to open settings
   - Test by clicking links on any website

## 📁 Project Structure

```
phishing_detector_v2/
├── src/                          # Core detection engine
│   ├── detector.py              # Main phishing detector
│   ├── feature_extractor.py     # URL feature extraction
│   ├── model_trainer.py         # ML model training
│   └── phiusiil_extractor.py    # Advanced features
├── frontend/
│   └── app.py                   # Streamlit web interface
├── chrome_extension/            # Chrome extension files
│   ├── manifest.json           # Extension configuration
│   ├── background.js           # Background service worker
│   ├── content.js              # Link interception script
│   ├── popup.html/js           # Extension popup UI
│   └── icons/                  # Extension icons
├── models/                      # Trained ML models
├── data/                        # Training datasets
├── tests/                       # Unit tests
├── main.py                      # CLI interface
├── setup_extension.py           # Automated setup
└── requirements.txt             # Python dependencies
```

## 🎯 How It Works

### Link Click Protection
1. **User clicks link** → Extension intercepts click
2. **URL analysis** → Local ML model analyzes URL features
3. **Risk assessment** → Homograph detection + pattern analysis
4. **User decision** → Show results, let user proceed or cancel
5. **Safe navigation** → Only allow safe links

### Detection Features
- **URL Structure**: Length, special characters, entropy
- **Domain Analysis**: IP detection, subdomain depth, TLD risk
- **Suspicious Patterns**: Token detection, double slashes, shorteners
- **Homograph Attacks**: Character substitution detection (0→O, 1→I, etc.)
- **Advanced Patterns**: Redirect chains, parameter analysis

## 🔧 Configuration

### Extension Settings
- **Enable/Disable**: Turn monitoring on/off
- **Detector URL**: Custom server URL (default: localhost:8501)
- **Auto-redirect**: Automatically check suspicious links
- **Show Warnings**: Display phishing alerts

### Model Training
```bash
# Train Scikit-Learn model
python main.py train --model sklearn --data data/url_dataset.csv

# Train Keras model
python main.py train --model keras --epochs 20
```

## 📈 Performance

- **Accuracy**: 85-94% depending on model type
- **Speed**: <100ms per URL analysis
- **Memory**: ~50MB for models + extension
- **Privacy**: 100% local processing

## 🧪 Testing

### Test Homograph Detection
```bash
python test_homograph.py
```

### Test Extension
```bash
# Start detector
streamlit run frontend/app.py

# Test URLs in browser with extension enabled
# Try: https://g00gle.com, https://amaz0n.com, etc.
```

### CLI Testing
```bash
# Single URL check
python main.py check "https://suspicious-site.com"

# Batch analysis
python main.py batch urls.csv --output results.csv
```

## 🔒 Security & Privacy

- **Local Processing**: All analysis happens on your machine
- **No Data Collection**: URLs are not sent to external servers
- **Offline Capable**: Works without internet for basic checks
- **Open Source**: Transparent detection algorithms

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PhiUSIIL Dataset**: For training data
- **Scikit-learn**: Machine learning framework
- **TensorFlow/Keras**: Neural network support
- **Streamlit**: Web interface framework
- **Chrome Extensions**: Browser integration

## 🆘 Troubleshooting

### Extension Not Working
- Ensure detector server is running on port 8501
- Check extension is enabled in `chrome://extensions/`
- Try refreshing the page

### Model Training Issues
- Check dataset format (url,label columns)
- Ensure sufficient RAM for large datasets
- Try with smaller batch sizes

### Performance Issues
- Use Scikit-Learn model for faster inference
- Reduce model complexity for older hardware
- Check system resources

---

**Made with ❤️ for safer browsing**

*Detect phishing URLs before they detect you!* 🛡️
