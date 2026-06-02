# Varausmuunnin

Kouvolan kaupungin urheilukenttien vakiovarausten muunnintyokalu.

Mie muunnan kaupungin vakiovaraus-PDF:n tai tekstidumpin CSV-, JSON-
tai XLSX-muottiin. Sie saat varaukset kayttokelposeen taulukkomuottiin
ilman mittaan sorkkimista.

## Asennus

```bash
pip install -e .
```

PDF-tukee varte:
```bash
pip install -e ".[pdf]"
```

XLSX-tukee varte:
```bash
pip install -e ".[xlsx]"
```

## Kaytto

### Peruskaytto

```bash
varausmuunnin vakiovuorot_dump.txt -s KJP -f csv -o varaukset.csv
```

### Eri muodot

CSV (oletus, puolipiste-erotin):
```bash
varausmuunnin vakiovuorot_dump.txt -s KJP -f csv -o kjp_varaukset.csv
```

JSON:
```bash
varausmuunnin vakiovuorot_dump.txt -s KJP -f json -o kjp_varaukset.json
```

XLSX (vaatii openpyxl-kirjaston):
```bash
varausmuunnin vakiovuorot_dump.txt -s KJP -f xlsx -o kjp_varaukset.xlsx
```

### Argumentit

| Argumentti | Kuvaus |
|---|---|
| `tiedosto` | Syotetiedoston polku (.txt tai .pdf) |
| `-s`, `--search` | Hakusana jolla suodatetaan varaukset (esim. KJP) |
| `-f`, `--format` | Tulosteen muoto: csv, json tai xlsx (oletus: csv) |
| `-o`, `--output` | Tulostiedoston polku (oletus: varaukset.<muoto>) |

### Esimerkkeja

Etitaan kaikki KJP:n varaukset:
```bash
python -m varausmuunnin examples/vakiovuorot_dump.txt -s KJP -f csv -o kjp.csv
```

Etitaan Purhan varaukset JSON-muodossa:
```bash
python -m varausmuunnin examples/vakiovuorot_dump.txt -s Purha -f json -o purha.json
```

## Miten dump-tiedosto tehaan

1. Avaa kaupungin vakiovaraus-PDF
2. Valite kaikki teksti (Ctrl+A)
3. Kopioi leikepoyalle (Ctrl+C)
4. Liita PLAIN TEXT -muodossa tekstitiedostoon ja tallenna

PDF-tuki toimii myos suoraan, mutta vaatii pdfplumber-kirjaston:
```bash
varausmuunnin "Vakiovuorot kesa 2024.pdf" -s KJP -f csv
```

## Kehitys

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check src/ tests/
```
