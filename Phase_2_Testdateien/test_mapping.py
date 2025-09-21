from __future__ import annotations
from typing import Iterable, List, Optional
from test_klassen import Pruefungsleistung

def _als_float(w: str) -> Optional[float]:
    s = (w or "").strip().replace(",", ".")
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None

def zeilen_zu_pruefungsleistungen(zeilen: Iterable[dict]) -> List[Pruefungsleistung]:
    ergebnis: List[Pruefungsleistung] = []
    for z in zeilen:
        note = _als_float(z.get("note", ""))
        if note is not None:
            ergebnis.append(Pruefungsleistung(note=note))
    return ergebnis