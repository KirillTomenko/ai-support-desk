from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    customer_external_id: str | None = Field(default=None, max_length=120)
    customer_email: str | None = Field(default=None, max_length=255)
    customer_name: str | None = Field(default=None, max_length=240)


class AnalyzeResponse(BaseModel):
    category: str = Field(..., examples=["billing"])
    priority: str = Field(..., examples=["high"])
    summary: str
    draft_reply: str
