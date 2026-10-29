"""
Vercel serverless entry point for PikCarz API.

Vercel rewrites /api/* -> /api/index but passes scope["path"] = "/api/index"
(the destination), NOT the original path.  We recover the real path from the
x-now-route-matches header that Vercel injects, e.g. "1=auth/login" for a
request to /api/auth/login, then patch scope before forwarding to FastAPI.
"""
import sys
import os

_backend = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from app.main import app as _fastapi_app  # noqa: E402


def _recover_path(scope: dict) -> str:
    """Extract the real request path from Vercel's x-now-route-matches header."""
    headers: dict[bytes, bytes] = dict(scope.get("headers", []))
    route_matches = headers.get(b"x-now-route-matches", b"").decode()
    if route_matches:
        for seg in route_matches.split("|"):
            seg = seg.strip()
            if seg.startswith("1="):
                captured = seg[2:]          # e.g. "auth/login"
                return "/api/" + captured   # -> "/api/auth/login"
    return scope.get("path", "/")


async def handler(scope, receive, send):
    if scope["type"] == "http":
        real_path = _recover_path(scope)
        scope = dict(scope)
        scope["path"] = real_path
        scope["raw_path"] = real_path.encode()
    await _fastapi_app(scope, receive, send)
