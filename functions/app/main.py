from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.finance.router import router as finance_router
from app.modules.system.router import router as system_router
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
    app.include_router(finance_router, prefix="/api")
    app.include_router(system_router, prefix="/api")

    return app


app = create_app()
