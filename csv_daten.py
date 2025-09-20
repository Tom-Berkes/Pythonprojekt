# Verantwortung: CSV robust einlesen, Kopfzeile validieren, Roh-Zeilen als Dict[str, str] liefern.
# Keine Mapping-/Fachlogik hier.

from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterator, List, Optional
import csv

class CsvLesefehler(Exception):
    """Fehler beim Lesen/Interpretieren der CSV-Datei mit verständlicher Meldung."""
    def __init__(self, nachricht: str) -> None:
        super().__init__(nachricht)
        self.nachricht = nachricht

class CsvRepository:
    """Kapselt den CSV-Zugriff und liefert jede Zeile als Dict[str, str] (roh/normalisiert)."""

    def __init__(self, dateipfad: Path, trennzeichen: str = ";", kodierung: str = "utf-8-sig") -> None:
        self._dateipfad = dateipfad
        self._trennzeichen = trennzeichen
        self._kodierung = kodierung
        self._kopfzeile: Optional[List[str]] = None
        self._spaltenindex: Optional[Dict[str, int]] = None

    @staticmethod
    def _sauber(wert: str) -> str:
        """Trimmt Whitespaces und entfernt paarige äußere Anführungszeichen."""
        if wert is None:
            return ""
        w = str(wert).strip()
        # Entfernt äußere Quotes ggf. zweimal (häufige Exporteigenheiten).
        for _ in range(2):
            if len(w) >= 2 and ((w[0] == '"' and w[-1] == '"') or (w[0] == "'" and w[-1] == "'")):
                w = w[1:-1].strip()
        return w

    def _pruefe_ob_datei_existiert(self) -> None:
        """Sichert ab, dass der Pfad existiert; sonst klare Ausnahme."""
        if not self._dateipfad.exists():
            raise CsvLesefehler(f"CSV-Datei nicht gefunden: {self._dateipfad}")

    def _lese_und_pruefe_kopfzeile(self) -> List[str]:
        """Liest die Kopfzeile, normalisiert Namen, prüft Pflichtspalten, wendet Aliasse an."""
        self._pruefe_ob_datei_existiert()
        with self._dateipfad.open("r", encoding=self._kodierung, newline="") as f:
            reader = csv.reader(
                f,
                delimiter=self._trennzeichen,
                quotechar='"',
                skipinitialspace=False
            )
            try:
                rohe_kopfzeile = next(reader)  # erste Zeile als Header
            except StopIteration:
                raise CsvLesefehler("CSV-Datei ist leer – keine Kopfzeile vorhanden.")

        # Fallback: manche Exporte liefern alles in einem Feld -> manuell splitten
        if len(rohe_kopfzeile) == 1 and self._trennzeichen in str(rohe_kopfzeile[0]):
            rohe_kopfzeile = str(rohe_kopfzeile[0]).split(self._trennzeichen)

        # Normalisieren: trim + lowercase (für robuste Indizierung)
        kopfzeile = [self._sauber(z).lower() for z in rohe_kopfzeile]
        if not kopfzeile or all(sp == "" for sp in kopfzeile):
            raise CsvLesefehler("Ungültige Kopfzeile – keine gültigen Spaltennamen gefunden.")

        # Aliasse erlauben (vereinheitlicht spätere Weiterverarbeitung)
        alias_map = {
            "semester": "semester_nummer",
            "modul": "kurs_name",
            "modul_name": "kurs_name",
        }
        kopfzeile = [alias_map.get(sp, sp) for sp in kopfzeile]

        # Pflichtspalten, die der weitere Code erwartet
        erwartet = ["studiengang", "semester_nummer", "kurs_name", "ects", "status", "note"]
        fehlend = [s for s in erwartet if s not in kopfzeile]
        if fehlend:
            raise CsvLesefehler(f"Erwartete Spalten fehlen: {fehlend}. Gefunden: {kopfzeile}")

        return kopfzeile

    def _lade_kopfzeile_und_spaltenindex(self) -> None:
        """Lazy-Init: liest Header und baut Spaltenindex nur bei Bedarf."""
        if self._kopfzeile is None or self._spaltenindex is None:
            kopfzeile = self._lese_und_pruefe_kopfzeile()
            spaltenindex = {name: i for i, name in enumerate(kopfzeile)}
            self._kopfzeile, self._spaltenindex = kopfzeile, spaltenindex

    @property
    def kopfzeile(self) -> List[str]:
        """Gibt die normalisierte Kopfzeile zurück (lädt bei Bedarf)."""
        self._lade_kopfzeile_und_spaltenindex()
        assert self._kopfzeile is not None
        return self._kopfzeile

    @property
    def spaltenindex(self) -> Dict[str, int]:
        """Gibt den Spaltennamen->Index-Mapper zurück (lädt bei Bedarf)."""
        self._lade_kopfzeile_und_spaltenindex()
        assert self._spaltenindex is not None
        return self._spaltenindex

    def datenzeilen_iterieren(self) -> Iterator[Dict[str, str]]:
        """
        Iteriert über Datenzeilen als Dict[str, str].
        - Überspringt leere Zeilen.
        - Passt Spaltenzahl an den Header an (auffüllen/abschneiden).
        - Bereinigt Zellwerte (Trim/Quotes).
        - Hat Fallback bei „eine Feld“-Zeilen (manuell splitten).
        """
        self._lade_kopfzeile_und_spaltenindex()
        with self._dateipfad.open("r", encoding=self._kodierung, newline="") as f:
            reader = csv.reader(
                f,
                delimiter=self._trennzeichen,
                quotechar='"',
                skipinitialspace=False
            )
            # Header überspringen
            try:
                next(reader)
            except StopIteration:
                return

            for rohzeile in reader:
                # Fallback bei „alles in einem Feld“
                if len(rohzeile) == 1 and self._trennzeichen in str(rohzeile[0]):
                    rohzeile = str(rohzeile[0]).split(self._trennzeichen)

                # vollständig leere/Whitespace-Zeilen ignorieren
                if not rohzeile or all((z is None or self._sauber(z) == "") for z in rohzeile):
                    continue

                zeile = rohzeile

                # Länge an Header angleichen
                if len(zeile) < len(self.kopfzeile):
                    zeile = zeile + [""] * (len(self.kopfzeile) - len(zeile))
                if len(zeile) > len(self.kopfzeile):
                    zeile = zeile[:len(self.kopfzeile)]

                bereinigt = [self._sauber(z) for z in zeile]
                yield {self.kopfzeile[i]: bereinigt[i] for i in range(len(self.kopfzeile))}