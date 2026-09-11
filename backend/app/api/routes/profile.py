from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    Achievement,
    Athlete,
    Attendance,
    FamilyLink,
    Group,
    GroupMembership,
    Hall,
    Person,
    TrainingSchedule,
)
from app.services.security import CurrentUser, get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


def _active_membership(db: Session, athlete_id: str) -> GroupMembership | None:
    return db.scalar(
        select(GroupMembership).where(
            GroupMembership.athlete_id == athlete_id,
            GroupMembership.status == "active",
        )
    )


def _trainer_info(db: Session, group: Group | None) -> dict | None:
    if not group:
        return None
    trainer = db.scalar(select(Person).where(Person.user_id == group.trainer_user_id))
    if not trainer:
        return {"user_id": group.trainer_user_id, "name": None, "phone": None}
    name = " ".join(
        part for part in (trainer.last_name, trainer.first_name, trainer.middle_name) if part
    )
    return {"user_id": group.trainer_user_id, "name": name, "phone": trainer.phone}


def _ensure_athlete_access(
    athlete: Athlete,
    person: Person,
    group: Group | None,
    c: CurrentUser,
    db: Session,
) -> None:
    if "admin" in c.roles:
        return
    if person.user_id == c.id:
        return
    if "trainer" in c.roles and group and group.trainer_user_id == c.id:
        return
    parent = db.scalar(
        select(Person)
        .join(FamilyLink, FamilyLink.parent_person_id == Person.id)
        .where(FamilyLink.athlete_id == athlete.id, Person.user_id == c.id)
    )
    if parent:
        return
    raise HTTPException(403, "No access")


@router.get("/athlete/{athlete_id}")
def athlete_profile(
    athlete_id: str,
    c: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(404, "Athlete not found")
    person = db.get(Person, athlete.person_id)
    if not person:
        raise HTTPException(404, "Athlete person not found")

    membership = _active_membership(db, athlete.id)
    group = db.get(Group, membership.group_id) if membership else None
    hall = db.get(Hall, group.hall_id) if group else None
    _ensure_athlete_access(athlete, person, group, c, db)

    schedule = []
    if group:
        rows = db.scalars(
            select(TrainingSchedule).where(
                TrainingSchedule.group_id == group.id,
                TrainingSchedule.active.is_(True),
            )
        ).all()
        schedule = [
            {
                "weekday": row.weekday,
                "start_time": str(row.start_time),
                "end_time": str(row.end_time),
                "location": row.location,
            }
            for row in rows
        ]

    achievements = [
        {
            "title": row.title,
            "description": row.description,
            "event_date": str(row.event_date) if row.event_date else None,
        }
        for row in db.scalars(
            select(Achievement).where(Achievement.athlete_id == athlete.id)
        ).all()
    ]

    return {
        "id": athlete.id,
        "name": " ".join(
            part for part in (person.last_name, person.first_name, person.middle_name) if part
        ),
        "phone": person.phone,
        "birth_date": str(person.birth_date) if person.birth_date else None,
        "gender": person.gender,
        "rating_points": athlete.rating_points,
        "group": group.name if group else None,
        "group_id": group.id if group else None,
        "hall": (
            {"id": hall.id, "name": hall.name, "address": hall.address, "phone": hall.phone}
            if hall
            else None
        ),
        "trainer": _trainer_info(db, group),
        "schedule": schedule,
        "achievements": achievements,
    }


@router.get("/children")
def my_children(
    c: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    parent = db.scalar(select(Person).where(Person.user_id == c.id))
    if not parent:
        return []
    links = db.scalars(
        select(FamilyLink).where(FamilyLink.parent_person_id == parent.id)
    ).all()
    out = []
    for link in links:
        athlete = db.get(Athlete, link.athlete_id)
        person = db.get(Person, athlete.person_id) if athlete else None
        if not athlete or not person:
            continue
        out.append(
            {
                "athlete_id": athlete.id,
                "name": " ".join(
                    part for part in (person.last_name, person.first_name, person.middle_name) if part
                ),
                "rating_points": athlete.rating_points,
                "relationship": link.relationship,
                "is_primary": link.is_primary,
            }
        )
    return out


@router.get("/me-athlete")
def my_athlete(
    c: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    person = db.scalar(select(Person).where(Person.user_id == c.id))
    if not person:
        raise HTTPException(404, "Athlete profile not found")
    athlete = db.scalar(select(Athlete).where(Athlete.person_id == person.id))
    if not athlete:
        raise HTTPException(404, "Athlete profile not found")
    return {"athlete_id": athlete.id}


@router.get("/athlete/{athlete_id}/attendance")
def athlete_attendance(
    athlete_id: str,
    c: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(404, "Athlete not found")
    person = db.get(Person, athlete.person_id)
    if not person:
        raise HTTPException(404, "Athlete person not found")
    membership = _active_membership(db, athlete.id)
    group = db.get(Group, membership.group_id) if membership else None
    _ensure_athlete_access(athlete, person, group, c, db)

    rows = db.scalars(
        select(Attendance)
        .where(Attendance.athlete_id == athlete_id)
        .order_by(Attendance.attendance_date.desc())
        .limit(100)
    ).all()
    return [
        {"date": str(row.attendance_date), "status": row.status, "group_id": row.group_id}
        for row in rows
    ]
