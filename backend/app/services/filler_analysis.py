import re

# ponytail: fixed filler list + regex counting (§28). No ML needed for this —
# upgrade to a learned disfluency detector only if this list misses real cases.
FILLERS = ["um", "uh", "like", "actually", "basically", "you know", "i mean"]

_FILLER_PATTERN = re.compile(r"\b(" + "|".join(re.escape(f) for f in FILLERS) + r")\b", re.IGNORECASE)


def count_fillers(transcript: str, duration_sec: float) -> dict:
    matches = _FILLER_PATTERN.findall(transcript)
    word_count = len(transcript.split())
    return {
        "filler_count": len(matches),
        "filler_density": round(len(matches) / word_count, 3) if word_count else None,
        "fillers_per_minute": round(len(matches) / (duration_sec / 60), 1) if duration_sec > 0 else None,
    }
