from fastapi import FastAPI
from backend.database import engine, Base

app = FastAPI()

# crea le tabelle nel database
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "API attiva"}

@app.get("/pdv")
def get_pdv():
    return [
        {"id": 1, "nome": "Milano - Coop Via Roma"},
        {"id": 2, "nome": "Roma - Centro"},
        {"id": 3, "nome": "Torino - Carrefour"}
    ]
