from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.analysis import AnalysisRecord
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import SupportAnalyzer, get_support_analyzer

router = APIRouter(tags=["analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a support message",
)
def analyze_message(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
    analyzer: SupportAnalyzer = Depends(get_support_analyzer),
) -> AnalyzeResponse:
    result = analyzer.analyze(payload.message)

    record = AnalysisRecord(
        message=payload.message,
        category=result.category,
        priority=result.priority,
        summary=result.summary,
        draft_reply=result.draft_reply,
    )
    db.add(record)
    db.commit()

    return result
