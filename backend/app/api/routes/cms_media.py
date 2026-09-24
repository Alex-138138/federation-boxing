import base64
import imghdr
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.services.security import CurrentUser, require_roles

router = APIRouter(prefix="/cms/media", tags=["cms-media"])
MEDIA_ROOT = Path("/app/media")
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
MAX_BYTES = 5 * 1024 * 1024
ALLOWED = {"jpeg": "jpg", "png": "png", "gif": "gif", "webp": "webp"}

class MediaIn(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    data_base64: str = Field(min_length=8)

@router.post("")
def upload_media(x: MediaIn, c: CurrentUser = Depends(require_roles("admin"))):
    raw = x.data_base64.split(",", 1)[-1]
    try:
        data = base64.b64decode(raw, validate=True)
    except Exception:
        raise HTTPException(400, "Invalid base64 image")
    if not data or len(data) > MAX_BYTES:
        raise HTTPException(400, "Image must be between 1 byte and 5 MB")
    kind = imghdr.what(None, data)
    if kind not in ALLOWED:
        raise HTTPException(400, "Only JPEG, PNG, GIF and WebP images are allowed")
    name = f"{secrets.token_hex(16)}.{ALLOWED[kind]}"
    (MEDIA_ROOT / name).write_bytes(data)
    return {"url": f"/media/{name}", "filename": x.filename, "size": len(data)}
