from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Achievement, Athlete, Attendance, Group, GroupMembership, RatingHistory
from app.services.security import CurrentUser, require_roles

router = APIRouter(prefix="/sport", tags=["sport"])


class AttendanceIn(BaseModel):
    athlete_id: str
    attendance_date: date
    status: str = Field(min_length=1, max_length=32)


class AchievementIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class RatingIn(BaseModel):
    points: int
    reason: str = Field(min_length=1, max_length=1000)


def _active_membership(db: Session, athlete_id: str, group_id: str | None = None) -> GroupMembership | None:
    query = select(GroupMembership).where(
        GroupMembership.athlete_id == athlete_id,
        GroupMembership.status == "active",
    )
    if group_id is not None:
        query = query.where(GroupMembership.group_id == group_id)
    return db.scalar(query)


def _require_trainer_access_to_athlete(db: Session, c: CurrentUser, athlete_id: str) -> GroupMembership | None:
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(404, "Athlete not found")
    if "admin" in c.roles:
        return _active_membership(db, athlete_id)

    memberships = db.scalars(
        select(GroupMembership).where(
            GroupMembership.athlete_id == athlete_id,
            GroupMembership.status == "active",
        )
    ).all()
    for membership in memberships:
        group = db.get(Group, membership.group_id)
        if group and group.trainer_user_id == c.id:
            return membership
    raise HTTPException(403, "Athlete is not in your group")


@router.post("/groups/{group_id}/attendance")
def mark_attendance(
    group_id: str,
    x: AttendanceIn,
    c: CurrentUser = Depends(require_roles("trainer", "admin")),
    db: Session = Depends(get_db),
):
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(404, "Group not found")
    if "admin" not in c.roles and group.trainer_user_id != c.id:
        raise HTTPException(403, "Not your group")
    if not db.get(Athlete, x.athlete_id):
        raise HTTPException(404, "Athlete not found")
    if not _active_membership(db, x.athlete_id, group_id):
        raise HTTPException(400, "Athlete is not an active member of this group")

    db.add(
        Attendance(
            group_id=group_id,
            athlete_id=x.athlete_id,
            attendance_date=x.attendance_date,
            status=x.status.strip(),
            marked_by=c.id,
        )
    )
    db.commit()
    return {"ok": True}


@router.post("/athletes/{athlete_id}/achievements")
def add_achievement(
    athlete_id: str,
    x: AchievementIn,
    c: CurrentUser = Depends(require_roles("trainer", "admin")),
    db: Session = Depends(get_db),
):
    _require_trainer_access_to_athlete(db, c, athlete_id)
    title = x.title.strip()
    if not title:
        raise HTTPException(400, "Achievement title cannot be empty")
    db.add(Achievement(athlete_id=athlete_id, title=title, description=x.description))
    db.commit()
    return {"ok": True}


@router.post("/athletes/{athlete_id}/rating")
def change_rating(
    athlete_id: str,
    x: RatingIn,
    c: CurrentUser = Depends(require_roles("trainer", "admin")),
    db: Session = Depends(get_db),
):
    _require_trainer_access_to_athlete(db, c, athlete_id)
    athlete = db.get(Athlete, athlete_id)
    before = athlete.rating_points
    reason = x.reason.strip()
    if not reason:
        raise HTTPException(400, "Rating change reason cannot be empty")
    athlete.rating_points = x.points
    db.add(
        RatingHistory(
            athlete_id=athlete.id,
            points_before=before,
            points_after=x.points,
            reason=reason,
            changed_by=c.id,
        )
    )
    db.commit()
    return {"athlete_id": athlete.id, "rating_points": athlete.rating_points}
