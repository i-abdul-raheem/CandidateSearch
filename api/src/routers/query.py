from collections import defaultdict

from fastapi import APIRouter
from src.container import get_service_container

router = APIRouter(tags=['query'])

@router.get("/")
async def query(q: str, top_k_people: int = 3) -> dict:
    service_container = get_service_container()
    em = service_container.get_embedding_manager
    vs = service_container.get_vector_store

    query_vector = em.model.encode(
        [f"query: {q}"],
        normalize_embeddings=True
    ).tolist()

    results = vs.collection.query(
        query_embeddings=query_vector,
        n_results=30,
        where={"chunk_type": {"$in": ["skills", "experience"]}}
    )

    # Guard for Pylance + empty DB
    if not results or not results.get('documents') or not results['documents'][0]: # type: ignore
        return {"results": []}

    docs = results['documents'][0] # type: ignore
    metas = results['metadatas'][0] # type: ignore
    dists = results['distances'][0] # type: ignore
    ids_list = results['ids'][0]

    # Now Pylance knows these are not None
    grouped = defaultdict(list)
    for doc, meta, dist, _id in zip(docs, metas, dists, ids_list):
        if doc is None or meta is None:
            continue
        score = 1 - dist
        grouped[meta['resume_id']].append({"score": score, "doc": doc, "type": meta.get('chunk_type')})

    ranked_people = []
    for resume_id, chunks in grouped.items():
        avg_score = sum(c['score'] for c in chunks) / len(chunks)
        if any(c['type']=='skills' for c in chunks) and any(c['type']=='experience' for c in chunks):
            avg_score *= 1.1
        ranked_people.append({"resume_id": resume_id, "score": avg_score, "evidence": chunks})

    ranked_people.sort(key=lambda x: x['score'], reverse=True)
    return {"results": ranked_people[:top_k_people]}
