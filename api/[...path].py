"""
Vercel catch-all Python handler — no rewrites needed.
Named [...path].py so Vercel routes /api/* here with scope["path"]
set to the ACTUAL requested path, not the destination.
"""
import os
import sys

_this_file = os.path.abspath(__file__)
_api_dir   = os.path.dirname(_this_file)
_root_dir  = os.path.dirname(_api_dir)

for _candidate in [
    os.path.join(_root_dir, "backend"),
    os.path.join(_api_dir, "..", "backend"),
    os.path.join(os.getcwd(), "backend"),
    "/var/task/backend",
]:
    _candidate = os.path.normpath(_candidate)
    if os.path.isdir(_candidate):
        if _candidate not in sys.path:
            sys.path.insert(0, _candidate)
        break

try:
    from app.main import app

except Exception as _exc:
    import traceback
    _tb = traceback.format_exc()
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
                "traceback": _tb,
                "scope_path": request.scope.get("path"),
                "sys_path_0": sys.path[0] if sys.path else None,
            },
        )

    app = _fallback
