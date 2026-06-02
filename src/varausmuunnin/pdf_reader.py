"""PDF-lukija vakiovarausten PDF-tiedostoille.

Kayttaa pdfplumber-kirjastoo jos se on asennettuna.
Jos ei oo, antaa selkeen virheilmotuksen.
"""

from __future__ import annotations


def lue_pdf(polku: str) -> str:
    """Lukee PDF-tiedoston ja palauttaa tekstisisallon.

    Args:
        polku: Polku PDF-tiedostoon.

    Returns:
        PDF:n tekstisisalto yhena merkkijonona.

    Raises:
        ImportError: Jos pdfplumber ei oo asennettuna.
        FileNotFoundError: Jos tiedostoo ei loydy.
    """
    try:
        import pdfplumber  # noqa: F401
    except ImportError:
        raise ImportError(
            "PDF-tukee varte pittaa asentaa pdfplumber: "
            "pip install varausmuunnin[pdf]"
        )

    if not __import__("os").path.isfile(polku):
        raise FileNotFoundError(f"Tiedostoo ei loydy: {polku}")

    with pdfplumber.open(polku) as pdf:
        sivut = []
        for sivu in pdf.pages:
            teksti = sivu.extract_text()
            if teksti:
                sivut.append(teksti)
        return "".join(sivut)
