async def handler(scope, receive, send):
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [(b"content-type", b"text/plain"), (b"access-control-allow-origin", b"*")],
    })
    await send({
        "type": "http.response.body",
        "body": b"PIKCARZ_HANDLER_ALIVE",
        "more_body": False,
    })
