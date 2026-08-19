"""
Flask REST API server for phishing detector.
"""
from flask import Flask, jsonify, request
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src import PhishingDetector

app = Flask(__name__)

# Load detector
try:
    detector = PhishingDetector("models/sklearn_model.joblib", "sklearn")
except FileNotFoundError:
    print("Warning: Model not found. Please train a model first.")
    detector = None


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "Phishing Detector API",
        "model_loaded": detector is not None
    })


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Predict if URL is phishing."""
    if detector is None:
        return jsonify({"error": "Model not loaded"}), 503
    
    # Get URL from query param or JSON body
    if request.method == 'GET':
        url = request.args.get('url', '')
    else:
        data = request.get_json() or {}
        url = data.get('url', '')
    
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    try:
        result = detector.predict(url)
        return jsonify({
            "url": result['url'],
            "is_phishing": result['is_phishing'],
            "confidence": result['confidence'],
            "risk_level": result['risk_level'],
            "model_type": result['model_type']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Predict multiple URLs."""
    if detector is None:
        return jsonify({"error": "Model not loaded"}), 503
    
    data = request.get_json() or {}
    urls = data.get('urls', [])
    
    if not urls or not isinstance(urls, list):
        return jsonify({"error": "URLs list is required"}), 400
    
    try:
        results = detector.predict_batch(urls)
        phishing_count = sum(1 for r in results if r['is_phishing'])
        
        return jsonify({
            "total": len(results),
            "phishing": phishing_count,
            "safe": len(results) - phishing_count,
            "predictions": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/model/info', methods=['GET'])
def model_info():
    """Get model information."""
    if detector is None:
        return jsonify({"error": "Model not loaded"}), 503
    
    return jsonify({
        "model_type": detector.model_type,
        "model_path": detector.model_path,
        "status": "ready"
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/health (GET)",
            "/predict (GET, POST)",
            "/predict/batch (POST)",
            "/model/info (GET)"
        ]
    }), 404


if __name__ == '__main__':
    port = 5000
    print(f"\n🚀 Starting Phishing Detector API Server")
    print(f"📡 Server: http://127.0.0.1:{port}")
    print(f"\n📚 Available Endpoints:")
    print(f"  GET  /health - Health check")
    print(f"  GET  /predict?url=<URL> - Predict single URL")
    print(f"  POST /predict - Predict with JSON body")
    print(f"  POST /predict/batch - Predict multiple URLs")
    print(f"  GET  /model/info - Model information")
    print(f"\n💡 Example:")
    print(f"  curl 'http://127.0.0.1:5000/predict?url=https://example.com'")
    print(f"\n")
    
    app.run(host='127.0.0.1', port=port, debug=False)
