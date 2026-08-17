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


class SearchRequest(BaseModel):
    query: str = Field(min_length=2)
    top_k_people: int = Field(default=3, ge=1, le=20)


class UploadResponse(BaseModel):
    message: str
    resume_id: str


class TalentCandidate(BaseModel):
    resume_id: str
    resume_url: str
    filename: str
    sections: list[str]


class TalentPoolResponse(BaseModel):
    results: list[TalentCandidate]
    total: int


class RoleInput(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    department: str = Field(default="", max_length=100)
    location: str = Field(default="", max_length=200)
    work_mode: str = Field(default="", max_length=50)
    description: str = Field(min_length=10)
    status: str = Field(default="open", pattern="^(open|paused|closed)$")


class Role(RoleInput):
    id: str
    created_at: str
    updated_at: str


class RecentSearch(BaseModel):
    id: str
    query: str
    result_count: int
    created_at: str


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
