from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr
import httpx
import csv
import io
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

app = FastAPI(title="Local Name Handler")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=100)


async def query_ollama(name: str):
    # Если включён mock-режим — вернуть предсказуемый фиктивный ответ
    if os.getenv("MOCK_LLM", "false").lower() in ("1", "true", "yes"):
        def mock_response_for(n: str):
            s = n.strip()
            low = s.lower()
            # Простые правила/отображения уменьшительных имён
            male_map = {
                "саша": "Александр",
                "женя": "Евгений",
                "женек": "Евгений",
                "сашка": "Александр",
                "алекс": "Александр",
            }
            female_map = {
                "маша": "Мария",
                "мария": "Мария",
                "маришка": "Мария",
                "аня": "Анна",
            }
            if low in male_map:
                return {"gender": "мужской", "full_name": male_map[low], "corrected_input": s}
            if low in female_map:
                return {"gender": "женский", "full_name": female_map[low], "corrected_input": s}
            # Простейшая эвристика по окончанию
            if low.endswith('а') or low.endswith('я'):
                return {"gender": "женский", "full_name": s.capitalize(), "corrected_input": s}
            return {"gender": "мужской", "full_name": s.capitalize(), "corrected_input": s}

        return mock_response_for(name)

    system = (
        "Ты — модуль анализа имён. Возвращай JSON с полом, официальным именем и очищенной "
        "версией имени. Никаких объяснений. Пример ввода: Саша. Пример ответа: {\"gender\": \"мужской\", "
        "\"full_name\": \"Александр\", \"corrected_input\": \"Саша\"}"
    )
    payload = {
        "model": "mistral",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": name},
        ],
        "stream": False,
    }

    url = f"{OLLAMA_URL}/api/chat"
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.post(url, json=payload)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"LLM request failed: {e}")

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"LLM returned {r.status_code}: {r.text}")

    # The model should return JSON text; try to parse
    try:
        return r.json()
    except Exception:
        # Try to extract JSON-like substring
        text = r.text
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                import json

                return json.loads(text[start:end+1])
            except Exception:
                raise HTTPException(status_code=502, detail="LLM returned invalid JSON")
        raise HTTPException(status_code=502, detail="LLM returned invalid response")


@app.post("/analyze-name")
async def analyze_name(payload: AnalyzeRequest):
    name = payload.name
    # basic validation
    if not name.strip():
        raise HTTPException(status_code=400, detail="Empty name")
    if len(name) > 100:
        raise HTTPException(status_code=400, detail="Name too long")
    if any(c.isdigit() for c in name):
        raise HTTPException(status_code=400, detail="Name contains digits")

    result = await query_ollama(name)
    # Ensure keys
    return {
        "gender": result.get("gender"),
        "full_name": result.get("full_name"),
        "corrected_input": result.get("corrected_input"),
    }


@app.post("/analyze-csv")
async def analyze_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    try:
        s = content.decode('utf-8')
    except Exception:
        s = content.decode('latin-1')

    reader = csv.DictReader(io.StringIO(s))
    output = io.StringIO()
    fieldnames = reader.fieldnames + ["gender", "full_name", "corrected_input"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        name = row.get('name') or row.get('Name') or ''
        if not name:
            row.update({"gender": "", "full_name": "", "corrected_input": ""})
            writer.writerow(row)
            continue
        try:
            res = await query_ollama(name)
            row.update({
                "gender": res.get('gender', ''),
                "full_name": res.get('full_name', ''),
                "corrected_input": res.get('corrected_input', ''),
            })
        except HTTPException:
            row.update({"gender": "", "full_name": "", "corrected_input": ""})
        writer.writerow(row)

    return {
        "filename": file.filename,
        "content": output.getvalue()
    }
