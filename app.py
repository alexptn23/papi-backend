from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
import uuid
import httpx
import os

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

# Modelo da requisição
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
    return data

# ------------------------------
# FUNÇÃO PRINCIPAL DE PROCESSAR
# ------------------------------

async def run_process_video(job_id: str, video_url: str, target_languages: list[str]):
    try:
        # Baixar vídeo
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url)
            response.raise_for_status()

        # Criar arquivo temporário
        input_path = f"/tmp/papi_input_{job_id}.mp4"
        with open(input_path, "wb") as f:
            f.write(response.content)

        # Aqui entraria WHISPER + TTS + tradução
        # Simulação:
        output_path = f"/tmp/papi_video_{job_id}.mp4"
        with open(output_path, "wb") as f:
            f.write(response.content)  # apenas copia na simulação

        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["result_url"] = output_path
        JOBS[job_id]["error"] = None

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["result_url"] = None
        JOBS[job_id]["error"] = str(e)


# ------------------------------
# ENDPOINT: PROCESSAR VÍDEO
# ------------------------------

@app.post("/process-video")
async def process_video(request: ProcessVideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())

    JOBS[job_id] = {
        "status": "queued",
        "result_url": None,
        "error": None
    }

    background_tasks.add_task(
        run_process_video,
        job_id,
        request.video_url,
        request.target_languages
    )

    return {"job_id": job_id, "status": "queued"}


# ------------------------------
# ENDPOINT: STATUS DO JOB
# ------------------------------

@app.get("/job-status/{job_id}")
def job_status(job_id: str):
    if job_id not in JOBS:
        return {"status": "not_found"}

    return {
        "status": JOBS[job_id]["status"],
        "result_url": JOBS[job_id]["result_url"],
        "error": JOBS[job_id]["error"]
    }


# ------------------------------
# ENDPOINT: DOWNLOAD FINAL
# ------------------------------

@app.get("/download/{job_id}")
def download_result(job_id: str):
    if job_id not in JOBS:
        return {"error": "job_not_found"}

    path = JOBS[job_id]["result_url"]

    if not path or not os.path.exists(path):
        return {"error": "file_not_ready"}

    return FileResponse(
        path,
        media_type="video/mp4",
        filename=f"papi_output_{job_id}.mp4"
    )
