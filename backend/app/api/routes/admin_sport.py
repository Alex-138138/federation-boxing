from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Achievement, Athlete, Attendance, Group, GroupMembership, Hall, Person, RatingHistory
from app.services.security import CurrentUser, require_roles

router = APIRouter(prefix="/admin/sport", tags=["admin-sport"])


@router.get("/athletes")
def athletes(
    c: CurrentUser = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    result = []
    for athlete in db.scalars(select(Athlete).order_by(Athlete.id)).all():
        person = db.get(Person, athlete.person_id)
        membership = db.scalar(
            select(GroupMembership).where(
                GroupMembership.athlete_id == athlete.id,
                GroupMembership.status == "active",
            )
        )
        group = db.get(Group, membership.group_id) if membership else None
        hall = db.get(Hall, group.hall_id) if group else None
        result.append(
            {
                "id": athlete.id,
                "name": f"{person.last_name} {person.first_name}" if person else "",
                "birth_date": person.birth_date if person else None,
                "phone": person.phone if person else None,
                "rating_points": athlete.rating_points,
                "status": athlete.status,
                "group_id": group.id if group else None,
                "group": group.name if group else None,
                "hall_id": hall.id if hall else None,
                "hall": hall.name if hall else None,
            }
        )
    return result


@router.get("/athletes/{athlete_id}/history")
def athlete_history(
    athlete_id: str,
    c: CurrentUser = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(404, "Athlete not found")

    achievements = db.scalars(
        select(Achievement)
        .where(Achievement.athlete_id == athlete_id)
        .order_by(Achievement.event_date.desc())
    ).all()
    ratings = db.scalars(
        select(RatingHistory)
        .where(RatingHistory.athlete_id == athlete_id)
        .order_by(RatingHistory.created_at.desc())
    ).all()
    attendance = db.scalars(
        select(Attendance)
        .where(Attendance.athlete_id == athlete_id)
        .order_by(Attendance.attendance_date.desc())
        .limit(100)
    ).all()

    return {
        "athlete_id": athlete.id,
        "rating_points": athlete.rating_points,
        "achievements": [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "event_date": item.event_date,
            }
            for item in achievements
        ],
        "rating": [
            {
                "id": item.id,
                "before": item.points_before,
                "after": item.points_after,
                "reason": item.reason,
                "created_at": item.created_at,
            }
            for item in ratings
        ],
        "attendance": [
            {
                "id": item.id,
                "date": item.attendance_date,
                "status": item.status,
                "group_id": item.group_id,
            }
            for item in attendance
        ],
    }
