from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import *
from app.services.security import get_current_user, require_roles, CurrentUser
from app.services.domain import age_on

router = APIRouter(prefix="/applications", tags=["applications"])

class ChildIn(BaseModel):
    join_code: str
    child_first_name: str
    child_last_name: str
    child_birth_date: date
    child_gender: str | None = None
    parent_first_name: str
    parent_last_name: str
    parent_address: str | None = None
    notes: str | None = None

class RejectIn(BaseModel):
    reason: str

@router.post("/child")
def submit_child(x: ChildIn, c: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    if age_on(x.child_birth_date) >= 18:
        raise HTTPException(400, "Child flow is only for users under 18")
    invite = db.scalar(select(JoinCode).where(JoinCode.code == x.join_code, JoinCode.active.is_(True)))
    if not invite:
        raise HTTPException(404, "Join code not found")
    app = Application(
        applicant_user_id=c.id,
        hall_id=invite.hall_id,
        trainer_user_id=invite.trainer_user_id,
        group_id=invite.group_id,
        snapshot=x.model_dump(mode="json"),
    )
    db.add(app)
    db.add(AuditLog(actor_user_id=c.id, action="application.submit", entity_type="application", entity_id=app.id))
    db.commit()
    return {"id": app.id, "status": app.status}

@router.get("/trainer")
def trainer_apps(c: CurrentUser = Depends(require_roles("trainer","admin")), db: Session = Depends(get_db)):
    q = select(Application)
    if "admin" not in c.roles:
        q = q.where(Application.trainer_user_id == c.id)
    rows = db.scalars(q.order_by(Application.id.desc())).all()
    return [{
        "id": a.id, "status": a.status, "snapshot": a.snapshot,
        "group_id": a.group_id, "athlete_id": a.athlete_id, "rejection_reason": a.rejection_reason
    } for a in rows]

@router.post("/{application_id}/approve")
def approve(application_id: str, c: CurrentUser = Depends(require_roles("trainer","admin")), db: Session = Depends(get_db)):
    a = db.get(Application, application_id)
    if not a: raise HTTPException(404, "Application not found")
    if "admin" not in c.roles and a.trainer_user_id != c.id: raise HTTPException(403, "Not your application")
    if a.status != "submitted": raise HTTPException(400, "Application already processed")
    snap = a.snapshot

    person = Person(
        first_name=snap["child_first_name"],
        last_name=snap["child_last_name"],
        birth_date=date.fromisoformat(snap["child_birth_date"]),
        gender=snap.get("child_gender"),
    )
    db.add(person); db.flush()
    athlete = Athlete(person_id=person.id, rating_points=100)
    db.add(athlete); db.flush()

    parent = db.scalar(select(Person).where(Person.user_id == a.applicant_user_id))
    if not parent:
        parent = Person(
            user_id=a.applicant_user_id,
            first_name=snap["parent_first_name"],
            last_name=snap["parent_last_name"],
            address=snap.get("parent_address"),
        )
        db.add(parent); db.flush()

    db.add(FamilyLink(parent_person_id=parent.id, athlete_id=athlete.id, relationship="parent", is_primary=True))
    if a.group_id:
        db.add(GroupMembership(group_id=a.group_id, athlete_id=athlete.id))
    a.status = "approved"
    a.athlete_id = athlete.id
    db.add(Notification(user_id=a.applicant_user_id, type="application_approved",
                        title="Заявление одобрено", body="Ребёнок добавлен в группу."))
    db.add(AuditLog(actor_user_id=c.id, action="application.approve", entity_type="application", entity_id=a.id))
    db.commit()
    return {"id": a.id, "status": a.status, "athlete_id": athlete.id}

@router.post("/{application_id}/reject")
def reject(application_id: str, x: RejectIn, c: CurrentUser = Depends(require_roles("trainer","admin")), db: Session = Depends(get_db)):
    a = db.get(Application, application_id)
    if not a: raise HTTPException(404, "Application not found")
    if "admin" not in c.roles and a.trainer_user_id != c.id: raise HTTPException(403, "Not your application")
    a.status = "rejected"
    a.rejection_reason = x.reason
    db.add(Notification(user_id=a.applicant_user_id, type="application_rejected",
                        title="Заявление отклонено", body=x.reason))
    db.commit()
    return {"id": a.id, "status": a.status}
