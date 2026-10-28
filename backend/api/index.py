"""
pikcarz.co.za — Vercel serverless entry point

PATH-FIX STRATEGY
-----------------
Vercel's rewrite rule  /(.*) → /api/index?__vp=$1  injects the original
request path into the query string as the `__vp` parameter.
e.g. POST /api/auth/login → scope["path"]="/api/index",
     scope["query_string"]="__vp=api/auth/login"

This handler reads `__vp`, reconstructs the real path, strips `__vp` from
the query string, and forwards the corrected scope to FastAPI.

No guessing about x-matched-path — we control the parameter ourselves.
"""
import sys
import json
import urllib.parse
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from starlette.types import Scope, Receive, Send

# ── Import the real FastAPI app ───────────────────────────────────────────────
_fastapi_app = None
_import_error = None
try:
    from app.main import app as _fastapi_app
except Exception as _exc:
    import traceback as _tb
    _import_error = {
        "type": type(_exc).__name__,
        "msg": str(_exc),
        "traceback": _tb.format_exc(),
    }


class Handler:
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Pass non-HTTP events through (WebSocket, lifespan, etc.)
        if scope["type"] != "http":
            if _fastapi_app:
                await _fastapi_app(scope, receive, send)
            return

        # ── Handle import failure early ───────────────────────────────────────
        if _import_error:
            body = json.dumps({"error": "App import failed", **_import_error}).encode()
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"access-control-allow-origin", b"*"),
                ],
            })
            await send({"type": "http.response.body", "body": body, "more_body": False})
            return

        # ── Decode query string and extract __vp ─────────────────────────────
        raw_qs = scope.get("query_string", b"").decode(errors="replace")
        params = urllib.parse.parse_qs(raw_qs, keep_blank_values=True)

        vp = params.pop("__vp", [None])[0]   # original path from rewrite capture

        if vp is not None:
            # Reconstruct the real path (capture group has no leading slash)
            real_path = ("/" + vp) if not vp.startswith("/") else vp
            # Rebuild query string without __vp
            remaining_qs = urllib.parse.urlencode(
                {k: v[0] for k, v in params.items()}, quote_via=urllib.parse.quote
            )
            scope = {
                **scope,
                "path": real_path,
                "raw_path": real_path.encode(),
                "query_string": remaining_qs.encode(),
            }
            print(f"[pikcarz] path restored from __vp: {real_path!r} qs={remaining_qs!r}", flush=True)
        else:
            # No __vp — request reached us without the rewrite (direct /api/index call)
            print(f"[pikcarz] no __vp; path={scope.get('path')!r}", flush=True)

        # ── Forward to FastAPI ────────────────────────────────────────────────
        await _fastapi_app(scope, receive, send)


handler = Handler()
