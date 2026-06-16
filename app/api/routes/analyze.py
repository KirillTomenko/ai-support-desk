from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import SupportAnalyzer, get_support_analyzer
from app.services.tickets import create_analyzed_ticket

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

    first_name = payload.customer_name
    create_analyzed_ticket(
        db=db,
        source="api",
        customer_external_id=payload.customer_external_id or payload.customer_email or "anonymous",
        email=payload.customer_email,
        first_name=first_name,
        message=payload.message,
        analysis=result,
    )

    return result
