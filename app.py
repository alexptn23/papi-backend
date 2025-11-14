from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import asyncio
import tempfile
import os
import httpx

app = FastAPI()

# CORS liberado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Banco de Jobs (em memória)
JOBS: dict[str, dict] = {}


# Modelo de requisição para processar vídeo
class ProcessVideoRequest(BaseModel):
    video_url: str
    target_languages: list[str] = []


@app.get("/")
def root():
    return {"message": "PAPI backend online 🚀"}


@app.get("/status")
def status():
    return {"status": "ok"}


@app.post("/echo")
def echo(payload: dict):
    return {"received": payload}


# ⚡ Função que roda o processamento do vídeo
async def run_process_video(job_id: str, params: ProcessVideoRequest):
    """
    Processa o vídeo de forma assíncrona:

    Etapa 1 — Baixa o arquivo de vídeo da URL enviada.
    (por enquanto só isso, mas depois colocamos transcrição, tradução e dublagem)
    """

    try:
        JOBS[job_id]["status"] = "processing"
        video_url = params.video_url

        # Cria nome único no diretório temporário
        suffix = f"_{job_id}.mp4"
        tmp_dir = tempfile.gettempdir()
        tmp_path = os.path.join(tmp_dir, f"papi_video{suffix}")

        # Baixar vídeo usando httpx (streaming)
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("GET", video_url) as resp:
                resp.raise_for_status()
                with open(tmp_path, "wb") as f:
                    async for chunk in resp.aiter_bytes():
                        f.write(chunk)

        # Aqui no futuro entrará:
        # - Extrair áudio (FFmpeg)
        # - Whisper transcrever
        # - Traduzir
        # - Gerar dublagem
        # - Montar novo vídeo
        # Por enquanto o "resultado" é só o arquivo baixado.

        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["result_url"] = tmp_path
        JOBS[job_id]["error"] = None

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)


@app.post("/process-video")
async def process_video(request: ProcessVideoRequest, background: BackgroundTasks):
    job_id = str(uuid.uuid4())

    JOBS[job_id] = {
        "status": "queued",
        "result_url": None,
        "error": None,
    }

    # Executa em background
    background.add_task(run_process_video, job_id, request)

    return {"job_id": job_id, "status": "queued"}


@app.get("/job-status/{job_id}")
def job_status(job_id: str):
    if job_id not in JOBS:
        return {
            "job_id": job_id,
            "status": "not_found",
            "error": "Job não encontrado"
        }

    return JOBS[job_id]
