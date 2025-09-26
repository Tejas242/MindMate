from fastapi import FastAPI

app = FastAPI(title="MindMate API")

@app.get("/")
def root():
    return {"msg": "MindMate API running 🚀"}
