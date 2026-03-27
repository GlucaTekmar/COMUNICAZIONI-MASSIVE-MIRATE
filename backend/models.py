from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

# ==========================================
# TABELLA PDV
# ==========================================

class PDV(Base):
    __tablename__ = "pdv"

    pdv_id = Column(Integer, primary_key=True, index=True)
    nome_pdv = Column(String, nullable=False)

    circolari = relationship("CircolarePDV", back_populates="pdv")
    log = relationship("Log", back_populates="pdv")


# ==========================================
# TABELLA CIRCOLARI
# ==========================================

class Circolare(Base):
    __tablename__ = "circolari"

    circolare_id = Column(Integer, primary_key=True, index=True)
    titolo = Column(String, nullable=False)
    link_pdf = Column(String, nullable=False)
    data_inizio = Column(Date, nullable=False)
    data_fine = Column(Date, nullable=False)

    pdv_associati = relationship("CircolarePDV", back_populates="circolare")
    log = relationship("Log", back_populates="circolare")

    @property
    def stato(self):
        today = datetime.utcnow().date()
        if self.data_inizio <= today <= self.data_fine:
            return "ATTIVO"
        elif today > self.data_fine:
            return "CHIUSO"
        else:
            return "PROGRAMMATO"


# ==========================================
# TABELLA CIRCOLARI_PDV
# ==========================================

class CircolarePDV(Base):
    __tablename__ = "circolari_pdv"

    id = Column(Integer, primary_key=True, index=True)
    circolare_id = Column(Integer, ForeignKey("circolari.circolare_id", ondelete="CASCADE"))
    pdv_id = Column(Integer, ForeignKey("pdv.pdv_id", ondelete="CASCADE"))

    circolare = relationship("Circolare", back_populates="pdv_associati")
    pdv = relationship("PDV", back_populates="circolari")


# ==========================================
# TABELLA LOG
# ==========================================

class Log(Base):
    __tablename__ = "log"

    log_id = Column(Integer, primary_key=True, index=True)
    nome_dipendente = Column(String, nullable=False)
    pdv_id = Column(Integer, ForeignKey("pdv.pdv_id"))
    circolare_id = Column(Integer, ForeignKey("circolari.circolare_id"))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    pdv = relationship("PDV", back_populates="log")
    circolare = relationship("Circolare", back_populates="log")

    __table_args__ = (
        UniqueConstraint("pdv_id", "circolare_id", "timestamp", name="unique_log_per_day_temp"),
    )
