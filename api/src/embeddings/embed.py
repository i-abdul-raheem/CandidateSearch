from typing import Any

from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer


class EmbeddingManager:
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name
        self._load_model()

    def _load_model(self) -> None:
        try:
            if not self.model_name:
                self.model_name = "intfloat/multilingual-e5-large"
            self.model = SentenceTransformer(self.model_name)
            print(f"Embeddings model loaded. Model: {self.model_name}")
        except Exception as e:
            raise e

    def generate_embeddings(self, chunks: list[Document]) -> list[Any]:
        if not self.model:
            raise ValueError("Model not loaded")
        valid_chunks = [
            c for c in chunks if c.page_content and len(c.page_content.strip()) > 20
        ]
        if not valid_chunks:
            return []

        text_for_embeddings = [f"passage: {c.page_content}" for c in valid_chunks]

        embeddings = self.model.encode(
            text_for_embeddings,
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return [
            {
                "id": f"{c.metadata.get('source', 'doc')}_{c.metadata.get('chunk_type', 'other')}_{i}",
                "vector": emb.tolist(),
                "document": c.page_content,  # clean text, no prefix
                "metadata": {
                    "resume_id": str(c.metadata.get("source", f"doc_{i}")),
                    "chunk_type": c.metadata.get("chunk_type", "other"),
                    **c.metadata,
                },
            }
            for i, (c, emb) in enumerate(zip(valid_chunks, embeddings))
        ]
