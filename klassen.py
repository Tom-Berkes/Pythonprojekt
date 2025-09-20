# Domänenmodell nach UML: Studiengang, Semester, KursStatus, Kurs, Pruefungsleistung.
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
from typing import List, Optional

# Aggregatwurzel: berechnet Kennzahlen und liefert Sichten (belegte Kurse).
@dataclass
class Studiengang:
    name: str
    regelzeitMonate: int
    startDatum: date
    maximaleEcts: int

    # Durchschnittsnote der vorhandenen Prüfungsleistungen (None bei keiner Note).
    def berechneGesamtdurchschnitt(self, pruefungsleistungen: List["Pruefungsleistung"]) -> Optional[float]:
        noten = [pl.note for pl in pruefungsleistungen if pl.note is not None]
        if not noten:
            return None
        return round(sum(noten) / len(noten), 2)

    # ECTS-Fortschritt als Prozentwert (0..100), auf 2 Nachkommastellen gerundet.
    def berechneEctsProzent(self, kurse: List["Kurs"]) -> float:
        ects_abgeschlossen = sum(
            (k.ects or 0)
            for k in kurse
            if k.status == KursStatus.ABGESCHLOSSEN and k.ects is not None
        )
        if self.maximaleEcts <= 0:
            return 0.0
        return round((ects_abgeschlossen / self.maximaleEcts) * 100.0, 2)

    # Verbleibende Tage bis Studienende (approximiert: 30 Tage pro Monat).
    def berechneVerbleibendeTage(self, heute: Optional[date] = None) -> int:
        today = heute or date.today()
        ende = self.startDatum + timedelta(days=self.regelzeitMonate * 30)
        return (ende - today).days

    # Liefert Kurse mit Status BELEGT (für die Tabelle).
    def getBelegteKurse(self, kurse: List["Kurs"]) -> List["Kurs"]:
        return [k for k in kurse if k.status == KursStatus.BELEGT]

# Schlanker Strukturbau-Stein (für Erweiterbarkeit).
@dataclass
class Semester:
    nummer: int

# Status der Kurse in der CSV/Domain.
class KursStatus(Enum):
    BELEGT = "BELEGT"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"

# Kurs entkoppelt vom Studiengang (Relation über Aggregat).
@dataclass
class Kurs:
    name: str
    ects: Optional[int]
    status: KursStatus
    semester_nummer: Optional[int] = None  # Rohe Zuordnung aus CSV

# Prüfungsleistung für Noten und ggf. Prüfungsform (hier optional).
@dataclass
class Pruefungsleistung:
    pruefungsForm: Optional[str]
    note: Optional[float]