from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/messaggi")
def get_messaggi(db: Session = Depends(get_db)):
    return db.query(models.Messaggio).all()


@router.post("/messaggi")
def crea_messaggio(titolo: str, contenuto: str, db: Session = Depends(get_db)):
    nuovo = models.Messaggio(titolo=titolo, contenuto=contenuto)
    db.add(nuovo)
    db.commit()
    db.refresh(nuovo)
    return nuovo


@router.get("/pdv")
def get_pdv(db: Session = Depends(get_db)):
    return db.query(models.PDV).all()


@router.post("/log")
def log_lettura(
    messaggio_id: int,
    pdv_id: int,
    letto: bool,
    presenza: bool,
    nome_operatore: str,
    db: Session = Depends(get_db)
):
    log = models.LogLettura(
        messaggio_id=messaggio_id,
        pdv_id=pdv_id,
        letto=letto,
        presenza=presenza,
        nome_operatore=nome_operatore
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
