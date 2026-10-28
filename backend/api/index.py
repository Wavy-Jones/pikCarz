"""
pikcarz.co.za — Vercel serverless entry point

PATH-FIX STRATEGY (layered, most-reliable first)
-------------------------------------------------
Vercel rewrites /(.*) → /api/index  which means scope["path"] = "/api/index"
for every incoming request.  We recover the original path via three strategies,
tried in order:

1. __vp query param  — set by vercel.json destination "?__vp=$1" when Vercel
   substitutes $1 in the query string (works on some runtime versions).
   Skipped if the value is the literal string "$1" (substitution didn't happen).

2. x-matched-path header — Vercel's routing layer sets this to the source-
   matched URL (i.e. the original request path) before calling the function.

3. Diagnostic fallback — if both fail we return a 200 JSON response containing
   all scope fields and all request headers so we can see exactly what Vercel
   is passing.  This is visible in the browser Network / Console tab.
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
    _import_error = {"type": type(_exc).__name__, "msg": str(_exc),
                     "traceback": _tb.format_exc()}

# Paths that indicate Vercel sent us the function destination, not the real URL
_FUNCTION_PATHS = {"", "/api/index", "api/index", "/$1", "$1"}


def _decode_headers(scope: Scope) -> dict[str, str]:
    result: dict[str, str] = {}
    for k, v in scope.get("headers", []):
        try:
            result[k.decode().lower()] = v.decode(errors="replace")
        except Exception:
            pass
    return result


async def _send_json(send: Send, status: int, body: dict) -> None:
    data = json.dumps(body, indent=2).encode()
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json"),
                            (b"access-control-allow-origin", b"*")]})
    await send({"type": "http.response.body", "body": data, "more_body": False})


class Handler:
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            if _fastapi_app:
                await _fastapi_app(scope, receive, send)
            return

        if _import_error:
            await _send_json(send, 500, {"error": "App import failed", **_import_error})
            return

        headers = _decode_headers(scope)
        raw_qs = scope.get("query_string", b"").decode(errors="replace")
        params = urllib.parse.parse_qs(raw_qs, keep_blank_values=True)

        real_path: str | None = None
        fix_source: str = "none"

        # ── Strategy 1: __vp from query string ───────────────────────────────
        vp = params.pop("__vp", [None])[0]
        if vp and vp not in ("$1", ""):
            candidate = ("/" + vp) if not vp.startswith("/") else vp
            if candidate not in _FUNCTION_PATHS:
                real_path = candidate
                fix_source = "__vp"

        # ── Strategy 2: x-matched-path (and siblings) ────────────────────────
        if real_path is None:
            for hdr in ("x-matched-path", "x-original-url", "x-forwarded-uri"):
                raw = headers.get(hdr, "").split("?")[0]
                candidate = ("/" + raw) if raw and not raw.startswith("/") else raw
                if candidate and candidate not in _FUNCTION_PATHS:
                    real_path = candidate
                    fix_source = hdr
                    break

        print(f"[pikcarz] method={scope.get('method')} "
              f"original={scope.get('path')!r} fix={fix_source} "
              f"real={real_path!r} vp={vp!r} "
              f"x-matched-path={headers.get('x-matched-path','NOT-SET')!r}",
              flush=True)

        # ── Strategy 3: diagnostic fallback ──────────────────────────────────
        if real_path is None or real_path in _FUNCTION_PATHS:
            diag = {
                "error": "pikcarz: cannot determine original request path",
                "scope_path": scope.get("path"),
                "scope_root_path": scope.get("root_path", ""),
                "scope_raw_path": scope.get("raw_path", b"").decode(errors="replace"),
                "scope_method": scope.get("method"),
                "scope_query_string_raw": raw_qs,
                "vp_param": vp,
                "fix_source": fix_source,
                "headers": {k: v for k, v in headers.items()
                            if not k.startswith("x-vercel-proxy")},
            }
            await _send_json(send, 200, diag)
            return

        # ── Apply the fix and route to FastAPI ────────────────────────────────
        remaining_qs = urllib.parse.urlencode(
            {k: v[0] for k, v in params.items()},
            quote_via=urllib.parse.quote,
        )
        scope = {
            **scope,
            "path": real_path,
            "raw_path": real_path.encode(),
            "query_string": remaining_qs.encode(),
        }
        await _fastapi_app(scope, receive, send)


handler = Handler()
