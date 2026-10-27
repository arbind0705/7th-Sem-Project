"""Human/AI agreement (§58, §62): reads filled-in rows from
data/rubrics/annotations_template.csv and compares them against the AI's own
evaluation scores stored on the matching interview_responses row, so results
aren't validated by "LLM judges LLM" alone.

Only three AI rubric dimensions have a direct human-rubric counterpart today
(completeness/depth/reasoning are LLM-only content scores — see
app/services/llm_service.py); communication, answer_structure, and
behavioral_evidence in the human rubric don't have an AI-scored equivalent yet,
so they're reported as "no AI counterpart" rather than silently skipped.

Usage:
    python experiments/agreement.py [--csv data/rubrics/annotations_template.csv]

Prints "no annotations yet" and exits if the CSV has no filled-in rows —
metrics are never fabricated from empty or placeholder data (§60).
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.database import SessionLocal  # noqa: E402
from app import models  # noqa: E402

# human rubric dimension -> AI evaluation key (see data/rubrics/human_rubric.md
# and app/services/llm_service.py's EVALUATE_ANSWER_PROMPT)
DIMENSION_MAP = {
    "technical_correctness": "correctness",
    "technical_depth": "depth",
    "reasoning": "reasoning",
}
NO_AI_COUNTERPART = ["communication", "answer_structure", "behavioral_evidence"]


def quadratic_weighted_kappa(human: list[int], ai: list[int], min_score=0, max_score=5) -> float:
    n = max_score - min_score + 1
    hist_h = np.zeros(n)
    hist_a = np.zeros(n)
    conf = np.zeros((n, n))
    for h, a in zip(human, ai):
        hist_h[h - min_score] += 1
        hist_a[a - min_score] += 1
        conf[h - min_score][a - min_score] += 1

    weights = np.array([[(i - j) ** 2 / (n - 1) ** 2 for j in range(n)] for i in range(n)])
    expected = np.outer(hist_h, hist_a) / len(human)

    numerator = (weights * conf).sum()
    denominator = (weights * expected).sum()
    return round(1 - numerator / denominator, 3) if denominator else float("nan")


def load_annotations(csv_path: Path) -> list[dict]:
    with open(csv_path, newline="") as f:
        return list(csv.DictReader(f))


def find_ai_response(db, candidate_id: int, round_name: str, question: str) -> dict | None:
    response = (
        db.query(models.InterviewResponse)
        .join(models.InterviewRound)
        .join(models.Interview)
        .filter(
            models.Interview.candidate_id == candidate_id,
            models.InterviewRound.name == round_name,
            models.InterviewResponse.question_text == question,
        )
        .first()
    )
    return response.evaluation if response else None


def run(csv_path: Path) -> None:
    rows = load_annotations(csv_path)
    if not rows:
        print(f"{csv_path} has no annotation rows yet — fill it in (see data/rubrics/human_rubric.md) before running this.")
        return

    db = SessionLocal()
    paired = defaultdict(list)  # human_dim -> [(human_score, ai_score), ...]
    unmatched = 0

    # Average across evaluators for the same (candidate, round, question) before pairing.
    grouped = defaultdict(list)
    for row in rows:
        key = (int(row["candidate_id"]), row["round"], row["question"])
        grouped[key].append(row)

    for (candidate_id, round_name, question), group in grouped.items():
        ai_eval = find_ai_response(db, candidate_id, round_name, question)
        if ai_eval is None:
            unmatched += 1
            continue
        for human_dim, ai_dim in DIMENSION_MAP.items():
            values = [int(r[human_dim]) for r in group if r.get(human_dim)]
            if not values:
                continue
            human_avg = round(sum(values) / len(values))
            paired[human_dim].append((human_avg, ai_eval[ai_dim]))

    if unmatched:
        print(f"Warning: {unmatched} annotation row(s) had no matching interview_response (check round/question text match exactly).")

    for dim in NO_AI_COUNTERPART:
        print(f"{dim}: no AI counterpart yet — human-only rubric dimension, cannot compute agreement.")

    for human_dim, pairs in paired.items():
        if len(pairs) < 2:
            print(f"{human_dim}: only {len(pairs)} matched pair(s) — need at least 2 to compute correlation.")
            continue
        humans, ais = zip(*pairs)
        humans, ais = np.array(humans), np.array(ais)
        pearson_r, _ = pearsonr(humans, ais)
        spearman_r, _ = spearmanr(humans, ais)
        kappa = quadratic_weighted_kappa(list(humans), list(ais))
        mae = float(np.mean(np.abs(humans - ais)))
        rmse = float(np.sqrt(np.mean((humans - ais) ** 2)))
        print(
            f"{human_dim} (n={len(pairs)}): pearson_r={pearson_r:.3f} spearman_r={spearman_r:.3f} "
            f"quadratic_weighted_kappa={kappa} MAE={mae:.3f} RMSE={rmse:.3f}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=str(ROOT / "backend" / "data" / "rubrics" / "annotations_template.csv"))
    args = parser.parse_args()
    run(Path(args.csv))
