"""
Vercel ASGI entrypoint for PikCarz API (root-level deployment).
The variable MUST be named 'app' for Vercel's Python runtime to detect it.
"""
import os
import sys

# Robust backend/ discovery — works whether __file__ is absolute or relative
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

# --- Import the real app, with a diagnostic fallback so errors are visible ---
_import_error: str | None = None
try:
    from app.main import app  # noqa: E402
except Exception as _exc:
    import traceback
    _import_error = traceback.format_exc()
    # Create a minimal fallback app that exposes the error so we can diagnose
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
    async def _error_handler(full_path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "startup_import_failed",
                "traceback": _import_error,
                "sys_path_0": sys.path[0] if sys.path else None,
                "backend_exists": os.path.isdir(os.path.join(_root_dir, "backend")),
            },
        )
