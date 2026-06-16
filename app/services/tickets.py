from sqlalchemy.orm import Session

from app.repositories.tickets import TicketRepository
from app.schemas.analysis import AnalyzeResponse


def create_analyzed_ticket(
    *,
    db: Session,
    source: str,
    message: str,
    analysis: AnalyzeResponse,
    customer_external_id: str,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
) -> None:
    repository = TicketRepository(db)
    customer = repository.upsert_customer(
        source=source,
        external_id=customer_external_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    repository.create_ticket(
        customer=customer,
        source=source,
        message=message,
        analysis=analysis,
    )
    db.commit()
