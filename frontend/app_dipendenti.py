import streamlit as st
import requests

BACKEND_URL = "https://backend-api-3jd8.onrender.com"

st.title("SELEZIONA PUNTO VENDITA")

nome = st.text_input("Inserisci nome e cognome")

# carica PDV
response = requests.get(f"{BACKEND_URL}/pdv")

if response.status_code != 200:
    st.error("Errore nel recupero PDV")
    st.stop()

pdv_list = response.json()

if not pdv_list:
    st.warning("Nessun PDV disponibile")
    st.stop()

pdv_dict = {f"{p['pdv_id']} - {p['nome_pdv']}": p["pdv_id"] for p in pdv_list}

scelta = st.selectbox("Seleziona PDV", list(pdv_dict.keys()))
pdv_id = pdv_dict[scelta]

if st.button("Conferma"):
    if not nome:
        st.warning("Inserisci il nome")
    else:
        st.success(f"PDV selezionato: {scelta}")

        # carica messaggi per PDV
        res_msg = requests.get(f"{BACKEND_URL}/messaggi/{pdv_id}")

        if res_msg.status_code != 200:
            st.error("Errore nel recupero messaggi")
            st.stop()

        messaggi = res_msg.json()

        if not messaggi:
            st.info("su questo PDV oggi NON sono previste Promo nè Comunicazioni Operative. Buon lavoro")
        else:
            for m in messaggi:
                st.subheader(m["titolo"])
                st.write(f"Dal {m['data_inizio']} al {m['data_fine']}")

                if st.button(f"Conferma lettura {m['messaggi_id']}"):
                    r = requests.post(
                        f"{BACKEND_URL}/log",
                        params={
                            "nome_dipendente": nome,
                            "pdv_id": pdv_id,
                            "messaggi_id": m["messaggi_id"],
                        },
                    )

                    if r.status_code == 200:
                        st.success("Conferma registrata")
                    else:
                        st.error("Errore invio log")
