FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install poetry && poetry config virtualenvs.create false || true
RUN poetry install --no-root --only main
COPY . /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
