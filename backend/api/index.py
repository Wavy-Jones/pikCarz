"""
pikcarz.co.za — NUCLEAR DEBUG
Returns diagnostic JSON for EVERY request so we can see exactly
what Vercel puts in scope/headers. Remove once fixed.
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

def _decode_headers(scope):
    result = {}
    for k, v in scope.get("headers", []):
        try: result[k.decode().lower()] = v.decode(errors="replace")
        except: pass
    return result

async def _send_json(send, status, body):
    try:
        data = json.dumps(body, indent=2, default=str).encode()
    except Exception as e:
        data = json.dumps({"json_error": str(e)}).encode()
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-type", b"application/json"),
                            (b"access-control-allow-origin", b"*")]})
    await send({"type": "http.response.body", "body": data, "more_body": False})

class Handler:
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            if _fastapi_app:
                await _fastapi_app(scope, receive, send)
            return

        headers = _decode_headers(scope)
        raw_qs = scope.get("query_string", b"").decode(errors="replace")
        params = urllib.parse.parse_qs(raw_qs, keep_blank_values=True)

        diag = {
            "import_error": _import_error,
            "scope_type": scope.get("type"),
            "scope_method": scope.get("method"),
            "scope_path": scope.get("path"),
            "scope_root_path": scope.get("root_path", ""),
            "scope_raw_path": scope.get("raw_path", b"").decode(errors="replace"),
            "scope_query_string": raw_qs,
            "query_params": {k: v for k, v in params.items()},
            "headers": {k: v for k, v in headers.items()
                        if not k.startswith("x-vercel-proxy")},
        }
        await _send_json(send, 200, diag)

handler = Handler()
