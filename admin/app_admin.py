@app.get("/log")
def get_log(db: Session = Depends(get_db)):
    logs = db.query(Log).all()

    return [
        {
            "nome_dipendente": l.nome_dipendente,
            "pdv_id": l.pdv_id,
            "timestamp": l.timestamp
        }
        for l in logs
    ]
