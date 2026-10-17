import math, os

from textpath import text_path

# Write next to the repo root (scripts/ -> ../assets), overridable with OUT_DIR.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUT_DIR") or os.path.join(REPO_ROOT, "assets")
os.makedirs(OUT, exist_ok=True)

W, H = 1584, 396
GRID_X0, GRID_STEP, GRID_N = 0.5, 173, 10   # 0.5 keeps the 1px rules crisp
GOLD, VIOLET = "#FED259", "#6600FF"
INK_DARK, INK_LIGHT = "#0F0F0E", "#FAF8F5"   # cover ground / cover type colour
# GitHub's two canvases. The banners use them as their ground so the artwork
# sits flush against the README page instead of reading as a block.
GH_DARK_BG, GH_LIGHT_BG = "#0D1117", "#FFFFFF"

TITLE = "Interdisciplinary Designer"
SUB = "Seeking Patterns in Complexity."
TITLE_SIZE, SUB_SIZE = 88, 32
X = 0          # flush left: the banner is shown at 100% width, so
               # x=0 puts the type on the README's own text margin
TITLE_Y, SUB_Y = 188, 252


def rays(cx, cy, n, length, spread_deg, start_deg, color_id, opacity, blur_id, blend="screen"):
    """Thin triangular light rays fanning out from (cx, cy)."""
    parts = []
    for i in range(n):
        a = math.radians(start_deg + spread_deg * i / max(n - 1, 1))
        half = math.radians(0.9 + 0.5 * ((i * 7) % 3))
        l = length * (0.75 + 0.25 * ((i * 5) % 4) / 3)
        p1 = (cx + l * math.cos(a - half), cy + l * math.sin(a - half))
        p2 = (cx + l * math.cos(a + half), cy + l * math.sin(a + half))
        parts.append(f'<polygon points="{cx:.1f},{cy:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="url(#{color_id})"/>')
    return f'<g opacity="{opacity}" filter="url(#{blur_id})" style="mix-blend-mode:{blend}">' + "".join(parts) + "</g>"


