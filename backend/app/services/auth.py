from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings

DEMO_CODE = "1234"

def create_token(user_id: str):
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": user_id, "exp": exp}, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str):
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError:
        return {}
