from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, UserRole
from app.services.auth import DEMO_CODE, create_token

router = APIRouter(prefix="/auth", tags=["auth"])

class PhoneIn(BaseModel):
    phone: str

class VerifyIn(BaseModel):
    phone: str
    code: str

@router.post("/request-code")
def request_code(x: PhoneIn):
    return {"ok": True, "demo_code": DEMO_CODE}

@router.post("/verify-code")
def verify(x: VerifyIn, db: Session = Depends(get_db)):
    if x.code != DEMO_CODE:
        raise HTTPException(400, "Invalid code")
    user = db.scalar(select(User).where(User.phone == x.phone))
    if not user:
        raise HTTPException(404, "User not found. Run demo seed first.")
    roles = list(db.scalars(select(UserRole.role).where(UserRole.user_id == user.id)))
    return {"access_token": create_token(user.id), "token_type": "bearer", "roles": roles}
