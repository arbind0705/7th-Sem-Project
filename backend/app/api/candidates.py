from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.resume_parser import extract_text
from ..services.llm_service import extract_resume_profile
from ..services.matching import match_score
from .deps import require_role

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


def _parse_and_match(db: Session, job_id: int, filename: str, content: bytes) -> dict:
    job = db.get(models.Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    try:
        resume_text = extract_text(filename, content)
    except ValueError as e:
        raise HTTPException(400, str(e))

    profile = extract_resume_profile(resume_text)
    skills = [s["name"] for s in profile.get("skills", [])]
    score = match_score(skills, job.required_skills, job.preferred_skills)
    return {"resume_text": resume_text, "resume_profile": profile, "match_score": score}


@router.post(
    "/resumes/upload", response_model=schemas.CandidateOut, dependencies=[Depends(require_role("recruiter"))]
)
async def upload_resume(job_id: int, file: UploadFile, db: Session = Depends(get_db)):
    """Recruiter uploads a resume on a candidate's behalf (e.g. from email) — no candidate account involved."""
    content = await file.read()
    parsed = _parse_and_match(db, job_id, file.filename, content)

    candidate = models.Candidate(job_id=job_id, name=parsed["resume_profile"].get("name"), **parsed)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.post("/apply", response_model=schemas.CandidateOut)
async def apply(
    job_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role("candidate")),
):
    """Candidate self-applies: uploads their own resume, creating a Candidate row
    owned by their account. Interview routes only allow the owning candidate through."""
    content = await file.read()
    parsed = _parse_and_match(db, job_id, file.filename, content)

    candidate = models.Candidate(job_id=job_id, user_id=user.id, name=parsed["resume_profile"].get("name"), **parsed)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("/me", response_model=list[schemas.MyApplicationOut])
def my_applications(db: Session = Depends(get_db), user: models.User = Depends(require_role("candidate"))):
    candidates = (
        db.query(models.Candidate)
        .filter(models.Candidate.user_id == user.id)
        .order_by(models.Candidate.id.desc())
        .all()
    )
    return [schemas.MyApplicationOut(**schemas.CandidateOut.model_validate(c).model_dump(), job_title=c.job.title) for c in candidates]


@router.get("/{candidate_id}", response_model=schemas.CandidateOut, dependencies=[Depends(require_role("recruiter"))])
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(models.Candidate, candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found")
    return candidate


@router.get(
    "/{candidate_id}/interviews",
    response_model=list[schemas.InterviewSummaryOut],
    dependencies=[Depends(require_role("recruiter"))],
)
def list_candidate_interviews(candidate_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Interview)
        .filter(models.Interview.candidate_id == candidate_id)
        .order_by(models.Interview.id.desc())
        .all()
    )
