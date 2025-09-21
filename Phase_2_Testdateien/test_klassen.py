from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Pruefungsleistung:
    note: Optional[float]

class StudiengangService:
    @staticmethod
    def berechne_gesamtdurchschnitt(pruefungen: List[Pruefungsleistung]) -> Optional[float]:
        noten = [p.note for p in pruefungen if p.note is not None]
        if not noten:
            return None
        return round(sum(noten) / len(noten), 2)