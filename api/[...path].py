"""
PURE BARE ASGI — no FastAPI, no imports.
Returns 200 with the raw scope as JSON for ANY request.
If this still returns {"detail":"Not Found"}, our function is NOT being called.
"""
import json


async def app(scope, receive, send):
    if scope.get("type") != "http":
        return

    hdrs = {
        k.decode("utf-8", "replace"): v.decode("utf-8", "replace")
        for k, v in scope.get("headers", [])
    }
    body = json.dumps({
        "served_by": "api/[...path].py BARE ASGI v2",
        "path": scope.get("path"),
        "raw_path": scope.get("raw_path", b"").decode("utf-8", "replace"),
        "root_path": scope.get("root_path", ""),
        "method": scope.get("method"),
        "headers": hdrs,
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
