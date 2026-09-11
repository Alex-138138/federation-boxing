from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    Application,
    Athlete,
    AuditLog,
    FamilyLink,
    GroupMembership,
    JoinCode,
    Notification,
    Person,
)
from app.services.domain import age_on
from app.services.security import CurrentUser, get_current_user, require_roles

router = APIRouter(prefix="/applications", tags=["applications"])


class ChildIn(BaseModel):
    join_code: str = Field(min_length=1, max_length=64)
    child_first_name: str = Field(min_length=1, max_length=100)
    child_last_name: str = Field(min_length=1, max_length=100)
    child_birth_date: date
    child_gender: str | None = Field(default=None, max_length=32)
    parent_first_name: str = Field(min_length=1, max_length=100)
    parent_last_name: str = Field(min_length=1, max_length=100)
    parent_address: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=2000)


class RejectIn(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


@router.post("/child")
def submit_child(
    x: ChildIn,
    c: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if x.child_birth_date > date.today():
        raise HTTPException(400, "Birth date cannot be in the future")
    if age_on(x.child_birth_date) >= 18:
        raise HTTPException(400, "Child flow is only for users under 18")

    invite = db.scalar(
        select(JoinCode).where(
            JoinCode.code == x.join_code.strip(),
            JoinCode.active.is_(True),
        )
    )
    if not invite:
        raise HTTPException(404, "Join code not found")

    application = Application(
        applicant_user_id=c.id,
        hall_id=invite.hall_id,
        trainer_user_id=invite.trainer_user_id,
        group_id=invite.group_id,
        snapshot=x.model_dump(mode="json"),
    )
    db.add(application)
    db.flush()
    db.add(
        AuditLog(
            actor_user_id=c.id,
            action="application.submit",
            entity_type="application",
            entity_id=application.id,
        )
    )
    db.commit()
    return {"id": application.id, "status": application.status}


@router.get("/trainer")
def trainer_apps(
    c: CurrentUser = Depends(require_roles("trainer", "admin")),
    db: Session = Depends(get_db),
):
    query = select(Application)
    if "admin" not in c.roles:
        query = query.where(Application.trainer_user_id == c.id)
    rows = db.scalars(query.order_by(Application.id.desc())).all()
    return [
        {
            "id": application.id,
            "status": application.status,
            "snapshot": application.snapshot,
            "group_id": application.group_id,
            "athlete_id": application.athlete_id,
            "rejection_reason": application.rejection_reason,
        }
        for application in rows
    ]


@router.post("/{application_id}/approve")
def approve(
    application_id: str,
    c: CurrentUser = Depends(require_roles("trainer", "admin")),
    db: Session = Depends(get_db),
):
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(404, "Application not found")
    if "admin" not in c.roles and application.trainer_user_id != c.id:
        raise HTTPException(403, "Not your application")
    if application.status != "submitted":
        raise HTTPException(400, "Application already processed")

    snapshot = application.snapshot
    person = Person(
        first_name=snapshot["child_first_name"],
        last_name=snapshot["child_last_name"],
        birth_date=date.fromisoformat(snapshot["child_birth_date"]),
        gender=snapshot.get("child_gender"),
    )
    db.add(person)
    db.flush()

    athlete = Athlete(person_id=person.id, rating_points=100)
    db.add(athlete)
    db.flush()

    parent = db.scalar(select(Person).where(Person.user_id == application.applicant_user_id))
    if not parent:
        parent = Person(
            user_id=application.applicant_user_id,
            first_name=snapshot["parent_first_name"],
            last_name=snapshot["parent_last_name"],
            address=snapshot.get("parent_address"),
        )
        db.add(parent)
        db.flush()

    db.add(
        FamilyLink(
            parent_person_id=parent.id,
            athlete_id=athlete.id,
            relationship="parent",
            is_primary=True,
        )
    )
    if application.group_id:
        db.add(GroupMembership(group_id=application.group_id, athlete_id=athlete.id))

    application.status = "approved"
    application.athlete_id = athlete.id
    db.add(
        Notification(
            user_id=application.applicant_user_id,
            type="application_approved",
            title="Заявление одобрено",
            body="Ребёнок добавлен в группу.",
        )
    )
    db.add(
        AuditLog(
            actor_user_id=c.id,
            action="application.approve",
            entity_type="application",
            entity_id=application.id,
            metadata_json={"athlete_id": athlete.id},
        )
    )
    db.commit()
    return {"id": application.id, "status": application.status, "athlete_id": athlete.id}


@router.post("/{application_id}/reject")
def reject(
    application_id: str,
    x: RejectIn,
    c: CurrentUser = Depends(require_roles("trainer", "admin")),
    db: Session = Depends(get_db),
):
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(404, "Application not found")
    if "admin" not in c.roles and application.trainer_user_id != c.id:
        raise HTTPException(403, "Not your application")
    if application.status != "submitted":
        raise HTTPException(400, "Application already processed")

    reason = x.reason.strip()
    application.status = "rejected"
    application.rejection_reason = reason
    db.add(
        Notification(
            user_id=application.applicant_user_id,
            type="application_rejected",
            title="Заявление отклонено",
            body=reason,
        )
    )
    db.add(
        AuditLog(
            actor_user_id=c.id,
            action="application.reject",
            entity_type="application",
            entity_id=application.id,
            metadata_json={"reason": reason},
        )
    )
    db.commit()
    return {"id": application.id, "status": application.status}
