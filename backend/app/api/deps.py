import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..services.auth_service import decode_access_token

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer), db: Session = Depends(get_db)
) -> models.User:
    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return user


def require_role(role: str):
    """Dependency factory: only lets through a User with the given role.
    Recruiter and candidate accounts share one users table/login but see
    entirely different routes — this is the only thing gating that."""

    def checker(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role != role:
            raise HTTPException(403, f"This action requires a {role} account")
        return user

    return checker
