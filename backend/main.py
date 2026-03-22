from fastapi import FastAPI
from backend.database import engine, Base

app = FastAPI()

# crea le tabelle nel database
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "API attiva"}
