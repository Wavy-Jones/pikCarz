"""
pikcarz.co.za — Vercel serverless entry point

Layered path recovery + 404-intercepting diagnostics.
"""
import sys, json, urllib.parse
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

_fastapi_app = None
_import_error = None
try:
    from app.main import app as _fastapi_app
except Exception as _exc:
    import traceback as _tb
    _import_error = {"type": type(_exc).__name__, "msg": str(_exc), "traceback": _tb.format_exc()}

_FUNCTION_PATHS = {"", "/api/index", "api/index", "/$1", "$1", "/api/index/"}

def _decode_headers(scope):
    result = {}
    for k, v in scope.get("headers", []):
        try: result[k.decode().lower()] = v.decode(errors="replace")
        except: pass
    return result

async def _send_json(send, status, body):
    data = json.dumps(body, indent=2).encode()
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json"), (b"access-control-allow-origin", b"*")]})
    await send({"type": "http.response.body", "body": data, "more_body": False})

class _CaptureSend:
    """Intercepts FastAPI's response; if 404, replaces with diagnostic JSON."""
    def __init__(self, real_send, diag_data):
        self._real_send = real_send
        self._diag = diag_data
        self._status = None
        self._is_404 = False
        self._chunks = []

    async def __call__(self, message):
        t = message.get("type")
        if t == "http.response.start":
            self._status = message["status"]
            if self._status == 404:
                self._is_404 = True
                return  # hold — don't forward yet
            await self._real_send(message)
        elif t == "http.response.body":
            if self._is_404:
                self._chunks.append(message.get("body", b""))
                if not message.get("more_body", False):
                    original = b"".join(self._chunks).decode(errors="replace")
                    self._diag["fastapi_404_body"] = original
                    self._diag["error"] = "pikcarz: FastAPI returned 404 for recovered path"
                    await _send_json(self._real_send, 200, self._diag)
            else:
                await self._real_send(message)
        else:
            if not self._is_404:
                await self._real_send(message)

class Handler:
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            if _fastapi_app: await _fastapi_app(scope, receive, send)
            return
        if _import_error:
            await _send_json(send, 500, {"error": "App import failed", **_import_error})
            return

        headers = _decode_headers(scope)
        raw_qs = scope.get("query_string", b"").decode(errors="replace")
        params = urllib.parse.parse_qs(raw_qs, keep_blank_values=True)
        real_path = None
        fix_source = "none"

        # Strategy 1: __vp query param (skip if Vercel didn't substitute $1)
        vp = params.pop("__vp", [None])[0]
        if vp and vp not in ("$1", ""):
            candidate = ("/" + vp) if not vp.startswith("/") else vp
            if candidate not in _FUNCTION_PATHS:
                real_path = candidate
                fix_source = "__vp"

        # Strategy 2: x-matched-path and siblings
        if real_path is None:
            for hdr in ("x-matched-path", "x-original-url", "x-forwarded-uri"):
                raw = headers.get(hdr, "").split("?")[0]
                candidate = ("/" + raw) if raw and not raw.startswith("/") else raw
                if candidate and candidate not in _FUNCTION_PATHS:
                    real_path = candidate
                    fix_source = hdr
                    break

        remaining_qs = urllib.parse.urlencode(
            {k: v[0] for k, v in params.items()}, quote_via=urllib.parse.quote
        )

        diag_data = {
            "scope_path": scope.get("path"),
            "scope_root_path": scope.get("root_path", ""),
            "scope_method": scope.get("method"),
            "scope_query_string_raw": raw_qs,
            "vp_param": vp,
            "fix_source": fix_source,
            "real_path_recovered": real_path,
            "headers_relevant": {
                k: v for k, v in headers.items()
                if any(k.startswith(p) for p in ("x-matched", "x-original", "x-forwarded", "host", "x-vercel"))
                and not k.startswith("x-vercel-proxy")
            },
            "all_headers": {k: v for k, v in headers.items() if not k.startswith("x-vercel-proxy")},
        }

        # Strategy 3: diagnostic fallback (no path recovered)
        if real_path is None or real_path in _FUNCTION_PATHS:
            diag_data["error"] = "pikcarz: cannot determine original request path"
            await _send_json(send, 200, diag_data)
            return

        new_scope = {**scope, "path": real_path, "raw_path": real_path.encode(),
                     "query_string": remaining_qs.encode()}
        capture = _CaptureSend(send, diag_data)
        await _fastapi_app(new_scope, receive, capture)

handler = Handler()
