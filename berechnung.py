# Orchestrierung: CSV lesen -> Domain mappen -> Studiengang instanziieren -> Kennzahlen berechnen.
from __future__ import annotations

from pathlib import Path
from datetime import date

from csv_daten import CsvRepository
from mapping import zeilen_zu_domaene
from klassen import Studiengang, KursStatus

# Pfad zur Datenquelle (CSV).
csv_datei_pfad = Path("studium.csv")

# Domänen-Parameter (Regelzeit/Start/ECTS) zentral gesetzt.
name_studiengang = "Softwareentwicklung"
regelzeit_monate = 36
# Studienende (hier fest gesetzt, entspricht Projektannahme/Anforderung)
studienende = date(2026, 9, 30)
maximale_ects = 180
# Startdatum ~ Ende minus Regelzeit (einfacher Rücksprung um 36*~30 Tage)
startdatum = date(studienende.year - 3, studienende.month, studienende.day)

# CSV-Rohdaten iterieren (robuster Reader, toleriert verschiedene Exportformen).
repo = CsvRepository(csv_datei_pfad)
if hasattr(repo, "datenzeilen_iterieren"):
    zeilen = repo.datenzeilen_iterieren()
else:
    # Abwärtskompatibilität, falls ältere Variante vorhanden wäre.
    zeilen = repo.iter_rows()  # type: ignore[attr-defined]

# Mapping in Domänenobjekte (keine Fachlogik; reine Konvertierung).
kurse, pruefungsleistungen = zeilen_zu_domaene(zeilen)

# Studiengang-Instanz als Aggregatwurzel.
studiengang = Studiengang(
    name=name_studiengang,
    regelzeitMonate=regelzeit_monate,
    startDatum=startdatum,
    maximaleEcts=maximale_ects
)

# Kennzahlen (nur Methodenaufrufe auf der Domäne, keine Berechnungs-„Lecks“ in die Orchestrierung).
durchschnitt = studiengang.berechneGesamtdurchschnitt(pruefungsleistungen)
ects_prozent = studiengang.berechneEctsProzent(kurse)
ects_abgeschlossen = sum((k.ects or 0) for k in kurse if k.status == KursStatus.ABGESCHLOSSEN)
verbleibende_tage = studiengang.berechneVerbleibendeTage()
belegte_kurse = studiengang.getBelegteKurse(kurse)