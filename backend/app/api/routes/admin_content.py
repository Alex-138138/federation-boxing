from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.deps import require_roles
from app.models import models as m

router=APIRouter(prefix='/admin/content',tags=['admin-content'])
admin_dep=require_roles('admin')

class ContentPayload(BaseModel):
    key:str
    title:str=''
    snapshot:dict={}

@router.get('/pages')
def pages(db:Session=Depends(get_db), user=Depends(admin_dep)):
    rows=db.query(m.CmsPage).order_by(m.CmsPage.key).all()
    return [{'id':x.id,'key':x.key,'title':x.title,'published_version_id':x.published_version_id} for x in rows]

@router.get('/pages/{key}/versions')
def versions(key:str,db:Session=Depends(get_db),user=Depends(admin_dep)):
    page=db.query(m.CmsPage).filter(m.CmsPage.key==key).first()
    if not page: raise HTTPException(404,'page_not_found')
    rows=db.query(m.CmsVersion).filter(m.CmsVersion.page_id==page.id).order_by(m.CmsVersion.id.desc()).all()
    return [{'id':x.id,'created_at':x.created_at,'snapshot':x.snapshot} for x in rows]
