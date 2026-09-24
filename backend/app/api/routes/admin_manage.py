import secrets
from datetime import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditLog, Group, GroupMembership, Hall, JoinCode, TrainingSchedule, User, UserRole
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

class HallUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=500)
    phone: str | None = Field(default=None, max_length=32)

class GroupUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    hall_id: str
    trainer_user_id: str


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

@router.put("/halls/{hall_id}")
def update_hall(hall_id: str, x: HallUpdate, c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    h = db.get(Hall, hall_id)
    if not h: raise HTTPException(404, "Hall not found")
    h.name=x.name.strip(); h.address=x.address.strip(); h.phone=x.phone
    db.add(AuditLog(actor_user_id=c.id,action="hall.update",entity_type="hall",entity_id=h.id,metadata_json={"name":h.name}))
    db.commit(); return {"ok":True}

@router.put("/groups/{group_id}")
def update_group(group_id: str, x: GroupUpdate, c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    g=db.get(Group,group_id)
    if not g: raise HTTPException(404,"Group not found")
    if not db.get(Hall,x.hall_id): raise HTTPException(404,"Hall not found")
    role=db.scalar(select(UserRole).where(UserRole.user_id==x.trainer_user_id,UserRole.role=="trainer"))
    if not role: raise HTTPException(400,"Selected user does not have trainer role")
    g.name=x.name.strip(); g.hall_id=x.hall_id; g.trainer_user_id=x.trainer_user_id
    db.add(AuditLog(actor_user_id=c.id,action="group.update",entity_type="group",entity_id=g.id,metadata_json={"hall_id":g.hall_id,"trainer_user_id":g.trainer_user_id}))
    db.commit(); return {"ok":True}

@router.delete("/groups/{group_id}/schedule/{schedule_id}")
def delete_schedule(group_id: str, schedule_id: str, c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    row=db.get(TrainingSchedule,schedule_id)
    if not row or row.group_id!=group_id: raise HTTPException(404,"Schedule not found")
    db.delete(row); db.add(AuditLog(actor_user_id=c.id,action="schedule.delete",entity_type="training_schedule",entity_id=schedule_id,metadata_json={"group_id":group_id})); db.commit(); return {"ok":True}

@router.post("/groups/{group_id}/archive")
def archive_group(group_id: str, c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    g=db.get(Group,group_id)
    if not g: raise HTTPException(404,"Group not found")
    for row in db.scalars(select(GroupMembership).where(GroupMembership.group_id==group_id,GroupMembership.status=="active")).all(): row.status="archived"
    for row in db.scalars(select(JoinCode).where(JoinCode.group_id==group_id,JoinCode.active==True)).all(): row.active=False
    for row in db.scalars(select(TrainingSchedule).where(TrainingSchedule.group_id==group_id,TrainingSchedule.active==True)).all(): row.active=False
    db.add(AuditLog(actor_user_id=c.id,action="group.archive",entity_type="group",entity_id=g.id)); db.commit(); return {"ok":True}

@router.post("/halls/{hall_id}/archive")
def archive_hall(hall_id: str, c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    h=db.get(Hall,hall_id)
    if not h: raise HTTPException(404,"Hall not found")
    active_groups=db.scalars(select(Group).where(Group.hall_id==hall_id)).all()
    for g in active_groups:
        for row in db.scalars(select(GroupMembership).where(GroupMembership.group_id==g.id,GroupMembership.status=="active")).all(): row.status="archived"
        for row in db.scalars(select(JoinCode).where(JoinCode.group_id==g.id,JoinCode.active==True)).all(): row.active=False
        for row in db.scalars(select(TrainingSchedule).where(TrainingSchedule.group_id==g.id,TrainingSchedule.active==True)).all(): row.active=False
    db.add(AuditLog(actor_user_id=c.id,action="hall.archive",entity_type="hall",entity_id=h.id,metadata_json={"groups":len(active_groups)})); db.commit(); return {"ok":True}

@router.put("/groups/{group_id}/schedule/{schedule_id}")
def update_schedule(group_id: str, schedule_id: str, x: ScheduleIn, c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    row=db.get(TrainingSchedule,schedule_id)
    if not row or row.group_id!=group_id: raise HTTPException(404,"Schedule not found")
    if x.end_time<=x.start_time: raise HTTPException(400,"end_time must be after start_time")
    row.weekday=x.weekday; row.start_time=x.start_time; row.end_time=x.end_time; row.location=x.location; row.active=True
    db.add(AuditLog(actor_user_id=c.id,action="schedule.update",entity_type="training_schedule",entity_id=row.id,metadata_json={"group_id":group_id,"weekday":x.weekday}))
    db.commit(); return {"ok":True}

@router.post("/groups/{group_id}/join-code/rotate")
def rotate_join_code(group_id: str, c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    g=db.get(Group,group_id)
    if not g: raise HTTPException(404,"Group not found")
    for row in db.scalars(select(JoinCode).where(JoinCode.group_id==group_id,JoinCode.active==True)).all(): row.active=False
    code="BOX-"+secrets.token_hex(4).upper()
    db.add(JoinCode(code=code,hall_id=g.hall_id,trainer_user_id=g.trainer_user_id,group_id=g.id,active=True))
    db.add(AuditLog(actor_user_id=c.id,action="join_code.rotate",entity_type="group",entity_id=g.id,metadata_json={"code":code}))
    db.commit(); return {"ok":True,"join_code":code}

@router.post("/groups/{group_id}/restore")
def restore_group(group_id: str, c: CurrentUser = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    g=db.get(Group,group_id)
    if not g: raise HTTPException(404,"Group not found")
    for row in db.scalars(select(TrainingSchedule).where(TrainingSchedule.group_id==group_id)).all(): row.active=True
    active=db.scalar(select(JoinCode).where(JoinCode.group_id==group_id,JoinCode.active==True))
    if not active:
        code="BOX-"+secrets.token_hex(4).upper(); db.add(JoinCode(code=code,hall_id=g.hall_id,trainer_user_id=g.trainer_user_id,group_id=g.id,active=True))
    db.add(AuditLog(actor_user_id=c.id,action="group.restore",entity_type="group",entity_id=g.id)); db.commit(); return {"ok":True}
