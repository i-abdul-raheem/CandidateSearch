from fastapi import FastAPI
from src.routers import apply, query

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(query.router)
    app.include_router(apply.router)
    return app
