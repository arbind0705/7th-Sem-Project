from pydantic import BaseModel, EmailStr
from typing import Literal, Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Literal["recruiter", "candidate"] = "recruiter"


class UserOut(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    rounds: list[str] = ["technical", "project", "behavioral"]


class JobOut(JobCreate):
    id: int

    class Config:
        from_attributes = True


class CandidateOut(BaseModel):
    id: int
    job_id: int
    name: Optional[str]
    resume_profile: Optional[dict]
    match_score: Optional[float]

    class Config:
        from_attributes = True


class MyApplicationOut(CandidateOut):
    job_title: str


class InterviewSummaryOut(BaseModel):
    id: int
    status: str
    rounds: list[str]

    class Config:
        from_attributes = True
