import json
import logging

from fastapi import HTTPException, status
from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.analysis import AnalyzeResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert customer support triage assistant.
Analyze the incoming support message and return strict JSON with:
- category: short snake_case category such as billing, account_access, bug_report, feature_request, cancellation, general
- priority: one of low, medium, high, urgent
- summary: one concise sentence
- draft_reply: a helpful, empathetic reply the support team can send
Do not include markdown or extra text.
"""


class SupportAnalyzer:
    def __init__(self, api_key: str | None, model: str, base_url: str | None = None) -> None:
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url) if api_key else None

    def analyze(self, message: str) -> AnalyzeResponse:
        if self.client is None:
            logger.warning("OPENAI_API_KEY is not configured; using local fallback analyzer.")
            return self._fallback_analysis(message)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                temperature=0.2,
            )
        except OpenAIError as exc:
            logger.exception("OpenAI analysis failed.")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI analysis provider is unavailable.",
            ) from exc

        content = response.choices[0].message.content
        if not content:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI analysis provider returned an empty response.",
            )

        try:
            payload = json.loads(content)
            return AnalyzeResponse.model_validate(payload)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.exception("OpenAI analysis response was invalid.")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI analysis provider returned an invalid response.",
            ) from exc

    @staticmethod
    def _fallback_analysis(message: str) -> AnalyzeResponse:
        normalized = message.lower()

        category = "general"
        if any(word in normalized for word in ("refund", "invoice", "payment", "charge", "billing")):
            category = "billing"
        elif any(word in normalized for word in ("login", "password", "account", "sign in")):
            category = "account_access"
        elif any(word in normalized for word in ("bug", "error", "crash", "broken", "issue")):
            category = "bug_report"
        elif any(word in normalized for word in ("feature", "request", "suggestion")):
            category = "feature_request"
        elif any(word in normalized for word in ("cancel", "unsubscribe")):
            category = "cancellation"

        priority = "medium"
        if any(word in normalized for word in ("urgent", "asap", "immediately", "critical", "down")):
            priority = "urgent"
        elif any(word in normalized for word in ("angry", "broken", "cannot", "can't", "failed")):
            priority = "high"
        elif any(word in normalized for word in ("question", "wondering", "maybe")):
            priority = "low"

        clean_message = " ".join(message.split())
        summary = clean_message[:180] + ("..." if len(clean_message) > 180 else "")

        return AnalyzeResponse(
            category=category,
            priority=priority,
            summary=summary,
            draft_reply=(
                "Hi, thanks for reaching out. We have received your message and will review it "
                "carefully. Our support team will follow up with the next steps shortly."
            ),
        )


def get_support_analyzer() -> SupportAnalyzer:
    return SupportAnalyzer(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        base_url=settings.openai_base_url,
    )
