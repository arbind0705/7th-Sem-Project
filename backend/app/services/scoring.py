from .. import models

# ponytail: plain configurable weighted sum (§38), not a "fusion agent" — this
# is exactly the kind of deterministic computation that doesn't need an LLM.
WEIGHTS = {"resume": 0.15, "technical": 0.35, "communication": 0.15, "behavioral": 0.20, "role_fit": 0.15}

# Filler density and speech rate bands used to turn raw acoustic observations
# into a 0-1 "observable delivery" signal (§36) — content-independent, never a
# proxy for technical competence or honesty.
FILLER_DENSITY_CEILING = 0.15
CLEAR_SPEECH_RATE_RANGE = (110, 170)


def _avg_rubric(responses: list[models.InterviewResponse]) -> float | None:
    scores = [
        (r.evaluation["completeness"] + r.evaluation["correctness"] + r.evaluation["depth"] + r.evaluation["reasoning"]) / 4 / 5
        for r in responses
        if r.evaluation
    ]
    return round(sum(scores) / len(scores), 3) if scores else None


def _norm_filler(density: float | None) -> float:
    return max(0.0, 1 - (density or 0) / FILLER_DENSITY_CEILING)


def _norm_speech_rate(wpm: float | None) -> float:
    if wpm is None:
        return 0.5
    lo, hi = CLEAR_SPEECH_RATE_RANGE
    if lo <= wpm <= hi:
        return 1.0
    distance = min(abs(wpm - lo), abs(wpm - hi))
    return max(0.0, 1 - distance / 100)


def _communication_score(responses: list[models.InterviewResponse]) -> tuple[float | None, float]:
    """Communication sub-score from observable delivery only (§36) — confidence
    reflects how many of this candidate's answers actually had audio evidence,
    so a text-only interview correctly reports low confidence rather than a
    fabricated communication score."""
    with_audio = [r.audio_metrics for r in responses if r.audio_metrics]
    if not with_audio:
        return None, 0.0
    scores = [(_norm_filler(m.get("filler_density")) + _norm_speech_rate(m.get("speech_rate_wpm"))) / 2 for m in with_audio]
    confidence = len(with_audio) / len(responses) if responses else 0.0
    return round(sum(scores) / len(scores), 3), round(confidence, 2)


def combine_components(components: dict) -> float | None:
    """The weighted-sum step alone (§38), reused by experiments/ablation.py to
    recompute a score with one component blanked out — a modality ablation is
    exactly what already happens when a component is None."""
    present = {k: v for k, v in components.items() if v is not None}
    total_weight = sum(WEIGHTS[k] for k in present)
    return round(sum(WEIGHTS[k] * v for k, v in present.items()) / total_weight, 3) if total_weight else None


def compute_final_score(candidate: models.Candidate, interview: models.Interview) -> dict:
    all_responses = [r for round_ in interview.interview_rounds for r in round_.responses]
    technical_responses = [r for round_ in interview.interview_rounds if round_.name == "technical" for r in round_.responses]
    behavioral_responses = [r for round_ in interview.interview_rounds if round_.name == "behavioral" for r in round_.responses]

    resume = candidate.match_score
    technical = _avg_rubric(technical_responses)
    behavioral = _avg_rubric(behavioral_responses)
    communication, communication_confidence = _communication_score(all_responses)
    # ponytail: role fit reuses the resume/JD match score as a proxy. A dedicated
    # role-fit model (beyond skill overlap) is out of scope until resume matching
    # itself moves past keyword overlap — see IMPLEMENTATION_PLAN.md.
    role_fit = resume

    components = {
        "resume": resume,
        "technical": technical,
        "communication": communication,
        "behavioral": behavioral,
        "role_fit": role_fit,
    }

    return {
        "final_score": combine_components(components),
        "components": components,
        "communication_confidence": communication_confidence,
    }
