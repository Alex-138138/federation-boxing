from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import *
from app.services.security import get_current_user, require_roles, CurrentUser
from app.services.domain import group_recipient_user_ids
from app.services.push import push_to_user

router = APIRouter(prefix="/messages", tags=["messages"])

class MessageIn(BaseModel):
    text: str

@router.post("/group/{group_id}")
def send_group(group_id: str, x: MessageIn,
               c: CurrentUser = Depends(require_roles("trainer","admin")),
               db: Session = Depends(get_db)):
    group = db.get(Group, group_id)
    if not group: raise HTTPException(404, "Group not found")
    if "admin" not in c.roles and group.trainer_user_id != c.id: raise HTTPException(403, "Not your group")
    m = Message(author_user_id=c.id, group_id=group_id, text=x.text)
    db.add(m); db.flush()
    recipients = group_recipient_user_ids(db, group_id)
    pushed = 0
    for uid in recipients:
        db.add(MessageReceipt(message_id=m.id, user_id=uid, delivered_at=datetime.now(timezone.utc)))
        db.add(Notification(user_id=uid, type="coach_message", title="Сообщение тренера", body=x.text))
        pushed += push_to_user(db, uid, "Сообщение тренера", x.text)
    db.add(AuditLog(actor_user_id=c.id, action="message.group.send", entity_type="group",
                    entity_id=group_id, metadata_json={"recipients": len(recipients), "push": pushed}))
    db.commit()
    return {"id": m.id, "recipients": len(recipients), "web_push_sent": pushed}

@router.get("/mine")
def mine(c: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        select(MessageReceipt, Message)
        .join(Message, MessageReceipt.message_id == Message.id)
        .where(MessageReceipt.user_id == c.id)
        .order_by(Message.created_at.desc())
    ).all()
    return [{"message_id": m.id, "text": m.text, "group_id": m.group_id, "read": r.read_at is not None} for r,m in rows]
