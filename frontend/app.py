import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(page_title="Comunicazioni PDV", layout="centered")

st.title("📢 Comunicazioni PDV")

menu = st.sidebar.selectbox("Seleziona sezione", ["Invio Messaggi", "Visualizza Messaggi"])

if menu == "Invio Messaggi":
    st.header("Invia nuovo messaggio")

    titolo = st.text_input("Titolo")
    contenuto = st.text_area("Contenuto")

    if st.button("Invia"):
        response = requests.post(
            f"{BACKEND_URL}/messaggi",
            params={"titolo": titolo, "contenuto": contenuto}
        )
        if response.status_code == 200:
            st.success("Messaggio inviato")
        else:
            st.error("Errore invio")


elif menu == "Visualizza Messaggi":
    st.header("Messaggi inviati")

    response = requests.get(f"{BACKEND_URL}/messaggi")

    if response.status_code == 200:
        messaggi = response.json()

        for m in messaggi:
            st.subheader(m["titolo"])
            st.write(m["contenuto"])
            st.caption(m["data_invio"])
    else:
        st.error("Errore caricamento messaggi")
