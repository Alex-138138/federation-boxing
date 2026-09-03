from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Group, Hall, GroupMembership, Athlete, Person, TrainingSchedule, JoinCode, Attendance
from app.services.security import require_roles, CurrentUser

router = APIRouter(prefix="/trainer", tags=["trainer"])

@router.get("/groups")
def my_groups(c: CurrentUser = Depends(require_roles("trainer", "admin")), db: Session = Depends(get_db)):
    q = select(Group)
    if "admin" not in c.roles:
        q = q.where(Group.trainer_user_id == c.id)
    rows = db.scalars(q.order_by(Group.name)).all()
    out=[]
    for g in rows:
        hall=db.get(Hall,g.hall_id)
        code=db.scalar(select(JoinCode).where(JoinCode.group_id==g.id, JoinCode.active.is_(True)))
        count=len(db.scalars(select(GroupMembership).where(GroupMembership.group_id==g.id,GroupMembership.status=="active")).all())
        schedule=[{"weekday":s.weekday,"start_time":str(s.start_time),"end_time":str(s.end_time),"location":s.location} for s in db.scalars(select(TrainingSchedule).where(TrainingSchedule.group_id==g.id,TrainingSchedule.active.is_(True))).all()]
        out.append({"id":g.id,"name":g.name,"hall":{"id":hall.id,"name":hall.name,"address":hall.address,"phone":hall.phone} if hall else None,"athletes_count":count,"join_code":code.code if code else None,"schedule":schedule})
    return out

@router.get("/groups/{group_id}/athletes")
def group_athletes(group_id: str, c: CurrentUser = Depends(require_roles("trainer", "admin")), db: Session = Depends(get_db)):
    g=db.get(Group,group_id)
    if not g: raise HTTPException(404,"Group not found")
    if "admin" not in c.roles and g.trainer_user_id!=c.id: raise HTTPException(403,"Not your group")
    memberships=db.scalars(select(GroupMembership).where(GroupMembership.group_id==group_id,GroupMembership.status=="active")).all()
    out=[]
    for m in memberships:
        a=db.get(Athlete,m.athlete_id); p=db.get(Person,a.person_id) if a else None
        if not a or not p: continue
        attendance=db.scalars(select(Attendance).where(Attendance.athlete_id==a.id).order_by(Attendance.attendance_date.desc()).limit(30)).all()
        present=sum(1 for x in attendance if x.status=="present")
        out.append({"athlete_id":a.id,"name":f"{p.last_name} {p.first_name}","birth_date":str(p.birth_date) if p.birth_date else None,"rating_points":a.rating_points,"attendance":{"present":present,"total":len(attendance)}})
    return out
