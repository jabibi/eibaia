"""Firebase Cloud Functions v2 entrypoint. Adapts the FastAPI (ASGI) app to an HTTP Cloud Function.

Builds the ASGI "scope" by hand from the Request (Flask/Werkzeug) handed over by
`https_fn.on_request`, and uses `asgiref.sync.async_to_sync` to invoke the FastAPI app
synchronously. `a2wsgi` is avoided because its WSGI bridge hangs in this environment.
"""

from firebase_functions import https_fn
from asgiref.sync import async_to_sync

from app.core import firebase as _firebase_init  # noqa: F401  (initializes the Admin SDK)
from app.main import app as fastapi_app


def _call_asgi_app(req: https_fn.Request) -> https_fn.Response:
    response_start: dict = {}
    body_chunks: list[bytes] = []

    async def receive():
        return {"type": "http.request", "body": req.get_data(), "more_body": False}

    async def send(message):
        if message["type"] == "http.response.start":
            response_start["status"] = message["status"]
            response_start["headers"] = message.get("headers", [])
        elif message["type"] == "http.response.body":
            body_chunks.append(message.get("body", b""))

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": req.method,
        "path": req.path,
        "raw_path": req.path.encode(),
        "root_path": "",
        "query_string": req.query_string,
        "headers": [(k.lower().encode(), v.encode()) for k, v in req.headers.items()],
        "scheme": req.scheme,
        "client": (req.remote_addr or "", 0),
        "server": (req.host.split(":")[0], 443 if req.scheme == "https" else 80),
    }

    async_to_sync(fastapi_app)(scope, receive, send)

    headers = [(k.decode(), v.decode()) for k, v in response_start.get("headers", [])]
    return https_fn.Response(
        b"".join(body_chunks),
        status=response_start.get("status", 500),
        headers=headers,
    )


@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    return _call_asgi_app(req)
