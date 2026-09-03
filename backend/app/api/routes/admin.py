from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, Athlete, Hall, Group, Application, AuditLog
from app.services.security import require_roles, CurrentUser

router=APIRouter(prefix="/admin",tags=["admin"])

@router.get("/stats")
def stats(c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    def count(model): return db.scalar(select(func.count()).select_from(model)) or 0
    return {
        "users":count(User),
        "athletes":count(Athlete),
        "halls":count(Hall),
        "groups":count(Group),
        "applications":count(Application)
    }

@router.get("/audit")
def audit(c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    rows=db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100)).all()
    return [{"action":r.action,"entity_type":r.entity_type,"entity_id":r.entity_id,"created_at":r.created_at} for r in rows]
