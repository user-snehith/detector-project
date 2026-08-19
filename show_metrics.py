#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Show detailed test results and metrics for trained model."""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_auc_score, precision_recall_fscore_support
from joblib import load
import time


def load_model_metrics():
    """Load trained model and show its metrics."""
    model_path = "models/sklearn_model.joblib"

    if not Path(model_path).exists():
        print("❌ No trained model found at models/sklearn_model.joblib")
        print("Please run training first: python train_final.py")
        return

    print("Loading trained model...")
    model_data = load(model_path)

    print("\n" + "="*80)
    print("MODEL EVALUATION RESULTS")
    print("="*80)

    print(f"Model Type: {model_data.get('model_name', 'Unknown')}")
    print(f"Dataset: {model_data.get('dataset', 'Unknown')}")
    print(".4f")
    print(".4f")

    # Load test data for detailed metrics
    print("\nLoading test dataset for detailed evaluation...")
    df = pd.read_csv("data/PhiUSIIL_Phishing_URL_Dataset.csv")

    # Use same sampling as training
    sample_size = 100000
    if len(df) > sample_size:
        df, _ = train_test_split(df, train_size=sample_size, random_state=42, stratify=df["label"])

    # Prepare features
    exclude_cols = ["FILENAME", "URL", "Domain", "TLD", "Title", "label"]
    feature_cols = [col for col in df.columns if col not in exclude_cols]

    X = df[feature_cols].values
    y = df["label"].values
    X = np.nan_to_num(X, nan=0.0)

    # Split same as training
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Test set: {X_test.shape[0]} samples")

    # Get predictions
    print("\nGenerating predictions...")
    start = time.time()
    y_pred = model_data['pipeline'].predict(X_test)
    y_proba = model_data['pipeline'].predict_proba(X_test)[:, 1]
    pred_time = time.time() - start

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)

    precision, recall, f1, support = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average='macro')

    print("\n" + "-"*80)
    print("OVERALL PERFORMANCE METRICS")
    print("-"*80)
    print(".4f")
    print(".4f")
    print(".4f")
    print(".4f")
    print(".4f")
    print(".4f")
    print(".2f")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\n" + "-"*80)
    print("CONFUSION MATRIX")
    print("-"*80)
    print("Predicted →     Legitimate (0)    Phishing (1)")
    print("Actual ↓")
    print("Legitimate (0)     %6d         %6d" % (cm[0,0], cm[0,1]))
    print("Phishing (1)       %6d         %6d" % (cm[1,0], cm[1,1]))

    # Calculate rates
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

    print("\nError Rates:")
    print(".4f")
    print(".4f")
    print(".4f")
    print(".4f")

    # Detailed Classification Report
    print("\n" + "-"*80)
    print("DETAILED CLASSIFICATION REPORT")
    print("-"*80)
    print(classification_report(y_test, y_pred, target_names=["Legitimate (0)", "Phishing (1)"]))

    # Per-class metrics
    print("\n" + "-"*80)
    print("PER-CLASS PERFORMANCE")
    print("-"*80)

    precision_0, recall_0, f1_0, _ = precision_recall_fscore_support(y_test, y_pred, average=None)
    print("Legitimate URLs (Class 0):")
    print(".4f")
    print(".4f")
    print(".4f")

    print("\nPhishing URLs (Class 1):")
    print(".4f")
    print(".4f")
    print(".4f")

    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    load_model_metrics()
