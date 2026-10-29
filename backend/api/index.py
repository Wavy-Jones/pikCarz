"""PURE DEBUG — no FastAPI dependency, just dumps raw ASGI scope."""
import json

async def handler(scope, receive, send):
    if scope["type"] != "http":
        return

    headers = {k.decode(errors="replace"): v.decode(errors="replace")
               for k, v in scope.get("headers", [])}

    body = json.dumps({
        "scope_path":   scope.get("path", "__missing__"),
        "raw_path":     scope.get("raw_path", b"").decode(errors="replace"),
        "query_string": scope.get("query_string", b"").decode(errors="replace"),
        "method":       scope.get("method", ""),
        "headers":      headers,
    }, indent=2).encode()

    await send({"type": "http.response.start", "status": 200,
                "headers": [(b"content-type", b"application/json"),
                            (b"access-control-allow-origin", b"*"),
                            (b"content-length", str(len(body)).encode())]})
    await send({"type": "http.response.body", "body": body, "more_body": False})
