from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)


class AnalyzeResponse(BaseModel):
    category: str = Field(..., examples=["billing"])
    priority: str = Field(..., examples=["high"])
    summary: str
    draft_reply: str