def banner(theme):
    dark = theme == "dark"
    bg = GH_DARK_BG if dark else GH_LIGHT_BG
    type_col = INK_LIGHT if dark else INK_DARK
    sub_col = "#C4C4C4" if dark else "#5F5D59"
    # The rules are drawn over everything, including the type, with a
    # difference blend: white lifts them off the dark ground and darkens them
    # where they cross a light letterform, so a rule never disappears.
    grid_op = 0.12 if dark else 0.07
    glow_blend = "screen" if dark else "multiply"
    # The dark banner gets no ground wash at all. Even at 0.05 it lifted the
    # whole canvas ~6 levels above GH_DARK_BG, and a flat offset across the
    # full width is exactly what reads as a box on the page. The light banner
    # keeps its wash: its gradient runs white-to-white, so it adds nothing.
    ground = "" if dark else f'<rect width="{W}" height="{H}" fill="url(#ground)" fill-opacity="0.6"/>' 

    title_d, title_w = text_path(TITLE, "serif", TITLE_SIZE, X, TITLE_Y)
    sub_d, sub_w = text_path(SUB, "sans", SUB_SIZE, X, SUB_Y, tracking=0.2)

    grid = "".join(
        f'<path d="M{GRID_X0 + GRID_STEP * i} 0V{H}" stroke="white"/>' for i in range(GRID_N)
    )

    # light sweep from top-right, as in the cover's star burst
    sweep_origin = (1720, -260)
    # The reference effect (reactbits "light rays") is a shader summing two
    # angular wave fields that drift in opposite directions at different
    # speeds; where they beat against each other the rays brighten, dim and
    # appear to travel across the fan. Two counter-rotating fans reproduce
    # that read. Rotation and opacity sit on plain wrapper groups, so the
    # expensive blur inside each fan is rasterised once and only composited.
    fan_a = rays(*sweep_origin, 9, 1500, 38, 118, "rayGrad", 0.42 if dark else 0.3, "blur40", glow_blend)
    fan_b = rays(*sweep_origin, 5, 1400, 30, 124, "rayGrad2", 0.28 if dark else 0.0, "blur14", glow_blend)
    sweep = (
        f'<g class="fanA"><g class="spinA">{fan_a}</g></g>'
        f'<g class="fanB"><g class="spinB">{fan_b}</g></g>'
    )

    # Held still for anyone who has asked their system to reduce motion.
    ox, oy = sweep_origin
    motion = f"""<style>
    .spinA, .spinB {{ transform-box: view-box; transform-origin: {ox}px {oy}px; }}
    @keyframes spinA {{ from {{ transform: rotate(-1.9deg); }} to {{ transform: rotate(1.9deg); }} }}
    @keyframes spinB {{ from {{ transform: rotate(2.6deg); }} to {{ transform: rotate(-2.6deg); }} }}
    @keyframes breatheA {{ from {{ opacity: 0.68; }} to {{ opacity: 1; }} }}
    @keyframes breatheB {{ from {{ opacity: 0.45; }} to {{ opacity: 1; }} }}
    @media (prefers-reduced-motion: no-preference) {{
      .spinA {{ animation: spinA 19s ease-in-out infinite alternate; }}
      .spinB {{ animation: spinB 13s ease-in-out infinite alternate; }}
      .fanA  {{ animation: breatheA 11s ease-in-out infinite alternate; }}
      .fanB  {{ animation: breatheB 8.5s ease-in-out infinite alternate; }}
    }}
  </style>"""

    # The banner is shown at 100% width, so its edges meet the page. Fading
    # them into the ground colour stops the artwork reading as a block on the
    # README. The grid is drawn after this, so the rules still run end to end.
    # Both themes get it, since both grounds now match a GitHub canvas.
    edge_fade = (
        f'<rect width="{W}" height="26" fill="url(#fadeTop)"/>'
        f'<rect y="{H - 26}" width="{W}" height="26" fill="url(#fadeBot)"/>'
        f'<rect width="14" height="{H}" fill="url(#fadeLeft)"/>'
        f'<rect x="{W - 72}" width="72" height="{H}" fill="url(#fadeRight)"/>'
    )

    # A tight, low halo. The old one (0.5 at a 10px blur, plus a 0.5 gradient
    # bloom) spread far enough past the letterforms that the title read as
    # soft-focus rather than lit.
    if dark:
        glow_title = (
            f'<g opacity="0.26" filter="url(#blur5)" style="mix-blend-mode:screen">'
            f'<path d="{title_d}" fill="{type_col}"/></g>'
            f'<g filter="url(#blur5)"><path d="{title_d}" fill="url(#titleGrad)" fill-opacity="0.28"/></g>'
        )
    else:
        glow_title = f'<g filter="url(#blur5)"><path d="{title_d}" fill="url(#titleGrad)" fill-opacity="0.3"/></g>'


    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg">
{motion}
<defs>
  <radialGradient id="ground" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(0 {H}) rotate(-14) scale(1632 1260)">
    <stop stop-color="{'#8E9AB5' if dark else '#FFFFFF'}"/><stop offset="1" stop-color="{bg}"/>
  </radialGradient>
  <linearGradient id="titleGrad" x1="{X}" y1="0" x2="{X + title_w}" y2="0" gradientUnits="userSpaceOnUse">
    <stop stop-color="{GOLD}"/><stop offset="0.5" stop-color="#C69AC4"/><stop offset="1" stop-color="{VIOLET}"/>
  </linearGradient>
  <linearGradient id="subShine" x1="0" y1="{SUB_Y - SUB_SIZE}" x2="0" y2="{SUB_Y + 6}" gradientUnits="userSpaceOnUse">
    <stop stop-color="{'white' if dark else INK_DARK}" stop-opacity="{0.32 if dark else 0.15}"/><stop offset="1" stop-color="{'white' if dark else INK_DARK}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="rayGrad" x1="{sweep_origin[0]}" y1="{sweep_origin[1]}" x2="{sweep_origin[0] - 1100}" y2="{sweep_origin[1] + 1000}" gradientUnits="userSpaceOnUse">
    <stop stop-color="{GOLD}" stop-opacity="{0.9 if dark else 0.7}"/><stop offset="0.3" stop-color="{'#DFB4A2' if dark else GOLD}" stop-opacity="{0.6 if dark else 0.35}"/><stop offset="0.6" stop-color="{VIOLET}" stop-opacity="{0.4 if dark else 0.3}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="rayGrad2" x1="{sweep_origin[0]}" y1="{sweep_origin[1]}" x2="{sweep_origin[0] - 1000}" y2="{sweep_origin[1] + 900}" gradientUnits="userSpaceOnUse">
    <stop stop-color="white" stop-opacity="0.9"/><stop offset="1" stop-color="white" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="fadeTop" x1="0" y1="0" x2="0" y2="26" gradientUnits="userSpaceOnUse">
    <stop stop-color="{bg}"/><stop offset="1" stop-color="{bg}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="fadeBot" x1="0" y1="{H - 26}" x2="0" y2="{H}" gradientUnits="userSpaceOnUse">
    <stop stop-color="{bg}" stop-opacity="0"/><stop offset="1" stop-color="{bg}"/>
  </linearGradient>
  <linearGradient id="fadeLeft" x1="0" y1="0" x2="14" y2="0" gradientUnits="userSpaceOnUse">
    <stop stop-color="{bg}"/><stop offset="1" stop-color="{bg}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="fadeRight" x1="{W - 72}" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse">
    <stop stop-color="{bg}" stop-opacity="0"/><stop offset="1" stop-color="{bg}"/>
  </linearGradient>
  <filter id="blur40" filterUnits="userSpaceOnUse" x="-300" y="-600" width="2200" height="1500"><feGaussianBlur stdDeviation="40"/></filter>
  <filter id="blur14" filterUnits="userSpaceOnUse" x="-300" y="-600" width="2200" height="1500"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="blur10" filterUnits="userSpaceOnUse" x="0" y="0" width="1584" height="396"><feGaussianBlur stdDeviation="10"/></filter>
  <filter id="blur5" filterUnits="userSpaceOnUse" x="0" y="0" width="1584" height="396"><feGaussianBlur stdDeviation="4.5"/></filter>
  <filter id="blur7" filterUnits="userSpaceOnUse" x="0" y="0" width="1584" height="396"><feGaussianBlur stdDeviation="7"/></filter>
