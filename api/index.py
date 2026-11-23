"""
Vercel ASGI entrypoint for PikCarz.

FIX: routes config passes the original path as ?__path=<rest>.
VercelPathFix reads it and restores scope["path"] before FastAPI routes.
Logging added so Vercel runtime logs show exactly what the function receives.
"""
import os
import sys
from urllib.parse import unquote

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
    Routes config: /api/(?<rest>.*) -> /api/index?__path=$rest
    This middleware reads __path from query_string and sets scope["path"]
    to the real requested URL before FastAPI routes the request.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            qs = scope.get("query_string", b"").decode("utf-8", "replace")
            current_path = scope.get("path", "")

            # Simple string parsing — no library dependencies
            path_val = None
            remaining_parts = []
            for part in qs.split("&"):
                if part.startswith("__path="):
                    path_val = unquote(part[len("__path="):])
                elif part:
                    remaining_parts.append(part)

            print(
                f"[VFIX] scope_path={current_path!r} "
                f"qs={qs!r} "
                f"path_val={path_val!r}",
                file=sys.stderr,
                flush=True,
            )

            if path_val is not None:
                original_path = "/api/" + path_val
                new_qs = "&".join(remaining_parts).encode("utf-8")
                scope = {**scope, "path": original_path, "query_string": new_qs}
                print(f"[VFIX] restored path={original_path!r}", file=sys.stderr, flush=True)

        await self.inner(scope, receive, send)


# ── load the real app ────────────────────────────────────────────────────────
_import_error = None
try:
    from app.main import app as _base_app
    print(f"[VFIX] app loaded OK: {type(_base_app)}", file=sys.stderr, flush=True)
    app = VercelPathFix(_base_app)

except Exception as _exc:
    import traceback
    _import_error = traceback.format_exc()
    print(f"[VFIX] IMPORT FAILED:\n{_import_error}", file=sys.stderr, flush=True)
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
