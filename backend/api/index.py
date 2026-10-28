"""
Vercel serverless entry point for pikCarz FastAPI backend.

Root cause fix: Vercel's uv-based Python runtime may set scope["path"] to
the function destination (/api/index) instead of the original request URL.
VercelPathFix corrects it from the x-matched-path header before FastAPI sees it.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from starlette.types import Scope, Receive, Send


class VercelPathFix:
    """
    Vercel's new uv runtime can pass the wrong scope['path'] to the ASGI app.
    It passes the function destination (/api/index) or empty string instead of
    the actual request path (/api/auth/login, /api/vehicles, etc.).

    Fix: read x-matched-path header (Vercel sets this to the original URL path)
    and override scope['path'] before FastAPI routes the request.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))

            matched = headers.get(b"x-matched-path", b"").decode()
            original = headers.get(b"x-forwarded-uri", b"").decode()
            host_url  = headers.get(b"x-vercel-deployment-url", b"").decode()

            # Pick the best path source: x-matched-path → x-forwarded-uri → scope
            candidate = (matched or original or "").split("?")[0]

            if candidate and candidate != scope.get("path", ""):
                scope = dict(scope)
                scope["path"] = candidate
                scope["raw_path"] = candidate.encode()

            # Guard: path must start with '/'
            if not scope.get("path", "").startswith("/"):
                scope = dict(scope)
                scope["path"] = "/" + scope.get("path", "")
                scope["raw_path"] = scope["path"].encode()

        await self.app(scope, receive, send)


# Import the real FastAPI application
try:
    from app.main import app as fastapi_app
    handler = VercelPathFix(fastapi_app)
except Exception as import_err:
    # If the app fails to import, return the error as JSON so we can debug
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import traceback

    fallback = FastAPI()

    @fallback.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    async def import_error_handler(path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "error": "App import failed",
                "detail": str(import_err),
                "traceback": traceback.format_exc(),
            },
        )

    handler = VercelPathFix(fallback)
