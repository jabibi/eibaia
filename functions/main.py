"""Entrypoint de Firebase Cloud Functions v2. Adapta la app FastAPI (ASGI) a una Cloud Function HTTP."""

from a2wsgi import ASGIMiddleware
from firebase_functions import https_fn

from app.core import firebase as _firebase_init  # noqa: F401  (inicializa Admin SDK)
from app.main import app as fastapi_app

_wsgi_app = ASGIMiddleware(fastapi_app)


@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response.from_app(_wsgi_app, req.environ)