</defs>
<g>
  <rect width="{W}" height="{H}" fill="{bg}"/>
  {ground}
  {sweep}
  {glow_title}
  <path d="{title_d}" fill="{type_col}"/>
  <path d="{sub_d}" fill="{sub_col}"/>
  <path d="{sub_d}" fill="url(#subShine)"/>
  <g opacity="{grid_op}" style="mix-blend-mode:difference">{grid}</g>
  {edge_fade}
</g>
</svg>'''
    path = os.path.join(OUT, f"banner-{theme}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def label(text, theme, size=34, pad=4):
    dark = theme == "dark"
    col = INK_LIGHT if dark else INK_DARK
    # No left padding — labels sit on the README's text margin like the banner.
    d, w = text_path(text, "serif", size, 0, size * 0.78 + pad)
    h = round(size * 1.05 + 2 * pad)
    w = math.ceil(w)
    svg = (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
           f'<path d="{d}" fill="{col}"/></svg>')
    slug = text.lower().replace(" ", "-")
    path = os.path.join(OUT, f"label-{slug}-{theme}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


if __name__ == "__main__":
    made = [banner("dark"), banner("light")]
    for t in ("Working with", "Writing", "Find me"):
        made += [label(t, "dark"), label(t, "light")]
    for p in made:
        print(p, os.path.getsize(p), "bytes")
