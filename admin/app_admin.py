import streamlit as st
import requests

API_URL = "https://backend-api-3jd8.onrender.com"

st.set_page_config(page_title="Admin Dashboard")

st.title("ADMIN - GESTIONE COMUNICAZIONI")

menu = st.sidebar.selectbox("Menu", ["Crea Messaggio", "Log Letture"])

# --- CREA MESSAGGIO ---
if menu == "Crea Messaggio":
    st.header("Nuovo Messaggio")

    titolo = st.text_input("Titolo messaggio")
    link_pdf = st.text_input("Link PDF")

    if st.button("Salva Messaggio"):
        requests.post(
            f"{API_URL}/messaggi",
            params={
                "titolo": titolo,
                "link_pdf": link_pdf
            }
        )
        st.success("Messaggio creato")

# --- LOG ---
if menu == "Log Letture":
    st.header("Log Letture")

    response = requests.get(f"{API_URL}/log")

    if response.status_code == 200:
        logs = response.json()

        for log in logs:
            st.write(
                f"Nome: {log['nome_dipendente']} | PDV: {log['pdv_id']} | Data: {log['timestamp']}"
            )
    else:
        st.error("Errore nel recupero dati")
