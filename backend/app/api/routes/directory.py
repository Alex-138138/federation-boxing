from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Hall, Group, JoinCode, Person, TrainingSchedule, User

router = APIRouter(prefix="/directory", tags=["directory"])

@router.get("/halls")
def halls(db: Session = Depends(get_db)):
    rows = db.scalars(select(Hall).order_by(Hall.name)).all()
    return [{"id": h.id, "name": h.name, "address": h.address, "phone": h.phone} for h in rows]

@router.get("/trainers")
def trainers(db: Session = Depends(get_db)):
    groups = db.scalars(select(Group).order_by(Group.name)).all()
    by_user = {}
    for g in groups:
        by_user.setdefault(g.trainer_user_id, []).append(g)
    out = []
    for user_id, trainer_groups in by_user.items():
        p = db.scalar(select(Person).where(Person.user_id == user_id))
        u = db.get(User, user_id)
        out.append({
            "user_id": user_id,
            "name": f"{p.last_name} {p.first_name}" if p else "Тренер",
            "phone": (p.phone if p and p.phone else (u.phone if u else None)),
            "groups": [{"id": g.id, "name": g.name, "hall_id": g.hall_id} for g in trainer_groups],
        })
    return out

@router.get("/groups")
def groups(db: Session = Depends(get_db)):
    rows = db.scalars(select(Group).order_by(Group.name)).all()
    out=[]
    for g in rows:
        schedule=db.scalars(select(TrainingSchedule).where(TrainingSchedule.group_id==g.id).order_by(TrainingSchedule.weekday,TrainingSchedule.start_time)).all()
        code=db.scalar(select(JoinCode).where(JoinCode.group_id==g.id,JoinCode.active==True))
        out.append({"id":g.id,"name":g.name,"hall_id":g.hall_id,"trainer_user_id":g.trainer_user_id,"join_code":code.code if code else None,"schedule":[{"id":x.id,"weekday":x.weekday,"start_time":x.start_time,"end_time":x.end_time,"location":x.location,"active":x.active} for x in schedule]})
    return out
