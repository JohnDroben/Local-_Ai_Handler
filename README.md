# Локальный обработчик имён (MVP)

Проект состоит из:
- backend (FastAPI) на порту 8000
- frontend (Vite + React) на порту 3000

Ollama должен быть запущен локально и доступен на http://localhost:11434

Запуск с Docker Compose:

1. Соберите и запустите:

```bash
docker compose up --build
```

2. Откройте http://localhost:3000

Mock режим (для разработки)
---------------------------
Если вы хотите протестировать UI и поток данных без локального Ollama, можно включить mock-режим в backend.

1. Скопируйте `.env.sample` в `.env` в корне репозитория:

```bash
cp .env.sample .env
```

2. Откройте `.env` и установите:

```text
MOCK_LLM=true
```

3. Перезапустите backend-контейнер, чтобы переменная вступила в силу:

```bash
docker compose -p local_name_handler restart backend
```

В mock-режиме `POST /analyze-name` и `POST /analyze-csv` будут возвращать фиктивные ответы, позволяя проверить UI и CSV pipeline без поднятой LLM.
