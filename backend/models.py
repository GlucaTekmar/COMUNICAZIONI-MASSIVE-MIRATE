from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from backend.database import Base


class PDV(Base):
    __tablename__ = "pdv"

    pdv_id = Column(Integer, primary_key=True)
    nome_pdv = Column(String, nullable=False)


class Messaggi(Base):
    __tablename__ = "messaggi"

    messaggi_id = Column(Integer, primary_key=True)
    titolo = Column(String)
    link_pdf = Column(String)
    data_inizio = Column(Date)
    data_fine = Column(Date)


class MessaggiPDV(Base):
    __tablename__ = "messaggi_pdv"

    id = Column(Integer, primary_key=True)
    messaggi_id = Column(Integer, ForeignKey("messaggi.messaggi_id"))
    pdv_id = Column(Integer, ForeignKey("pdv.pdv_id"))


class Log(Base):
    __tablename__ = "log"

    log_id = Column(Integer, primary_key=True)
    nome_dipendente = Column(String)
    pdv_id = Column(Integer)
    messaggi_id = Column(Integer)
    timestamp = Column(TIMESTAMP, server_default=func.now())
