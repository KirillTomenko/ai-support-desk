# AI Support Inbox

Production-ready FastAPI сервис для анализа входящих обращений в службу поддержки с помощью LLM через OpenAI-compatible API.

Сервис принимает текст сообщения клиента, определяет категорию и приоритет, формирует краткое резюме и черновик ответа для оператора поддержки.

## Возможности

- REST API на FastAPI
- SQLite через SQLAlchemy
- Интеграция с OpenAI API или OpenAI-compatible proxy API
- Сохранение результатов анализа в базе данных
- Модульная структура проекта
- Dockerfile для запуска в контейнере
- Health check endpoint
- Тестовый контур для API

## Скриншоты и демо

В репозитории предусмотрены места для наглядных материалов. После запуска проекта можно добавить скриншоты Swagger UI, примеры запросов или короткую GIF-демонстрацию.

Рекомендуемая структура:

```text
docs/
  screenshots/
    swagger.png
    analyze-request.png
    analyze-response.png
  demo/
    api-demo.gif
```

Пример вставки скриншотов в README:

```markdown
![Swagger UI](docs/screenshots/swagger.png)
![Analyze request](docs/screenshots/analyze-request.png)
![Analyze response](docs/screenshots/analyze-response.png)
```

Пример вставки демо:

```markdown
![API demo](docs/demo/api-demo.gif)
```

После добавления файлов можно раскомментировать или вставить эти блоки ниже:

<!--
![Swagger UI](docs/screenshots/swagger.png)

![Analyze request](docs/screenshots/analyze-request.png)

![Analyze response](docs/screenshots/analyze-response.png)

![API demo](docs/demo/api-demo.gif)
-->

## API

### `POST /analyze`

Анализирует сообщение клиента и возвращает структурированный результат.

Запрос:

```json
{
  "message": "I cannot log into my account and need help urgently."
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

Поля ответа:

| Поле | Описание |
| --- | --- |
| `category` | Категория обращения, например `billing`, `account_access`, `bug_report` |
| `priority` | Приоритет: `low`, `medium`, `high`, `urgent` |
| `summary` | Краткое резюме обращения |
| `draft_reply` | Черновик ответа клиенту |

### `GET /health`

Проверка доступности сервиса.

Ответ:

```json
{
  "status": "ok"
}
```

## Быстрый старт

### 1. Создать виртуальное окружение

Проект рассчитан на Python 3.12.

```powershell
py -3.12 -m venv .venv
```

### 2. Активировать окружение

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить переменные окружения

Скопируйте пример конфигурации:

```bash
cp .env.example .env
```

Для обычного OpenAI API достаточно указать:

```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4.1-mini
```

Если доступ к LLM идет через proxy API, укажите `OPENAI_BASE_URL`:

```env
OPENAI_API_KEY=your-proxy-api-key
OPENAI_BASE_URL=https://your-proxy.example.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

### 5. Запустить API

```bash
uvicorn app.main:app --reload
```

Документация Swagger UI будет доступна по адресу:

```text
http://localhost:8000/docs
```

## Пример запроса

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"I cannot log into my account and need help urgently.\"}"
```

## Тесты

Установите dev-зависимости:

```bash
pip install -r requirements-dev.txt
```

Запустите тесты:

```bash
pytest
```

## Docker

Сборка образа:

```bash
docker build -t ai-support-inbox .
```

Запуск контейнера:

```bash
docker run --rm -p 8000:8000 --env-file .env ai-support-inbox
```

После запуска API будет доступен по адресу:

```text
http://localhost:8000
```

## Переменные окружения

| Переменная | Значение по умолчанию | Описание |
| --- | --- | --- |
| `APP_NAME` | `AI Support Inbox` | Название приложения в FastAPI |
| `APP_ENV` | `development` | Окружение запуска |
| `DATABASE_URL` | `sqlite:///./data/support_inbox.db` | URL подключения SQLAlchemy |
| `OPENAI_API_KEY` | пусто | API-ключ OpenAI или proxy API |
| `OPENAI_BASE_URL` | пусто | Base URL OpenAI-compatible proxy API |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Модель для анализа обращений |

## Структура проекта

```text
app/
  api/
    routes/
      analyze.py
  core/
    config.py
    logging.py
  db/
    base.py
    session.py
  models/
    analysis.py
  schemas/
    analysis.py
  services/
    analyzer.py
  main.py
tests/
  test_analyze.py
```

## Архитектура

- `app/api/routes` содержит REST endpoints.
- `app/schemas` содержит Pydantic-схемы запросов и ответов.
- `app/models` содержит SQLAlchemy-модели.
- `app/db` отвечает за подключение к базе данных и сессии.
- `app/services` содержит бизнес-логику анализа сообщений.
- `app/core` содержит конфигурацию и инфраструктурные настройки.

## Поведение без API-ключа

Если `OPENAI_API_KEY` не задан, сервис использует локальный fallback-анализатор. Это удобно для локального запуска, тестирования Docker-образа и демонстрации API без реального LLM-запроса.

В production-режиме рекомендуется всегда задавать `OPENAI_API_KEY`, `OPENAI_MODEL` и при необходимости `OPENAI_BASE_URL`.
