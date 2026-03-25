import io
import os
from datetime import date, datetime
from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import and_, delete, func, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend.models import Log, Messaggi, MessaggiPDV, PDV

APP_NAME = "COMUNICAZIONI OPERATIVE API"
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", "/var/data/storage"))
PDF_STORAGE_DIR = STORAGE_ROOT / "circolari"
BACKUP_DIR = STORAGE_ROOT / "backup"

PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if PDF_STORAGE_DIR.exists():
    app.mount("/storage", StaticFiles(directory=str(STORAGE_ROOT)), name="storage")

DB_ERROR_MESSAGE = (
    "Sistema temporaneamente non disponibile.\n"
    "Riprova tra qualche minuto.\n\n"
    "Per ADMIN - necessario il ripristino del Database"
)


@app.exception_handler(SQLAlchemyError)
def sqlalchemy_exception_handler(_, __):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": DB_ERROR_MESSAGE},
    )


@app.get("/")
def root() -> dict:
    return {"status": "API attiva"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail=DB_ERROR_MESSAGE) from exc


@app.get("/pdv")
def list_pdv(db: Session = Depends(get_db)) -> List[dict]:
    rows = db.execute(select(PDV).order_by(PDV.nome_pdv.asc())).scalars().all()
    return [{"pdv_id": row.pdv_id, "nome_pdv": row.nome_pdv} for row in rows]


@app.post("/admin/pdv/bulk")
def replace_pdv_list(lista_pdv: str, db: Session = Depends(get_db)) -> dict:
    lines = [line.strip() for line in lista_pdv.splitlines() if line.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail="La lista PDV è vuota")

    parsed_rows = []
    seen_ids = set()

    for raw in lines:
        if "," not in raw:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Formato lista PDV non valido. Ogni riga deve essere nel formato: "
                    "ID,Nome PDV"
                ),
            )
        left, right = raw.split(",", 1)
        left = left.strip()
        right = right.strip()
        if not left.isdigit() or not right:
            raise HTTPException(
                status_code=400,
                detail=f"Riga non valida: {raw}",
            )

        pdv_id = int(left)
        if pdv_id in seen_ids:
            raise HTTPException(status_code=400, detail=f"ID PDV duplicato: {pdv_id}")

        seen_ids.add(pdv_id)
        parsed_rows.append({"pdv_id": pdv_id, "nome_pdv": right})

    try:
        existing = {
            row.pdv_id: row
            for row in db.execute(select(PDV).where(PDV.pdv_id.in_(list(seen_ids)))).scalars().all()
        }

        for row in parsed_rows:
            if row["pdv_id"] in existing:
                existing[row["pdv_id"]].nome_pdv = row["nome_pdv"]
            else:
                db.add(PDV(pdv_id=row["pdv_id"], nome_pdv=row["nome_pdv"]))

        db.execute(delete(PDV).where(PDV.pdv_id.not_in(list(seen_ids))))
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=DB_ERROR_MESSAGE) from exc

    return {"status": "ok", "count": len(parsed_rows)}


@app.get("/admin/messaggi")
def list_messaggi_admin(db: Session = Depends(get_db)) -> List[dict]:
    rows = db.execute(select(Messaggi).order_by(Messaggi.data_inizio.desc(), Messaggi.messaggi_id.desc())).scalars().all()
    return [
        {
            "messaggi_id": row.messaggi_id,
            "titolo": row.titolo,
            "link_pdf": row.link_pdf,
            "data_inizio": row.data_inizio.isoformat(),
            "data_fine": row.data_fine.isoformat(),
        }
        for row in rows
    ]


@app.post("/admin/messaggi")
def create_messaggio(
    titolo: str,
    link_pdf: str,
    data_inizio: date,
    data_fine: date,
    pdv_ids: str,
    db: Session = Depends(get_db),
) -> dict:
    titolo = titolo.strip()
    link_pdf = link_pdf.strip()
    if not titolo:
        raise HTTPException(status_code=400, detail="Titolo obbligatorio")
    if not link_pdf:
        raise HTTPException(status_code=400, detail="Link PDF obbligatorio")
    if data_fine < data_inizio:
        raise HTTPException(status_code=400, detail="Data fine precedente alla data inizio")

    try:
        parsed_ids = sorted({int(item.strip()) for item in pdv_ids.split(",") if item.strip()})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Lista PDV non valida") from exc

    if not parsed_ids:
        raise HTTPException(status_code=400, detail="Selezionare almeno un PDV")

    existing_ids = set(
        db.execute(select(PDV.pdv_id).where(PDV.pdv_id.in_(parsed_ids))).scalars().all()
    )
    missing = [pid for pid in parsed_ids if pid not in existing_ids]
    if missing:
        raise HTTPException(status_code=400, detail=f"PDV inesistenti: {missing}")

    try:
        message = Messaggi(
            titolo=titolo,
            link_pdf=link_pdf,
            data_inizio=data_inizio,
            data_fine=data_fine,
        )
        db.add(message)
        db.flush()

        for pdv_id in parsed_ids:
            db.add(MessaggiPDV(messaggi_id=message.messaggi_id, pdv_id=pdv_id))

        db.commit()
        db.refresh(message)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Errore di integrità sui dati inviati") from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=DB_ERROR_MESSAGE) from exc

    return {"status": "ok", "messaggi_id": message.messaggi_id}


