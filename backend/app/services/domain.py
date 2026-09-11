from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Athlete, FamilyLink, GroupMembership, Person


def age_on(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def group_recipient_user_ids(db: Session, group_id: str) -> set[str]:
    user_ids: set[str] = set()
    memberships = db.scalars(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.status == "active",
        )
    ).all()

    for membership in memberships:
        athlete = db.get(Athlete, membership.athlete_id)
        if not athlete:
            continue

        person = db.get(Person, athlete.person_id)
        if person and person.user_id:
            user_ids.add(person.user_id)

        links = db.scalars(
            select(FamilyLink).where(FamilyLink.athlete_id == athlete.id)
        ).all()
        for link in links:
            parent = db.get(Person, link.parent_person_id)
            if parent and parent.user_id:
                user_ids.add(parent.user_id)

    return user_ids
