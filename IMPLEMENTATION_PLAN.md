# Implementation Plan — AI Multimodal Recruitment Intelligence Platform

Source spec: `AI_Multimodal_Recruitment_Project_FULL_HANDOFF.md`. This plan sequences that spec into buildable phases for a semester timeline (~12–14 weeks), cutting scope so something real ships early and complexity is added only once the layer below it works.

Guiding rule: **build MVP v1 end-to-end before touching audio/video/multi-agent orchestration.** A working resume→interview→report loop with one LLM call per step beats a half-built 16-agent graph.

---

## Phase 0 — Setup (2–3 days)

- Repo skeleton, minimal — grow it as phases need it, not upfront:
  ```
  backend/app/{api,services,models,schemas}/
  frontend/src/
  data/question_bank/
  ```
- FastAPI + PostgreSQL (skip pgvector until Phase 3 needs it).
- Pick one LLM provider to start (e.g. Claude); keep the call behind one `llm_service.py` function so swapping later is a one-file change — don't build a provider-abstraction layer for a project with one consumer.
- Auth: simplest thing that works (JWT via FastAPI, or even session cookie) — skip role-based access until a recruiter-vs-candidate distinction is actually exercised.

## Phase 1 — MVP v1: Resume → JD → Interview → Report (weeks 1–4)

This is the whole spine of the project. Everything else is enrichment.

1. **Job intake**: recruiter form → store JD text + required/preferred skills + rounds config (Postgres row, no agent needed — it's just a form).
2. **Resume parsing**: PyMuPDF/python-docx → raw text → one LLM call for structured extraction (skills, projects, experience) per §8. Store as JSON on the candidate row. No spaCy/NER pipeline yet — an LLM extraction prompt covers this at MVP scale.
3. **Resume↔JD matching** (§10): start with embeddings-only (Sentence Transformers, cosine similarity) + explicit required-skill-list overlap. That's the whole "hybrid" score for now — skip the 5-term weighted formula until you have data to tune weights against.
4. **Question selection**: a small static question bank (JSON file, ~30–50 questions tagged by skill/difficulty/round) + resume-specific questions from one LLM prompt. Skip the Question Validator Agent — validate by hand while the bank is this small.
5. **Interview loop (text-only first)**: one endpoint, `POST /interviews/{id}/respond` — takes candidate's text answer, LLM evaluates it against expected concepts (§34), returns either a follow-up or the next question. This *is* the adaptive interviewer — one prompt with the current Q&A history in context, not a separate agent graph.
6. **Report**: aggregate per-round scores + LLM-written evidence summary (§40 style) → recruiter-facing page. Human accept/review/override buttons (§43) from day one — it's a UI state, not a feature to defer.

**Exit criterion**: a recruiter can post a job, a candidate can upload a resume and do a full text-based interview, and a report comes out the other end with scores tied to quoted evidence.

## Phase 2 — MVP v2: Adaptive depth + voice (weeks 5–7)

Only start this once Phase 1 runs end-to-end.

- Swap text-answer input for voice: capture audio in-browser → Whisper transcription → same evaluation pipeline as Phase 1. Whisper is the only new moving part here.
- Cross-round memory (§21–22): pass a running candidate-evidence summary into each round's prompt instead of raw full history — keep it a plain JSON blob updated after each round, not a formal "memory service."
- Adaptive difficulty (§18): fold into the existing evaluate→next-question prompt as an instruction, not a separate decision agent.
- Multi-round support: technical + project-defense rounds minimum (behavioral/HR can wait).

**Exit criterion**: full spoken interview, 2+ rounds, evidence persists and updates across rounds.

## Phase 3 — Research v1: Acoustic signal (weeks 8–9)

This is where the research paper's first real experiment lives.

- librosa for pitch/energy/speech-rate/pause features — skip OpenSMILE unless librosa's features prove insufficient (fewer deps, same signal for the features actually listed in §25).
- Filler-word counting from the Whisper transcript (regex over a fixed filler list — no ML needed, §28).
- Feed these as *additional evidence*, reported as raw observations (§26–29), never as inferred emotional state.
- Start the human-rubric annotation process now (§58) — you need this data early since Phase 4's fairness/ablation experiments depend on it, and collecting it takes calendar time independent of coding.

## Phase 4 — Research v2: Video + fusion + experiments (weeks 10–13)

- MediaPipe for face presence / head pose / blink rate — one library covers all of §30's "start simple" list, skip OpenFace.
- Evidence fusion (§37): a scoring function that takes {resume, text, audio, video} evidence dicts and produces the hierarchical score (§38) — plain weighted sum with configurable weights, not a fusion "agent."
- Run the experiments already scoped in §59–60 (matching comparison, adaptive-vs-fixed, modality ablation) using the human annotations collected in Phase 3.
- Fairness pass (§63): re-run a subset of interviews with synthetic accent/audio variation, compare subgroup score deltas.

## Phase 5 — Write-up (weeks 13–14)

- Fill the paper structure in §69 using actual results from Phase 4 — no placeholder numbers.
- Limitations/ethics sections should state plainly what was cut (video emotion inference, OpenSMILE, full multi-agent orchestration) and why, per this plan.

---

## What this plan deliberately skips vs. the handoff doc

| Handoff item | Decision | Reasoning |
|---|---|---|
| LangGraph orchestrator, 16-agent architecture | Skip — use direct function calls between pipeline stages | One LLM-reasoning step per pipeline stage doesn't need a graph framework; add LangGraph only if branching logic (follow-up loops) gets too tangled to read as plain code |
| pgvector / Qdrant / FAISS | Skip until candidate volume needs indexed similarity search | Sentence-Transformers cosine similarity in-process handles a class-sized candidate pool fine |
| OpenSMILE | Skip, use librosa | Same acoustic features needed (§25), one less dependency |
| OpenFace | Skip, use MediaPipe | Covers §30's feature list; MediaPipe is lighter to deploy |
| Question Validator Agent | Skip until question bank is LLM-generated at scale | Manual review works fine for a ~50-question bank |
| Full RBAC / audit logs / signed URLs (§55) | Minimal auth only until a real second user role is exercised | Security theater without a second real actor isn't testable |

Each "skip" is reversible — if a phase reveals the shortcut doesn't hold (e.g., matching quality is bad with cosine-only), that's the trigger to add the next rung (hybrid scoring, then a vector DB), not something to build preemptively.

## Immediate next step

Start Phase 0 + Phase 1 step 1–2 (job intake + resume parsing) — say the word and I'll scaffold the FastAPI backend and the resume-upload endpoint.
