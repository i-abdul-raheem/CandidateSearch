from functools import cached_property, lru_cache
from src.config import Settings, settings

class ServiceContainer:
    def __init__(self, config: Settings = settings):
        self.config = config

    @cached_property
    def get_embedding_manager(self):
        from src.embeddings.embed import EmbeddingManager
        return EmbeddingManager(self.config.embedding_model)

    @cached_property
    def get_vector_store(self):
        from src.store.chroma_db import VectorStore
        return VectorStore(collection_name="resumes", persist_directory=self.config.data_dir)

    @cached_property
    def get_data_loader(self):
        from src.ingest.data_loader import DataLoader
        return DataLoader(data_dir=self.config.resume_dir)

    @cached_property
    def get_metadata_store(self):
        from src.store.metadata_db import MetadataStore
        return MetadataStore(self.config.data_dir / "candidate_search.sqlite3")

    @cached_property
    def get_llm_chain(self):
        from langchain_ollama import ChatOllama
        from langchain_core.prompts import ChatPromptTemplate
        
        llm = ChatOllama(
            model=self.config.ollama_model,
            temperature=0.2,
            format="json",
            keep_alive="5m",
            base_url=self.config.ollama_base_url,
        )
        
        system_message = """
            You are a senior technical recruiter. Compare JD and Resume.
            Return JSON with this exact structure:
            {{
            "verdict": "Strong Match / Partial Match / No Match",
            "strengths": ["3-5 bullets why they fit"],
            "gaps": ["1-3 missing skills"],
            "summary": "2-3 sentence summary"
            }}
            Only return valid JSON. No thinking tags.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "JOB DESCRIPTION:\n{jd_text}\n\nRESUME ({resume_id}):\n{full_resume_text}")
        ])
        
        return prompt | llm

@lru_cache(maxsize=1)
def get_service_container() -> ServiceContainer:
    """Return the shared service container for this application process."""
    return ServiceContainer()
