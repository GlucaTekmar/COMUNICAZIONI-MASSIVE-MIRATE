from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.database import Base
import datetime

class Messaggio(Base):
    __tablename__ = "messaggi"

    id = Column(Integer, primary_key=True, index=True)
    titolo = Column(String)
    contenuto = Column(String)
    data_invio = Column(DateTime, default=datetime.datetime.utcnow)


class PDV(Base):
    __tablename__ = "pdv"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    codice = Column(String)


class LogLettura(Base):
    __tablename__ = "log_lettura"

    id = Column(Integer, primary_key=True, index=True)
    messaggio_id = Column(Integer)
    pdv_id = Column(Integer)
    letto = Column(Boolean, default=False)
    presenza = Column(Boolean, default=False)
    nome_operatore = Column(String)
