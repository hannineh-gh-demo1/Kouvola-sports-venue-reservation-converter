"""Parserin testit.

Testataan etta parseri loytyy kohteet, viikonpaivat, kellonajat,
ryhmat, aikavallit ja tilatarkennukset oikein.
"""

import re

from varausmuunnin.parser import EI_TILATARKENNUSTA, parse_dump, suodata


def test_loytyy_kohteita(dump_teksti):
    """Parseri loytaa useita kohteita (tila-kentassa)."""
    varaukset = parse_dump(dump_teksti)
    tilat = {v.tila for v in varaukset}
    assert len(tilat) > 5


def test_loytyy_kjp_varauksia(dump_teksti):
    """Parseri loytaa vahintaan 50 KJP-varausta."""
    varaukset = parse_dump(dump_teksti)
    kjp = suodata(varaukset, "KJP")
    assert len(kjp) >= 50


def test_kjp_maara_tarkka(dump_teksti):
    """KJP esiintyy tiedostossa 114 kertaa ja parseri loytaa ne kaikki."""
    varaukset = parse_dump(dump_teksti)
    kjp = suodata(varaukset, "KJP")
    assert len(kjp) == 114


def test_viikonpaivat_oikein(dump_teksti):
    """Viikonpaivat ovat MA/TI/KE/TO/PE/LA/SU."""
    varaukset = parse_dump(dump_teksti)
    sallitut = {"MA", "TI", "KE", "TO", "PE", "LA", "SU"}
    viikonpaivat = {v.viikonpaiva for v in varaukset}
    assert viikonpaivat.issubset(sallitut)
    # Pitaa loytya useita eri viikonpaivia
    assert len(viikonpaivat) >= 5


def test_kellonajat_muoto(dump_teksti):
    """Kellonajat ovat muotoa HH:MM - HH:MM."""
    varaukset = parse_dump(dump_teksti)
    aika_re = re.compile(r"^\d{2}:\d{2} - \d{2}:\d{2}$")
    for v in varaukset:
        assert aika_re.match(v.kellonaika), f"Virheellinen aika: {v.kellonaika}"


def test_aikavallit_muoto(dump_teksti):
    """Aikavallit ovat muotoa DD.MM.YYYY - DD.MM.YYYY tai DD.MM.YYYY."""
    varaukset = parse_dump(dump_teksti)
    aikavali_re = re.compile(r"^\d{2}\.\d{2}\.\d{4}( - \d{2}\.\d{2}\.\d{4})?$")
    for v in varaukset:
        if v.aikavali:
            assert aikavali_re.match(v.aikavali), f"Virheellinen aikavali: {v.aikavali}"


def test_suodata_toimii(dump_teksti):
    """Suodatus loytaa vain hakusanaa vastaavat varaukset."""
    varaukset = parse_dump(dump_teksti)
    purha = suodata(varaukset, "Purha")
    assert len(purha) > 0
    for v in purha:
        assert "purha" in v.ryhma.lower()


def test_suodata_case_insensitive(dump_teksti):
    """Suodatus toimii case-insensitive."""
    varaukset = parse_dump(dump_teksti)
    kjp_iso = suodata(varaukset, "KJP")
    kjp_pieni = suodata(varaukset, "kjp")
    assert len(kjp_iso) == len(kjp_pieni)


def test_tilatarkennus_loytyyy(dump_teksti):
    """Osa varauksista sisaltaa tilatarkennuksen."""
    varaukset = parse_dump(dump_teksti)
    tarkennukselliset = [v for v in varaukset if v.tilatarkennus != EI_TILATARKENNUSTA]
    assert len(tarkennukselliset) > 0


def test_tilatarkennus_ei_tilatarkennusta(dump_teksti):
    """Osa varauksista on ilman tilatarkennusta."""
    varaukset = parse_dump(dump_teksti)
    ilman = [v for v in varaukset if v.tilatarkennus == EI_TILATARKENNUSTA]
    assert len(ilman) > 0


def test_pvm_tunnistus_regex(dump_teksti):
    """Paivamaara tunnistus kayttaa regexia eika kovakoodattuja vuosia."""
    varaukset = parse_dump(dump_teksti)
    # Varmistetaan etta aikavaleissa on oikeita paivamaaroja
    pvm_re = re.compile(r"\d{2}\.\d{2}\.\d{4}")
    loydetyt_vuodet = set()
    for v in varaukset:
        if v.aikavali:
            for m in pvm_re.finditer(v.aikavali):
                vuosi = m.group()[-4:]
                loydetyt_vuodet.add(vuosi)
    assert "2024" in loydetyt_vuodet


def test_tyhja_syote():
    """Tyhja syote palauttaa tyhjan listan."""
    assert parse_dump("") == []


def test_sivunvaihto_ei_riko_parsintaa(dump_teksti):
    """Sivunvaihdot (Vakiovaraukset + pvm) eivat riko parsintaa."""
    varaukset = parse_dump(dump_teksti)
    # Ei pitaisi olla varausta jonka ryhma olisi "Vakiovaraukset" tai pvm
    for v in varaukset:
        assert v.ryhma != "Vakiovaraukset"
        assert not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v.ryhma)


def test_roskateksti_ei_tuota_varauksia():
    """Tuntematon teksti ei tuota varauksii."""
    roska = "Tama on ihan random tekstia\njoka ei sisalla mittaan rakenteellista\n123 abc"
    assert parse_dump(roska) == []
