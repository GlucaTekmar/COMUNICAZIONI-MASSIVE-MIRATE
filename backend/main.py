from fastapi import FastAPI
from backend.routes import router as api_router
from backend.database import engine, Base

app = FastAPI()

# CREA TABELLE AUTOMATICAMENTE
Base.metadata.create_all(bind=engine)

app.include_router(api_router)

@app.get("/")
def root():
    return {"status": "ok"}
