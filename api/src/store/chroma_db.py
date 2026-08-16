from pathlib import Path
from uuid import uuid4

import chromadb
from chromadb.api.types import Metadata
from langchain_core.documents import Document
import numpy as np


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
            self.collection_name, metadata={"description": "candidate resumes"}
        )

    def add_document(self, documents: list[Document], embeddings: np.ndarray) -> None:
        if len(documents) != len(embeddings):
            raise ValueError(
                "Length of documents should be equal to the length of embeddings"
            )

        ids: list[str] = []
        documents_text: list[str] = []
        metadatas: list[Metadata] = []
        embeddings_list: list[np.ndarray] = []

        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            doc_id: str = uuid4().hex[:8]
            ids.append(doc_id)
            documents_text.append(doc.page_content)
            embeddings_list.append(embedding.tolist())
            metadata = dict(doc.metadata)
            metadatas.append(metadata)

        self.collection.add(ids, embeddings_list, metadatas, documents_text)
