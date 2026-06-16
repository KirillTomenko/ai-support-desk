import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.services.analyzer import get_support_analyzer
from app.services.tickets import create_analyzed_ticket

logger = logging.getLogger(__name__)


def build_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    analyzer = get_support_analyzer()

    @dispatcher.message(CommandStart())
    async def start(message: Message) -> None:
        await message.answer(
            "Привет! Опишите проблему одним сообщением, а я создам тикет и подготовлю черновик ответа."
        )

    @dispatcher.message(F.text)
    async def handle_support_message(message: Message) -> None:
        if not message.text:
            return

        analysis = analyzer.analyze(message.text)
        user = message.from_user

        with SessionLocal() as db:
            create_analyzed_ticket(
                db=db,
                source="telegram",
                customer_external_id=str(user.id if user else message.chat.id),
                username=user.username if user else None,
                first_name=user.first_name if user else None,
                last_name=user.last_name if user else None,
                message=message.text,
                analysis=analysis,
            )

        await message.answer(
            "\n".join(
                [
                    "Тикет создан.",
                    f"Категория: {analysis.category}",
                    f"Приоритет: {analysis.priority}",
                    f"Резюме: {analysis.summary}",
                    "",
                    f"Черновик ответа: {analysis.draft_reply}",
                ]
            )
        )

    return dispatcher


async def main() -> None:
    configure_logging()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured.")

    init_db()
    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = build_dispatcher()
    logger.info("Starting Telegram bot polling.")
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
