#!/usr/bin/env python
"""CLI entry point for phishing detector."""

import argparse
import sys
from pathlib import Path

from src import PhishingDetector, ModelTrainer


def main():
    parser = argparse.ArgumentParser(description="AI-based URL Phishing Detector")
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    
    # Train command
    train_p = subparsers.add_parser("train", help="Train model")
    train_p.add_argument("--model", choices=["sklearn", "keras"], default="sklearn",
                        help="Model type to train")
    train_p.add_argument("--data", type=str, default=None,
                        help="CSV file with url,label columns")
    train_p.add_argument("--output", type=str,
                        help="Output model path")
    train_p.add_argument("--epochs", type=int, default=20,
                        help="Epochs for Keras training")
    
    # Check command
    check_p = subparsers.add_parser("check", help="Check single URL")
    check_p.add_argument("url", type=str, help="URL to check")
    check_p.add_argument("--model", type=str, default="models/sklearn_model.joblib",
                        help="Path to trained model")
    check_p.add_argument("--model-type", choices=["sklearn", "keras"], default="sklearn")
    
    # Batch check command
    batch_p = subparsers.add_parser("batch", help="Check multiple URLs from CSV")
    batch_p.add_argument("csv_file", type=str, help="CSV file with URL column")
    batch_p.add_argument("--model", type=str, default="models/sklearn_model.joblib")
    batch_p.add_argument("--model-type", choices=["sklearn", "keras"], default="sklearn")
    batch_p.add_argument("--output", type=str, help="Output CSV file")
    
    # Streamlit command
    streamlit_p = subparsers.add_parser("ui", help="Start Streamlit web interface")
    streamlit_p.add_argument("--port", type=int, default=8501)
    streamlit_p.add_argument("--host", type=str, default="localhost")
    
    args = parser.parse_args()
    
    # Train
    if args.cmd == "train":
        print(f"Training {args.model.upper()} model...")
        output = args.output
        
        if args.model == "sklearn":
            if not output:
                output = "models/sklearn_model.joblib"
            result = ModelTrainer.train_sklearn_model(
                data_path=args.data,
                output_path=output
            )
            print(f"\n✅ Model saved to: {result['path']}")
            print(f"Accuracy: {result['accuracy']:.4f}\n")
            print(result['report'])
        
        elif args.model == "keras":
            if not output:
                output = "models/keras_model.h5"
            result = ModelTrainer.train_keras_model(
                data_path=args.data,
                output_path=output,
                epochs=args.epochs
            )
            print(f"\n✅ Model saved to: {result['path']}")
            print(f"Accuracy: {result['accuracy']:.4f}")
    
    # Check
    elif args.cmd == "check":
        print(f"Checking: {args.url}")
        
        if not Path(args.model).exists():
            print(f"❌ Model not found: {args.model}")
            sys.exit(1)
        
        detector = PhishingDetector(args.model, args.model_type)
        result = detector.predict(args.url)
        
        status = "🚨 PHISHING" if result['is_phishing'] else "✅ SAFE"
        print(f"\nStatus: {status}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Risk Level: {result['risk_level'].upper()}")
    
    # Batch
    elif args.cmd == "batch":
        import pandas as pd
        
        if not Path(args.csv_file).exists():
            print(f"❌ File not found: {args.csv_file}")
            sys.exit(1)
        
        if not Path(args.model).exists():
            print(f"❌ Model not found: {args.model}")
            sys.exit(1)
        
        print(f"Processing batch: {args.csv_file}")
        df = pd.read_csv(args.csv_file)
        
        if 'url' not in df.columns:
            print("❌ CSV must have 'url' column")
            sys.exit(1)
        
        detector = PhishingDetector(args.model, args.model_type)
        results = detector.predict_batch(df['url'].tolist())
        
        results_df = pd.DataFrame(results)
        phishing_count = results_df['is_phishing'].sum()
        
        print(f"\n📊 Results:")
        print(f"Total URLs: {len(results_df)}")
        print(f"🚨 Phishing: {phishing_count}")
        print(f"✅ Safe: {len(results_df) - phishing_count}")
        print(f"Phishing Rate: {phishing_count/len(results_df)*100:.1f}%")
        
        if args.output:
            results_df.to_csv(args.output, index=False)
            print(f"\n✅ Results saved to: {args.output}")
        else:
            print("\nDetailed Results:")
            print(results_df.to_string())
    
    # UI
    elif args.cmd == "ui":
        import subprocess
        cmd = [
            "streamlit", "run", "frontend/app.py",
            "--server.port", str(args.port),
            "--server.address", args.host
        ]
        print(f"Starting Streamlit app on {args.host}:{args.port}...")
        print("Open browser to http://localhost:8501\n")
        subprocess.run(cmd)


if __name__ == "__main__":
    main()
