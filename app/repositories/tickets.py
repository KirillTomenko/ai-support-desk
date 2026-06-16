from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis import Customer, Ticket, TicketHistory
from app.schemas.analysis import AnalyzeResponse


class TicketRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def upsert_customer(
        self,
        *,
        source: str,
        external_id: str,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> Customer:
        customer = self.db.scalar(
            select(Customer).where(
                Customer.source == source,
                Customer.external_id == external_id,
            )
        )
        if customer is None:
            customer = Customer(source=source, external_id=external_id)
            self.db.add(customer)

        customer.username = username
        customer.first_name = first_name
        customer.last_name = last_name
        customer.email = email
        self.db.flush()
        return customer

    def create_ticket(
        self,
        *,
        customer: Customer,
        source: str,
        message: str,
        analysis: AnalyzeResponse,
    ) -> Ticket:
        ticket = Ticket(
            customer_id=customer.id,
            source=source,
            status="new",
            message=message,
            category=analysis.category,
            priority=analysis.priority,
            summary=analysis.summary,
            draft_reply=analysis.draft_reply,
        )
        self.db.add(ticket)
        self.db.flush()

        self.db.add(
            TicketHistory(
                ticket_id=ticket.id,
                event_type="created",
                to_status="new",
                note=f"Ticket created from {source}.",
            )
        )
        return ticket
