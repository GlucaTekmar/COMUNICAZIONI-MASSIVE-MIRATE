from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List
import os
import shutil

from backend.database import Base, engine, get_db, check_db_connection
from backend import models

# ==========================================
# APP INIT
# ==========================================

app = FastAPI()

# Creazione tabelle (DB vuoto → OK)
Base.metadata.create_all(bind=engine)

# ==========================================
# COSTANTI
# ==========================================

STORAGE_PATH = "/var/data"

# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health():
    if not check_db_connection():
        return {"status": "error", "message": "Sistema temporaneamente non disponibile. Riprovare tra qualche minuto."}
    return {"status": "ok"}

# ==========================================
# PDV LIST
# ==========================================

@app.get("/pdv")
def get_pdv(db: Session = Depends(get_db)):
    try:
        return db.query(models.PDV).all()
    except:
        raise HTTPException(status_code=500, detail="Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")

# ==========================================
# CIRCOLARE ATTIVA PER PDV
# ==========================================

@app.get("/circolare/{pdv_id}")
def get_circolare(pdv_id: int, db: Session = Depends(get_db)):
    try:
        today = date.today()

        circolare = (
            db.query(models.Circolare)
            .join(models.CircolarePDV)
            .filter(
                models.CircolarePDV.pdv_id == pdv_id,
                models.Circolare.data_inizio <= today,
                models.Circolare.data_fine >= today
            )
            .first()
        )

        if not circolare:
            return {"message": "su questo PDV oggi non ci sono Promo né Comunicazioni Operative. Buon lavoro"}

        return {
            "circolare_id": circolare.circolare_id,
            "titolo": circolare.titolo,
            "link_pdf": circolare.link_pdf
        }

    except:
        raise HTTPException(status_code=500, detail="Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")

# ==========================================
# REGISTRA LOG
# ==========================================

@app.post("/log")
def registra_log(nome_dipendente: str, pdv_id: int, circolare_id: int, db: Session = Depends(get_db)):
    try:
        today = date.today()

        existing = db.query(models.Log).filter(
            models.Log.pdv_id == pdv_id,
            models.Log.circolare_id == circolare_id
        ).all()

        for log in existing:
            if log.timestamp.date() == today:
                return {"message": "già registrato oggi"}

        new_log = models.Log(
            nome_dipendente=nome_dipendente,
            pdv_id=pdv_id,
            circolare_id=circolare_id,
            timestamp=datetime.utcnow()
        )

        db.add(new_log)
        db.commit()

        return {"message": "ok"}

    except:
        raise HTTPException(status_code=500, detail="Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")

# ==========================================
# ADMIN — CREA CIRCOLARE
# ==========================================

@app.post("/admin/circolare")
def crea_circolare(
    titolo: str,
    link_pdf: str,
    pdv_ids: List[int],
    data_inizio: date,
    data_fine: date,
    db: Session = Depends(get_db)
):
    try:
        circolare = models.Circolare(
            titolo=titolo,
            link_pdf=link_pdf,
            data_inizio=data_inizio,
            data_fine=data_fine
        )

        db.add(circolare)
        db.commit()
        db.refresh(circolare)

        for pdv_id in pdv_ids:
            relazione = models.CircolarePDV(
                circolare_id=circolare.circolare_id,
                pdv_id=pdv_id
            )
            db.add(relazione)

        db.commit()

        return {"message": "circolare creata"}

    except:
        raise HTTPException(status_code=500, detail="Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")

# ==========================================
# ADMIN — LISTA CIRCOLARI
# ==========================================

@app.get("/admin/circolari")
def lista_circolari(db: Session = Depends(get_db)):
    try:
        circolari = db.query(models.Circolare).all()

        return [
            {
                "id": c.circolare_id,
                "titolo": c.titolo,
                "link_pdf": c.link_pdf,
                "data_inizio": c.data_inizio,
                "data_fine": c.data_fine,
                "stato": c.stato
            }
            for c in circolari
        ]

    except:
        raise HTTPException(status_code=500, detail="Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")

# ==========================================
# ADMIN — LOG
# ==========================================

@app.get("/admin/log")
def lista_log(db: Session = Depends(get_db)):
    try:
        logs = db.query(models.Log).all()

        return [
            {
                "nome": l.nome_dipendente,
                "pdv": l.pdv_id,
                "circolare": l.circolare_id,
                "timestamp": l.timestamp
            }
            for l in logs
        ]

    except:
        raise HTTPException(status_code=500, detail="Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")

# ==========================================
# ADMIN — PULIZIA STORAGE
# ==========================================

@app.post("/admin/clean-storage")
def clean_storage(db: Session = Depends(get_db)):
    try:
        files = os.listdir(STORAGE_PATH)
        db_links = [c.link_pdf for c in db.query(models.Circolare).all()]

        removed = []

        for f in files:
            full_path = os.path.join(STORAGE_PATH, f)
            if full_path not in db_links:
                os.remove(full_path)
                removed.append(f)

        return {"removed": removed}

    except:
        raise HTTPException(status_code=500, detail="Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")
