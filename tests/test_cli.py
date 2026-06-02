"""CLI:n testit.

Testataan argumenttien parsinta, --help ja virhetilanteet.
"""

import os
import subprocess
import sys
from pathlib import Path


def test_help_toimii():
    """--help nayttaa ohjetekstin ja palauttaa 0."""
    tulos = subprocess.run(
        [sys.executable, "-m", "varausmuunnin", "--help"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent / "src")},
    )
    assert tulos.returncode == 0
    assert "varausmuunnin" in tulos.stdout
    assert "hakusana" in tulos.stdout.lower() or "--search" in tulos.stdout


def test_argumentit_puuttuu():
    """Ilman argumentteja tulee virhe."""
    tulos = subprocess.run(
        [sys.executable, "-m", "varausmuunnin"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent / "src")},
    )
    assert tulos.returncode != 0


def test_tiedostoa_ei_loydy():
    """Olematon tiedosto antaa virheen."""
    tulos = subprocess.run(
        [sys.executable, "-m", "varausmuunnin", "olematon.txt", "-s", "KJP"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
        env={**os.environ, "PYTHONPATH": str(Path(__file__).parent.parent / "src")},
    )
    assert tulos.returncode != 0
    assert "ei loydy" in tulos.stderr.lower() or "error" in tulos.stderr.lower()


def test_csv_tuloste_syntyy(tmp_path):
    """CSV-tuloste syntyy oikein."""
    tuloste = tmp_path / "testi.csv"
    projekti = Path(__file__).parent.parent
    tulos = subprocess.run(
        [
            sys.executable, "-m", "varausmuunnin",
            str(projekti / "examples" / "vakiovuorot_dump.txt"),
            "-s", "KJP", "-f", "csv", "-o", str(tuloste),
        ],
        capture_output=True,
        text=True,
        cwd=str(projekti),
        env={**os.environ, "PYTHONPATH": str(projekti / "src")},
    )
    assert tulos.returncode == 0
    assert tuloste.exists()
    rivit = tuloste.read_text(encoding="utf-8").strip().split("\n")
    # Otsikko + dataa
    assert len(rivit) > 10
    assert "Tila" in rivit[0]
