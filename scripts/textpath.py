"""Shape a string with HarfBuzz and return SVG path data (text as outlines)."""
import os

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

# The banner is set in Instrument Serif (titles, labels) and Inter (subtitle).
# `python scripts/fetch_fonts.py` drops both into scripts/fonts/ as serif.ttf
# and sans.ttf. Override per-machine with SERIF_FONT / SANS_FONT if you keep
# them elsewhere.
FONTS_DIR = os.environ.get("FONTS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"))
FONTS = {
    "serif": os.path.expanduser(os.environ.get("SERIF_FONT") or os.path.join(FONTS_DIR, "serif.ttf")),
    "sans": os.path.expanduser(os.environ.get("SANS_FONT") or os.path.join(FONTS_DIR, "sans.ttf")),
}
_cache = {}


def _load(key):
    if key not in _cache:
        path = FONTS[key]
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"No {key} font at {path}. Run `python scripts/fetch_fonts.py` "
                f"to download it, or set {key.upper()}_FONT to a .ttf path."
            )
        tt = TTFont(path)
        blob = hb.Blob.from_file_path(path)
        face = hb.Face(blob)
        font = hb.Font(face)
        upem = tt["head"].unitsPerEm
        _cache[key] = (tt, font, upem)
    return _cache[key]


def text_path(text, key, size, x=0.0, y=0.0, tracking=0.0, features=None):
    """Return (path_d, advance_width) for `text` drawn at font `size` px with
    its baseline at (x, y). `tracking` is extra letter-spacing in px."""
    tt, font, upem = _load(key)
    scale = size / upem
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {"kern": True, "liga": True})
    glyphset = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    pen = SVGPathPen(glyphset, ntos=lambda v: (f"{v:.1f}".rstrip("0").rstrip(".") or "0"))
    cx = x
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        gx = cx + pos.x_offset * scale
        gy = y - pos.y_offset * scale
        tpen = TransformPen(pen, (scale, 0, 0, -scale, gx, gy))
        glyphset[name].draw(tpen)
        cx += pos.x_advance * scale + tracking
    return pen.getCommands(), cx - x


def text_width(text, key, size, tracking=0.0):
    return text_path(text, key, size, tracking=tracking)[1]
