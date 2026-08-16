from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .pdf_parser import parse_resume

class DataLoader:
    def __init__(self, data_dir : Path):
        self.data_dir = data_dir
        if not self.data_dir.exists():
            raise ValueError("Data directory not found!")
        self._documents: list[Document] = self._load_docs()
    
    def _load_docs(self) -> list[Document]:
        docs: list[Document] = []
        for resume in list(self.data_dir.rglob("*.pdf")):
            doc = parse_resume(resume)
            doc.metadata['source'] = str(resume)
            docs.append(doc)
        return docs
    
    def split_documents(self):
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        return splitter.split_documents(self._documents)