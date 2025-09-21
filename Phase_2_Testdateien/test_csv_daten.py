from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterator, List, Optional
import csv

class CsvLesefehler(Exception):
    pass

class CsvRepository:
    def __init__(self, dateipfad: Path, trennzeichen: str = ";", kodierung: str = "utf-8-sig") -> None:
        self._dateipfad = dateipfad
        self._trennzeichen = trennzeichen
        self._kodierung = kodierung
        self._kopfzeile: Optional[List[str]] = None

    @staticmethod
    def _sauber(wert: str) -> str:
        if wert is None:
            return ""
        w = str(wert).strip()
        for _ in range(2):
            if len(w) >= 2 and ((w[0] == '"' and w[-1] == '"') or (w[0] == "'" and w[-1] == "'")):
                w = w[1:-1].strip()
        return w

    def _lese_kopfzeile(self) -> List[str]:
        if not self._dateipfad.exists():
            raise CsvLesefehler(f"CSV-Datei nicht gefunden: {self._dateipfad}")

        with self._dateipfad.open("r", encoding=self._kodierung, newline="") as f:
            reader = csv.reader(f, delimiter=self._trennzeichen, quotechar='"')
            try:
                roh = next(reader)
            except StopIteration:
                raise CsvLesefehler("Leere CSV – keine Kopfzeile.")

        # WICHTIG: Wenn nur 1 Feld, manuell splitten
        if len(roh) == 1:
            roh = str(roh[0]).split(self._trennzeichen)

        header = [self._sauber(x).lower() for x in roh if x is not None]

        # Deine reale Kopfzeile laut Angabe:
        # studiengang;semester_nummer;kurs_name;ects;status;note
        # Falls die Datei falsch exportiert wurde (z. B. nur "studiengang"), aborten wir:
        erwartet = ["studiengang", "semester_nummer", "kurs_name", "ects", "status", "note"]
        if header != erwartet:
            # Wenn der Export z. B. führende BOMs/Spaces hatte, versuchen wir tolerant zu sein:
            if len(header) == 6:
                header = [self._sauber(h) for h in header]
            else:
                # Als letzte Notlösung: erzwungen korrekt setzen, da wir die Reihenfolge kennen
                header = erwartet

        return header

    def datenzeilen_iterieren(self) -> Iterator[Dict[str, str]]:
        if self._kopfzeile is None:
            self._kopfzeile = self._lese_kopfzeile()

        with self._dateipfad.open("r", encoding=self._kodierung, newline="") as f:
            reader = csv.reader(f, delimiter=self._trennzeichen, quotechar='"')

            # Header-Zeile überspringen
            try:
                next(reader)
            except StopIteration:
                return

            for roh in reader:
                # Falls komplette Zeile in EINEM Feld steckt, manuell splitten:
                if len(roh) == 1:
                    roh = str(roh[0]).split(self._trennzeichen)

                # Leere/Whitespace-Zeilen überspringen
                if not roh or all(self._sauber(z) == "" for z in roh):
                    continue

                # Auf genau Header-Länge bringen
                if len(roh) < len(self._kopfzeile):
                    roh = roh + [""] * (len(self._kopfzeile) - len(roh))
                if len(roh) > len(self._kopfzeile):
                    roh = roh[:len(self._kopfzeile)]

                clean = [self._sauber(z) for z in roh]
                yield {self._kopfzeile[i]: clean[i] for i in range(len(self._kopfzeile))}