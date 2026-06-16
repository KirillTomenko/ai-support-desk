# AI Support Desk
*система автоматизации клиентской поддержки*

Production-ready FastAPI проект для анализа обращений в поддержку с помощью LLM, Telegram-ботом и Streamlit dashboard.

Сервис принимает сообщение клиента, определяет категорию и приоритет, формирует краткое резюме и черновик ответа. Все обращения сохраняются как тикеты в Supabase PostgreSQL через SQLAlchemy.

## Бизнес-задача

Многие компании получают обращения клиентов из разных каналов: Telegram, email, веб-формы и внутренние системы.

Обработка таких обращений вручную занимает время и приводит к потере заявок, задержкам ответов и отсутствию прозрачной статистики.

AI Support Inbox автоматизирует первичный разбор обращений:

- определяет категорию обращения;
- оценивает приоритет;
- формирует краткое резюме;
- генерирует черновик ответа;
- сохраняет историю взаимодействия;
- предоставляет статистику для менеджеров поддержки.

## Workflow

Клиент
↓
Telegram Bot / REST API
↓
FastAPI
↓
OpenAI API
↓
AI-анализ обращения
↓
Supabase PostgreSQL
↓
Streamlit Dashboard
↓
Менеджер поддержки

## Возможности

- REST API на FastAPI
- Интеграция с OpenAI API или OpenAI-compatible proxy API
- Telegram-бот на `aiogram`
- Streamlit dashboard со статистикой обращений
- Supabase PostgreSQL вместо SQLite
- SQLAlchemy ORM
- Таблицы `customers`, `tickets`, `ticket_history`
- Dockerfile и Docker Compose
- Тестовый контур для API

## Почему Supabase

Для MVP-проектов часто используется SQLite.

В данном проекте выбрана Supabase PostgreSQL, поскольку она позволяет:

хранить данные в облаке;
работать с несколькими пользователями одновременно;
использовать полноценную PostgreSQL-базу данных;
масштабировать решение без изменения архитектуры;
использовать проект как основу для production-развертывания.

## Возможный сценарий использования
Клиент пишет сообщение в Telegram-бота.
FastAPI-сервис получает обращение и отправляет его на анализ через OpenAI API.
Система определяет:
категорию обращения;
приоритет;
краткое резюме;
черновик ответа.
Результат сохраняется в Supabase PostgreSQL.
Менеджер открывает Dashboard и видит новые обращения, приоритеты и статистику.

## Скриншоты и демо

В проекте уже созданы папки для наглядных материалов:

```text
docs/
  screenshots/
    swagger.png
    dashboard.png
    telegram-bot.png
  demo/
    api-demo.gif
```

После запуска проекта можно добавить изображения и вставить их так:

```markdown
![Swagger UI](docs/screenshots/swagger.png)
![Dashboard](docs/screenshots/dashboard.png)
![Telegram bot](docs/screenshots/telegram-bot.png)
![API demo](docs/demo/api-demo.gif)
```

Готовый блок для будущей вставки:

<!--
![Swagger UI](docs/screenshots/swagger.png)

![Dashboard](docs/screenshots/dashboard.png)

![Telegram bot](docs/screenshots/telegram-bot.png)

![API demo](docs/demo/api-demo.gif)
-->

## Архитектура

```text
app/
  api/
    routes/
      analyze.py
  core/
    config.py
    logging.py
  dashboard/
    main.py
  db/
    base.py
    init_db.py
    session.py
  models/
    analysis.py
  repositories/
    tickets.py
  schemas/
    analysis.py
  services/
    analyzer.py
    tickets.py
  telegram/
    bot.py
  main.py
tests/
  test_analyze.py
docker-compose.yml
Dockerfile
```

## Модель данных

### `customers`

Хранит клиентов из разных источников: API, Telegram и будущих интеграций.

Ключевые поля:

| Поле | Описание |
| --- | --- |
| `id` | Внутренний ID клиента |
| `source` | Источник клиента, например `api` или `telegram` |
| `external_id` | ID клиента во внешней системе |
| `username`, `first_name`, `last_name`, `email` | Данные клиента |
| `created_at`, `updated_at` | Временные метки |

### `tickets`

Хранит обращения клиентов и результат AI-анализа.

Ключевые поля:

| Поле | Описание |
| --- | --- |
| `id` | ID тикета |
| `customer_id` | Ссылка на клиента |
| `source` | Источник обращения |
| `status` | Статус тикета, по умолчанию `new` |
| `message` | Исходное сообщение клиента |
| `category` | Категория обращения |
| `priority` | Приоритет обращения |
| `summary` | Краткое резюме |
| `draft_reply` | Черновик ответа |
| `created_at`, `updated_at` | Временные метки |

### `ticket_history`

Хранит историю событий по тикетам.

Ключевые поля:

| Поле | Описание |
| --- | --- |
| `ticket_id` | Ссылка на тикет |
| `event_type` | Тип события, например `created` |
| `from_status`, `to_status` | Изменение статуса |
| `note` | Комментарий к событию |
| `created_at` | Дата события |

