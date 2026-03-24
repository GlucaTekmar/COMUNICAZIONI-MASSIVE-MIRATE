from fastapi import FastAPI
from backend.database import engine, Base

app = FastAPI()

# crea le tabelle nel database
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "API attiva"}

@app.get("/pdv")
def get_pdv(db: Session = Depends(get_db)):
    pdv = db.query(PDV).all()
    return [{"id": p.pdv_id, "nome": p.nome_pdv} for p in pdv]
    
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Log

@app.post("/log")
def crea_log(pdv_id: int, nome_dipendente: str, db: Session = Depends(get_db)):
    nuovo_log = Log(
        pdv_id=pdv_id,
        nome_dipendente=nome_dipendente
    )
    db.add(nuovo_log)
    db.commit()
    return {"status": "log salvato"}

@app.get("/log")
def get_log(db: Session = Depends(get_db)):
    logs = db.query(Log).all()

    result = []
    for l in logs:
        result.append({
            "nome_dipendente": l.nome_dipendente,
            "pdv_id": l.pdv_id,
            "timestamp": str(l.timestamp)
        })

    return result

from backend.models import Messaggi

from datetime import date

@app.post("/messaggi")
def crea_messaggio(
    titolo: str,
    link_pdf: str,
    data_inizio: date,
    data_fine: date,
    db: Session = Depends(get_db)
):
    nuovo = Messaggi(
        titolo=titolo,
        link_pdf=link_pdf,
        data_inizio=data_inizio,
        data_fine=data_fine
    )
    db.add(nuovo)
    db.commit()
    return {"status": "messaggio creato"}

@app.post("/pdv_bulk")
def crea_pdv_bulk(lista_pdv: str, db: Session = Depends(get_db)):
    righe = lista_pdv.split("\n")

    for riga in righe:
        nome = riga.strip()
        if nome:
            nuovo = PDV(nome_pdv=nome)
            db.add(nuovo)

    db.commit()
    return {"status": "pdv caricati"}

@app.post("/reset_pdv")
def reset_pdv(db: Session = Depends(get_db)):
    db.query(PDV).delete()
    db.commit()
    return {"status": "pdv cancellati"}
