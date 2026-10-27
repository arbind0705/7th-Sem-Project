from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="recruiter")  # "recruiter" | "candidate"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    rounds = Column(JSON, default=list)  # e.g. ["technical", "project", "behavioral"]

    candidates = relationship("Candidate", back_populates="job")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # set when a candidate self-applies
    name = Column(String, nullable=True)
    resume_text = Column(Text, nullable=True)
    resume_profile = Column(JSON, nullable=True)  # structured extraction: skills/projects/experience
    match_score = Column(Float, nullable=True)

    job = relationship("Job", back_populates="candidates")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    rounds = Column(JSON, default=list)  # ordered round names, copied from job at start
    current_round_index = Column(Integer, default=0)
    status = Column(String, default="in_progress")  # in_progress | complete
    evidence_summary = Column(JSON, default=dict)  # running cross-round evidence, see IMPLEMENTATION_PLAN.md Phase 2
    report = Column(JSON, nullable=True)

    candidate = relationship("Candidate")
    interview_rounds = relationship("InterviewRound", back_populates="interview", order_by="InterviewRound.id")


class InterviewRound(Base):
    __tablename__ = "interview_rounds"

    id = Column(Integer, primary_key=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    name = Column(String, nullable=False)
    questions_asked = Column(Integer, default=0)
    status = Column(String, default="active")  # active | complete
    pending_question = Column(JSON, nullable=True)  # {question_id, question_text, expected_concepts, is_followup}
    difficulty = Column(String, default="medium")  # easy | medium | hard, adapts per §18

    interview = relationship("Interview", back_populates="interview_rounds")
    responses = relationship("InterviewResponse", back_populates="round", order_by="InterviewResponse.id")


class InterviewResponse(Base):
    __tablename__ = "interview_responses"

    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey("interview_rounds.id"), nullable=False)
    question_id = Column(String, nullable=True)  # bank question_id, null if LLM-generated follow-up
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    is_followup = Column(Boolean, default=False)
    evaluation = Column(JSON, nullable=True)  # {completeness, correctness, depth, reasoning, decision, reason}
    audio_metrics = Column(JSON, nullable=True)  # raw acoustic + filler observations (§25-29), voice answers only
    video_metrics = Column(JSON, nullable=True)  # raw face-presence/gaze observations (§30-31), webcam answers only

    round = relationship("InterviewRound", back_populates="responses")