## Настройка Supabase

1. Создайте проект в Supabase.

2. Откройте раздел подключения к базе данных:

```text
Project Settings -> Database -> Connection string
```

или кнопку `Connect` в панели Supabase.

3. Выберите строку подключения для Postgres. Для backend-приложений обычно подходит pooled connection string через Supavisor. Если окружение поддерживает IPv6, можно использовать direct connection.

4. Приведите строку подключения к формату SQLAlchemy:

```env
DATABASE_URL=postgresql+psycopg://postgres.your-project-ref:your-password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require
```

5. Если пароль содержит специальные символы, URL-encode его. Например `@` нужно заменить на `%40`.

Таблицы создаются автоматически при старте API или Telegram-бота через `SQLAlchemy Base.metadata.create_all`.

Документация Supabase по подключению к Postgres: [supabase.com/docs/guides/database/connecting-to-postgres](https://supabase.com/docs/guides/database/connecting-to-postgres).

## Переменные окружения

Создайте `.env` из примера:

```bash
cp .env.example .env
```

Заполните значения:

```env
APP_NAME=AI Support Inbox
APP_ENV=development

DATABASE_URL=postgresql+psycopg://postgres.your-project-ref:your-password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?sslmode=require

OPENAI_API_KEY=your-openai-or-proxy-api-key
OPENAI_BASE_URL=https://your-proxy.example.com/v1
OPENAI_MODEL=gpt-4.1-mini

TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

| Переменная | Описание |
| --- | --- |
| `APP_NAME` | Название приложения в FastAPI |
| `APP_ENV` | Окружение запуска |
| `DATABASE_URL` | Supabase PostgreSQL connection string для SQLAlchemy |
| `OPENAI_API_KEY` | API-ключ OpenAI или proxy API |
| `OPENAI_BASE_URL` | Base URL OpenAI-compatible proxy API, если используется |
| `OPENAI_MODEL` | Модель для анализа обращений |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram-бота от BotFather |

## REST API

### `POST /analyze`

Анализирует сообщение и сохраняет тикет в PostgreSQL.

Минимальный запрос:

```json
{
  "message": "I cannot log into my account and need help urgently."
}
```

Расширенный запрос:

```json
{
  "message": "I cannot log into my account and need help urgently.",
  "customer_external_id": "customer-123",
  "customer_email": "customer@example.com",
  "customer_name": "Alex"
}
```

Ответ:

```json
{
  "category": "account_access",
  "priority": "high",
  "summary": "The customer cannot log into their account and needs urgent assistance.",
  "draft_reply": "Hi, thanks for reaching out. I am sorry you are having trouble signing in. Please try resetting your password first, and if that does not work, send us the email address on the account so we can investigate."
}
```

### `GET /health`

```json
{
  "status": "ok"
}
```

## Локальный запуск

Проект рассчитан на Python 3.12.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Telegram-бот

1. Создайте бота через BotFather.
2. Укажите токен в `.env`:

```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

3. Запустите polling:

```bash
python -m app.telegram.bot
```

Пользователь отправляет сообщение боту, бот анализирует обращение, сохраняет тикет и возвращает категорию, приоритет, резюме и черновик ответа.

## Streamlit Dashboard

Запуск dashboard:

```bash
streamlit run app/dashboard/main.py
```

Интерфейс будет доступен по адресу:

```text
http://localhost:8501
```

Dashboard показывает:

- общее количество тикетов
- количество новых обращений
- количество `urgent` и `high` обращений
- распределение по категориям
- распределение по приоритетам
- таблицу последних обращений

## Docker Compose

Запуск всех сервисов:

```bash
docker compose up --build
```

Сервисы:

| Сервис | Порт | Описание |
| --- | --- | --- |
| `api` | `8000` | FastAPI REST API |
| `telegram-bot` | - | Telegram polling bot |
| `dashboard` | `8501` | Streamlit dashboard |

После запуска:

```text
API: http://localhost:8000
Swagger: http://localhost:8000/docs
Dashboard: http://localhost:8501
```

## Тесты

Для тестов используется in-memory SQLite, чтобы не зависеть от Supabase.

```bash
pip install -r requirements-dev.txt
pytest
```
## Roadmap
v1.0
FastAPI REST API
OpenAI Integration
Telegram Bot
Supabase PostgreSQL
Streamlit Dashboard
Ticket History
v1.1
Email Integration
Webhook Integration
SLA Monitoring
CSV Export
v1.2
Automatic Ticket Escalation
AI Customer Summary
Multi-Agent Support Workflow
Analytics Dashboard

## Поведение без API-ключа

Если `OPENAI_API_KEY` не задан, сервис использует локальный fallback-анализатор. Это удобно для проверки API, Telegram-бота и dashboard без реального LLM-запроса.

В production-режиме рекомендуется всегда задавать `OPENAI_API_KEY`, `OPENAI_MODEL`, `DATABASE_URL` и при необходимости `OPENAI_BASE_URL`.
