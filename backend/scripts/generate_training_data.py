"""
Synthetic Training Dataset Generator for Procurement Anomaly Detection.

Generates 1,000 synthetic procurement network observations:
- Normal procurement baseline observations
- Synthetic anomalous network observations (e.g. high shared directors, shared addresses, verification conflicts)

IMPORTANT:
Does NOT falsely label synthetic anomalies as real fraud.
Uses explicit label: SYNTHETIC_ANOMALY.
"""
import os
import json
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "training")

def generate_synthetic_dataset(num_samples: int = 1000):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    np.random.seed(42)

    data = []
    for i in range(num_samples):
        is_anomaly = (i % 10 == 0)  # 10% synthetic anomalies

        if not is_anomaly:
            # Normal baseline features
            bid_count = float(np.random.randint(1, 10))
            win_rate = float(np.random.uniform(0.05, 0.30))
            shared_address_count = 0.0
            shared_director_count = 0.0
            shared_bank_count = 0.0
            verification_mismatch_count = 0.0
            document_contradiction_count = 0.0
            compliance_failure_count = float(np.random.choice([0, 0, 0, 1]))
            network_centrality = float(np.random.uniform(0.1, 0.4))
            label = "SYNTHETIC_NORMAL"
        else:
            # Synthetic anomalous features
            bid_count = float(np.random.randint(15, 40))
            win_rate = float(np.random.uniform(0.40, 0.90))
            shared_address_count = float(np.random.randint(1, 4))
            shared_director_count = float(np.random.randint(1, 3))
            shared_bank_count = float(np.random.choice([0, 1]))
            verification_mismatch_count = float(np.random.randint(1, 3))
            document_contradiction_count = float(np.random.randint(1, 4))
            compliance_failure_count = float(np.random.randint(1, 3))
            network_centrality = float(np.random.uniform(0.6, 1.0))
            label = "SYNTHETIC_ANOMALY"

        data.append({
            "observation_id": f"obs_{i:04d}",
            "features": [
                bid_count,
                win_rate,
                shared_address_count,
                shared_director_count,
                shared_bank_count,
                verification_mismatch_count,
                document_contradiction_count,
                compliance_failure_count,
                network_centrality,
            ],
            "label": label,
        })

    filepath = os.path.join(OUTPUT_DIR, "procurement_synthetic_training.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Generated {num_samples} synthetic training observations -> {filepath}")
    return filepath

if __name__ == "__main__":
    generate_synthetic_dataset()
