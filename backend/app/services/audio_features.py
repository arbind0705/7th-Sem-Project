import io

import av
import librosa
import numpy as np

# ponytail: PyAV bundles its own ffmpeg libs, so webm/opus clips (what
# MediaRecorder produces in-browser) decode without installing a system
# ffmpeg binary. librosa then works on the plain PCM array it hands back.


def _decode_to_mono_pcm(content: bytes) -> tuple[np.ndarray, int]:
    container = av.open(io.BytesIO(content))
    stream = container.streams.audio[0]
    sr = stream.rate
    frames = [frame.to_ndarray() for frame in container.decode(audio=0)]
    pcm = np.concatenate(frames, axis=1).astype(np.float32)
    if pcm.shape[0] > 1:  # downmix to mono if needed
        pcm = pcm.mean(axis=0, keepdims=True)
    return pcm.flatten(), sr


def extract_features(content: bytes, word_count: int) -> dict:
    """Raw acoustic observations only (§25-29) — no claims about emotion or
    intent. pitch/energy via librosa; speech rate derived from the transcript
    word count already produced by Whisper, so no separate VAD/word-alignment
    step is needed for an MVP-level number."""
    pcm, sr = _decode_to_mono_pcm(content)
    duration_sec = len(pcm) / sr if sr else 0.0

    f0, voiced_flag, _ = librosa.pyin(pcm, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr)
    voiced_f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])

    rms = librosa.feature.rms(y=pcm)[0]

    # Silence ratio: fraction of frames below a fixed energy threshold — a
    # simple stand-in for pause detection (§27), not a full VAD model.
    silence_ratio = float(np.mean(rms < 0.02)) if len(rms) else 0.0

    return {
        "duration_sec": round(duration_sec, 2),
        "mean_pitch_hz": round(float(np.mean(voiced_f0)), 1) if len(voiced_f0) else None,
        "pitch_variation_hz": round(float(np.std(voiced_f0)), 1) if len(voiced_f0) else None,
        "mean_energy": round(float(np.mean(rms)), 4) if len(rms) else None,
        "energy_variation": round(float(np.std(rms)), 4) if len(rms) else None,
        "silence_ratio": round(silence_ratio, 3),
        "speech_rate_wpm": round(word_count / (duration_sec / 60), 1) if duration_sec > 0 else None,
    }
