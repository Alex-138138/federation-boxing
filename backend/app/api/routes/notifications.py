from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Notification
from app.services.security import CurrentUser, get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    c: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.scalars(
        select(Notification)
        .where(Notification.user_id == c.id)
        .order_by(Notification.created_at.desc())
        .limit(200)
    ).all()
    return [
        {
            "id": item.id,
            "type": item.type,
            "title": item.title,
            "body": item.body,
            "created_at": item.created_at,
            "read_at": item.read_at,
            "read": item.read_at is not None,
        }
        for item in rows
    ]


@router.post("/{notification_id}/read")
def read_notification(
    notification_id: str,
    c: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = db.get(Notification, notification_id)
    if not notification or notification.user_id != c.id:
        raise HTTPException(404, "Notification not found")

    if notification.read_at is None:
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
    return {"ok": True, "read_at": notification.read_at}

@router.post("/read-all")
def read_all_notifications(c: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    rows=db.scalars(select(Notification).where(Notification.user_id==c.id,Notification.read_at.is_(None))).all()
    now=datetime.now(timezone.utc)
    for item in rows: item.read_at=now
    db.commit(); return {"ok":True,"updated":len(rows)}

@router.get("/unread-count")
def unread_count(c: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    rows=db.scalars(select(Notification).where(Notification.user_id==c.id,Notification.read_at.is_(None))).all()
    return {"count":len(rows)}
