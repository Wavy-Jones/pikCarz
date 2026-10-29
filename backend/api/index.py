"""
Vercel serverless entry point for PikCarz API.

Root vercel.json rewrites  /api/(.*)  →  /backend/api/index
which means Vercel sets scope["path"] = "/backend/api/index" (the
destination), not the original request path.

The original path is recoverable from the x-now-route-matches header
that Vercel injects for every rewritten request.  For a rule whose
source is  /api/(.*),  the header value for a request to
/api/auth/login  will be  "1=auth/login"  (capture-group 1).

We reconstruct "/api/" + group-1, overwrite scope["path"], and hand
the scope to the real FastAPI application.
"""
import sys
import os

# Make  backend/  importable so  `from app.main import app`  works.
_backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from app.main import app as _fastapi_app   # noqa: E402


def _recover_path(scope: dict) -> str:
    """
    Return the real request path from Vercel routing headers.

    Priority:
      1. x-now-route-matches  – "1=auth/login" → "/api/auth/login"
      2. x-matched-path       – may contain the pre-rewrite path
      3. scope["path"]        – last resort (will be the function path)
    """
    headers: dict[bytes, bytes] = dict(scope.get("headers", []))

    # ── Strategy 1: x-now-route-matches ─────────────────────────────────────
    route_matches = headers.get(b"x-now-route-matches", b"").decode()
    if route_matches:
        for seg in route_matches.split("|"):
            seg = seg.strip()
            if seg.startswith("1="):
                return "/api/" + seg[2:]  # e.g. "/api/auth/login"

    # ── Strategy 2: x-matched-path ──────────────────────────────────────────
    matched = headers.get(b"x-matched-path", b"").decode().strip()
    if matched and matched not in ("/backend/api/index", "/api/index", ""):
        return matched

    # ── Fallback ─────────────────────────────────────────────────────────────
    return scope.get("path", "/")


async def handler(scope, receive, send):
    if scope["type"] == "http":
        real_path = _recover_path(scope)
        scope = dict(scope)          # make it mutable
        scope["path"] = real_path
        scope["raw_path"] = real_path.encode()

    await _fastapi_app(scope, receive, send)
