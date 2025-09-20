# Streamlit-UI: zeigt die in berechnung.py vorbereiteten Kennzahlen in 2x2-Kacheln + Tabelle.
import streamlit as st
import berechnung  # lädt Top-Level-Variablen (bereits berechnet)

st.set_page_config(page_title="Studium-Dashboard", layout="wide")

# CI-Farben für Kacheln.
FARBE_LILA = "#8e44ad"
FARBE_BLAU = "#2E86C1"
FARBE_ROT = "#c0392b"

# Grundlegendes Styling (Abstände/Kachel-Visuals).
st.markdown(f"""
<style>
.block-container {{
  padding-top: 2.5rem;
  padding-bottom: 2rem;
}}
.kachel {{
  padding: 24px;
  border-radius: 12px;
  color: white;
  text-align: center;
  height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}}
.k_title {{ font-size: 18px; margin-bottom: 8px; font-weight: 600; }}
.k_value {{ font-size: 36px; font-weight: 800; }}
.table_header {{
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}}
</style>
""", unsafe_allow_html=True)

# Kopfbereich
st.markdown("<h2 style='text-align:center; margin: 0 0 16px 0;'>Studium-Dashboard</h2>", unsafe_allow_html=True)

# Kennzahlen aus Orchestrierung importiert (keine Berechnung in der UI).
durchschnitt = berechnung.durchschnitt          # Optional[float]
ects_prozent = berechnung.ects_prozent          # float
verbleibende_tage = berechnung.verbleibende_tage  # int
belegte_kurse = berechnung.belegte_kurse        # List[Kurs]
ects_abgeschlossen = getattr(berechnung, "ects_abgeschlossen", None)  # optional

# 2x2-Layout
oben_links, oben_rechts = st.columns(2)
unten_links, unten_rechts = st.columns(2)

# Kachel: Gesamtnotendurchschnitt (Formatierung bei None -> "-").
durchschnitt_text = "-" if durchschnitt is None else f"{durchschnitt:.2f}"
with oben_links:
    st.markdown(
        f"""
        <div class="kachel" style="background:{FARBE_LILA};">
          <div class="k_title">Gesamtnotendurchschnitt</div>
          <div class="k_value">{durchschnitt_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Kachel: ECTS-Fortschritt in % + Absolutwert (z. B. 150/180).
ects_abs_text = f"{ects_abgeschlossen}/180" if ects_abgeschlossen is not None else ""
with oben_rechts:
    st.markdown(
        f"""
        <div class="kachel" style="background:{FARBE_BLAU};">
          <div class="k_title">ECTS-Fortschritt</div>
          <div class="k_value">{ects_prozent:.2f}%</div>
          <div style="margin-top:4px; font-size:16px; font-weight:600;">{ects_abs_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Tabelle: Aktuell belegte Kurse (neutrale Darstellung, keine Kachel).
with unten_links:
    tabellen_headline = "Aktuell belegte Kurse"  # Überschrift der ersten Spalte
    if belegte_kurse:
        rows = []
        for k in belegte_kurse:
            rows.append({
                tabellen_headline: k.name,
                "ECTS": k.ects if k.ects is not None else "",
            })
        st.table(rows)
    else:
        st.info("Derzeit sind keine Kurse mit Status 'BELEGT' vorhanden.")

# Kachel: Verbleibende Tage bis Studienende.
with unten_rechts:
    st.markdown(
        f"""
        <div class="kachel" style="background:{FARBE_ROT};">
          <div class="k_title">Verbleibende Tage bis Studienende</div>
          <div class="k_value">{verbleibende_tage}</div>
        </div>
        """,
        unsafe_allow_html=True
    )