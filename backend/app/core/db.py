"""Compatibility exports for Full Build 2.1 routes.

Database ownership remains in app.db.*.  Some newer admin/CMS routes import
app.core.db, so this module deliberately re-exports the canonical objects
instead of creating a second SQLAlchemy engine/Base registry.
"""

from app.db.base import Base
from app.db.session import SessionLocal, engine, get_db, ready

__all__ = ["Base", "SessionLocal", "engine", "get_db", "ready"]
