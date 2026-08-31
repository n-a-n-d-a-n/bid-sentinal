"""
Procurement Anomaly IsolationForest Model Training Script.

Trains scikit-learn IsolationForest on synthetic procurement observations and saves model artifacts to models/procurement_anomaly/.
"""
import os
import json
import pickle
import numpy as np

from generate_training_data import generate_synthetic_dataset

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "procurement_anomaly")

def train_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    dataset_path = generate_synthetic_dataset(1000)

    with open(dataset_path, "r") as f:
        data = json.load(f)

    X = np.array([item["features"] for item in data])

    try:
        from sklearn.ensemble import IsolationForest
        model = IsolationForest(n_estimators=100, contamination=0.10, random_state=42)
        model.fit(X)

        # Save trained pickle
        model_path = os.path.join(MODEL_DIR, "model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        print(f"✓ Saved trained model -> {model_path}")
    except Exception as exc:
        print(f"⚠ scikit-learn training fallback: {exc}")

    # Save metadata.json & feature_schema.json
    meta = {
        "model_version": "isolation_forest_v1.0",
        "algorithm": "IsolationForest",
        "contamination": 0.10,
        "n_estimators": 100,
        "training_samples": len(data),
        "dataset_version": "synthetic_dataset_v1.0",
        "feature_schema_version": "v1.0",
    }
    with open(os.path.join(MODEL_DIR, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    schema = {
        "features": [
            "bid_count",
            "win_rate",
            "shared_address_count",
            "shared_director_count",
            "shared_bank_account_count",
            "verification_mismatch_count",
            "document_contradiction_count",
            "compliance_failure_count",
            "network_centrality",
        ]
    }
    with open(os.path.join(MODEL_DIR, "feature_schema.json"), "w") as f:
        json.dump(schema, f, indent=2)

    print("✓ Model metadata & feature schema saved successfully.")

if __name__ == "__main__":
    train_model()
