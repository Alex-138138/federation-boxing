import uuid
from sqlalchemy import String, Integer, Boolean, Date, Time, DateTime, ForeignKey, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def uid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    phone: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="active")

class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String(32), primary_key=True)

class Person(Base):
    __tablename__ = "persons"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[object | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(32), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

class Hall(Base):
    __tablename__ = "halls"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(500))
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)

class Group(Base):
    __tablename__ = "groups"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    hall_id: Mapped[str] = mapped_column(ForeignKey("halls.id"))
    trainer_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))

class TrainingSchedule(Base):
    __tablename__ = "training_schedules"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"))
    weekday: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[object] = mapped_column(Time)
    end_time: Mapped[object] = mapped_column(Time)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Athlete(Base):
    __tablename__ = "athletes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    person_id: Mapped[str] = mapped_column(ForeignKey("persons.id"), unique=True)
    rating_points: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="active")

class GroupMembership(Base):
    __tablename__ = "group_memberships"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"))
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id"))
    status: Mapped[str] = mapped_column(String(32), default="active")

class FamilyLink(Base):
    __tablename__ = "family_links"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    parent_person_id: Mapped[str] = mapped_column(ForeignKey("persons.id"))
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id"))
    relationship: Mapped[str] = mapped_column(String(64))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

class JoinCode(Base):
    __tablename__ = "join_codes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hall_id: Mapped[str] = mapped_column(ForeignKey("halls.id"))
    trainer_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[str | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Application(Base):
    __tablename__ = "applications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    applicant_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    hall_id: Mapped[str] = mapped_column(ForeignKey("halls.id"))
    trainer_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[str | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    application_type: Mapped[str] = mapped_column(String(32), default="child")
    status: Mapped[str] = mapped_column(String(32), default="submitted")
    snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    athlete_id: Mapped[str | None] = mapped_column(ForeignKey("athletes.id"), nullable=True)

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    author_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"))
    text: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())

class MessageReceipt(Base):
    __tablename__ = "message_receipts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    delivered_at: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
    read_at: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)

class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"))
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id"))
    attendance_date: Mapped[object] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32))
    marked_by: Mapped[str] = mapped_column(ForeignKey("users.id"))

class Achievement(Base):
    __tablename__ = "achievements"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_date: Mapped[object | None] = mapped_column(Date, nullable=True)

class RatingHistory(Base):
    __tablename__ = "rating_history"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    athlete_id: Mapped[str] = mapped_column(ForeignKey("athletes.id"))
    points_before: Mapped[int] = mapped_column(Integer)
    points_after: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(255))
    changed_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())

class PushSubscription(Base):
    __tablename__ = "push_subscriptions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    endpoint: Mapped[str] = mapped_column(String(2000), unique=True)
    p256dh: Mapped[str | None] = mapped_column(String(512), nullable=True)
    auth: Mapped[str | None] = mapped_column(String(512), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Page(Base):
    __tablename__ = "pages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    page_key: Mapped[str] = mapped_column(String(120), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    published_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

class PageVersion(Base):
    __tablename__ = "page_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    page_id: Mapped[str] = mapped_column(ForeignKey("pages.id"))
    version_no: Mapped[int] = mapped_column(Integer)
    snapshot: Mapped[dict] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
    published_at: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    entity_type: Mapped[str] = mapped_column(String(120))
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
