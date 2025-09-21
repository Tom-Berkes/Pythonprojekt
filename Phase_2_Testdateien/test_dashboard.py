import streamlit as st
import test_berechnung as berechnung

st.set_page_config(page_title="Notendurchschnitt (Test)", layout="centered")
st.title("Gesamtnotendurchschnitt (Test)")

wert = berechnung.gesamtnotendurchschnitt
if wert is None:
    st.warning("Kein Durchschnitt berechenbar (keine gültigen Noten oder CSV-Problem).")
else:
    st.success(f"{wert:.2f}")