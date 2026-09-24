from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditLog, Group, GroupMembership, Notification, Person, TrainingSchedule, User, UserRole, Athlete
from app.services.push import push_to_user
from app.services.security import CurrentUser, require_roles

router=APIRouter(prefix="/events",tags=["events"])

class EventIn(BaseModel):
    title:str=Field(min_length=1,max_length=255)
    body:str=Field(min_length=1,max_length=2000)
    event_type:str="federation_event"
    starts_at:datetime
    audience_role:str|None=None
    remind_minutes:int=Field(default=60,ge=0,le=10080)

EVENTS=[]

def _notify(db,user_id,event_type,title,body,url="/"):
    db.add(Notification(user_id=user_id,type=event_type,title=title,body=body))
    db.flush()
    return push_to_user(db,user_id,title,body,url=url,tag=event_type)

@router.get("/public")
def public_events():
    now=datetime.now(timezone.utc)
    return sorted([x for x in EVENTS if x["starts_at"]>=now],key=lambda x:x["starts_at"])[:50]

@router.post("/admin")
def create_event(x:EventIn,c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    if x.event_type not in {"federation_event","competition","holiday","news"}: raise HTTPException(400,"Invalid event type")
    row={"id":f"evt-{len(EVENTS)+1}","title":x.title.strip(),"body":x.body.strip(),"event_type":x.event_type,"starts_at":x.starts_at,"audience_role":x.audience_role,"remind_minutes":x.remind_minutes}
    EVENTS.append(row)
    db.add(AuditLog(actor_user_id=c.id,action="event.create",entity_type="event",entity_id=row["id"],metadata_json={"type":x.event_type,"starts_at":x.starts_at.isoformat()}));db.commit();return row

@router.post("/admin/run-birthdays")
def run_birthdays(c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    today=date.today();sent=0;push=0
    people=db.scalars(select(Person).where(Person.birth_date.is_not(None),Person.user_id.is_not(None))).all()
    for p in people:
        if p.birth_date.month==today.month and p.birth_date.day==today.day:
            title="С днём рождения!"
            body=f"{p.first_name}, Федерация бокса поздравляет Вас с днём рождения!"
            exists=db.scalar(select(Notification).where(Notification.user_id==p.user_id,Notification.type=="birthday",Notification.title==title))
            if not exists: push+=_notify(db,p.user_id,"birthday",title,body);sent+=1
    db.add(AuditLog(actor_user_id=c.id,action="events.birthdays.run",entity_type="notification",metadata_json={"sent":sent,"push":push}));db.commit();return {"sent":sent,"push":push}

@router.post("/admin/run-training-reminders")
def run_training_reminders(c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    now=datetime.now();weekday=now.weekday();sent=0;push=0
    schedules=db.scalars(select(TrainingSchedule).where(TrainingSchedule.weekday==weekday,TrainingSchedule.active==True)).all()
    for sc in schedules:
        start=datetime.combine(now.date(),sc.start_time);minutes=(start-now).total_seconds()/60
        if 0<=minutes<=120:
            memberships=db.scalars(select(GroupMembership).where(GroupMembership.group_id==sc.group_id,GroupMembership.status=="active")).all()
            for m in memberships:
                athlete=db.get(Athlete,m.athlete_id);person=db.get(Person,athlete.person_id) if athlete else None
                if person and person.user_id:
                    body=f"Сегодня тренировка в {str(sc.start_time)[:5]}. {sc.location or ''}".strip();push+=_notify(db,person.user_id,"training_reminder","Напоминание о тренировке",body);sent+=1
    db.add(AuditLog(actor_user_id=c.id,action="events.training_reminders.run",entity_type="notification",metadata_json={"sent":sent,"push":push}));db.commit();return {"sent":sent,"push":push}

@router.post("/admin/run-event-reminders")
def run_event_reminders(c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    now=datetime.now(timezone.utc);sent=0;push=0
    for e in EVENTS:
        mins=(e["starts_at"]-now).total_seconds()/60
        if 0<=mins<=e["remind_minutes"]:
            users=db.scalars(select(User).where(User.status=="active")).all()
            for u in users:
                if e["audience_role"] and not db.scalar(select(UserRole).where(UserRole.user_id==u.id,UserRole.role==e["audience_role"])): continue
                push+=_notify(db,u.id,"event_reminder",e["title"],e["body"]);sent+=1
    db.add(AuditLog(actor_user_id=c.id,action="events.reminders.run",entity_type="event",metadata_json={"sent":sent,"push":push}));db.commit();return {"sent":sent,"push":push}
