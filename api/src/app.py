from pathlib import Path

from fastapi import FastAPI
from src.routers import apply
from src.embeddings.embed import EmbeddingManager
from src.store.chroma_db import VectorStore

def create_app() -> FastAPI:
    app = FastAPI()
    @app.get("/load")
    def load_docs():
        em = EmbeddingManager()
        vs = VectorStore(collection_name='resumes', persist_directory=Path("data"))
        query_vector = em.model.encode(
            ["query: I am looking for AI engineer with NLP experience. Experience with langchain and python is a plus"],
            normalize_embeddings=True
        )
        results = vs.collection.query(
            query_embeddings=query_vector,
            n_results=6
        )
        return {
            'results': results
        }
    app.include_router(apply.router)
    return app