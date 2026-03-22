import streamlit as st
import requests

API_URL = "https://backend-api-3jd8.onrender.com"

st.set_page_config(page_title="Selezione PDV")

st.title("SELEZIONA PUNTO VENDITA")

response = requests.get(f"{API_URL}/pdv")
pdv_list = response.json()

nomi_pdv = [p["nome"] for p in pdv_list]

pdv = st.selectbox("Scegli PDV", nomi_pdv)

if pdv:
    st.success(f"Hai selezionato: {pdv}")
