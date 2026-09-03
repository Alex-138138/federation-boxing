from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Page, PageVersion, AuditLog
from app.services.security import require_roles, CurrentUser

router = APIRouter(tags=["cms"])

class PageSave(BaseModel):
    title: str
    blocks: list[dict]

@router.get("/public/pages/{page_key}")
def public_page(page_key:str,db:Session=Depends(get_db)):
    page=db.scalar(select(Page).where(Page.page_key==page_key))
    if not page or not page.published_version_id:
        raise HTTPException(404,"Published page not found")
    version=db.get(PageVersion,page.published_version_id)
    if not version: raise HTTPException(404,"Published version not found")
    return version.snapshot

@router.get("/cms/pages/{page_key}")
def admin_page(page_key:str,c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    page=db.scalar(select(Page).where(Page.page_key==page_key))
    if not page:
        return {"page_key":page_key,"title":"","blocks":[],"published_version_id":None}
    versions=db.scalars(select(PageVersion).where(PageVersion.page_id==page.id).order_by(PageVersion.version_no.desc())).all()
    return {
        "page_key":page.page_key,
        "title":page.title,
        "published_version_id":page.published_version_id,
        "versions":[{"id":v.id,"version_no":v.version_no,"snapshot":v.snapshot,"published_at":v.published_at} for v in versions]
    }

@router.post("/cms/pages/{page_key}/save")
def save(page_key:str,x:PageSave,c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    page=db.scalar(select(Page).where(Page.page_key==page_key))
    if not page:
        page=Page(page_key=page_key,title=x.title)
        db.add(page); db.flush()
    page.title=x.title
    max_v=db.scalar(select(func.max(PageVersion.version_no)).where(PageVersion.page_id==page.id)) or 0
    snapshot={"page_key":page_key,"title":x.title,"blocks":x.blocks}
    v=PageVersion(page_id=page.id,version_no=max_v+1,snapshot=snapshot,created_by=c.id)
    db.add(v); db.flush()
    db.add(AuditLog(actor_user_id=c.id,action="cms.save",entity_type="page",entity_id=page.id))
    db.commit()
    return {"version_id":v.id,"version_no":v.version_no}

@router.post("/cms/pages/{page_key}/publish/{version_id}")
def publish(page_key:str,version_id:str,c:CurrentUser=Depends(require_roles("admin")),db:Session=Depends(get_db)):
    page=db.scalar(select(Page).where(Page.page_key==page_key))
    v=db.get(PageVersion,version_id)
    if not page or not v or v.page_id!=page.id:
        raise HTTPException(404,"Version not found")
    page.published_version_id=v.id
    v.published_at=datetime.now(timezone.utc)
    db.add(AuditLog(actor_user_id=c.id,action="cms.publish",entity_type="page",entity_id=page.id))
    db.commit()
    return {"ok":True,"published_version_id":v.id}
