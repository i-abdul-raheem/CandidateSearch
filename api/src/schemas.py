from pydantic import BaseModel, Field


class Evidence(BaseModel):
    score: float
    text: str
    section: str | None = None


class CandidateMatch(BaseModel):
    id: str
    resume_id: str
    score: float
    evidence: list[Evidence]


class SearchResponse(BaseModel):
    results: list[CandidateMatch]


class UploadResponse(BaseModel):
    message: str
    resume_id: str


class ExplainRequest(BaseModel):
    resume_id: str = Field(min_length=1, max_length=128)
    jd_text: str = Field(min_length=20)


class ExplainResponse(BaseModel):
    resume_id: str
    match_score: int = Field(ge=0, le=100)
    verdict: str
    strengths: list[str]
    gaps: list[str]
    summary: str
