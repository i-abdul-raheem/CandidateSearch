from pathlib import Path

from fastapi import FastAPI
from src.routers import apply
from src.ingest.data_loader import DataLoader

def create_app() -> FastAPI:
    app = FastAPI()
    @app.get("/load")
    def load_docs():
        loader = DataLoader(Path("data/pdf"))
        chunks = loader.split_documents()
        return {
            'docs': chunks
        }
    app.include_router(apply.router)
    return app