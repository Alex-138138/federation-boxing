from dataclasses import dataclass
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, UserRole
from app.services.auth import decode_token

bearer = HTTPBearer(auto_error=False)

@dataclass
class CurrentUser:
    id: str
    phone: str
    roles: set[str]

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(401, "Authentication required")
    payload = decode_token(credentials.credentials)
    uid = payload.get("sub")
    user = db.get(User, uid) if uid else None
    if not user:
        raise HTTPException(401, "Invalid token")
    roles = set(db.scalars(select(UserRole.role).where(UserRole.user_id == uid)))
    return CurrentUser(user.id, user.phone, roles)

def require_roles(*roles):
    def dep(c: CurrentUser = Depends(get_current_user)):
        if not c.roles.intersection(set(roles)):
            raise HTTPException(403, "Insufficient permissions")
        return c
    return dep
