from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Notification
from app.services.security import get_current_user, CurrentUser

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("")
def list_notifications(c: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Notification).where(Notification.user_id == c.id).order_by(Notification.created_at.desc())).all()
    return [{"id": n.id, "type": n.type, "title": n.title, "body": n.body, "read": n.read_at is not None} for n in rows]

@router.post("/{notification_id}/read")
def read_notification(notification_id: str, c: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.get(Notification, notification_id)
    if not n or n.user_id != c.id:
        raise HTTPException(404, "Notification not found")
    n.read_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}
