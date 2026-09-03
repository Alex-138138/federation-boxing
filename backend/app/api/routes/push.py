from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import PushSubscription
from app.core.config import settings
from app.services.security import get_current_user, CurrentUser

router=APIRouter(prefix="/push",tags=["push"])

class PushIn(BaseModel):
    endpoint:str
    keys:dict[str,str]|None=None

@router.get("/vapid-public-key")
def vapid_public_key():
    return {"public_key":settings.vapid_public_key}

@router.post("/register")
def register(x:PushIn,c:CurrentUser=Depends(get_current_user),db:Session=Depends(get_db)):
    keys=x.keys or {}
    row=db.scalar(select(PushSubscription).where(PushSubscription.endpoint==x.endpoint))
    if not row:
        row=PushSubscription(user_id=c.id,endpoint=x.endpoint)
        db.add(row)
    row.user_id=c.id
    row.p256dh=keys.get("p256dh")
    row.auth=keys.get("auth")
    row.active=True
    db.commit()
    return {"ok":True}
