"""
Configurable Synthetic Dataset Generator for PROCUREX.

Generates realistic but fictional procurement observations across 7 populations:
1. NORMAL
2. LOW_VARIATION
3. HIGH_PARTICIPATION
4. NETWORK_CONCENTRATION
5. VERIFICATION_INCONSISTENCY
6. DOCUMENT_CONTRADICTION
7. MIXED_SIGNAL

Explicitly labels output as SYNTHETIC DEMONSTRATION DATA.
"""
import argparse
import json
import numpy as np
import os
import random
import sys

def generate_dataset(num_records: int = 1000, anomaly_rate: float = 0.05, seed: int = 42, output_file: str = "synthetic_procurement_dataset.json"):
    random.seed(seed)
    np.random.seed(seed)

    records = []
    populations = [
        "NORMAL", "LOW_VARIATION", "HIGH_PARTICIPATION",
        "NETWORK_CONCENTRATION", "VERIFICATION_INCONSISTENCY",
        "DOCUMENT_CONTRADICTION", "MIXED_SIGNAL"
    ]

    for i in range(num_records):
        is_anom = random.random() < anomaly_rate
        pop = random.choice(populations) if is_anom else "NORMAL"

        if pop == "NORMAL":
            bid_count = int(np.random.poisson(3)) + 1
            win_rate = round(float(np.random.beta(2, 5)), 2)
            shared_address = 0
            shared_director = 0
            shared_bank = 0
            v_mismatch = 0
            doc_contradiction = 0
            comp_failure = 0
            centrality = round(float(np.random.beta(1, 10)), 3)
        elif pop == "NETWORK_CONCENTRATION":
            bid_count = int(np.random.poisson(8)) + 1
            win_rate = round(float(np.random.beta(4, 2)), 2)
            shared_address = random.randint(1, 4)
            shared_director = random.randint(1, 3)
            shared_bank = random.randint(0, 2)
            v_mismatch = 0
            doc_contradiction = 0
            comp_failure = 0
            centrality = round(float(np.random.beta(5, 2)), 3)
        elif pop == "VERIFICATION_INCONSISTENCY":
            bid_count = int(np.random.poisson(4)) + 1
            win_rate = round(float(np.random.beta(2, 4)), 2)
            shared_address = 0
            shared_director = 0
            shared_bank = 0
            v_mismatch = random.randint(1, 3)
            doc_contradiction = 0
            comp_failure = 1
            centrality = round(float(np.random.beta(2, 5)), 3)
        else:
            bid_count = int(np.random.poisson(6)) + 1
            win_rate = round(float(np.random.beta(3, 3)), 2)
            shared_address = random.randint(0, 2)
            shared_director = random.randint(0, 2)
            shared_bank = random.randint(0, 1)
            v_mismatch = random.randint(0, 2)
            doc_contradiction = random.randint(0, 2)
            comp_failure = random.randint(0, 2)
            centrality = round(float(np.random.beta(3, 3)), 3)

        records.append({
            "observation_id": f"OBS-SYNTH-{i+1:05d}",
            "population_type": pop,
            "is_synthetic": True,
            "disclaimer": "SYNTHETIC DEMONSTRATION DATA",
            "features": {
                "bid_count": float(bid_count),
                "win_rate": float(win_rate),
                "shared_address_count": float(shared_address),
                "shared_director_count": float(shared_director),
                "shared_bank_account_count": float(shared_bank),
                "verification_mismatch_count": float(v_mismatch),
                "document_contradiction_count": float(doc_contradiction),
                "compliance_failure_count": float(comp_failure),
                "network_centrality": float(centrality)
            }
        })

    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump({
            "dataset_name": "PROCUREX Synthetic Procurement Intelligence Dataset",
            "version": "1.0.0",
            "total_records": len(records),
            "anomaly_rate": anomaly_rate,
            "seed": seed,
            "data_disclaimer": "SYNTHETIC DEMONSTRATION DATA FOR SIH EVALUATION ONLY. NO REAL BIDDER OR GOVERNMENT DATA CONTAINED.",
            "records": records
        }, f, indent=2)

    print(f"Successfully generated {len(records)} synthetic records in {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PROCUREX Synthetic Dataset Generator")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--records", type=int, default=1000, help="Number of records")
    parser.add_argument("--anomaly-rate", type=float, default=0.05, help="Synthetic anomaly rate")
    parser.add_argument("--output", type=str, default="backend/demo/synthetic_procurement_dataset.json", help="Output file path")
    args = parser.parse_args()

    generate_dataset(num_records=args.records, anomaly_rate=args.anomaly_rate, seed=args.seed, output_file=args.output)
