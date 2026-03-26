import os
from datetime import date

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(page_title="Comunicazioni PDV - Admin", layout="wide")

st.title("📢 Comunicazioni PDV - Admin")

# ---------- FUNZIONI API ----------

def api_get(path):
    try:
        r = requests.get(f"{BACKEND_URL}{path}", timeout=10)
        if r.status_code == 200:
            return r.json()
        st.error(f"Errore API: {r.text[:200]}")
        return []
    except Exception as e:
        st.error(f"Errore connessione backend: {e}")
        return []


def api_post(path, data):
    try:
        r = requests.post(f"{BACKEND_URL}{path}", params=data, timeout=10)
        if r.status_code == 200:
            return r.json()
        st.error(f"Errore API: {r.text[:200]}")
        return None
    except Exception as e:
        st.error(f"Errore connessione backend: {e}")
        return None


# ---------- MENU ----------

menu = st.sidebar.radio(
    "Seleziona sezione",
    [
        "Dashboard",
        "Gestione PDV",
        "Nuovo Messaggio",
        "Messaggi Inseriti",
        "Log Conferme",
    ],
)

# ---------- DASHBOARD ----------

if menu == "Dashboard":
    st.subheader("Stato sistema")

    db_ok = False
    try:
        r = requests.get(f"{BACKEND_URL}/health/db", timeout=5)
        db_ok = r.status_code == 200
    except:
        pass

    st.metric("Database", "OK" if db_ok else "ERRORE")

    st.divider()

# ---------- PDV ----------

elif menu == "Gestione PDV":
    st.subheader("Carica elenco PDV")

    lista = st.text_area(
        "Formato: ID,Nome PDV",
        height=300,
        placeholder="1001,PDV Milano\n1002,PDV Roma",
    )

    if st.button("Salva elenco PDV"):
        if not lista.strip():
            st.error("Inserisci dati")
        else:
            res = api_post("/admin/pdv/bulk", {"lista_pdv": lista})
            if res:
                st.success("Salvato")

    st.divider()

    st.subheader("PDV attuali")
    pdv = api_get("/pdv")

    if pdv:
        st.dataframe(pdv, use_container_width=True)
    else:
        st.info("Nessun PDV")

# ---------- NUOVO MESSAGGIO ----------

elif menu == "Nuovo Messaggio":
    st.subheader("Nuovo messaggio")

    titolo = st.text_input("Titolo")
    link_pdf = st.text_input("Link PDF")

    col1, col2 = st.columns(2)

    with col1:
        data_inizio = st.date_input("Data inizio", value=date.today())
    with col2:
        data_fine = st.date_input("Data fine", value=date.today())

    st.markdown("### PDV destinatari")

    pdv_input = st.text_area(
        "Inserisci ID PDV (uno per riga)",
        height=200,
        placeholder="1001\n1002\n1003",
    )

    if st.button("Crea messaggio"):

        if not titolo.strip():
            st.error("Titolo obbligatorio")

        elif not link_pdf.strip():
            st.error("Link obbligatorio")

        elif not pdv_input.strip():
            st.error("Inserisci almeno un PDV")

        else:
            try:
                pdv_ids = ",".join(
                    str(int(x.strip()))
                    for x in pdv_input.splitlines()
                    if x.strip()
                )
            except:
                st.error("Formato PDV non valido")
                st.stop()

            data = {
                "titolo": titolo,
                "link_pdf": link_pdf,
                "data_inizio": data_inizio.isoformat(),
                "data_fine": data_fine.isoformat(),
                "pdv_ids": pdv_ids,
            }

            res = api_post("/admin/messaggi", data)

            if res:
                st.success("Messaggio creato")

# ---------- MESSAGGI ----------

elif menu == "Messaggi Inseriti":
    st.subheader("Messaggi")

    data = api_get("/admin/messaggi")

    if data:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("Nessun messaggio")

# ---------- LOG ----------

elif menu == "Log Conferme":
    st.subheader("Log")

    data = api_get("/admin/log")

    if data:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("Nessun log")
