from src.store.chroma_db import VectorStore


def test_public_resume_id_preserves_new_ids() -> None:
    resume_id = "0123456789abcdef0123456789abcdef"
    assert VectorStore.public_resume_id(resume_id) == resume_id


def test_public_resume_id_anonymizes_legacy_paths() -> None:
    public_id = VectorStore.public_resume_id("data/pdf/Profiles/A Candidate.pdf")
    assert len(public_id) == 32
    assert "/" not in public_id
