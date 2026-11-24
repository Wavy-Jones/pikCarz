"""
Vercel catch-all for /api/** — wraps the real FastAPI app with a path fix.
Vercel strips the /api/ prefix when routing to api/[...path].py, so
scope["path"] arrives as e.g. "/test" instead of "/api/test".
This middleware prepends "/api" so FastAPI routes match correctly.
"""
import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"),
)

from app.main import app as _fastapi_app


class VercelPathFix:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            scope = dict(scope)
            path = scope.get("path", "")
            if not path.startswith("/api"):
                scope["path"] = "/api" + path
        await self.app(scope, receive, send)


app = VercelPathFix(_fastapi_app)
