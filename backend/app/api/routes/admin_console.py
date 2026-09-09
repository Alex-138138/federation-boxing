from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User, UserRole, Person, Athlete, Hall, Group, TrainingSchedule, Application, Message, AuditLog
from app.services.security import require_roles, CurrentUser

router = APIRouter(prefix="/admin/console", tags=["admin-console"])

class StatusUpdate(BaseModel):
    status: str

class RoleUpdate(BaseModel):
    roles: list[str]

@router.get("/users")
def users(c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    rows = db.scalars(select(User)).all()
    result = []
    for u in rows:
        person = db.scalar(select(Person).where(Person.user_id == u.id))
        roles = db.scalars(select(UserRole.role).where(UserRole.user_id == u.id)).all()
        result.append({"id": u.id, "phone": u.phone, "status": u.status, "name": f"{person.last_name} {person.first_name}" if person else "", "roles": list(roles)})
    return result

@router.put("/users/{user_id}/status")
def user_status(user_id: str, x: StatusUpdate, c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u: raise HTTPException(404, "User not found")
    u.status = x.status
    db.add(AuditLog(actor_user_id=c.id, action="admin.user.status", entity_type="user", entity_id=u.id, metadata_json={"status": x.status}))
    db.commit()
    return {"ok": True}

@router.put("/users/{user_id}/roles")
def user_roles(user_id: str, x: RoleUpdate, c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    allowed = {"admin", "trainer", "parent", "athlete"}
    roles = sorted(set(x.roles) & allowed)
    if not roles: raise HTTPException(400, "At least one valid role required")
    existing = db.scalars(select(UserRole).where(UserRole.user_id == user_id)).all()
    for r in existing: db.delete(r)
    for role in roles: db.add(UserRole(user_id=user_id, role=role))
    db.add(AuditLog(actor_user_id=c.id, action="admin.user.roles", entity_type="user", entity_id=user_id, metadata_json={"roles": roles}))
    db.commit()
    return {"ok": True, "roles": roles}

@router.get("/halls")
def halls(c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return [{"id": h.id, "name": h.name, "address": h.address, "phone": h.phone} for h in db.scalars(select(Hall)).all()]

@router.get("/groups")
def groups(c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    return [{"id": g.id, "name": g.name, "hall_id": g.hall_id, "trainer_user_id": g.trainer_user_id} for g in db.scalars(select(Group)).all()]

@router.get("/applications")
def applications(c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    rows = db.scalars(select(Application)).all()
    return [{"id": a.id, "status": a.status, "type": a.application_type, "hall_id": a.hall_id, "group_id": a.group_id, "trainer_user_id": a.trainer_user_id, "snapshot": a.snapshot, "rejection_reason": a.rejection_reason} for a in rows]

@router.get("/messages")
def messages(c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    rows = db.scalars(select(Message).order_by(Message.created_at.desc()).limit(500)).all()
    return [{"id": m.id, "author_user_id": m.author_user_id, "group_id": m.group_id, "text": m.text, "created_at": m.created_at} for m in rows]
