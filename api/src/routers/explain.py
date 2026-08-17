import json
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from src.container import get_service_container

router = APIRouter(tags=['explain'])

class ExplainRequest(BaseModel):
    resume_id: str
    jd_text: str

class ExplainResponse(BaseModel):
    resume_id: str
    match_score: int
    verdict: str
    strengths: list[str]
    gaps: list[str]
    summary: str

@router.post("/explain", response_model=ExplainResponse)
async def explain(request: ExplainRequest):
    service_container = get_service_container()
    vs = service_container.get_vector_store

    result = vs.collection.get(where={"resume_id": request.resume_id})
    if not result['documents']:
        raise HTTPException(404, "resume not found")

    resume_text = "\n\n".join(result['documents'])
    full_resume_text = resume_text[:3000]

    chain = service_container.get_llm_chain
    # use ainvoke for async endpoint
    llm_result = chain.invoke({
        'jd_text': request.jd_text,
        'resume_id': request.resume_id,
        'full_resume_text': full_resume_text
    })

    # llm_result.content is a JSON string
    data = json.loads(llm_result.content) # type: ignore

    return {
        "resume_id": request.resume_id,
        "match_score": 75 if data['verdict'] == "Strong Match" else 55 if data['verdict'] == "Partial Match" else 20,
        **data
    }