@app.get("/messaggi/{pdv_id}")
def list_messaggi_for_pdv(pdv_id: int, db: Session = Depends(get_db)) -> List[dict]:
    today = date.today()

    query = (
        select(Messaggi, Log.log_id, Log.timestamp)
        .join(MessaggiPDV, MessaggiPDV.messaggi_id == Messaggi.messaggi_id)
        .outerjoin(
            Log,
            and_(
                Log.messaggi_id == Messaggi.messaggi_id,
                Log.pdv_id == pdv_id,
                func.date(Log.timestamp) == today,
            ),
        )
        .where(
            MessaggiPDV.pdv_id == pdv_id,
            Messaggi.data_inizio <= today,
            Messaggi.data_fine >= today,
        )
        .order_by(Messaggi.data_inizio.desc(), Messaggi.messaggi_id.desc())
    )

    rows = db.execute(query).all()

    output = []
    for msg, log_id, timestamp in rows:
        output.append(
            {
                "messaggi_id": msg.messaggi_id,
                "titolo": msg.titolo,
                "link_pdf": msg.link_pdf,
                "data_inizio": msg.data_inizio.isoformat(),
                "data_fine": msg.data_fine.isoformat(),
                "gia_confermato_oggi": log_id is not None,
                "timestamp_conferma": timestamp.isoformat() if timestamp else None,
            }
        )
    return output


@app.post("/log")
def create_log(nome_dipendente: str, pdv_id: int, messaggi_id: int, db: Session = Depends(get_db)) -> dict:
    nome_dipendente = nome_dipendente.strip()
    if not nome_dipendente:
        raise HTTPException(status_code=400, detail="Nome dipendente obbligatorio")

    pdv_exists = db.execute(select(PDV.pdv_id).where(PDV.pdv_id == pdv_id)).scalar_one_or_none()
    if pdv_exists is None:
        raise HTTPException(status_code=404, detail="PDV non trovato")

    message_exists = db.execute(
        select(Messaggi.messaggi_id).where(Messaggi.messaggi_id == messaggi_id)
    ).scalar_one_or_none()
    if message_exists is None:
        raise HTTPException(status_code=404, detail="Messaggio non trovato")

    try:
        log_row = Log(
            nome_dipendente=nome_dipendente,
            pdv_id=pdv_id,
            messaggi_id=messaggi_id,
        )
        db.add(log_row)
        db.commit()
        db.refresh(log_row)
    except IntegrityError:
        db.rollback()
        return {"status": "ok", "detail": "Conferma già registrata oggi"}
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=DB_ERROR_MESSAGE) from exc

    return {"status": "ok", "log_id": log_row.log_id}


@app.get("/admin/log")
def list_log_admin(db: Session = Depends(get_db)) -> List[dict]:
    query = (
        select(
            Log.log_id,
            Log.nome_dipendente,
            Log.timestamp,
            PDV.pdv_id,
            PDV.nome_pdv,
            Messaggi.messaggi_id,
            Messaggi.titolo,
        )
        .join(PDV, PDV.pdv_id == Log.pdv_id)
        .join(Messaggi, Messaggi.messaggi_id == Log.messaggi_id)
        .order_by(Log.timestamp.desc(), Log.log_id.desc())
    )

    rows = db.execute(query).all()
    return [
        {
            "log_id": row.log_id,
            "nome_dipendente": row.nome_dipendente,
            "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            "pdv_id": row.pdv_id,
            "nome_pdv": row.nome_pdv,
            "messaggi_id": row.messaggi_id,
            "titolo": row.titolo,
        }
        for row in rows
    ]


@app.get("/admin/backup/latest")
def download_latest_backup() -> Response:
    if not BACKUP_DIR.exists():
        raise HTTPException(status_code=404, detail="Cartella backup non trovata")

    backup_files = sorted(BACKUP_DIR.glob("*.sql"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not backup_files:
        raise HTTPException(status_code=404, detail="Nessun backup disponibile")

    latest = backup_files[0]
    return FileResponse(
        path=latest,
        filename=latest.name,
        media_type="application/sql",
    )
