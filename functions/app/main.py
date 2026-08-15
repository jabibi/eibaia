from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.users.router import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(title="ElosuE! API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users_router, prefix="/api")

    return app


app = create_app()
