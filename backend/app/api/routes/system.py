from fastapi import APIRouter, Response
from app.db.session import ready
router=APIRouter(tags=["system"])
@router.get("/health")
def health(): return {"status":"ok","version":"Full Build 2.0"}
@router.get("/ready")
def readiness(response:Response):
    if not ready():
        response.status_code=503; return {"status":"not_ready"}
    return {"status":"ready"}
