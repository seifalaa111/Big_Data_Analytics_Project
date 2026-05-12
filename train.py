"""
train.py - Local Model Training (alternative to Colab notebook)
Trains the XGBoost model with SMOTE and saves model.pkl.
Run this only if you prefer training locally instead of Colab.
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, average_precision_score, f1_score
import joblib

DATA_PATH = "creditcard.csv"
MODEL_PATH = "model.pkl"


def main():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)

    X = df.drop("Class", axis=1)
    y = df["Class"]
    print(f"Dataset: {X.shape[0]} rows, {X.shape[1]} features")
    print(f"Fraud: {y.sum()} ({y.mean()*100:.3f}%)\n")

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # SMOTE
    print("Applying SMOTE...")
    smote = SMOTE(sampling_strategy=0.1, random_state=42)
    X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
    print(f"After SMOTE: {X_train_sm.shape[0]} samples ({y_train_sm.sum()} fraud)\n")

    # Train
    print("Training XGBoost...")
    model = xgb.XGBClassifier(
        n_estimators=150, max_depth=5, learning_rate=0.1,
        random_state=42, eval_metric="aucpr", n_jobs=-1
    )
    model.fit(X_train_sm, y_train_sm)

    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    auprc = average_precision_score(y_test, y_proba)
    f1 = f1_score(y_test, y_pred)

    print(f"\nAUPRC:    {auprc:.4f}")
    print(f"F1-Score: {f1:.4f}\n")
    print(classification_report(y_test, y_pred))

    # Save
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
