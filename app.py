from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "PAPI backend online 🚀"}

@app.get("/status")
def status():
    return {"status": "ok"}
