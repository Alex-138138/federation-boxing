import secrets
from datetime import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Hall, Group, JoinCode, TrainingSchedule, AuditLog
from app.services.security import require_roles, CurrentUser

router=APIRouter(prefix="/admin/manage",tags=["admin-manage"])

class HallIn(BaseModel):
    name:str; address:str; phone:str|None=None
class GroupIn(BaseModel):
    name:str; hall_id:str; trainer_user_id:str
class ScheduleIn(BaseModel):
    weekday:int; start_time:time; end_time:time; location:str|None=None

@router.post("/halls")
def create_hall(x:HallIn,c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    h=Hall(name=x.name,address=x.address,phone=x.phone); db.add(h); db.flush()
    db.add(AuditLog(actor_user_id=c.id,action="hall.create",entity_type="hall",entity_id=h.id)); db.commit()
    return {"id":h.id,"name":h.name}

@router.post("/groups")
def create_group(x:GroupIn,c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    if not db.get(Hall,x.hall_id): raise HTTPException(404,"Hall not found")
    g=Group(name=x.name,hall_id=x.hall_id,trainer_user_id=x.trainer_user_id); db.add(g); db.flush()
    code="BOX-"+secrets.token_hex(3).upper(); db.add(JoinCode(code=code,hall_id=g.hall_id,trainer_user_id=g.trainer_user_id,group_id=g.id))
    db.add(AuditLog(actor_user_id=c.id,action="group.create",entity_type="group",entity_id=g.id)); db.commit()
    return {"id":g.id,"name":g.name,"join_code":code}

@router.post("/groups/{group_id}/schedule")
def add_schedule(group_id:str,x:ScheduleIn,c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    g=db.get(Group,group_id)
    if not g: raise HTTPException(404,"Group not found")
    s=TrainingSchedule(group_id=group_id,weekday=x.weekday,start_time=x.start_time,end_time=x.end_time,location=x.location); db.add(s); db.commit()
    return {"ok":True,"id":s.id}
