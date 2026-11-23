"""
Vercel ASGI entrypoint for PikCarz.

ROOT CAUSE: Vercel rewrites set scope["path"] to the destination ("/api/index").
raw_path is also the destination — no way to recover the original URL from scope alone.

FIX: vercel.json rewrite passes the original path as a query param:
  source: /api/(.*)  →  destination: /api/index?__path=$1
The VercelPathFix middleware reads __path from query_string, sets scope["path"]
back to the real URL, and strips __path so FastAPI never sees it.
"""
import os
import sys
from urllib.parse import parse_qs, urlencode

# ── backend/ path setup ──────────────────────────────────────────────────────
_this_file = os.path.abspath(__file__)
_api_dir   = os.path.dirname(_this_file)
_root_dir  = os.path.dirname(_api_dir)

for _candidate in [
    os.path.join(_root_dir, "backend"),
    os.path.join(_api_dir,  "..", "backend"),
    os.path.join(os.getcwd(), "backend"),
    "/var/task/backend",
]:
    _candidate = os.path.normpath(_candidate)
    if os.path.isdir(_candidate):
        if _candidate not in sys.path:
            sys.path.insert(0, _candidate)
        break


class VercelPathFix:
    """
    vercel.json rewrites /api/<anything> to /api/index?__path=<anything>.
    This middleware reads __path, restores scope["path"] = /api/<anything>,
    and removes __path from the query string before FastAPI sees the request.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            qs_str = scope.get("query_string", b"").decode("utf-8", "replace")
            params = parse_qs(qs_str, keep_blank_values=True)
            path_parts = params.pop("__path", None)
            if path_parts:
                original_path = "/api/" + path_parts[0]
                new_qs = urlencode(params, doseq=True).encode("utf-8")
                scope = {**scope, "path": original_path, "query_string": new_qs}
        await self.inner(scope, receive, send)


# ── load the real app ────────────────────────────────────────────────────────
_import_error = None
try:
    from app.main import app as _base_app
    app = VercelPathFix(_base_app)

except Exception as _exc:
    import traceback
    _import_error = traceback.format_exc()
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse

    _fallback = FastAPI()

    @_fallback.api_route(
        "/{full_path:path}",
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    )
    async def _error_handler(request: Request, full_path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "startup_import_failed",
                "traceback": _import_error,
                "scope_path": request.scope.get("path"),
                "query_string": request.scope.get("query_string", b"").decode(),
                "sys_path_0": sys.path[0] if sys.path else None,
            },
        )

    app = VercelPathFix(_fallback)
