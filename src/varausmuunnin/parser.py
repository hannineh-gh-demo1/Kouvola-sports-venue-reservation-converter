"""Parseri vakiovarausten dump-tiedostolle.

Lukee tekstitiedoston rivi kerrallaan ja tunnistaa rakenteelliset
elementit: kohteet, viikonpaivat, tilatarkennukset, kellonajat,
ryhmat ja aikavallit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Varaus:
    """Yksittainen vakiovaraus."""

    tila: str
    viikonpaiva: str
    tilatarkennus: str
    kellonaika: str
    ryhma: str
    aikavali: str


# Viikonpaivat
VIIKONPAIVAT = {"MA", "TI", "KE", "TO", "PE", "LA", "SU"}

# Sentinelli-arvo kun tilatarkennusta ei ole
EI_TILATARKENNUSTA = "ei-tilatarkennusta"

# Regex: aika-muoto HH:MM - HH:MM
AIKA_RE = re.compile(r"^\d{2}:\d{2} - \d{2}:\d{2}$")

# Regex: paivamaara DD.MM.YYYY tai aikavali DD.MM.YYYY - DD.MM.YYYY
AIKAVALI_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}( - \d{2}\.\d{2}\.\d{4})?$")

# Regex: yksittainen paivamaara DD.MM.YYYY (sivunvaihdon jalkeen)
PVM_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def _on_viikonpaiva(rivi: str) -> bool:
    """Tarkistaa onko rivi viikonpaiva."""
    return rivi in VIIKONPAIVAT


def _on_aika(rivi: str) -> bool:
    """Tarkistaa onko rivi kellonaika (HH:MM - HH:MM)."""
    return bool(AIKA_RE.match(rivi))


def _on_aikavali(rivi: str) -> bool:
    """Tarkistaa onko rivi aikavali tai yksittainen paivamaara."""
    return bool(AIKAVALI_RE.match(rivi))


def parse_dump(teksti: str) -> list[Varaus]:
    """Parsii vakiovarausten dump-tekstin ja palauttaa listan varauksista.

    Lukee tekstin rivi kerrallaan tilakoneena. Tunnistaa:
    - Sivunvaihdot (Vakiovaraukset + pvm)
    - Kohteet (Kohde: + nimi + alikohde)
    - Viikonpaivat (MA/TI/KE/TO/PE/LA/SU)
    - Varauslohkot: [tilatarkennus] + aika + ryhma + aikavali

    Args:
        teksti: Dump-tiedoston sisalto merkkijonona.

    Returns:
        Lista Varaus-olioita.
    """
    rivit = teksti.split("\n")
    varaukset: list[Varaus] = []

    tila: str = ""
    viikonpaiva: str = ""
    i = 0

    while i < len(rivit):
        rivi = rivit[i].strip()

        # Tyhjat rivit ohitetaan
        if not rivi:
            i += 1
            continue

        # Sivunvaihto: "Vakiovaraukset" + seuraava rivi on paivamaara
        if rivi == "Vakiovaraukset":
            # Ohitetaan "Vakiovaraukset" ja sita seuraava pvm-rivi
            i += 1
            if i < len(rivit) and PVM_RE.match(rivit[i].strip()):
                i += 1
            continue

        # Kohde: seuraavalla rivilla nimi, sen jalkeen alikohde
        if rivi == "Kohde:":
            kohdenimi = ""
            alikohde = ""
            i += 1
            if i < len(rivit):
                kohdenimi = rivit[i].strip()
                i += 1
            if i < len(rivit):
                seuraava = rivit[i].strip()
                # Alikohde on rivi joka ei ole viikonpaiva eika Kohde:
                if not _on_viikonpaiva(seuraava) and seuraava != "Kohde:":
                    alikohde = seuraava
                    i += 1
            tila = f"{kohdenimi} - {alikohde}" if alikohde else kohdenimi
            # Poistetaan pilkut tilanimesta
            tila = tila.replace(",", "")
            continue

        # Viikonpaiva
        if _on_viikonpaiva(rivi):
            viikonpaiva = rivi
            i += 1
            continue

        # Varauslohkon parsinta: tilatarkennus (valinnainen) + aika + ryhma + aikavali
        # Tarkistetaan onko nykyinen rivi kellonaika tai tilatarkennus
        if _on_aika(rivi):
            # Ei tilatarkennusta, tama on suoraan kellonaika
            kellonaika = rivi
            ryhma = ""
            aikavali = ""
            tilatarkennus = EI_TILATARKENNUSTA

            i += 1
            if i < len(rivit):
                ryhma = rivit[i].strip()
                i += 1
            if i < len(rivit) and _on_aikavali(rivit[i].strip()):
                aikavali = rivit[i].strip()
                i += 1

            if ryhma and viikonpaiva:
                varaukset.append(
                    Varaus(
                        tila=tila,
                        viikonpaiva=viikonpaiva,
                        tilatarkennus=tilatarkennus,
                        kellonaika=kellonaika,
                        ryhma=ryhma,
                        aikavali=aikavali,
                    )
                )
            continue

        # Jos rivi ei ole aika, viikonpaiva, aikavali, kohde tai vakiovaraukset,
        # se voi olla tilatarkennus. Tarkistetaan onko seuraava rivi kellonaika.
        if not _on_aikavali(rivi) and i + 1 < len(rivit) and _on_aika(rivit[i + 1].strip()):
            tilatarkennus = rivi
            i += 1
            kellonaika = rivit[i].strip()
            ryhma = ""
            aikavali = ""

            i += 1
            if i < len(rivit):
                ryhma = rivit[i].strip()
                i += 1
            if i < len(rivit) and _on_aikavali(rivit[i].strip()):
                aikavali = rivit[i].strip()
                i += 1

            if ryhma and viikonpaiva:
                varaukset.append(
                    Varaus(
                        tila=tila,
                        viikonpaiva=viikonpaiva,
                        tilatarkennus=tilatarkennus,
                        kellonaika=kellonaika,
                        ryhma=ryhma,
                        aikavali=aikavali,
                    )
                )
            continue

        # Muu rivi (esim. aikavali ilman varauslohkoa) - ohitetaan
        i += 1

    return varaukset


def suodata(varaukset: list[Varaus], hakusana: str) -> list[Varaus]:
    """Suodattaa varaukset hakusanan perusteella.

    Etsii hakusanaa ryhma-kentasta (case-insensitive).

    Args:
        varaukset: Lista varauksista.
        hakusana: Hakusana jolla suodatetaan.

    Returns:
        Suodatettu lista varauksista.
    """
    hakusana_lower = hakusana.lower()
    return [v for v in varaukset if hakusana_lower in v.ryhma.lower()]
