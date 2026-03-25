import streamlit as st
import requests

API_URL = "https://backend-api-3jd8.onrender.com"

st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("ADMIN - GESTIONE COMUNICAZIONI")

menu = st.sidebar.selectbox("Menu", ["PDV", "Crea Messaggio", "Log Letture"])

# =========================
# PDV
# =========================
if menu == "PDV":
    st.header("Gestione Lista PDV")

    lista_pdv = st.text_area("Incolla lista PDV (formato: ID,Nome)")

    if st.button("Carica PDV"):
        if not lista_pdv.strip():
            st.warning("Inserisci almeno un PDV")
        else:
            r = requests.post(
                f"{API_URL}/admin/pdv/bulk",
                params={"lista_pdv": lista_pdv}
            )

            if r.status_code == 200:
                st.success("PDV salvati correttamente")
            else:
                st.error(f"Errore: {r.text}")

    st.subheader("Lista PDV")

    res = requests.get(f"{API_URL}/pdv")

    if res.status_code == 200:
        pdv = res.json()

        if not pdv:
            st.info("Nessun PDV presente")
        else:
            for p in pdv:
                st.write(f"{p['pdv_id']} - {p['nome_pdv']}")
    else:
        st.error("Errore recupero PDV")


# =========================
# CREA MESSAGGIO
# =========================
elif menu == "Crea Messaggio":
    st.header("Nuovo Messaggio")

    titolo = st.text_input("Titolo messaggio")
    link_pdf = st.text_input("Link PDF")
    data_inizio = st.date_input("Data inizio")
    data_fine = st.date_input("Data fine")

    res = requests.get(f"{API_URL}/pdv")

    pdv_ids = []
    if res.status_code == 200:
        pdv = res.json()
        opzioni = {f"{p['pdv_id']} - {p['nome_pdv']}": p["pdv_id"] for p in pdv}
        selezionati = st.multiselect("Seleziona PDV", list(opzioni.keys()))
        pdv_ids = [opzioni[s] for s in selezionati]

    if st.button("Salva Messaggio"):
        if not titolo or not link_pdf or not pdv_ids:
            st.warning("Compila tutti i campi")
        else:
            r = requests.post(
                f"{API_URL}/admin/messaggi",
                params={
                    "titolo": titolo,
                    "link_pdf": link_pdf,
                    "data_inizio": data_inizio,
                    "data_fine": data_fine,
                    "pdv_ids": ",".join(map(str, pdv_ids))
                }
            )

            if r.status_code == 200:
                st.success("Messaggio creato")
            else:
                st.error(f"Errore: {r.text}")


# =========================
# LOG LETTURE
# =========================
elif menu == "Log Letture":
    st.header("Log Letture")

    res = requests.get(f"{API_URL}/admin/log")

    if res.status_code == 200:
        logs = res.json()

        if not logs:
            st.info("Nessun log presente")
        else:
            for l in logs:
                st.write(
                    f"{l['timestamp']} | {l['nome_dipendente']} | "
                    f"{l['nome_pdv']} | {l['titolo']}"
                )
    else:
        st.error("Errore nel recupero dati")
