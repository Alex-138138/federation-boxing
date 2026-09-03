from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import JoinCode, Hall, Group, User, Person

router = APIRouter(prefix="/qr", tags=["qr"])

@router.get("/resolve/{code}")
def resolve(code: str, db: Session = Depends(get_db)):
    invite = db.scalar(select(JoinCode).where(JoinCode.code == code, JoinCode.active.is_(True)))
    if not invite: raise HTTPException(404, "Join code not found")
    hall=db.get(Hall,invite.hall_id); group=db.get(Group,invite.group_id) if invite.group_id else None
    trainer=db.get(User,invite.trainer_user_id); trainer_person=db.scalar(select(Person).where(Person.user_id==invite.trainer_user_id))
    return {"code":code,"hall":{"id":hall.id,"name":hall.name,"address":hall.address,"phone":hall.phone} if hall else None,"group":{"id":group.id,"name":group.name} if group else None,"trainer":{"name":f"{trainer_person.last_name} {trainer_person.first_name}" if trainer_person else "Тренер"} if trainer else None}
