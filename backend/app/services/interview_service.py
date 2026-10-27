from sqlalchemy.orm import Session

from .. import models
from . import question_bank, llm_service, scoring

# ponytail: fixed per-round question counts. Move to Job.rounds config
# (per-round count) once a recruiter needs to tune this per job.
ROUND_QUESTION_COUNTS = {"technical": 3, "project": 2, "behavioral": 2, "problem_solving": 2, "hr": 2}

# Hard cap on follow-up questions across the entire interview.
# This keeps the interview length predictable while still allowing
# the LLM to probe genuinely incomplete or ambiguous answers.
MAX_FOLLOWUPS = 2

DIFFICULTY_LADDER = ["easy", "medium", "hard"]


def _candidate_skills(candidate: models.Candidate) -> list[str]:
    profile = candidate.resume_profile or {}
    return [s["name"] for s in profile.get("skills", [])]


def _asked_ids(round_: models.InterviewRound) -> set[str]:
    return {r.question_id for r in round_.responses if r.question_id}


def _followups_used(interview: models.Interview) -> int:
    """Count follow-up questions already asked in this interview."""
    return sum(
        1
        for round_ in interview.interview_rounds
        for response in round_.responses
        if response.is_followup
    )


def _next_difficulty(current: str, evaluation: dict) -> str:
    """Adaptive difficulty per §18: a strong answer escalates, a weak one steps back."""
    avg = (evaluation["completeness"] + evaluation["correctness"] + evaluation["depth"] + evaluation["reasoning"]) / 4
    idx = DIFFICULTY_LADDER.index(current)
    if avg >= 4 and idx < len(DIFFICULTY_LADDER) - 1:
        idx += 1
    elif avg <= 2 and idx > 0:
        idx -= 1
    return DIFFICULTY_LADDER[idx]


def _record_evidence(interview: models.Interview, round_name: str, evaluation: dict) -> None:
    """Append this answer's one-line evaluation reason to the interview's rolling
    evidence log (§21-22 cross-round memory) — reuses the reason the evaluation
    call already produces, no separate summarization agent."""
    notes = list((interview.evidence_summary or {}).get("notes", []))
    notes.append(f"[{round_name}] {evaluation.get('reason', '')}")
    interview.evidence_summary = {"notes": notes}


def _start_round(db: Session, interview: models.Interview, round_index: int) -> models.InterviewRound:
    round_ = models.InterviewRound(interview_id=interview.id, name=interview.rounds[round_index])
    db.add(round_)
    db.commit()
    db.refresh(round_)

    q = question_bank.next_question(round_.name, set(), _candidate_skills(interview.candidate), round_.difficulty)
    if q is None:
        raise ValueError(f"No questions configured for round '{round_.name}'")
    round_.pending_question = {
        "question_id": q["question_id"],
        "question_text": q["text"],
        "expected_concepts": q.get("expected_concepts", []),
        "is_followup": False,
    }
    db.commit()
    return round_


def start_interview(db: Session, candidate_id: int) -> dict:
    candidate = db.get(models.Candidate, candidate_id)
    if not candidate:
        raise ValueError("Candidate not found")

    interview = models.Interview(candidate_id=candidate_id, rounds=candidate.job.rounds)
    db.add(interview)
    db.commit()
    db.refresh(interview)

    round_ = _start_round(db, interview, 0)
    return {
        "interview_id": interview.id,
        "round": round_.name,
        "question": round_.pending_question["question_text"],
    }


def _finalize_report(db: Session, interview: models.Interview) -> dict:
    evidence = {"rounds": [], "cross_round_notes": (interview.evidence_summary or {}).get("notes", [])}
    for round_ in interview.interview_rounds:
        evidence["rounds"].append(
            {
                "round": round_.name,
                "responses": [
                    {
                        "question": r.question_text,
                        "is_followup": r.is_followup,
                        "evaluation": r.evaluation,
                        "acoustic_observations": r.audio_metrics,
                        "video_observations": r.video_metrics,
                    }
                    for r in round_.responses
                ],
            }
        )
    report = llm_service.generate_report(evidence)
    report["fusion"] = scoring.compute_final_score(interview.candidate, interview)
    interview.report = report
    db.commit()
    return report


def _advance(db: Session, interview: models.Interview, round_: models.InterviewRound) -> dict:
    """Round's question budget is used up — move to the next round, or finish the interview."""
    round_.status = "complete"
    round_.pending_question = None
    db.commit()

    next_index = interview.current_round_index + 1
    if next_index >= len(interview.rounds):
        interview.status = "complete"
        db.commit()
        report = _finalize_report(db, interview)
        return {"type": "interview_complete", "report": report}

    interview.current_round_index = next_index
    db.commit()
    new_round = _start_round(db, interview, next_index)
    return {"type": "next_round", "round": new_round.name, "question": new_round.pending_question["question_text"]}


def submit_answer(
    db: Session,
    interview_id: int,
    answer_text: str,
    audio_metrics: dict | None = None,
    video_metrics: dict | None = None,
) -> dict:
    interview = db.get(models.Interview, interview_id)
    if not interview:
        raise ValueError("Interview not found")
    if interview.status == "complete":
        raise ValueError("Interview already complete")

    round_ = interview.interview_rounds[interview.current_round_index]
    pending = round_.pending_question
    if not pending:
        raise ValueError("No question is currently pending for this interview")

    prior_evidence = (interview.evidence_summary or {}).get("notes", [])
    evaluation = llm_service.evaluate_answer(
        question_text=pending["question_text"],
        expected_concepts=pending.get("expected_concepts", []),
        answer_text=answer_text,
        is_followup=pending.get("is_followup", False),
        prior_evidence=prior_evidence,
    )

    db.add(
        models.InterviewResponse(
            round_id=round_.id,
            question_id=pending.get("question_id"),
            question_text=pending["question_text"],
            answer_text=answer_text,
            is_followup=pending.get("is_followup", False),
            evaluation=evaluation,
            audio_metrics=audio_metrics,
            video_metrics=video_metrics,
        )
    )
    _record_evidence(interview, round_.name, evaluation)
    db.commit()

    # Follow-ups are optional and globally limited. A single original
    # question can still have at most one follow-up.
    followups_used = _followups_used(interview)
    if (
        evaluation.get("decision") == "FOLLOW_UP"
        and not pending.get("is_followup")
        and followups_used < MAX_FOLLOWUPS
        and evaluation.get("follow_up_question")
    ):
        round_.pending_question = {
            "question_id": None,
            "question_text": evaluation["follow_up_question"],
            "expected_concepts": pending.get("expected_concepts", []),
            "is_followup": True,
        }
        db.commit()
        return {"type": "follow_up", "question": evaluation["follow_up_question"]}

    round_.difficulty = _next_difficulty(round_.difficulty, evaluation)
    round_.questions_asked += 1
    if round_.questions_asked >= ROUND_QUESTION_COUNTS.get(round_.name, 3):
        return _advance(db, interview, round_)

    next_q = question_bank.next_question(
        round_.name, _asked_ids(round_), _candidate_skills(interview.candidate), round_.difficulty
    )
    if next_q is None:
        return _advance(db, interview, round_)

    round_.pending_question = {
        "question_id": next_q["question_id"],
        "question_text": next_q["text"],
        "expected_concepts": next_q.get("expected_concepts", []),
        "is_followup": False,
    }
    db.commit()
    return {"type": "next_question", "question": next_q["text"]}
