import secrets
from datetime import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditLog, Group, Hall, JoinCode, TrainingSchedule, User, UserRole
from app.services.security import CurrentUser, require_roles

router = APIRouter(prefix="/admin/manage", tags=["admin-manage"])


class HallIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=500)
    phone: str | None = Field(default=None, max_length=32)


class GroupIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    hall_id: str
    trainer_user_id: str


class ScheduleIn(BaseModel):
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    location: str | None = Field(default=None, max_length=255)


@router.post("/halls")
def create_hall(
    x: HallIn,
    c: CurrentUser = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    h = Hall(name=x.name.strip(), address=x.address.strip(), phone=x.phone)
    db.add(h)
    db.flush()
    db.add(
        AuditLog(
            actor_user_id=c.id,
            action="hall.create",
            entity_type="hall",
            entity_id=h.id,
        )
    )
    db.commit()
    return {"id": h.id, "name": h.name}


@router.post("/groups")
def create_group(
    x: GroupIn,
    c: CurrentUser = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    if not db.get(Hall, x.hall_id):
        raise HTTPException(404, "Hall not found")

    trainer = db.get(User, x.trainer_user_id)
    if not trainer or trainer.status != "active":
        raise HTTPException(404, "Active trainer user not found")

    trainer_role = db.scalar(
        select(UserRole).where(
            UserRole.user_id == x.trainer_user_id,
            UserRole.role == "trainer",
        )
    )
    if not trainer_role:
        raise HTTPException(400, "Selected user does not have trainer role")

    g = Group(
        name=x.name.strip(),
        hall_id=x.hall_id,
        trainer_user_id=x.trainer_user_id,
    )
    db.add(g)
    db.flush()

    code = "BOX-" + secrets.token_hex(3).upper()
    db.add(
        JoinCode(
            code=code,
            hall_id=g.hall_id,
            trainer_user_id=g.trainer_user_id,
            group_id=g.id,
        )
    )
    db.add(
        AuditLog(
            actor_user_id=c.id,
            action="group.create",
            entity_type="group",
            entity_id=g.id,
            metadata_json={"hall_id": g.hall_id, "trainer_user_id": g.trainer_user_id},
        )
    )
    db.commit()
    return {"id": g.id, "name": g.name, "join_code": code}


@router.post("/groups/{group_id}/schedule")
def add_schedule(
    group_id: str,
    x: ScheduleIn,
    c: CurrentUser = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    g = db.get(Group, group_id)
    if not g:
        raise HTTPException(404, "Group not found")
    if x.end_time <= x.start_time:
        raise HTTPException(400, "end_time must be after start_time")

    s = TrainingSchedule(
        group_id=group_id,
        weekday=x.weekday,
        start_time=x.start_time,
        end_time=x.end_time,
        location=x.location,
    )
    db.add(s)
    db.flush()
    db.add(
        AuditLog(
            actor_user_id=c.id,
            action="schedule.create",
            entity_type="training_schedule",
            entity_id=s.id,
            metadata_json={"group_id": group_id, "weekday": x.weekday},
        )
    )
    db.commit()
    return {"ok": True, "id": s.id}
