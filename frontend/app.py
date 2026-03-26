import os
from datetime import date

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:10000").rstrip("/")

st.set_page_config(page_title="Comunicazioni PDV - Admin", layout="wide")

st.title("📢 Comunicazioni PDV - Admin")


def api_get(path: str, params=None):
    return requests.get(f"{BACKEND_URL}{path}", params=params, timeout=30)


def api_post(path: str, params=None):
    return requests.post(f"{BACKEND_URL}{path}", params=params, timeout=30)


def load_pdv():
    try:
        response = api_get("/pdv")
        if response.status_code == 200:
            return response.json()
        st.error(f"Errore caricamento PDV: {response.text}")
        return []
    except requests.RequestException as exc:
        st.error(f"Backend non raggiungibile: {exc}")
        return []


def load_messaggi():
    try:
        response = api_get("/admin/messaggi")
        if response.status_code == 200:
            return response.json()
        st.error(f"Errore caricamento messaggi: {response.text}")
        return []
    except requests.RequestException as exc:
        st.error(f"Backend non raggiungibile: {exc}")
        return []


def load_log():
    try:
        response = api_get("/admin/log")
        if response.status_code == 200:
            return response.json()
        st.error(f"Errore caricamento log: {response.text}")
        return []
    except requests.RequestException as exc:
        st.error(f"Backend non raggiungibile: {exc}")
        return []


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

if menu == "Dashboard":
    st.subheader("Stato sistema")

    col1, col2, col3 = st.columns(3)

    try:
        health = api_get("/health/db")
        db_ok = health.status_code == 200
    except requests.RequestException:
        db_ok = False

    pdv = load_pdv()
    messaggi = load_messaggi()
    logs = load_log()

    with col1:
        st.metric("Database", "OK" if db_ok else "ERRORE")

    with col2:
        st.metric("PDV caricati", len(pdv))

    with col3:
        st.metric("Messaggi inseriti", len(messaggi))

    st.divider()

    st.subheader("Ultimi log")
    if logs:
        st.dataframe(logs, use_container_width=True)
    else:
        st.info("Nessun log disponibile.")


elif menu == "Gestione PDV":
    st.subheader("Caricamento / sostituzione elenco PDV")

    st.write("Formato richiesto: un PDV per riga nel formato `ID,Nome PDV`")

    lista_pdv = st.text_area(
        "Lista PDV",
        height=300,
        placeholder="1001,PDV Milano Centro\n1002,PDV Roma Termini",
    )

    if st.button("Salva elenco PDV"):
        if not lista_pdv.strip():
            st.error("Inserisci almeno una riga.")
        else:
            try:
                response = api_post("/admin/pdv/bulk", params={"lista_pdv": lista_pdv})
                if response.status_code == 200:
                    st.success("Elenco PDV aggiornato correttamente.")
                else:
                    st.error(f"Errore salvataggio PDV: {response.text}")
            except requests.RequestException as exc:
                st.error(f"Backend non raggiungibile: {exc}")

    st.divider()
    st.subheader("PDV attuali")

    pdv = load_pdv()
    if pdv:
        st.dataframe(pdv, use_container_width=True)
    else:
        st.info("Nessun PDV presente.")


elif menu == "Nuovo Messaggio":
    st.subheader("Inserisci nuovo messaggio")

    pdv = load_pdv()
    pdv_options = {f'{row["pdv_id"]} - {row["nome_pdv"]}': row["pdv_id"] for row in pdv}

    titolo = st.text_input("Titolo")
    link_pdf = st.text_input("Link PDF")
    col1, col2 = st.columns(2)

    with col1:
        data_inizio = st.date_input("Data inizio", value=date.today())

    with col2:
        data_fine = st.date_input("Data fine", value=date.today())

    selected_labels = st.multiselect(
        "Seleziona PDV destinatari",
        options=list(pdv_options.keys()),
    )

    if st.button("Crea messaggio"):
        if not titolo.strip():
            st.error("Titolo obbligatorio.")
        elif not link_pdf.strip():
            st.error("Link PDF obbligatorio.")
        elif not selected_labels:
            st.error("Seleziona almeno un PDV.")
        else:
            pdv_ids = ",".join(str(pdv_options[label]) for label in selected_labels)

            params = {
                "titolo": titolo.strip(),
                "link_pdf": link_pdf.strip(),
                "data_inizio": data_inizio.isoformat(),
                "data_fine": data_fine.isoformat(),
                "pdv_ids": pdv_ids,
            }

            try:
                response = api_post("/admin/messaggi", params=params)
                if response.status_code == 200:
                    st.success("Messaggio creato correttamente.")
                else:
                    st.error(f"Errore creazione messaggio: {response.text}")
            except requests.RequestException as exc:
                st.error(f"Backend non raggiungibile: {exc}")


elif menu == "Messaggi Inseriti":
    st.subheader("Elenco messaggi")

    messaggi = load_messaggi()
    if messaggi:
        st.dataframe(messaggi, use_container_width=True)
    else:
        st.info("Nessun messaggio presente.")


elif menu == "Log Conferme":
    st.subheader("Log conferme dipendenti")

    logs = load_log()
    if logs:
        st.dataframe(logs, use_container_width=True)
    else:
        st.info("Nessuna conferma registrata.")
