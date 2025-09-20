# Verantwortung: Roh-Dicts (CSV) in Domänenobjekte transformieren. Keine IO/GUI hier.
from __future__ import annotations
from typing import Iterable, List, Optional, Tuple

from klassen import Kurs, KursStatus, Pruefungsleistung

def _als_int(wert: str) -> Optional[int]:
    """Konvertiert String nach int; leere/ungültige Werte -> None."""
    w = (wert or "").strip()
    if w == "":
        return None
    try:
        return int(w)
    except ValueError:
        return None

def _als_float(wert: str) -> Optional[float]:
    """Konvertiert String (inkl. deutschem Komma) nach float; leer/ungültig -> None."""
    w = (wert or "").strip().replace(",", ".")
    if w == "":
        return None
    try:
        return float(w)
    except ValueError:
        return None

def _als_kursstatus(wert: str) -> KursStatus:
    """Mappt CSV-Status-Strings robust auf KursStatus-Enum (Default: BELEGT)."""
    w = (wert or "").strip().upper()
    if w == "ABGESCHLOSSEN":
        return KursStatus.ABGESCHLOSSEN
    return KursStatus.BELEGT  # Fallback

def zeile_zu_kurs(zeile: dict) -> Kurs:
    """
    Baut Kurs aus CSV-Zeile. Erwartete Keys: studiengang, semester_nummer, kurs_name, ects, status, note.
    Hinweis: Studiengang wird im Kurs nicht gespeichert (Domänenwurzel ist Studiengang).
    """
    name = (zeile.get("kurs_name") or "").strip()
    ects = _als_int(zeile.get("ects", ""))
    status = _als_kursstatus(zeile.get("status", ""))
    semester_nummer = _als_int(zeile.get("semester_nummer", ""))

    return Kurs(
        name=name,
        ects=ects,
        status=status,
        semester_nummer=semester_nummer
    )

def zeile_zu_pruefungsleistung(zeile: dict) -> Optional[Pruefungsleistung]:
    """
    Baut Prüfungsleistung nur, wenn eine Note vorliegt.
    Prüfungsform ist nicht in der CSV -> bleibt None.
    """
    note = _als_float(zeile.get("note", ""))
    if note is None:
        return None
    return Pruefungsleistung(
        pruefungsForm=None,
        note=note
    )

def zeilen_zu_domaene(zeilen: Iterable[dict]) -> Tuple[List[Kurs], List[Pruefungsleistung]]:
    """
    Transformiert CSV-Rohzeilen in Domänenlisten.
    - Kurse: aus allen Zeilen
    - Prüfungsleistungen: nur Zeilen mit Note
    """
    kurse: List[Kurs] = []
    pruefungen: List[Pruefungsleistung] = []
    for z in zeilen:
        kurse.append(zeile_zu_kurs(z))
        pl = zeile_zu_pruefungsleistung(z)
        if pl is not None:
            pruefungen.append(pl)
    return kurse, pruefungen