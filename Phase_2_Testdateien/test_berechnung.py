from __future__ import annotations
from pathlib import Path

from test_csv_daten import CsvRepository, CsvLesefehler
from test_mapping import zeilen_zu_pruefungsleistungen
from test_klassen import StudiengangService

# Eigene Test-CSV
csv_datei_pfad = Path("test_studium.csv")

try:
    repo = CsvRepository(csv_datei_pfad)
    zeilen = list(repo.datenzeilen_iterieren())
    pruefungen = zeilen_zu_pruefungsleistungen(zeilen)
    gesamtnotendurchschnitt = StudiengangService.berechne_gesamtdurchschnitt(pruefungen)
except CsvLesefehler as e:
    gesamtnotendurchschnitt = None
    print(f"CSV-Fehler: {e}")