"""
Diagnostic catch-all — returns raw scope info for every request.
Tells us: which file Vercel is actually calling, what scope["path"] is,
and whether scope["query_string"] carries the __path= param.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
)
async def catch_all(request: Request, full_path: str = ""):
    return JSONResponse({
        "served_by":        "[...path].py",
        "url":              str(request.url),
        "scope_path":       request.scope.get("path"),
        "query_string":     request.scope.get("query_string", b"").decode(),
        "query_params":     dict(request.query_params),
        "headers":          dict(request.headers),
    })
