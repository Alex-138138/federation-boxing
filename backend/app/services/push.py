import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from pywebpush import webpush, WebPushException
from app.core.config import settings
from app.models import PushSubscription

def push_to_user(db: Session, user_id: str, title: str, body: str):
    if not settings.vapid_private_key:
        return 0
    sent = 0
    rows = db.scalars(select(PushSubscription).where(
        PushSubscription.user_id == user_id,
        PushSubscription.active.is_(True)
    )).all()
    for row in rows:
        sub = {"endpoint": row.endpoint, "keys": {}}
        if row.p256dh: sub["keys"]["p256dh"] = row.p256dh
        if row.auth: sub["keys"]["auth"] = row.auth
        try:
            webpush(
                subscription_info=sub,
                data=json.dumps({"title": title, "body": body}, ensure_ascii=False),
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.vapid_subject},
            )
            sent += 1
        except WebPushException:
            pass
    return sent
