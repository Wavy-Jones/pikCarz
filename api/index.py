"""
DEBUG handler — dumps raw scope and headers so we can see exactly what
Vercel passes to the ASGI function.  Remove once routing is confirmed.
"""
import json

async def handler(scope, receive, send):
    if scope["type"] != "http":
        return

    headers_raw = scope.get("headers", [])
    headers = {k.decode(errors="replace"): v.decode(errors="replace") for k, v in headers_raw}

    body = json.dumps({
        "scope_path":   scope.get("path", "__missing__"),
        "raw_path":     scope.get("raw_path", b"__missing__").decode(errors="replace"),
        "query_string": scope.get("query_string", b"").decode(),
        "method":       scope.get("method", ""),
        "headers":      headers,
    }, indent=2).encode()

    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [
            (b"content-type", b"application/json"),
            (b"access-control-allow-origin", b"*"),
            (b"content-length", str(len(body)).encode()),
        ],
    })
    await send({
        "type": "http.response.body",
        "body": body,
        "more_body": False,
    })
