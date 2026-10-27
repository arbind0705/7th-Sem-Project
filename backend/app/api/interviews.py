from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..services import audio_features, av_utils, filler_analysis, interview_service, video_features, whisper_service
from .deps import require_role

router = APIRouter(prefix="/api/interviews", tags=["interviews"])


class AnswerIn(BaseModel):
    answer: str


def _require_owning_candidate(db: Session, candidate_id: int, user: models.User) -> None:
    """A candidate account may only act on interviews for its own Candidate row —
    otherwise anyone who guessed/was given a candidate_id could take someone
    else's interview, since candidate_id appears directly in the interview URL."""
    candidate = db.get(models.Candidate, candidate_id)
    if not candidate or candidate.user_id != user.id:
        raise HTTPException(403, "Not authorized for this candidate")


def _owning_candidate_id_for_interview(db: Session, interview_id: int) -> int | None:
    interview = db.get(models.Interview, interview_id)
    return interview.candidate_id if interview else None


@router.post("/start")
def start_interview(
    candidate_id: int, db: Session = Depends(get_db), user: models.User = Depends(require_role("candidate"))
):
    _require_owning_candidate(db, candidate_id, user)
    try:
        return interview_service.start_interview(db, candidate_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{interview_id}/respond")
def respond(
    interview_id: int,
    body: AnswerIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role("candidate")),
):
    owner_candidate_id = _owning_candidate_id_for_interview(db, interview_id)
    if owner_candidate_id is None:
        raise HTTPException(404, "Interview not found")
    _require_owning_candidate(db, owner_candidate_id, user)
    try:
        return interview_service.submit_answer(db, interview_id, body.answer)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        # An unhandled exception here (e.g. the local LLM returning malformed
        # JSON) would otherwise crash out through Starlette's default error
        # path, which skips CORSMiddleware and makes the browser report it as
        # a misleading "CORS policy" / net::ERR_FAILED error. Catching it here
        # keeps the response normal so the real message reaches the frontend.
        raise HTTPException(502, f"The AI evaluation step failed, please try answering again: {e}")


@router.post("/{interview_id}/respond/audio")
async def respond_audio(
    interview_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role("candidate")),
):
    """Same loop as /respond, but the answer comes from a recorded clip transcribed
    via Whisper (§24) plus raw acoustic/filler observations (§25-29, Phase 3) and,
    if the clip includes a webcam track, face-presence/gaze observations (§30-31,
    Phase 4) — all stored as supplementary evidence, never fed into content scoring."""
    owner_candidate_id = _owning_candidate_id_for_interview(db, interview_id)
    if owner_candidate_id is None:
        raise HTTPException(404, "Interview not found")
    _require_owning_candidate(db, owner_candidate_id, user)

    content = await file.read()
    try:
        audio_only = av_utils.extract_audio_only(content)
        transcript = whisper_service.transcribe(file.filename or "audio.webm", audio_only)

        audio_metrics = None
        try:
            features = audio_features.extract_features(audio_only, word_count=len(transcript.split()))
            fillers = filler_analysis.count_fillers(transcript, features["duration_sec"])
            audio_metrics = {**features, **fillers}
        except Exception:
            pass  # acoustic features are supplementary — a decode failure shouldn't block the interview

        video_metrics = None
        if av_utils.has_video_stream(content):
            try:
                video_metrics = video_features.extract_video_features(content)
            except Exception:
                pass  # same: video observations are supplementary, never block the interview

        result = interview_service.submit_answer(
            db, interview_id, transcript, audio_metrics=audio_metrics, video_metrics=video_metrics
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(502, f"The AI evaluation step failed, please try answering again: {e}")
    return {"transcript": transcript, "audio_metrics": audio_metrics, "video_metrics": video_metrics, **result}


@router.get("/{interview_id}/report", dependencies=[Depends(require_role("recruiter"))])
def get_report(interview_id: int, db: Session = Depends(get_db)):
    interview = db.get(models.Interview, interview_id)
    if not interview:
        raise HTTPException(404, "Interview not found")
    if interview.status != "complete":
        raise HTTPException(400, "Interview is not complete yet")
    return {
        **interview.report,
        "candidate_name": interview.candidate.name,
        "job_title": interview.candidate.job.title,
    }
