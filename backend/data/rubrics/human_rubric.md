# Human Evaluation Rubric

Used to independently score recorded interviews, so AI-generated scores can later
be checked for agreement (Cohen's Kappa / ICC / Pearson correlation, §58) rather
than validated only by "LLM judges LLM" (§62).

## Process

1. Export a candidate's interview responses (question + answer text, or the recording) — use `evaluation` rows in `interview_responses`, not the AI's own scores.
2. At least two evaluators score independently, without seeing the AI's scores or each other's.
3. Fill in one row per (candidate, round, question) in `annotations_template.csv`. Paste the `question` text exactly as asked (copy from the transcript/DB) — `experiments/agreement.py` matches rows to the AI's stored evaluation by exact question text, and a typo means that row is silently skipped as unmatched.
4. Once N≥10 interviews are scored, run `python experiments/agreement.py` to compute agreement metrics before trusting AI scores for the paper's results section.

## Dimensions (1-5 each)

| Dimension | What to look for |
|---|---|
| Technical Correctness | Is the answer factually right? |
| Technical Depth | Does it go beyond surface-level definitions? |
| Reasoning | Is the justification for choices/tradeoffs sound? |
| Communication | Clarity, structure, conciseness — content only, not accent or voice quality |
| Answer Structure | Does the answer have a clear beginning/middle/end, or ramble? |
| Behavioral Evidence | For behavioral/project questions: concrete situation + personal action + result (STAR), not vague generalities |

Score each independently of the others — a technically correct but poorly structured
answer should score high on Correctness and low on Structure, not be averaged down
on both.

## Rules for evaluators

- Do not use accent, camera/mic quality, or background as input to any score (§36, §63).
- Do not infer nervousness, honesty, or personality from pauses or filler words — those are separate acoustic observations, not part of this rubric.
- If unsure, score conservatively and note it in `notes` rather than guessing.
