from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import *
from app.services.security import get_current_user, CurrentUser

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/athlete/{athlete_id}")
def athlete_profile(athlete_id: str, c: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    athlete = db.get(Athlete, athlete_id)
    if not athlete: raise HTTPException(404, "Athlete not found")
    person = db.get(Person, athlete.person_id)
    allowed = "admin" in c.roles
    gm = db.scalar(select(GroupMembership).where(GroupMembership.athlete_id == athlete.id, GroupMembership.status == "active"))
    group = db.get(Group, gm.group_id) if gm else None
    hall = db.get(Hall, group.hall_id) if group else None
    if "trainer" in c.roles and group and group.trainer_user_id == c.id: allowed = True
    if person.user_id == c.id: allowed = True
    parent = db.scalar(select(Person).join(FamilyLink, FamilyLink.parent_person_id == Person.id).where(FamilyLink.athlete_id == athlete.id, Person.user_id == c.id))
    if parent: allowed = True
    if not allowed: raise HTTPException(403, "No access")
    schedule=[]
    if group:
        for s in db.scalars(select(TrainingSchedule).where(TrainingSchedule.group_id == group.id, TrainingSchedule.active.is_(True))):
            schedule.append({"weekday": s.weekday, "start_time": str(s.start_time), "end_time": str(s.end_time), "location": s.location})
    achievements=[{"title":a.title,"description":a.description} for a in db.scalars(select(Achievement).where(Achievement.athlete_id==athlete.id))]
    return {"id":athlete.id,"name":f"{person.last_name} {person.first_name}","rating_points":athlete.rating_points,"group":group.name if group else None,"group_id":group.id if group else None,"hall":{"name":hall.name,"address":hall.address} if hall else None,"schedule":schedule,"achievements":achievements}

@router.get("/children")
def my_children(c: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    parent=db.scalar(select(Person).where(Person.user_id==c.id))
    if not parent:return []
    links=db.scalars(select(FamilyLink).where(FamilyLink.parent_person_id==parent.id)).all();out=[]
    for link in links:
        a=db.get(Athlete,link.athlete_id);p=db.get(Person,a.person_id) if a else None
        if a and p: out.append({"athlete_id":a.id,"name":f"{p.last_name} {p.first_name}","rating_points":a.rating_points})
    return out

@router.get("/me-athlete")
def my_athlete(c: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    person=db.scalar(select(Person).where(Person.user_id==c.id))
    if not person: raise HTTPException(404,"Athlete profile not found")
    athlete=db.scalar(select(Athlete).where(Athlete.person_id==person.id))
    if not athlete: raise HTTPException(404,"Athlete profile not found")
    return {"athlete_id":athlete.id}

@router.get("/athlete/{athlete_id}/attendance")
def athlete_attendance(athlete_id: str, c: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    athlete_profile(athlete_id,c,db)
    rows=db.scalars(select(Attendance).where(Attendance.athlete_id==athlete_id).order_by(Attendance.attendance_date.desc()).limit(100)).all()
    return [{"date":str(r.attendance_date),"status":r.status,"group_id":r.group_id} for r in rows]
