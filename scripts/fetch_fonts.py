"""Download the two typefaces the banner is set in.

Instrument Serif (titles, labels) and Inter (subtitle) — both SIL Open Font
License, pulled straight from the Google Fonts repo into scripts/fonts/.

    python scripts/fetch_fonts.py
"""
import os
import urllib.request

RAW = "https://raw.githubusercontent.com/google/fonts/main/ofl"
FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

FILES = {
    "serif.ttf": f"{RAW}/instrumentserif/InstrumentSerif-Regular.ttf",
    "sans.ttf": f"{RAW}/inter/Inter%5Bopsz,wght%5D.ttf",
    "OFL-InstrumentSerif.txt": f"{RAW}/instrumentserif/OFL.txt",
    "OFL-Inter.txt": f"{RAW}/inter/OFL.txt",
}


def main():
    os.makedirs(FONTS_DIR, exist_ok=True)
    for name, url in FILES.items():
        dest = os.path.join(FONTS_DIR, name)
        if os.path.exists(dest):
            print(f"have  {name}")
            continue
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        with open(dest, "wb") as f:
            f.write(data)
        print(f"got   {name}  {len(data):,} bytes")
    print(f"\nfonts in {FONTS_DIR}")


if __name__ == "__main__":
    main()
