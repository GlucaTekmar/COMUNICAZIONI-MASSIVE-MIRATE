import streamlit as st
import requests
from datetime import date

# ==========================================
# CONFIG
# ==========================================

BACKEND_URL = "https://backend-api-3jd8.onrender.com"
HOME_URL = "https://eu.jotform.com/app/253605296903360"

st.set_page_config(layout="wide")

# ==========================================
# STYLE
# ==========================================

st.markdown("""
<style>
body {
    background-color: red;
}
.stButton>button {
    background-color: black;
    color: red;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================

st.title("COMUNICAZIONI OPERATIVE")
st.markdown(f"Data: {date.today()}")

st.markdown(f"[TORNA ALLA HOME]({HOME_URL})")

# ==========================================
# SESSION STATE
# ==========================================

if "pdv_id" not in st.session_state:
    st.session_state.pdv_id = None

if "pdv_nome" not in st.session_state:
    st.session_state.pdv_nome = None

if "confermato" not in st.session_state:
    st.session_state.confermato = False

# ==========================================
# SELEZIONE PDV
# ==========================================

if not st.session_state.pdv_id:

    st.header("SELEZIONA PDV")

    try:
        res = requests.get(f"{BACKEND_URL}/pdv")
        pdv_list = res.json()

        pdv_dict = {f"{p['nome_pdv']} ({p['pdv_id']})": p['pdv_id'] for p in pdv_list}

        scelta = st.selectbox("digita le prime lettere della città", list(pdv_dict.keys()))

        if st.button("CONFERMA"):
            st.session_state.pdv_id = pdv_dict[scelta]
            st.session_state.pdv_nome = scelta
            st.rerun()

    except:
        st.error("Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")

# ==========================================
# CONFERMA PDV
# ==========================================

elif not st.session_state.confermato:

    st.markdown("### TI TROVI AL PUNTO VENDITA")
    st.markdown(f"## {st.session_state.pdv_nome}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("CONFERMA"):
            st.session_state.confermato = True
            st.rerun()

    with col2:
        if st.button("CAMBIA PDV"):
            st.session_state.pdv_id = None
            st.session_state.pdv_nome = None
            st.rerun()

# ==========================================
# VISUALIZZAZIONE CIRCOLARE
# ==========================================

else:

    try:
        res = requests.get(f"{BACKEND_URL}/circolare/{st.session_state.pdv_id}")
        data = res.json()

        if "message" in data:
            st.info(data["message"])
        else:
            st.header(data["titolo"])
            st.markdown(f"[APRI PDF]({data['link_pdf']})")

            nome = st.text_input("Nome e Cognome")

            conferma = st.checkbox("Confermo di aver letto la comunicazione")

            if conferma and st.button("INVIA"):
                requests.post(
                    f"{BACKEND_URL}/log",
                    params={
                        "nome_dipendente": nome,
                        "pdv_id": st.session_state.pdv_id,
                        "circolare_id": data["circolare_id"]
                    }
                )
                st.success("Registrazione effettuata")

    except:
        st.error("Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")
