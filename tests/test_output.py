"""Tulosteen muotoilun testit.

Testataan CSV-, JSON- ja XLSX-tulosteet.
"""

import json
import tempfile
from pathlib import Path

import pytest

from varausmuunnin.output import kirjoita_csv, kirjoita_json, kirjoita_xlsx
from varausmuunnin.parser import Varaus


@pytest.fixture
def esimerkkivaraukset():
    """Muutama testivaraus."""
    return [
        Varaus(
            tila="TESTKENTTA - Nurmi",
            viikonpaiva="MA",
            tilatarkennus="Kentta A",
            kellonaika="17:00 - 18:30",
            ryhma="KJP juniorit",
            aikavali="01.06.2024 - 30.09.2024",
        ),
        Varaus(
            tila="TESTKENTTA - Nurmi",
            viikonpaiva="TI",
            tilatarkennus="ei-tilatarkennusta",
            kellonaika="18:00 - 19:30",
            ryhma="Purha aik.",
            aikavali="15.05.2024",
        ),
    ]


def test_csv_puolipiste_erotin(esimerkkivaraukset):
    """CSV kayttaa puolipistetta erottimena."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        polku = f.name
    kirjoita_csv(esimerkkivaraukset, polku)
    sisalto = Path(polku).read_text(encoding="utf-8")
    rivit = sisalto.strip().split("\n")
    # Otsikkorivi
    assert ";" in rivit[0]
    # Ei pilkkuerotinta (paitsi tietysti datassa)
    otsikko_osat = rivit[0].split(";")
    assert len(otsikko_osat) == 6


def test_csv_otsikot(esimerkkivaraukset):
    """CSV:n otsikkorivi on oikein."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        polku = f.name
    kirjoita_csv(esimerkkivaraukset, polku)
    sisalto = Path(polku).read_text(encoding="utf-8")
    rivit = sisalto.strip().split("\n")
    otsikko = rivit[0]
    assert otsikko == "Tila;Viikonpäivä;Tilatarkennus;Klo;Ryhmä;Aikaväli"


def test_csv_datarivit(esimerkkivaraukset):
    """CSV:n datarivit sisaltavat oikeat tiedot."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        polku = f.name
    kirjoita_csv(esimerkkivaraukset, polku)
    sisalto = Path(polku).read_text(encoding="utf-8")
    rivit = sisalto.strip().split("\n")
    assert len(rivit) == 3  # otsikko + 2 datarivia
    # Tarkista eka datarivi
    osat = rivit[1].split(";")
    assert osat[0] == "TESTKENTTA - Nurmi"
    assert osat[1] == "MA"
    assert osat[2] == "Kentta A"
    assert osat[3] == "17:00 - 18:30"
    assert osat[4] == "KJP juniorit"
    assert osat[5] == "01.06.2024 - 30.09.2024"


def test_json_validi(esimerkkivaraukset):
    """JSON-tuloste on validi JSON-taulukko."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        polku = f.name
    kirjoita_json(esimerkkivaraukset, polku)
    sisalto = Path(polku).read_text(encoding="utf-8")
    data = json.loads(sisalto)
    assert isinstance(data, list)
    assert len(data) == 2


def test_json_kentat(esimerkkivaraukset):
    """JSON sisaltaa oikeat kentat."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        polku = f.name
    kirjoita_json(esimerkkivaraukset, polku)
    data = json.loads(Path(polku).read_text(encoding="utf-8"))
    eka = data[0]
    assert eka["tila"] == "TESTKENTTA - Nurmi"
    assert eka["viikonpaiva"] == "MA"
    assert eka["tilatarkennus"] == "Kentta A"
    assert eka["kellonaika"] == "17:00 - 18:30"
    assert eka["ryhma"] == "KJP juniorit"
    assert eka["aikavali"] == "01.06.2024 - 30.09.2024"


def test_xlsx_import_error(esimerkkivaraukset):
    """XLSX nostaa ImportErrorin kun openpyxl ei oo asennettuna."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False) as f:
        polku = f.name
    with pytest.raises(ImportError, match="openpyxl"):
        kirjoita_xlsx(esimerkkivaraukset, polku)
