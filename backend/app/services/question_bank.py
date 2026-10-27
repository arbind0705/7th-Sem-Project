import json
from pathlib import Path

BANK_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "question_bank"

# ponytail: load + filter in-memory each call. Fine for a ~50-question bank;
# swap to a DB table (with a Question model) once questions are managed via UI.
_QUESTIONS_BY_ROUND: dict[str, list[dict]] | None = None


def _load() -> dict[str, list[dict]]:
    global _QUESTIONS_BY_ROUND
    if _QUESTIONS_BY_ROUND is None:
        by_round: dict[str, list[dict]] = {}
        for f in BANK_DIR.glob("*.json"):
            for q in json.loads(f.read_text()):
                by_round.setdefault(q["round"], []).append(q)
        _QUESTIONS_BY_ROUND = by_round
    return _QUESTIONS_BY_ROUND


def next_question(
    round_name: str, asked_ids: set[str], candidate_skills: list[str], difficulty: str = "medium"
) -> dict | None:
    """Pick the next unused question for a round. Prefers resume-skill match
    (§13) and target difficulty (§18 adaptive difficulty) together, then either
    alone, then whatever's left unused."""
    questions = _load().get(round_name, [])
    unused = [q for q in questions if q["question_id"] not in asked_ids]
    if not unused:
        return None

    skills_lower = {s.lower() for s in candidate_skills}

    def skill_match(q: dict) -> bool:
        return q.get("skill", "").lower() in skills_lower

    def difficulty_match(q: dict) -> bool:
        return q.get("difficulty") == difficulty

    for predicate in (
        lambda q: skill_match(q) and difficulty_match(q),
        skill_match,
        difficulty_match,
        lambda _: True,
    ):
        matched = [q for q in unused if predicate(q)]
        if matched:
            return matched[0]
    return None
