from pathlib import Path

import chromadb


class VectorStore:
    def __init__(self, collection_name: str, persist_directory: Path | None = None):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self._initiate_store()

    def _initiate_store(self) -> None:
        if self.persist_directory:
            Path(self.persist_directory).mkdir(exist_ok=True, parents=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
        else:
            self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            self.collection_name, metadata={"hnsw:space": "cosine"}
        )
        
    def _clean_meta(self, meta: dict) -> dict:
        clean = {}
        for k, v in meta.items():
            if v is None:
                continue
            if isinstance(v, (str, int, float, bool)):
                clean[k] = v
            elif isinstance(v, list):
                # ["Python", "AWS"] -> "Python, AWS"
                clean[k] = ", ".join(map(str, v))
            else:
                clean[k] = str(v)
        return clean

    def add_documents(self, embedded_list: list) -> None:
        self.collection.add(
            ids=[e["id"] for e in embedded_list],
            embeddings=[e["vector"] for e in embedded_list],
            metadatas=[self._clean_meta(e["metadata"]) for e in embedded_list],
            documents=[e["document"] for e in embedded_list],
        )
