from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Page, PageVersion
from app.services.security import CurrentUser, require_roles

router = APIRouter(prefix="/admin/content", tags=["admin-content"])


@router.get("/pages")
def pages(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_roles("admin")),
):
    rows = db.scalars(select(Page).order_by(Page.page_key)).all()
    return [
        {
            "id": page.id,
            "key": page.page_key,
            "page_key": page.page_key,
            "title": page.title,
            "published_version_id": page.published_version_id,
        }
        for page in rows
    ]


@router.get("/pages/{key}/versions")
def versions(
    key: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_roles("admin")),
):
    page = db.scalar(select(Page).where(Page.page_key == key))
    if not page:
        raise HTTPException(status_code=404, detail="page_not_found")

    rows = db.scalars(
        select(PageVersion)
        .where(PageVersion.page_id == page.id)
        .order_by(PageVersion.version_no.desc())
    ).all()

    return [
        {
            "id": version.id,
            "version_no": version.version_no,
            "created_at": version.created_at,
            "published_at": version.published_at,
            "snapshot": version.snapshot,
            "is_published": version.id == page.published_version_id,
        }
        for version in rows
    ]
