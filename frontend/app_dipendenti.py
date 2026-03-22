import streamlit as st

st.set_page_config(page_title="Selezione PDV")

st.title("SELEZIONA PUNTO VENDITA")

st.write("Digita le prime lettere della città")

pdv = st.selectbox("Scegli PDV", ["Milano - Coop Via Roma", "Roma - Centro", "Torino - Carrefour"])

if pdv:
    st.success(f"Hai selezionato: {pdv}")
