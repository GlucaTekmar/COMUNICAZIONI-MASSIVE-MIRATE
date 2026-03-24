import streamlit as st
import requests

API_URL = "https://backend-api-3jd8.onrender.com"

st.set_page_config(page_title="Selezione PDV")

st.title("SELEZIONA PUNTO VENDITA")

nome = st.text_input("Inserisci nome e cognome")

response = requests.get(f"{API_URL}/pdv")
pdv_list = response.json()

nomi_pdv = [p["nome"] for p in pdv_list]

pdv = st.selectbox("Scegli PDV", nomi_pdv)

if pdv and nome:
    pdv_id = next(p["id"] for p in pdv_list if p["nome"] == pdv)

    requests.post(
        f"{API_URL}/log",
        params={
            "pdv_id": pdv_id,
            "nome_dipendente": nome
        }
    )

    st.success(f"Hai selezionato: {pdv}")
