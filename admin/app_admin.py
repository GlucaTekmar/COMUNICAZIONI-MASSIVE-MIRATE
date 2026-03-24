import streamlit as st
import requests

API_URL = "https://backend-api-3jd8.onrender.com"

st.set_page_config(page_title="Admin Dashboard")

st.title("ADMIN - GESTIONE COMUNICAZIONI")

menu = st.sidebar.selectbox("Menu", ["PDV", "Crea Messaggio", "Log Letture"])

if menu == "PDV":
    st.header("Gestione Lista PDV")

    lista_pdv = st.text_area("Incolla lista PDV (uno per riga)")

    if st.button("Carica PDV"):
        requests.post(
            f"{API_URL}/pdv_bulk",
            params={"lista_pdv": lista_pdv}
        )
        st.success("PDV caricati")

    st.subheader("Lista PDV")

    response = requests.get(f"{API_URL}/pdv")

    if response.status_code == 200:
        for p in response.json():
            st.write(f"{p['id']} - {p['nome']}")

# --- CREA MESSAGGIO ---
if menu == "Crea Messaggio":
    st.header("Nuovo Messaggio")

    titolo = st.text_input("Titolo messaggio")
    link_pdf = st.text_input("Link PDF")

    data_inizio = st.date_input("Data inizio", format="DD/MM/YYYY")
    data_fine = st.date_input("Data fine", format="DD/MM/YYYY")

    if st.button("Salva Messaggio"):
        requests.post(
            f"{API_URL}/messaggi",
            params={
                "titolo": titolo,
                "link_pdf": link_pdf,
                "data_inizio": data_inizio,
                "data_fine": data_fine
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
