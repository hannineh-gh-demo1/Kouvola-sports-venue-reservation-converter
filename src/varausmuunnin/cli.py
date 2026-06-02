"""Komentorivityokalu vakiovarausten muuntamiseen.

Kaytetaan nain: varausmuunnin <tiedosto> -s <hakusana> [-f csv|json|xlsx] [-o tulostiedosto]
"""

from __future__ import annotations

import argparse
import logging
import sys

from varausmuunnin.output import kirjoita_csv, kirjoita_json, kirjoita_xlsx
from varausmuunnin.parser import parse_dump, suodata

logger = logging.getLogger("varausmuunnin")


def _luo_argumenttiparse() -> argparse.ArgumentParser:
    """Luoo argparse-parserin Kouvolan murteella."""
    parser = argparse.ArgumentParser(
        prog="varausmuunnin",
        description=(
            "Muuntaa Kouvolan kaupungin vakiovaraus-PDF:n tai -tekstidumpin "
            "CSV-, JSON- tai XLSX-muottiin. Mie hoijan homman!"
        ),
    )
    parser.add_argument(
        "tiedosto",
        help="Syotetiedoston polku (.txt tai .pdf)",
    )
    parser.add_argument(
        "-s", "--search",
        required=True,
        help="Hakusana jolla suodatetaan varaukset (esim. KJP)",
        dest="hakusana",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json", "xlsx"],
        default="csv",
        help="Tulosteen muoto: csv, json tai xlsx (oletus: csv)",
        dest="muoto",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Tulostiedoston polku (oletus: varaukset.<muoto>)",
        dest="tuloste",
    )
    return parser


def main() -> None:
    """Paaohjelma - tasta lahtee."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    parser = _luo_argumenttiparse()
    args = parser.parse_args()

    # Maarita tulostiedosto
    tuloste = args.tuloste or f"varaukset.{args.muoto}"

    # Lue syotetiedosto
    tiedosto: str = args.tiedosto
    if tiedosto.lower().endswith(".pdf"):
        try:
            from varausmuunnin.pdf_reader import lue_pdf

            teksti = lue_pdf(tiedosto)
        except ImportError as e:
            logger.error(str(e))
            sys.exit(1)
        except FileNotFoundError as e:
            logger.error(str(e))
            sys.exit(1)
    else:
        try:
            with open(tiedosto, encoding="utf-8") as f:
                teksti = f.read()
        except FileNotFoundError:
            logger.error("Tiedostoo ei loydy: %s", tiedosto)
            sys.exit(1)
        except OSError as e:
            logger.error("Tiedoston lukeminen epaonnisttu: %s", e)
            sys.exit(1)

    # Parsitaan ja suodatetaan
    varaukset = parse_dump(teksti)
    suodatetut = suodata(varaukset, args.hakusana)

    if not suodatetut:
        logger.warning(
            "Hakusanalla '%s' ei loytynny mittaan varauksii.", args.hakusana
        )
        sys.exit(0)

    logger.info(
        "Loytty %d varausta hakusanalla '%s'.", len(suodatetut), args.hakusana
    )

    # Kirjoita tuloste
    if args.muoto == "csv":
        kirjoita_csv(suodatetut, tuloste)
    elif args.muoto == "json":
        kirjoita_json(suodatetut, tuloste)
    elif args.muoto == "xlsx":
        try:
            kirjoita_xlsx(suodatetut, tuloste)
        except ImportError as e:
            logger.error(str(e))
            sys.exit(1)

    logger.info("Tuloste kirjotettu: %s", tuloste)


if __name__ == "__main__":
    main()
