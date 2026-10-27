from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, jobs, candidates, interviews

# Schema is managed by Alembic migrations now (see backend/alembic/) — run
# `alembic upgrade head` instead of relying on create_all.
app = FastAPI(title="Recruitment AI — MVP v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(candidates.router)
app.include_router(interviews.router)


@app.get("/health")
def health():
    return {"status": "ok"}
