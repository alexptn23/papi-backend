from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import asyncio

app = FastAPI()

# 🔓 CORS liberado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧰 Banco de jobs (em memória)
JOBS: dict[str, dict] = {}


# 📦 Modelo da requisição para processar vídeo
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
def echo(data: dict):
    return {"you_sent": data}


# ⚙ Processamento (simulado por enquanto)
async def run_process_video(job_id: str, params: ProcessVideoRequest):
    try:
        JOBS[job_id]["status"] = "processing"

        # SIMULA o processamento por 5 segundos
        await asyncio.sleep(5)

        # Resultado temporário
        result_url = params.video_url

        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["result_url"] = result_url

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)


# 🚀 Inicia o job
@app.post("/process-video")
async def process_video(body: ProcessVideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())

    JOBS[job_id] = {
        "status": "queued",
        "result_url": None,
        "error": None,
        "request": body.dict(),
    }

    background_tasks.add_task(run_process_video, job_id, body)

    return {
        "job_id": job_id,
        "status": "queued",
    }


# 🔍 Consulta status do job
@app.get("/job-status/{job_id}")
def job_status(job_id: str):
    job = JOBS.get(job_id)

    if not job:
        return {
            "job_id": job_id,
            "status": "not_found",
            "error": "Job não encontrado",
        }

    return {
        "job_id": job_id,
        "status": job["status"],
        "result_url": job["result_url"],
        "error": job["error"],
    }
