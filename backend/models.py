from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database import Base


class PDV(Base):
    __tablename__ = "pdv"

    pdv_id = Column(Integer, primary_key=True, index=True)
    nome_pdv = Column(String, nullable=False)


class Messaggi(Base):
    __tablename__ = "messaggi"

    messaggi_id = Column(Integer, primary_key=True, index=True)
    titolo = Column(String, nullable=False)
    link_pdf = Column(String, nullable=False)
    data_inizio = Column(Date, nullable=False)
    data_fine = Column(Date, nullable=False)


class MessaggiPDV(Base):
    __tablename__ = "messaggi_pdv"

    id = Column(Integer, primary_key=True, index=True)
    messaggi_id = Column(Integer, ForeignKey("messaggi.messaggi_id"), nullable=False)
    pdv_id = Column(Integer, ForeignKey("pdv.pdv_id"), nullable=False)


class Log(Base):
    __tablename__ = "log"

    log_id = Column(Integer, primary_key=True, index=True)
    nome_dipendente = Column(String, nullable=False)
    pdv_id = Column(Integer, ForeignKey("pdv.pdv_id"), nullable=False)
    messaggi_id = Column(Integer, ForeignKey("messaggi.messaggi_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('pdv_id', 'messaggi_id', 'timestamp', name='unique_log_per_day'),
    )
