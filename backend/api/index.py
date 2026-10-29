"""
Vercel ASGI entrypoint for PikCarz API.

How it works:
  backend/vercel.json rewrites every request:
    /(.*) → /api/index?__vp=$1
  So /api/auth/login becomes /api/index?__vp=api/auth/login.
  We recover the original path from __vp and pass the fixed scope to FastAPI.

Vercel requires the entrypoint variable to be named 'app' (not 'handler').
"""
import os
import sys
from urllib.parse import parse_qs

# Ensure 'backend/' is on sys.path so `from app.main import app` resolves
_here = os.path.dirname(os.path.abspath(__file__))          # backend/api/
_backend = os.path.dirname(_here)                            # backend/
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from app.main import app as _fastapi_app  # noqa: E402


async def app(scope, receive, send):
    """ASGI entrypoint — recover original path from __vp then delegate to FastAPI."""
    if scope["type"] == "http":
        qs_raw = scope.get("query_string", b"")
        params = parse_qs(qs_raw.decode("utf-8", errors="replace"))

        if "__vp" in params:
            original_path = "/" + params["__vp"][0].lstrip("/")
            # Rebuild query string without __vp
            remaining = "&".join(
                f"{k}={v[0]}" for k, v in params.items() if k != "__vp"
            )
            scope = {
                **scope,
                "path": original_path,
                "raw_path": original_path.encode("utf-8"),
                "query_string": remaining.encode("utf-8"),
            }

    await _fastapi_app(scope, receive, send)
