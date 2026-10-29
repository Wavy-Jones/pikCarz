"""
Vercel serverless entry point for PikCarz API.

backend/vercel.json rewrites every request as:
    /(.*) -> /api/index?__vp=$1

So the real path arrives as the __vp query parameter.
We extract it, patch scope["path"], then hand off to FastAPI.
"""
import sys
import os
from urllib.parse import parse_qs

_backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.main import app as _fastapi_app  # noqa: E402


def _recover_path(scope: dict) -> str:
    qs = scope.get("query_string", b"").decode()
    params = parse_qs(qs, keep_blank_values=True)
    if "__vp" in params:
        return "/" + params["__vp"][0]        # e.g. /api/auth/login
    return scope.get("path", "/")


async def handler(scope, receive, send):
    if scope["type"] == "http":
        real_path = _recover_path(scope)

        # Rebuild query string without __vp so FastAPI never sees it
        qs = scope.get("query_string", b"").decode()
        clean_qs = "&".join(p for p in qs.split("&") if p and not p.startswith("__vp="))

        scope = dict(scope)
        scope["path"] = real_path
        scope["raw_path"] = real_path.encode()
        scope["query_string"] = clean_qs.encode()

    await _fastapi_app(scope, receive, send)
