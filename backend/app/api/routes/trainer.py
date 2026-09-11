from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Athlete, Attendance, Group, GroupMembership, Hall, JoinCode, Person, TrainingSchedule
from app.services.security import CurrentUser, require_roles

router = APIRouter(prefix="/trainer", tags=["trainer"])


@router.get("/groups")
def my_groups(
    c: CurrentUser = Depends(require_roles("trainer", "admin")),
    db: Session = Depends(get_db),
):
    query = select(Group)
    if "admin" not in c.roles:
        query = query.where(Group.trainer_user_id == c.id)

    rows = db.scalars(query.order_by(Group.name)).all()
    result = []
    for group in rows:
        hall = db.get(Hall, group.hall_id)
        code = db.scalar(
            select(JoinCode).where(
                JoinCode.group_id == group.id,
                JoinCode.active.is_(True),
            )
        )
        athlete_count = db.scalar(
            select(func.count())
            .select_from(GroupMembership)
            .where(
                GroupMembership.group_id == group.id,
                GroupMembership.status == "active",
            )
        ) or 0
        schedule_rows = db.scalars(
            select(TrainingSchedule)
            .where(
                TrainingSchedule.group_id == group.id,
                TrainingSchedule.active.is_(True),
            )
            .order_by(TrainingSchedule.weekday, TrainingSchedule.start_time)
        ).all()
        schedule = [
            {
                "weekday": item.weekday,
                "start_time": str(item.start_time),
                "end_time": str(item.end_time),
                "location": item.location,
            }
            for item in schedule_rows
        ]
        result.append(
            {
                "id": group.id,
                "name": group.name,
                "hall": {
                    "id": hall.id,
                    "name": hall.name,
                    "address": hall.address,
                    "phone": hall.phone,
                }
                if hall
                else None,
                "athletes_count": athlete_count,
                "join_code": code.code if code else None,
                "schedule": schedule,
            }
        )
    return result


@router.get("/groups/{group_id}/athletes")
def group_athletes(
    group_id: str,
    c: CurrentUser = Depends(require_roles("trainer", "admin")),
    db: Session = Depends(get_db),
):
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(404, "Group not found")
    if "admin" not in c.roles and group.trainer_user_id != c.id:
        raise HTTPException(403, "Not your group")

    memberships = db.scalars(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.status == "active",
        )
    ).all()
    result = []
    for membership in memberships:
        athlete = db.get(Athlete, membership.athlete_id)
        person = db.get(Person, athlete.person_id) if athlete else None
        if not athlete or not person:
            continue

        attendance = db.scalars(
            select(Attendance)
            .where(
                Attendance.athlete_id == athlete.id,
                Attendance.group_id == group_id,
            )
            .order_by(Attendance.attendance_date.desc())
            .limit(30)
        ).all()
        present = sum(1 for item in attendance if item.status == "present")
        result.append(
            {
                "athlete_id": athlete.id,
                "name": f"{person.last_name} {person.first_name}",
                "birth_date": str(person.birth_date) if person.birth_date else None,
                "rating_points": athlete.rating_points,
                "attendance": {"present": present, "total": len(attendance)},
            }
        )
    return result
