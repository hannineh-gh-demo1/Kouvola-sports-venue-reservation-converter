"""Tulosteen muotoilumoduuli.

Tukee CSV (puolipiste-erotin), JSON ja XLSX -muotoja.
CSV ja JSON toimii ilman ulkosia kirjastoja.
XLSX vaatii openpyxl-kirjaston.
"""

from __future__ import annotations

import csv
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from varausmuunnin.parser import Varaus


CSV_OTSIKOT = ["Tila", "Viikonpäivä", "Tilatarkennus", "Klo", "Ryhmä", "Aikaväli"]


def kirjoita_csv(varaukset: list[Varaus], polku: str) -> None:
    """Kirjoittaa varaukset CSV-tiedostoon puolipiste-erottimella.

    Args:
        varaukset: Lista varauksista.
        polku: Kohdetiedoston polku.
    """
    with open(polku, "w", newline="", encoding="utf-8") as f:
        kirjoittaja = csv.writer(f, delimiter=";")
        kirjoittaja.writerow(CSV_OTSIKOT)
        for v in varaukset:
            kirjoittaja.writerow([
                v.tila,
                v.viikonpaiva,
                v.tilatarkennus,
                v.kellonaika,
                v.ryhma,
                v.aikavali,
            ])


def kirjoita_json(varaukset: list[Varaus], polku: str) -> None:
    """Kirjoittaa varaukset JSON-tiedostoon.

    Args:
        varaukset: Lista varauksista.
        polku: Kohdetiedoston polku.
    """
    data = [
        {
            "tila": v.tila,
            "viikonpaiva": v.viikonpaiva,
            "tilatarkennus": v.tilatarkennus,
            "kellonaika": v.kellonaika,
            "ryhma": v.ryhma,
            "aikavali": v.aikavali,
        }
        for v in varaukset
    ]
    with open(polku, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def kirjoita_xlsx(varaukset: list[Varaus], polku: str) -> None:
    """Kirjoittaa varaukset XLSX-tiedostoon.

    Args:
        varaukset: Lista varauksista.
        polku: Kohdetiedoston polku.

    Raises:
        ImportError: Jos openpyxl ei oo asennettuna.
    """
    try:
        from openpyxl import Workbook
    except ImportError:
        raise ImportError(
            "XLSX-tukee varte pittaa asentaa openpyxl: "
            "pip install varausmuunnin[xlsx]"
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Varaukset"
    ws.append(CSV_OTSIKOT)

    for v in varaukset:
        ws.append([
            v.tila,
            v.viikonpaiva,
            v.tilatarkennus,
            v.kellonaika,
            v.ryhma,
            v.aikavali,
        ])

    wb.save(polku)
