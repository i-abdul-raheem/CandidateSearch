from collections import defaultdict

from fastapi import APIRouter, Depends, Query, Request
from starlette.concurrency import run_in_threadpool
from src.container import get_service_container
from src.config import settings
from src.schemas import CandidateMatch, Evidence, SearchResponse
from src.security import require_api_key

router = APIRouter(tags=["query"], dependencies=[Depends(require_api_key)])

@router.get("/", response_model=SearchResponse)
async def query(
    request: Request,
    q: str = Query(min_length=2),
    top_k_people: int = Query(default=3, ge=1, le=20),
) -> SearchResponse:
    if len(q) > settings.max_query_length:
        from fastapi import HTTPException
        raise HTTPException(422, "Query is too long")
    service_container = get_service_container()
    em = service_container.get_embedding_manager
    vs = service_container.get_vector_store

    query_vector = await run_in_threadpool(em.model.encode,
        [f"query: {q}"],
        normalize_embeddings=True
    )
    query_vector = query_vector.tolist()

    available = vs.collection.count()
    if available == 0:
        return SearchResponse(results=[])
    results = await run_in_threadpool(vs.collection.query,
        query_embeddings=query_vector,
        n_results=min(max(top_k_people * 10, 30), available),
    )

    # Guard for Pylance + empty DB
    if not results or not results.get('documents') or not results['documents'][0]: # type: ignore
        return SearchResponse(results=[])

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
        grouped[meta['resume_id']].append({"score": score, "text": doc, "section": meta.get('chunk_type')})

    ranked_people = []
    for resume_id, chunks in grouped.items():
        public_id = vs.public_resume_id(resume_id)
        avg_score = sum(c['score'] for c in chunks) / len(chunks)
        if any(c['section']=='skills' for c in chunks) and any(c['section']=='experience' for c in chunks):
            avg_score *= 1.1
        ranked_people.append(CandidateMatch(
            id=str(request.url_for("get_resume_file", resume_id=public_id)),
            resume_id=public_id,
            score=max(0.0, min(1.0, avg_score)),
            evidence=[Evidence(**chunk) for chunk in chunks[:5]],
        ))

    ranked_people.sort(key=lambda x: x.score, reverse=True)
    return SearchResponse(results=ranked_people[:top_k_people])
