"""
Vercel catch-all for /api/** with diagnostic logging.
"""
import sys
import os
import json

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend"),
)

try:
    from app.main import app as _fastapi_app
    IMPORT_OK = True
    IMPORT_ERROR = None
except Exception as _exc:
    import traceback as _tb
    IMPORT_OK = False
    IMPORT_ERROR = _tb.format_exc()
    _fastapi_app = None


class VercelPathFix:
    def __init__(self, inner_app):
        self.inner_app = inner_app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            scope = dict(scope)
            original_path = scope.get("path", "")
            if not original_path.startswith("/api"):
                scope["path"] = "/api" + original_path
            # This line appears in Vercel function logs
            print(
                f"[pikcarz] import_ok={IMPORT_OK}"
                f"  original_path={original_path!r}"
                f"  fixed_path={scope['path']!r}",
                flush=True,
            )

        if not IMPORT_OK:
            body = json.dumps(
                {"error": "import_failed", "detail": IMPORT_ERROR}
            ).encode()
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                    (b"access-control-allow-origin", b"*"),
                ],
            })
            await send({"type": "http.response.body", "body": body})
            return

        await self.inner_app(scope, receive, send)


app = VercelPathFix(_fastapi_app)
