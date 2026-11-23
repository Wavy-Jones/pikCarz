"""
TEMPORARY DIAGNOSTIC — dumps raw ASGI scope as JSON.
Replace with the real entrypoint once we know what Vercel passes.
"""
import json, sys

async def app(scope, receive, send):
    if scope.get("type") != "http":
        return

    hdrs = {k.decode("utf-8", "replace"): v.decode("utf-8", "replace")
            for k, v in scope.get("headers", [])}

    body = json.dumps({
        "path":         scope.get("path"),
        "raw_path":     scope.get("raw_path", b"").decode("utf-8", "replace"),
        "query_string": scope.get("query_string", b"").decode("utf-8", "replace"),
        "root_path":    scope.get("root_path", ""),
        "headers":      hdrs,
        "method":       scope.get("method"),
    }, indent=2).encode()

    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
            (b"access-control-allow-origin", b"*"),
        ],
    })
    await send({"type": "http.response.body", "body": body})
