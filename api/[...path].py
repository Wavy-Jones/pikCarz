"""
MINIMAL TEST — bare FastAPI, no backend imports.
If /api/test returns {"status":"routing_works"}, routing is fine
and the problem is in the backend import chain.
If it still returns {"detail":"Not Found"}, the path Vercel passes
does NOT start with /api and we need to see the raw scope.
"""
import json
from fastapi import FastAPI, Request

_app = FastAPI()


@_app.get("/api/test")
async def test_route(request: Request):
    return {
        "status": "routing_works",
        "scope_path": request.scope.get("path"),
        "root_path": request.scope.get("root_path", ""),
        "url_path": str(request.url.path),
    }


@_app.get("/test")
async def test_no_prefix(request: Request):
    return {
        "status": "routing_works_no_prefix",
        "scope_path": request.scope.get("path"),
        "root_path": request.scope.get("root_path", ""),
    }


# Bare ASGI wrapper — logs the raw scope path before FastAPI sees it
class ScopeLogger:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            print(
                f"[pikcarz-raw] path={scope.get('path')!r}"
                f" root_path={scope.get('root_path', '')!r}",
                flush=True,
            )
        await self.inner(scope, receive, send)


app = ScopeLogger(_app)
