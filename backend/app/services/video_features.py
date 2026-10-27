import io
import math
from pathlib import Path

import av
import httpx
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# ponytail: MediaPipe's Tasks API needs a downloadable model bundle (no more
# self-contained mp.solutions.face_mesh in this mediapipe version) — fetch it
# once to disk on first use instead of requiring a manual setup step.
_MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "face_landmarker.task"
_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

SAMPLE_FPS = 2  # sparse sampling — presence/pose only, not fast enough here for blink counting
GAZE_AWAY_YAW_DEG = 20.0

_landmarker = None


def _get_landmarker():
    global _landmarker
    if _landmarker is None:
        if not _MODEL_PATH.exists():
            _MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
            resp = httpx.get(_MODEL_URL, timeout=60, follow_redirects=True)
            resp.raise_for_status()
            _MODEL_PATH.write_bytes(resp.content)

        options = vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(_MODEL_PATH)),
            num_faces=1,
            output_facial_transformation_matrixes=True,
            running_mode=vision.RunningMode.IMAGE,
        )
        _landmarker = vision.FaceLandmarker.create_from_options(options)
    return _landmarker


def _yaw_degrees(matrix) -> float:
    """Rough yaw estimate from the facial transformation matrix's rotation
    block — approximate by design (§30 "start simple"), good enough to flag
    "facing away from camera", not precise head-pose tracking."""
    r02, r22 = matrix[0][2], matrix[2][2]
    return math.degrees(math.atan2(r02, r22))


def extract_video_features(content: bytes) -> dict:
    """Raw observations only (§30-31): face presence and approximate gaze
    direction. No emotion/identity inference, no claims from a single frame."""
    landmarker = _get_landmarker()
    container = av.open(io.BytesIO(content))
    video_stream = container.streams.video[0]
    fps = float(video_stream.average_rate) if video_stream.average_rate else 30.0
    sample_every = max(1, round(fps / SAMPLE_FPS))

    sampled = 0
    with_face = 0
    yaw_values: list[float] = []

    for i, frame in enumerate(container.decode(video=0)):
        if i % sample_every != 0:
            continue
        sampled += 1
        rgb = frame.to_ndarray(format="rgb24")
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = landmarker.detect(mp_image)
        if result.face_landmarks:
            with_face += 1
            if result.facial_transformation_matrixes:
                yaw_values.append(_yaw_degrees(result.facial_transformation_matrixes[0]))

    gaze_away = [y for y in yaw_values if abs(y) > GAZE_AWAY_YAW_DEG]
    return {
        "frames_sampled": sampled,
        "face_presence_ratio": round(with_face / sampled, 3) if sampled else None,
        "mean_head_yaw_deg": round(sum(yaw_values) / len(yaw_values), 1) if yaw_values else None,
        "gaze_away_ratio": round(len(gaze_away) / len(yaw_values), 3) if yaw_values else None,
    }
