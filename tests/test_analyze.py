from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.analyze import get_support_analyzer
from app.db.session import Base, get_db
from app.main import app
from app.schemas.analysis import AnalyzeResponse


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


class FakeAnalyzer:
    def analyze(self, message: str) -> AnalyzeResponse:
        return AnalyzeResponse(
            category="account_access",
            priority="high",
            summary=f"Customer needs help: {message}",
            draft_reply="Hi, thanks for reaching out. We will help you regain access.",
        )


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_support_analyzer() -> FakeAnalyzer:
    return FakeAnalyzer()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_support_analyzer] = override_get_support_analyzer
client = TestClient(app)


def test_analyze_returns_structured_response() -> None:
    response = client.post("/analyze", json={"message": "I cannot log in."})

    assert response.status_code == 200
    assert response.json() == {
        "category": "account_access",
        "priority": "high",
        "summary": "Customer needs help: I cannot log in.",
        "draft_reply": "Hi, thanks for reaching out. We will help you regain access.",
    }


def test_analyze_rejects_empty_message() -> None:
    response = client.post("/analyze", json={"message": ""})

    assert response.status_code == 422
