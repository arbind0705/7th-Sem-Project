"""Modality ablation (§60): for every completed interview, recompute the final
score with each evidence component removed one at a time, to see how much that
modality moved the result. Reads real interview data only — if none exists yet,
it says so and exits, rather than printing placeholder numbers (§60: "do not
invent results before running the experiments").

Usage:
    python experiments/ablation.py [--out ablation_results.csv]
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database import SessionLocal  # noqa: E402
from app import models  # noqa: E402
from app.services import scoring  # noqa: E402

MODALITIES = ["resume", "technical", "communication", "behavioral", "role_fit"]


def run(out_path: str) -> None:
    db = SessionLocal()
    interviews = (
        db.query(models.Interview)
        .filter(models.Interview.status == "complete", models.Interview.report.isnot(None))
        .all()
    )
    interviews = [iv for iv in interviews if iv.report and "fusion" in iv.report]

    if not interviews:
        print("No completed interviews with a fusion score yet — nothing to ablate. Run some interviews first.")
        return

    rows = []
    for iv in interviews:
        fusion = iv.report["fusion"]
        baseline = fusion["components"]
        baseline_final = fusion["final_score"]
        row = {"interview_id": iv.id, "candidate_id": iv.candidate_id, "baseline_final": baseline_final}
        for modality in MODALITIES:
            if baseline.get(modality) is None:
                row[f"{modality}_delta"] = None  # wasn't present in the baseline either — nothing to ablate
                continue
            ablated = {**baseline, modality: None}
            ablated_final = scoring.combine_components(ablated)
            row[f"{modality}_delta"] = (
                round(baseline_final - ablated_final, 3) if baseline_final is not None and ablated_final is not None else None
            )
        rows.append(row)

    fieldnames = ["interview_id", "candidate_id", "baseline_final"] + [f"{m}_delta" for m in MODALITIES]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} completed interview(s) analyzed. Results written to {out_path}")
    print("delta = baseline_final - final_score_with_that_modality_removed (larger delta = that modality mattered more)")
    for row in rows:
        print(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="ablation_results.csv")
    args = parser.parse_args()
    run(args.out)
