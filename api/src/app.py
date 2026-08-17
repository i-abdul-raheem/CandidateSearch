from fastapi import FastAPI
from src.routers import apply, query, explain

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(query.router)
    app.include_router(apply.router)
    app.include_router(explain.router)
    return app
