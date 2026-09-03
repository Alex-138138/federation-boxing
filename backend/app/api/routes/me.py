from fastapi import APIRouter, Depends
from app.services.security import get_current_user, CurrentUser
router = APIRouter(prefix="/me", tags=["me"])

@router.get("/roles")
def roles(c: CurrentUser = Depends(get_current_user)):
    return {"roles": sorted(c.roles)}

@router.get("")
def me(c: CurrentUser = Depends(get_current_user)):
    return {"id": c.id, "phone": c.phone, "roles": sorted(c.roles)}
