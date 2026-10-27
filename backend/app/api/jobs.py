from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from .deps import require_role

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=schemas.JobOut, dependencies=[Depends(require_role("recruiter"))])
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    db_job = models.Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("", response_model=list[schemas.JobOut])
def list_jobs(db: Session = Depends(get_db)):
    # Public: candidates browse open roles to apply to, same as recruiters browsing their board.
    return db.query(models.Job).order_by(models.Job.id.desc()).all()


@router.get("/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    return db.get(models.Job, job_id)


@router.get(
    "/{job_id}/candidates",
    response_model=list[schemas.CandidateOut],
    dependencies=[Depends(require_role("recruiter"))],
)
def list_job_candidates(job_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Candidate)
        .filter(models.Candidate.job_id == job_id)
        .order_by(models.Candidate.id.desc())
        .all()
    )
