"""Pytest-fixturet vakiovarausten testeille."""

from pathlib import Path

import pytest


@pytest.fixture
def dump_teksti():
    """Lataa vakiovuorot_dump.txt testidata."""
    polku = Path(__file__).parent.parent / "examples" / "vakiovuorot_dump.txt"
    return polku.read_text(encoding="utf-8")
