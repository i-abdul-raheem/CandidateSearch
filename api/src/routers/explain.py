import json
from fastapi import APIRouter, Depends, HTTPException
from src.container import get_service_container
from src.config import settings
from src.schemas import ExplainRequest, ExplainResponse
from src.security import require_api_key

router = APIRouter(tags=["explain"], dependencies=[Depends(require_api_key)])

@router.post("/explain", response_model=ExplainResponse)
async def explain(request: ExplainRequest):
    if len(request.jd_text) > settings.max_jd_length:
        raise HTTPException(422, "Job description is too long")
    service_container = get_service_container()
    vs = service_container.get_vector_store

    internal_id = vs.resolve_resume_id(request.resume_id)
    if internal_id is None:
        raise HTTPException(404, "resume not found")
    result = vs.collection.get(where={"resume_id": internal_id})
    if not result['documents']:
        raise HTTPException(404, "resume not found")

    resume_text = "\n\n".join(result['documents'])
    full_resume_text = resume_text[:3000]

    chain = service_container.get_llm_chain
    llm_result = await chain.ainvoke({
        'jd_text': request.jd_text,
        'resume_id': request.resume_id,
        'full_resume_text': full_resume_text
    })

    # llm_result.content is a JSON string
    try:
        data = json.loads(str(llm_result.content))
        validated = ExplainResponse(
            resume_id=request.resume_id,
            match_score=75 if data.get("verdict") == "Strong Match" else 55 if data.get("verdict") == "Partial Match" else 20,
            **data,
        )
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise HTTPException(502, "The explanation service returned an invalid response") from exc

    return validated
