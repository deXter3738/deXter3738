# Banner + label generator

Regenerates every SVG in `../assets` — the dark/light profile banner and the
small serif section labels used in the README.

## Typefaces

| Role | Face | Used for |
| --- | --- | --- |
| serif | [Instrument Serif](https://fonts.google.com/specimen/Instrument+Serif) Regular | banner title, section labels |
| sans | [Inter](https://fonts.google.com/specimen/Inter) (variable, default 400) | banner subtitle |

Both are SIL Open Font License. Text is converted to **outlines**, not webfont
references — GitHub strips `<link>` and `<style>` tags from a README, so a
Google Fonts embed would never load there. Baking the letterforms into vector
shapes is what makes the banner look identical for everyone.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
python scripts/fetch_fonts.py        # downloads both faces into scripts/fonts/
```

`scripts/fonts/` is gitignored — the fonts are fetched, not committed.

## Run

```bash
python scripts/build.py
```

Writes to `assets/` by default; set `OUT_DIR` to send it elsewhere, or
`SERIF_FONT` / `SANS_FONT` to point at your own copies of the faces.
