"""Static contract checks for critical Full Build 2.1 routes.

FastAPI composes a final URL from APIRouter(prefix=...) plus each route
path. Validate those source fragments separately instead of searching for
the fully composed URL as one literal string.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

checks = {
    "backend/app/api/routes/cms.py": [
        'router = APIRouter(tags=["cms"])',
        '@router.get("/public/pages/{page_key}")',
        '@router.post("/cms/pages/{page_key}/save")',
        '@router.post("/cms/pages/{page_key}/publish/{version_id}")',
    ],
    "backend/app/api/routes/profile.py": [
        'APIRouter(prefix="/profile"',
        '@router.get("/children")',
        '@router.get("/me-athlete")',
    ],
    "backend/app/api/routes/trainer.py": [
        'APIRouter(prefix="/trainer"',
        '@router.get("/groups")',
    ],
    "backend/app/api/routes/admin_console.py": [
        'APIRouter(prefix="/admin/console"',
        '@router.get("/users")',
        '@router.get("/halls")',
        '@router.get("/groups")',
        '@router.get("/applications")',
        '@router.get("/messages")',
    ],
}

failed = []
for rel, needles in checks.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            failed.append(f"{rel}: missing source fragment {needle}")

if failed:
    raise SystemExit("\n".join(failed))

print("API contract static checks: OK")
