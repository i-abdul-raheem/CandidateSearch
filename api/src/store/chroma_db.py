import hashlib
import re
from pathlib import Path

import chromadb


class VectorStore:
    PUBLIC_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
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
        if not embedded_list:
            raise ValueError("No indexable resume content was found.")
        self.collection.upsert(
            ids=[e["id"] for e in embedded_list],
            embeddings=[e["vector"] for e in embedded_list],
            metadatas=[self._clean_meta(e["metadata"]) for e in embedded_list],
            documents=[e["document"] for e in embedded_list],
        )

    def delete_resume(self, resume_id: str) -> None:
        self.collection.delete(where={"resume_id": resume_id})

    @staticmethod
    def public_resume_id(resume_id: str) -> str:
        """Return existing UUID IDs unchanged and anonymize legacy path IDs."""
        if VectorStore.PUBLIC_ID_PATTERN.fullmatch(resume_id):
            return resume_id
        return hashlib.sha256(resume_id.encode()).hexdigest()[:32]

    def resolve_resume_id(self, public_id: str) -> str | None:
        """Resolve a public ID to the internal Chroma ID, including legacy records."""
        if not self.PUBLIC_ID_PATTERN.fullmatch(public_id):
            return None

        direct = self.collection.get(where={"resume_id": public_id}, include=[])
        if direct.get("ids"):
            return public_id

        result = self.collection.get(include=["metadatas"])
        for metadata in result.get("metadatas") or []:
            if not metadata:
                continue
            internal_id = str(metadata.get("resume_id", ""))
            if internal_id and self.public_resume_id(internal_id) == public_id:
                return internal_id
        return None
