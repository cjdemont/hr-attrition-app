# =============================================================================
# model/train_model.py
# Run this script ONCE to train the model and save it as attrition_model.pkl
# The app loads the pkl at runtime — no training happens in the live app.
#
# Usage:  python model/train_model.py
# Output: model/attrition_model.pkl
# =============================================================================

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# --- Paths ---
DATA_PATH  = Path("data/ibm_hr_attrition.csv")
MODEL_PATH = Path("model/attrition_model.pkl")

# --- The 10 features selected for the model ---
# Chosen for predictive power AND interpretability for an HR audience
FEATURES = [
    "OverTime",              # Yes/No — strongest single predictor
    "StockOptionLevel",      # 0-3 — financial tie to company
    "YearsAtCompany",        # Continuous — tenure
    "NumCompaniesWorked",    # Continuous — job-hopping history
    "JobSatisfaction",       # 1-4 — survey score
    "TrainingTimesLastYear", # Continuous — investment signal
    "JobLevel",              # 1-5 — seniority
    "WorkLifeBalance",       # 1-4 — survey score
    "MonthlyIncome",         # Continuous — compensation
    "YearsSinceLastPromotion", # Continuous — career momentum
]

CATEGORICAL = ["OverTime"]
NUMERIC     = [f for f in FEATURES if f not in CATEGORICAL]
TARGET      = "Attrition"


def load_and_prepare(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df[TARGET] = (df[TARGET] == "Yes").astype(int)
    return df


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OrdinalEncoder(), CATEGORICAL),
            ("num", "passthrough", NUMERIC),
        ]
    )
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=5,
        class_weight="balanced",   # handles the ~16% attrition imbalance
        random_state=42,
        n_jobs=-1,
    )
    return Pipeline([("preprocessor", preprocessor), ("classifier", clf)])


def train():
    print("Loading data...")
    df = load_and_prepare(DATA_PATH)

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print("Training Random Forest (300 trees)...")
    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    print("\nEvaluation on held-out test set:")
    y_pred = pipe.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["Stay", "Attrite"]))

    # Save model + metadata the app will need
    artifact = {
        "pipeline": pipe,
        "features": FEATURES,
        "categorical": CATEGORICAL,
        "numeric": NUMERIC,
        "target": TARGET,
    }
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
