from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uuid

app = FastAPI()

# Modelo de entrada: SEMPRE { "input": "mediaId" }
class MediaInput(BaseModel):
    input: str  # media_id vindo do frontend


# CORS liberado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Banco de Jobs (em memória)
jobs: dict[str, dict] = {}


@app.get("/")
def root():
    return {"message": "PAPI backend online 🚀"}


@app.get("/status")
def status():
    return {"status": "ok"}


# --------- PROCESSAMENTO PRINCIPAL /process-video --------- #
@app.post("/process-video")
async def process_video(payload: MediaInput):
    """
    Inicia o processamento do vídeo a partir de um media_id.
    O frontend envia: { "input": mediaId }
    """
    media_id = payload.input

    # cria um job_id único
    job_id = str(uuid.uuid4())

    # registra o job como "processing"
    jobs[job_id] = {
        "status": "processing",
        "media_id": media_id,
        "result_url": None,
    }

    # dispara tarefa assíncrona simulando processamento
    asyncio.create_task(fake_processing(job_id))

    # retorna o job_id para o frontend acompanhar
    return {"job_id": job_id, "status": "processing"}


async def fake_processing(job_id: str):
    """
    Simula um processamento leve só para teste
    (no futuro aqui entra Whisper/FFmpeg/etc).
    """
    await asyncio.sleep(5)  # simula trabalho

    job = jobs.get(job_id)
    if job is not None:
        job["status"] = "completed"
        # URL de exemplo; o frontend pode ignorar por enquanto
        job["result_url"] = f"https://papi.example.com/output/{job_id}.mp4"


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    """
    Consulta o status de um job.
    """
    job = jobs.get(job_id)
    if job is None:
        return {"status": "not_found"}
    return job


# --------- STUBS PARA OS OUTROS ENDPOINTS --------- #
# Todos recebem { "input": mediaId } só pra não quebrar o frontend.


@app.post("/process-translation")
async def process_translation(payload: MediaInput):
    """
    Stub: processamento de tradução para um media_id.
    """
    media_id = payload.input
    # no futuro: lógica real de tradução aqui
    return {"status": "ok", "media_id": media_id}


@app.post("/process-all-translations")
async def process_all_translations(payload: MediaInput):
    """
    Stub: processa todas as traduções para um media_id.
    """
    media_id = payload.input
    return {"status": "ok", "media_id": media_id}


@app.post("/embed-subtitles")
async def embed_subtitles(payload: MediaInput):
    """
    Stub: incorpora legendas em um vídeo já processado.
    """
    media_id = payload.input
    return {"status": "ok", "media_id": media_id}
