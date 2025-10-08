# Backend

FastAPI backend для Local Name Handler. Использует Ollama по адресу, указанному в переменной окружения OLLAMA_URL.

Endpoints:
- POST /analyze-name {"name": "Саша"}
- POST /analyze-csv (multipart form, file field)
