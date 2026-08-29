from __future__ import annotations

import base64
import io
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
PAYLOAD = ROOT / ".payload"

parts = sorted(PAYLOAD.glob("part*.b64"))
if len(parts) != 6:
    raise SystemExit(f"Expected 6 payload parts, found {len(parts)}")

encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
data = base64.b64decode(encoded, validate=True)

with zipfile.ZipFile(io.BytesIO(data)) as zf:
    bad = zf.testzip()
    if bad:
        raise SystemExit(f"Corrupted archive member: {bad}")
    zf.extractall(ROOT)

print("Full Build 1.0 restored successfully.")
print("Next: docker compose up --build")
