from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PAPI Backend")

# ✅ Libera chamadas do frontend (Base44)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # depois podemos restringir ao domínio do Front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "PAPI backend online 🚀"}

@app.get("/status")
def status():
    return {"status": "ok"}

# Rota POST simples para testar envio do Front
@app.post("/echo")
def echo(payload: dict):
    return {"received": payload}
