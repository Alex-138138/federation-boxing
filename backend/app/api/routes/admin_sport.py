from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Athlete, Person, GroupMembership, Group, Hall, Achievement, RatingHistory, Attendance
from app.services.security import require_roles, CurrentUser

router=APIRouter(prefix="/admin/sport",tags=["admin-sport"])

@router.get("/athletes")
def athletes(c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    result=[]
    for a in db.scalars(select(Athlete)).all():
        p=db.get(Person,a.person_id)
        m=db.scalar(select(GroupMembership).where(GroupMembership.athlete_id==a.id,GroupMembership.status=="active"))
        g=db.get(Group,m.group_id) if m else None
        h=db.get(Hall,g.hall_id) if g else None
        result.append({"id":a.id,"name":f"{p.last_name} {p.first_name}" if p else "","birth_date":p.birth_date if p else None,"phone":p.phone if p else None,"rating_points":a.rating_points,"status":a.status,"group_id":g.id if g else None,"group":g.name if g else None,"hall":h.name if h else None})
    return result

@router.get("/athletes/{athlete_id}/history")
def athlete_history(athlete_id:str,c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    achievements=db.scalars(select(Achievement).where(Achievement.athlete_id==athlete_id).order_by(Achievement.event_date.desc())).all()
    ratings=db.scalars(select(RatingHistory).where(RatingHistory.athlete_id==athlete_id).order_by(RatingHistory.created_at.desc())).all()
    attendance=db.scalars(select(Attendance).where(Attendance.athlete_id==athlete_id).order_by(Attendance.attendance_date.desc()).limit(100)).all()
    return {"achievements":[{"title":x.title,"description":x.description,"event_date":x.event_date} for x in achievements],"rating":[{"before":x.points_before,"after":x.points_after,"reason":x.reason,"created_at":x.created_at} for x in ratings],"attendance":[{"date":x.attendance_date,"status":x.status,"group_id":x.group_id} for x in attendance]}
