from fastapi import FastAPI
from src.routers import apply

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(apply.router)
    return app