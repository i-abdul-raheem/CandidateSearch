from functools import cached_property, lru_cache
from pathlib import Path

class ServiceContainer:
    def __init__(self):
        pass

    @cached_property
    def get_embedding_manager(self):
        from src.embeddings.embed import EmbeddingManager
        return EmbeddingManager("intfloat/multilingual-e5-large")

    @cached_property
    def get_vector_store(self):
        from src.store.chroma_db import VectorStore
        return VectorStore(collection_name='resumes', persist_directory=Path("data"))

    @cached_property
    def get_data_loader(self):
        from src.ingest.data_loader import DataLoader
        return DataLoader(data_dir=Path("data/pdf"))


@lru_cache(maxsize=1)
def get_service_container() -> ServiceContainer:
    """Return the shared service container for this application process."""
    return ServiceContainer()
