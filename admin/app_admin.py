import streamlit as st
import requests

API_URL = "https://backend-api-3jd8.onrender.com"

st.set_page_config(page_title="Admin Dashboard")

st.title("DASHBOARD ADMIN - LOG LETTURE")

response = requests.get(f"{API_URL}/log")

if response.status_code == 200:
    logs = response.json()

    for log in logs:
        st.write(
            f"Nome: {log['nome_dipendente']} | PDV: {log['pdv_id']} | Data: {log['timestamp']}"
        )
else:
    st.error("Errore nel recupero dati")
