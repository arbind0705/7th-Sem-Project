import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# ponytail: one implicit "recruiter" role, no per-job ownership scoping or
# multi-tenant isolation — any logged-in user sees every job/candidate. Fine
# for a single team; add ownership checks if multiple orgs ever share this.
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = "HS256"
TOKEN_TTL = timedelta(hours=12)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def _require_secret() -> str:
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET is not set")
    return JWT_SECRET


def create_access_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "exp": datetime.now(timezone.utc) + TOKEN_TTL}
    return jwt.encode(payload, _require_secret(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int:
    """Returns the user id, or raises jwt.InvalidTokenError (expired/malformed/bad signature)."""
    payload = jwt.decode(token, _require_secret(), algorithms=[JWT_ALGORITHM])
    return int(payload["sub"])
