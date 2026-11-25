"""
Vercel catch-all entrypoint for PikCarz API.

File-based routing: Vercel calls this for all /api/** requests.
Vercel may strip the /api prefix from scope["path"] before calling us,
so we prepend it back if needed before FastAPI routes the request.
"""
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))   # backend/api/
_backend = os.path.dirname(_here)                     # backend/
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from app.main import app as _fastapi_app  # noqa: E402


class VercelPathFix:
    """Ensure scope['path'] starts with /api before FastAPI sees it."""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            scope = dict(scope)
            path = scope.get("path", "")
            if not path.startswith("/api"):
                scope["path"] = "/api" + path
            print(
                f"[pikcarz] path_in={scope.get('path')!r}  "
                f"root_path={scope.get('root_path', '')!r}",
                flush=True,
            )
        await self.inner(scope, receive, send)


app = VercelPathFix(_fastapi_app)
