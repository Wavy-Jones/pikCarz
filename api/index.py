"""
Vercel ASGI entrypoint for PikCarz API (root-level deployment).
The variable MUST be named 'app' for Vercel's Python runtime to detect it.

ROOT CAUSE: Vercel rewrites set scope["path"] to the DESTINATION ("/api/index"),
not the original URL ("/api/auth/login"). FastAPI never sees the real path.
FIX: VercelPathFix middleware reads scope["raw_path"] (which preserves the
original URL) and overwrites scope["path"] before FastAPI routes the request.
"""
import os
import sys

# Robust backend/ discovery
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
    Vercel rewrites deliver scope["path"] = "/api/index" for every request,
    regardless of the actual URL the browser requested. The original URL is
    preserved in scope["raw_path"] (bytes). This middleware copies raw_path
    back into scope["path"] so FastAPI routes work correctly.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            raw = scope.get("raw_path")
            if raw:
                # raw_path is bytes like b"/api/auth/login" or b"/api/auth/login?foo=bar"
                fixed = raw.decode("utf-8", "replace").split("?")[0]
                if fixed:
                    scope = {**scope, "path": fixed}
        await self.inner(scope, receive, send)


_import_error = None
try:
    from app.main import app as _base_app
    app = VercelPathFix(_base_app)

except Exception as _exc:
    import traceback
    _import_error = traceback.format_exc()
    # Diagnostic fallback: expose the exact import error so we can fix it
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    _fallback = FastAPI()

    @_fallback.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
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

    app = VercelPathFix(_fallback)
