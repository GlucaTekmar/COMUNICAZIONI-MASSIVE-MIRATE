import streamlit as st
import requests
import pandas as pd
from datetime import date

# ==========================================
# CONFIG
# ==========================================

BACKEND_URL = "https://backend-api-3jd8.onrender.com"
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin123")

st.set_page_config(layout="wide")

# ==========================================
# LOGIN
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("LOGIN ADMIN")

    password = st.text_input("Password", type="password")

    if st.button("Accedi"):
        if password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Password errata")

    st.stop()

# ==========================================
# HEADER
# ==========================================

st.title("AREA ADMIN")

col1, col2 = st.columns([8, 1])
with col2:
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

st.markdown(f"Data: {date.today()}")

# ==========================================
# MENU
# ==========================================

page = st.sidebar.selectbox(
    "Seleziona pagina",
    ["NUOVO MESSAGGIO", "TABELLA MESSAGGI", "TABELLA LOG"]
)

# ==========================================
# NUOVO MESSAGGIO
# ==========================================

if page == "NUOVO MESSAGGIO":

    st.header("Nuova Circolare")

    titolo = st.text_input("Titolo")
    link_pdf = st.text_input("Link PDF")

    st.markdown("PDV destinatari (uno per riga)")
    pdv_text = st.text_area("")

    data_inizio = st.date_input("Data inizio")
    data_fine = st.date_input("Data fine")

    if st.button("CREA CIRCOLARE"):
        try:
            pdv_ids = [int(x.strip()) for x in pdv_text.split("\n") if x.strip()]

            res = requests.post(
                f"{BACKEND_URL}/admin/circolare",
                params={
                    "titolo": titolo,
                    "link_pdf": link_pdf,
                    "pdv_ids": pdv_ids,
                    "data_inizio": data_inizio,
                    "data_fine": data_fine
                }
            )

            if res.status_code == 200:
                st.success("Circolare creata")
            else:
                st.error("Errore")

        except:
            st.error("Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")

# ==========================================
# TABELLA MESSAGGI
# ==========================================

elif page == "TABELLA MESSAGGI":

    st.header("Circolari")

    if st.button("AGGIORNA"):
        st.rerun()

    try:
        res = requests.get(f"{BACKEND_URL}/admin/circolari")
        data = res.json()

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "Download Excel",
            df.to_csv(index=False),
            file_name="circolari.csv"
        )

    except:
        st.error("Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")

# ==========================================
# TABELLA LOG
# ==========================================

elif page == "TABELLA LOG":

    st.header("Log Lettura")

    if st.button("AGGIORNA"):
        st.rerun()

    try:
        res = requests.get(f"{BACKEND_URL}/admin/log")
        data = res.json()

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        st.download_button(
            "Download Excel",
            df.to_csv(index=False),
            file_name="log.csv"
        )

    except:
        st.error("Sistema temporaneamente non disponibile. Riprovare tra qualche minuto.")
