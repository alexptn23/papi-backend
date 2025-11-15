from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uuid
import asyncio

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
jobs: dict[str, dict] = {}

@app.get("/")
def root():
    return {"message": "PAPI backend online 🚀"}

@app.get("/status")
def status():
    return {"status": "ok"}

# 🔥 PROCESSAMENTO LEVE (Funciona no Render FREE)
@app.post("/process-video")
async def process_video(file: UploadFile = File(...)):
    # cria um job_id único
    job_id = str(uuid.uuid4())

    # registra o job como "processing"
    jobs[job_id] = {"status": "processing"}

    # função interna só pra simular um processamento leve
    async def fake_processing():
        await asyncio.sleep(2)  # simula trabalho
        jobs[job_id]["status"] = "completed"

    asyncio.create_task(fake_processing())

    return {"job_id": job_id}

# Rota para consultar o status do job
@app.get("/job-status/{job_id}")
def job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return {"status": "not_found"}
    return job
