"""Static contract check for the authentication flow.

FastAPI composes APIRouter(prefix="/auth") with the individual route paths,
so check the prefix and decorators separately instead of looking for the
fully-composed URL as one literal string in auth.py.
"""
from pathlib import Path

p = Path("backend/app/api/routes/auth.py")
assert p.exists(), "auth route missing"
s = p.read_text(encoding="utf-8")

assert 'prefix="/auth"' in s or "prefix='/auth'" in s, "missing auth router prefix /auth"
for route in ["/request-code", "/verify-code"]:
    assert route in s, f"missing auth route {route}"

print("Auth flow contract: OK")
