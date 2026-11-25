"""
Vercel ASGI entrypoint for PikCarz API.

Vercel custom 'routes' rewrites scope["path"] to the destination path,
so we wrap the FastAPI app to restore the original URL from the
x-matched-path or x-invoke-path headers that Vercel injects.
"""
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))   # backend/api/
_backend = os.path.dirname(_here)                     # backend/
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from app.main import app as _fastapi_app  # noqa: E402


class VercelPathRestore:
    """
    Vercel custom routes set scope['path'] to the destination (/api/index.py).
    The real request path is preserved in the 'x-matched-path' or
    'x-invoke-path' or 'x-forwarded-uri' request headers.
    This middleware restores scope['path'] before FastAPI sees it.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            scope = dict(scope)

            # Build a header lookup (lowercase keys)
            hdrs = {
                k.decode("utf-8", "replace").lower(): v.decode("utf-8", "replace")
                for k, v in scope.get("headers", [])
            }

            original = (
                hdrs.get("x-matched-path")
                or hdrs.get("x-invoke-path")
                or hdrs.get("x-forwarded-uri")
                or hdrs.get("x-original-url")
            )

            if original:
                # Strip query string if present
                scope["path"] = original.split("?")[0]

            print(
                f"[pikcarz] scope_path={scope.get('path')!r}"
                f"  original_header={original!r}",
                flush=True,
            )

        await self.inner(scope, receive, send)


app = VercelPathRestore(_fastapi_app)
