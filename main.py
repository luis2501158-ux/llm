from datetime import datetime
from enum import Enum
from pathlib import Path
import os

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from supabase import create_client

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL y SUPABASE_KEY deben estar definidos en las variables de entorno.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
HISTORY_TABLE = "history"

class Mode(str, Enum):
    grammar = "grammar"
    suggest = "suggest"
    generate = "generate"

class ProcessRequest(BaseModel):
    mode: Mode
    text: str

class HistoryItem(BaseModel):
    id: int
    created_at: datetime
    mode: Mode
    prompt: str
    result: str

app = FastAPI(
    title="Text Studio API",
    description="API sencilla para sugerencias de oraciones, corrección de gramática y generación de texto con OpenAI.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/style.css")
def get_css():
    return FileResponse(BASE_DIR / "style.css", media_type="text/css")


@app.get("/index.js")
def get_js():
    return FileResponse(BASE_DIR / "index.js", media_type="application/javascript")


def create_prompt(mode: Mode, text: str) -> str:
    if mode == Mode.grammar:
        return (
            "Corrige y mejora la gramática, puntuación y estilo de este texto en español. "
            "Devuelve solo el texto corregido sin explicaciones adicionales.\n\n" + text
        )
    if mode == Mode.suggest:
        return (
            "Sugiere nuevas formas de expresar o mejorar esta oración en español. "
            "Mantén el mismo significado y ofrece un ejemplo mejorado.\n\n" + text
        )
    return (
        "Genera un texto completo en español basado en el tema o idea proporcionada. "
        "Hazlo claro, natural y bien estructurado.\n\n" + text
    )


def get_openai_response(mode: Mode, text: str) -> str:
    if not openai.api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY no está definido. Establece la variable de entorno antes de iniciar la aplicación.",
        )

    prompt = create_prompt(mode, text)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente de escritura en español. Ayuda al usuario a corregir gramática, "
                        "mejorar estilo y generar texto completo con claridad y fluidez."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error en OpenAI: {exc}")


def save_history(mode: Mode, prompt: str, result: str) -> dict:
    record = {
        "mode": mode.value,
        "prompt": prompt,
        "result": result,
        "created_at": datetime.utcnow().isoformat(),
    }
    response = supabase.table(HISTORY_TABLE).insert(record).select("*").execute()
    if response.error:
        error_message = getattr(response.error, "message", str(response.error))
        raise HTTPException(status_code=500, detail=f"Error guardando historial: {error_message}")
    return response.data[0]


@app.post("/api/process", response_model=HistoryItem)
def process_text(request: ProcessRequest):
    result = get_openai_response(request.mode, request.text)
    record = save_history(request.mode, request.text, result)
    return HistoryItem(
        id=record.get("id"),
        created_at=record.get("created_at"),
        mode=Mode(record.get("mode")),
        prompt=record.get("prompt"),
        result=record.get("result"),
    )


@app.get("/api/history", response_model=list[HistoryItem])
def read_history():
    response = supabase.table(HISTORY_TABLE).select("*").order("id", desc=True).limit(20).execute()
    if response.error:
        error_message = getattr(response.error, "message", str(response.error))
        raise HTTPException(status_code=500, detail=f"Error consultando historial: {error_message}")
    return [
        HistoryItem(
            id=item.get("id"),
            created_at=item.get("created_at"),
            mode=Mode(item.get("mode")),
            prompt=item.get("prompt"),
            result=item.get("result"),
        )
        for item in response.data
    ]


@app.get("/")
def read_index():
    return FileResponse(BASE_DIR / "index.html")
