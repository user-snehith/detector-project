#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Train models on PhiUSIIL dataset - optimized for speed."""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_auc_score
from joblib import dump
import time


def main():
    # Load and sample dataset
    print("Loading dataset...")
    df = pd.read_csv("data/PhiUSIIL_Phishing_URL_Dataset.csv")
    
    # Using 100K sample for balanced speed/accuracy
    sample_size = 100000
    if len(df) > sample_size:
        print("Sampling %d from %d total records..." % (sample_size, len(df)))
        df, _ = train_test_split(df, train_size=sample_size, random_state=42, stratify=df["label"])
    
    print("Dataset shape: %d x %d" % df.shape)
    print("Class distribution:")
    for label, count in df['label'].value_counts().items():
        print("  Label %d: %d" % (label, count))
    
    # Prepare features
    exclude_cols = ["FILENAME", "URL", "Domain", "TLD", "Title", "label"]
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols].values
    y = df["label"].values
    
    # Handle NaN
    X = np.nan_to_num(X, nan=0.0)
    
    print("\nFeatures extracted: %d" % len(feature_cols))
    print("Feature matrix: %d x %d" % X.shape)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("\nTraining set: %d samples" % X_train.shape[0])
    print("Testing set: %d samples" % X_test.shape[0])
    
    # Train Random Forest (best balance of speed and accuracy)
    print("\n" + "="*60)
    print("TRAINING RANDOM FOREST CLASSIFIER")
    print("="*60)
    
    start = time.time()
    rf = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            n_jobs=-1,
            random_state=42,
            verbose=2
        )),
    ])
    
    print("Fitting model...")
    rf.fit(X_train, y_train)
    
    elapsed = time.time() - start
    print("Training completed in %.1f seconds" % elapsed)
    
    # Evaluate
    print("\nEvaluating on test set...")
    y_pred = rf.predict(X_test)
    y_proba = rf.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    print("\nPERFORMANCE METRICS")
    print("-"*60)
    print("Accuracy: %.4f" % accuracy)
    print("AUC Score: %.4f" % auc)
    
    # Classification report
    print("\nCLASSIFICATION REPORT")
    print("-"*60)
    print(classification_report(y_test, y_pred, target_names=["Legitimate (0)", "Phishing (1)"]))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nCONFUSION MATRIX")
    print("-"*60)
    print("True Negatives (TN):  %d" % cm[0,0])
    print("False Positives (FP): %d" % cm[0,1])
    print("False Negatives (FN): %d" % cm[1,0])
    print("True Positives (TP):  %d" % cm[1,1])
    
    specificity = cm[0,0] / (cm[0,0] + cm[0,1])
    sensitivity = cm[1,1] / (cm[1,1] + cm[1,0])
    print("\nSpecificity (True Negative Rate): %.4f" % specificity)
    print("Sensitivity (True Positive Rate): %.4f" % sensitivity)
    
    # Save model
    print("\n" + "="*60)
    Path("models").mkdir(exist_ok=True)
    model_data = {
        "pipeline": rf,
        "model_name": "RandomForest",
        "accuracy": accuracy,
        "auc": auc,
        "dataset": "PhiUSIIL",
    }
    dump(model_data, "models/sklearn_model.joblib")
    print("Model saved: models/sklearn_model.joblib")
    print("="*60)
    print("\nTRAINING SUCCESSFULLY COMPLETED!")


if __name__ == "__main__":
    main()
