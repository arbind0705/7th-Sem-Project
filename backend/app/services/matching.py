# ponytail: keyword-overlap matching, no embeddings dependency yet.
# Upgrade to sentence-transformers cosine similarity once overlap-only
# scoring proves too coarse against real resumes (see IMPLEMENTATION_PLAN.md Phase 1.3).


def match_score(resume_skills: list[str], required_skills: list[str], preferred_skills: list[str]) -> float:
    resume_set = {s.lower() for s in resume_skills}
    required = {s.lower() for s in required_skills}
    preferred = {s.lower() for s in preferred_skills}

    required_coverage = len(resume_set & required) / len(required) if required else 1.0
    preferred_coverage = len(resume_set & preferred) / len(preferred) if preferred else 0.0

    return round(0.7 * required_coverage + 0.3 * preferred_coverage, 3)
