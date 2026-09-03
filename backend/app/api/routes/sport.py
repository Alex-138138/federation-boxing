from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import *
from app.services.security import require_roles, CurrentUser

router = APIRouter(prefix="/sport", tags=["sport"])

class AttendanceIn(BaseModel):
    athlete_id: str
    attendance_date: date
    status: str

class AchievementIn(BaseModel):
    title: str
    description: str | None = None

class RatingIn(BaseModel):
    points: int
    reason: str

@router.post("/groups/{group_id}/attendance")
def mark_attendance(group_id: str, x: AttendanceIn,
                    c: CurrentUser = Depends(require_roles("trainer","admin")),
                    db: Session = Depends(get_db)):
    group=db.get(Group,group_id)
    if not group: raise HTTPException(404,"Group not found")
    if "admin" not in c.roles and group.trainer_user_id != c.id: raise HTTPException(403,"Not your group")
    db.add(Attendance(group_id=group_id,athlete_id=x.athlete_id,
                      attendance_date=x.attendance_date,status=x.status,marked_by=c.id))
    db.commit()
    return {"ok":True}

@router.post("/athletes/{athlete_id}/achievements")
def add_achievement(athlete_id:str,x:AchievementIn,
                    c:CurrentUser=Depends(require_roles("trainer","admin")),
                    db:Session=Depends(get_db)):
    db.add(Achievement(athlete_id=athlete_id,title=x.title,description=x.description))
    db.commit()
    return {"ok":True}

@router.post("/athletes/{athlete_id}/rating")
def change_rating(athlete_id:str,x:RatingIn,
                  c:CurrentUser=Depends(require_roles("trainer","admin")),
                  db:Session=Depends(get_db)):
    a=db.get(Athlete,athlete_id)
    if not a: raise HTTPException(404,"Athlete not found")
    before=a.rating_points
    a.rating_points=x.points
    db.add(RatingHistory(athlete_id=a.id,points_before=before,points_after=x.points,reason=x.reason,changed_by=c.id))
    db.commit()
    return {"athlete_id":a.id,"rating_points":a.rating_points}
