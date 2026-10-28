"""
pikcarz.co.za — Vercel serverless entry point (diagnostic + smart-fix build)

Every request logs the full ASGI scope to stdout (visible in Vercel → Logs →
Runtime Logs).  A path patch is applied ONLY when scope["path"] is empty or is
"/api/index" (i.e., clearly the function destination, not the real URL).
Any other path is passed through untouched — the previous VercelPathFix was
overwriting the correct path with x-matched-path=/api/index, causing the 404.
"""
import sys
import json
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


# ── ASGI handler ──────────────────────────────────────────────────────────────
class Handler:
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Pass non-HTTP events straight through (WebSocket lifespan, etc.)
        if scope["type"] != "http":
            if _fastapi_app:
                await _fastapi_app(scope, receive, send)
            return

        # ── Decode headers ────────────────────────────────────────────────────
        headers: dict[str, str] = {}
        for k, v in scope.get("headers", []):
            try:
                headers[k.decode().lower()] = v.decode(errors="replace")
            except Exception:
                pass

        # ── Snapshot what Vercel actually sent us ─────────────────────────────
        original_path = scope.get("path", "")
        diag = {
            "original_path": original_path,
            "root_path": scope.get("root_path", ""),
            "raw_path": scope.get("raw_path", b"").decode(errors="replace"),
            "method": scope.get("method", ""),
            "x-matched-path": headers.get("x-matched-path", "NOT-SET"),
            "x-forwarded-uri": headers.get("x-forwarded-uri", "NOT-SET"),
            "x-original-url": headers.get("x-original-url", "NOT-SET"),
            "x-vercel-id": headers.get("x-vercel-id", "NOT-SET"),
            "import_ok": _import_error is None,
        }
        # Always print — visible in Vercel → Logs → Runtime Logs
        print(f"[pikcarz-diag] {json.dumps(diag)}", flush=True)

        # ── Handle import failure ─────────────────────────────────────────────
        if _import_error:
            body = json.dumps({
                "error": "App import failed",
                **_import_error,
            }).encode()
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

        # ── Fix path ONLY if it is clearly wrong ─────────────────────────────
        # The previous VercelPathFix was unconditionally overwriting scope["path"]
        # with x-matched-path. When x-matched-path == "/api/index" (the Vercel
        # function destination) and scope["path"] was already the real URL, the
        # "fix" corrupted the path and caused all 404s.
        #
        # Safe rule: only patch when the path is clearly the function destination.
        WRONG_PATHS = {"", "/api/index", "api/index"}
        if original_path in WRONG_PATHS:
            for hdr in ("x-matched-path", "x-original-url", "x-forwarded-uri"):
                candidate = headers.get(hdr, "").split("?")[0]
                if candidate and candidate not in WRONG_PATHS:
                    scope = {**scope, "path": candidate, "raw_path": candidate.encode()}
                    print(
                        f"[pikcarz-diag] path patched via {hdr}: "
                        f"{original_path!r} → {candidate!r}",
                        flush=True,
                    )
                    break

        # Ensure path starts with /
        p = scope.get("path", "/")
        if not p.startswith("/"):
            scope = {**scope, "path": "/" + p, "raw_path": ("/" + p).encode()}

        # ── Route to real app, capturing response status for logging ──────────
        status_holder: list[int | None] = [None]

        async def capturing_send(msg):
            if msg["type"] == "http.response.start":
                status_holder[0] = msg.get("status")
                print(
                    f"[pikcarz-diag] response: status={msg.get('status')} "
                    f"path={scope.get('path')}",
                    flush=True,
                )
            await send(msg)

        await _fastapi_app(scope, receive, capturing_send)


handler = Handler()
