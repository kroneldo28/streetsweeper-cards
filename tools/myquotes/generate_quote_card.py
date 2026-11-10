#!/usr/bin/env python3
"""
QUOTE CARD GENERATOR — Ronel Kouakep (#TheStreetSweeper)
Format : 1080x1080 px

Usage :
    python3 generate_quote_card.py "Ta citation ici" [sortie.png]

Syntaxe supportee dans le texte :
    \\n            -> nouveau paragraphe (ligne vierge entre les blocs)
    [[ ... ]]     -> portion mise en Selective Yellow
    « ... »       -> ligne(s) entre guillemets francais mises en jaune

Arborescence attendue (chemins relatifs au script) :
    generate_quote_card.py
    assets/pattern-kouakep.jpg
    assets/profile.png
    fonts/BaiJamjuree-Bold.ttf
    fonts/BaiJamjuree-Regular.ttf
    fonts/BaiJamjuree-Medium.ttf
    fonts/BaiJamjuree-Italic.ttf
    fonts/BaiJamjuree-BoldItalic.ttf
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# CHEMINS (relatifs au dossier du script)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

PATTERN_PATH = os.path.join(ASSETS_DIR, "pattern-kouakep.jpg")
PROFILE_PHOTO_PATH = os.path.join(ASSETS_DIR, "profile.png")

# ---------------------------------------------------------------------------
# CHARTE
# ---------------------------------------------------------------------------
SIZE = 1080
RICH_BLACK = (2, 25, 35)
SELECTIVE_YELLOW = (249, 181, 19)
WHITE = (255, 255, 255)
TWITTER_BLUE = (29, 155, 240)

NAME = "Ronel Kouakep"
HANDLE = "@RonelKouakep"
WEBSITE = "https://ronelkouakep.com"
SIGNATURE = "#TheStreetSweeper"

# ---------------------------------------------------------------------------
# MISE EN PAGE
# ---------------------------------------------------------------------------
BORDER_MARGIN = 30      # distance bord image <-> cadre jaune
BORDER_WIDTH = 3        # epaisseur du cadre jaune
BORDER_RADIUS = 8
INNER_PADDING = 140     # respiration interieure (gauche/droite/haut/bas)
PROFILE_SIZE = 100      # diametre de la photo de profil

GAP_HEADER_QUOTE = 50   # entre le bloc identite et la citation
GAP_QUOTE_FOOTER = 40   # entre la citation et le site web
FOOTER_HEIGHT = 30

LINE_SPACING = 1.55     # interligne de la citation

# Fond : methode Strava (tuiles RGBA collees avec masque alpha)
PATTERN_TILE_SIZE = 220
PATTERN_ALPHA = 110     # 110/255 ~ 43 %

# Mots toujours mis en jaune, sans marqueur
HIGHLIGHT_WORDS = ["ndockmangolo", "ndockmangolos"]

# ---------------------------------------------------------------------------
# POLICES — Bai Jamjuree (Poppins en secours si un fichier manque)
# ---------------------------------------------------------------------------
FONT_PATHS = {
    "bold": os.path.join(FONTS_DIR, "BaiJamjuree-Bold.ttf"),
    "regular": os.path.join(FONTS_DIR, "BaiJamjuree-Regular.ttf"),
    "medium": os.path.join(FONTS_DIR, "BaiJamjuree-Medium.ttf"),
    "italic": os.path.join(FONTS_DIR, "BaiJamjuree-Italic.ttf"),
    "bold_italic": os.path.join(FONTS_DIR, "BaiJamjuree-BoldItalic.ttf"),
}

FALLBACKS = {
    "bold": "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "regular": "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
    "medium": "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf",
    "italic": "/usr/share/fonts/truetype/google-fonts/Poppins-Italic.ttf",
    "bold_italic": "/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf",
}

# Tailles de police
FS_NAME = 35
FS_HANDLE = 28
FS_WEBSITE = 25
FS_SIGNATURE = 21

# Taille de la citation selon la longueur du texte
QUOTE_SIZES = [(80, 50), (150, 44), (250, 39), (10 ** 9, 32)]


def get_font(weight, size):
    """Charge Bai Jamjuree, bascule sur Poppins si le fichier est absent."""
    path = FONT_PATHS.get(weight, FONT_PATHS["regular"])
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return ImageFont.truetype(path, size)
    fb = FALLBACKS.get(weight, FALLBACKS["regular"])
    if os.path.exists(fb) and os.path.getsize(fb) > 0:
        return ImageFont.truetype(fb, size)
    return ImageFont.load_default()


def quote_font_size(text):
    n = len(text)
    for limit, size in QUOTE_SIZES:
        if n < limit:
            return size
    return QUOTE_SIZES[-1][1]


# ---------------------------------------------------------------------------
# FOND — methode Strava
# ---------------------------------------------------------------------------
def create_background():
    """Rich Black + pattern tuile en 220 px, colle en RGBA a alpha 110."""
    canvas = Image.new("RGBA", (SIZE, SIZE), (*RICH_BLACK, 255))

    pat = Image.open(PATTERN_PATH).convert("RGBA")

    # 1. Rogner les bordures blanches du fichier source
    arr = np.array(pat)
    bright = arr[:, :, :3].max(axis=2)
    dark = bright < 200
    rows, cols = np.any(dark, axis=1), np.any(dark, axis=0)
    if rows.any() and cols.any():
        r0, r1 = np.where(rows)[0][[0, -1]]
        c0, c1 = np.where(cols)[0][[0, -1]]
        pat = pat.crop((c0, r0, c1 + 1, r1 + 1))

    # 2. Reduire en tuile
    pat = pat.resize((PATTERN_TILE_SIZE, PATTERN_TILE_SIZE), Image.LANCZOS)

    # 3. Forcer l'alpha sur tous les pixels
    px = pat.load()
    for y in range(pat.height):
        for x in range(pat.width):
            r, g, b, _ = px[x, y]
            px[x, y] = (r, g, b, PATTERN_ALPHA)

    # 4. Tuiler avec masque alpha
    for ty in range(0, SIZE, PATTERN_TILE_SIZE):
        for tx in range(0, SIZE, PATTERN_TILE_SIZE):
            canvas.paste(pat, (tx, ty), pat)

    return canvas


# ---------------------------------------------------------------------------
# PHOTO DE PROFIL CIRCULAIRE
# ---------------------------------------------------------------------------
def make_circular_profile(size):
    """Detoure le fond noir ET le fond blanc, recadre en carre, masque rond."""
    photo = Image.open(PROFILE_PHOTO_PATH).convert("RGBA")
    d = np.array(photo, dtype=np.float32)

    brightness = np.max(d[:, :, :3], axis=2)
    min_brightness = np.min(d[:, :, :3], axis=2)
    alpha = d[:, :, 3].copy()

    # Fond sombre -> transparent (avec degrade sur les bords)
    alpha = np.where(brightness < 8, 0, alpha)
    alpha = np.where(
        (brightness >= 8) & (brightness < 40),
        np.minimum(alpha, (brightness - 8) / 32 * 255),
        alpha,
    )

    # Fond blanc -> transparent (avec degrade sur les bords)
    alpha = np.where(min_brightness > 245, 0, alpha)
    alpha = np.where(
        (min_brightness > 220) & (min_brightness <= 245),
        np.minimum(alpha, (245 - min_brightness) / 25 * 255),
        alpha,
    )

    d[:, :, 3] = alpha
    photo = Image.fromarray(d.astype(np.uint8))

    # Recadrage carre centre
    w, h = photo.size
    s = min(w, h)
    photo = photo.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    photo = photo.resize((size, size), Image.LANCZOS)

    # Masque circulaire
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    a = np.array(photo)
    a[:, :, 3] = np.minimum(a[:, :, 3], np.array(mask))
    return Image.fromarray(a)


# ---------------------------------------------------------------------------
# BADGE VERIFIE — dessine par le code, aucun fichier image requis
# ---------------------------------------------------------------------------
def draw_verified_badge(draw, cx, cy, r=12):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TWITTER_BLUE)
    pts = [
        (cx - r * 0.35, cy),
        (cx - r * 0.05, cy + r * 0.35),
        (cx + r * 0.40, cy - r * 0.30),
    ]
    draw.line(pts, fill=WHITE, width=max(3, r // 4))


# ---------------------------------------------------------------------------
# DECOUPE DU TEXTE
# ---------------------------------------------------------------------------
def wrap_text(draw, text, font, max_w):
    """Coupe le texte. Un \\n ouvre un nouveau paragraphe (ligne vierge)."""
    paragraphs = text.split("\n")
    all_lines = []
    for i, para in enumerate(paragraphs):
        if i > 0:
            all_lines.append("")  # ligne vierge entre les paragraphes
        cur = ""
        for word in para.split():
            candidate = f"{cur} {word}".strip()
            measure = candidate.replace("[[", "").replace("]]", "")
            if draw.textbbox((0, 0), measure, font=font)[2] <= max_w:
                cur = candidate
            else:
                if cur:
                    all_lines.append(cur)
                cur = word
        if cur:
            all_lines.append(cur)
    return all_lines


# ---------------------------------------------------------------------------
# GENERATEUR
# ---------------------------------------------------------------------------
def generate_quote_card(quote_text, output_path="quote_card.png"):
    img = create_background()
    draw = ImageDraw.Draw(img)

    # --- Cadre jaune ---
    bm = BORDER_MARGIN
    draw.rounded_rectangle(
        [bm, bm, SIZE - bm, SIZE - bm],
        radius=BORDER_RADIUS,
        outline=SELECTIVE_YELLOW,
        width=BORDER_WIDTH,
    )

    # --- Zone de contenu ---
    cl = bm + INNER_PADDING                 # bord gauche
    cr = SIZE - bm - INNER_PADDING          # bord droit
    ct = bm + INNER_PADDING                 # bord haut
    cb = SIZE - bm - INNER_PADDING          # bord bas
    cw = cr - cl

    # --- Mesures : bloc identite ---
    nf = get_font("bold", FS_NAME)
    hf = get_font("regular", FS_HANDLE)
    nb = draw.textbbox((0, 0), NAME, font=nf)
    hb = draw.textbbox((0, 0), HANDLE, font=hf)
    nh, hh = nb[3] - nb[1], hb[3] - hb[1]
    header_h = max(PROFILE_SIZE, nh + 10 + hh)

    # --- Mesures : citation ---
    qf = get_font("medium", quote_font_size(quote_text))
    lines = wrap_text(draw, quote_text, qf, cw)
    ag = draw.textbbox((0, 0), "Ag", font=qf)
    lh = int((ag[3] - ag[1]) * LINE_SPACING)
    quote_h = len(lines) * lh

    # --- Mesures : pied ---
    sf = get_font("bold", FS_WEBSITE)
    sigf = get_font("bold_italic", FS_SIGNATURE)

    # --- Centrage vertical de l'ensemble ---
    total = header_h + GAP_HEADER_QUOTE + quote_h + GAP_QUOTE_FOOTER + FOOTER_HEIGHT
    y0 = ct + max(0, (cb - ct - total) // 2)

    # --- Photo de profil ---
    prof = make_circular_profile(PROFILE_SIZE)
    img.paste(prof, (cl, y0), prof)

    # --- Nom + badge + handle ---
    tx = cl + PROFILE_SIZE + 18
    ny = y0 + (PROFILE_SIZE - (nh + 10 + hh)) // 2
    draw.text((tx, ny), NAME, fill=WHITE, font=nf)
    draw_verified_badge(draw, tx + (nb[2] - nb[0]) + 20, ny + nh // 2, r=12)
    draw.text((tx, ny + nh + 6), HANDLE, fill=(*WHITE, 130), font=hf)

    # --- Citation ---
    qy = y0 + header_h + GAP_HEADER_QUOTE
    in_guillemets = False
    in_marker = False
    for line in lines:
        if "«" in line:
            in_guillemets = True

        if in_guillemets:
            # Ligne entiere en jaune
            draw.text((cl, qy), line, fill=(*SELECTIVE_YELLOW, 255), font=qf)
        else:
            # Mot par mot, pour gerer les marqueurs [[...]]
            cx = cl
            for word in line.split(" "):
                clean = word
                starts, ends = "[[" in clean, "]]" in clean
                if starts:
                    in_marker = True
                    clean = clean.replace("[[", "")
                if ends:
                    clean = clean.replace("]]", "")
                is_hl = in_marker or clean.strip(".,;:!?").lower() in HIGHLIGHT_WORDS
                draw.text(
                    (cx, qy),
                    clean,
                    fill=(*SELECTIVE_YELLOW, 255) if is_hl else WHITE,
                    font=qf,
                )
                cx += draw.textbbox((0, 0), clean + " ", font=qf)[2]
                if ends:
                    in_marker = False

        if "»" in line:
            in_guillemets = False
        qy += lh

    # --- Site web : aligne a gauche, gras, jaune ---
    fy = y0 + header_h + GAP_HEADER_QUOTE + quote_h + GAP_QUOTE_FOOTER
    draw.text((cl, fy), WEBSITE, fill=(*SELECTIVE_YELLOW, 160), font=sf)

    # --- Signature : bas-droite, colle au cadre, gras italique ---
    draw.text(
        (SIZE - bm - 15, SIZE - bm - 25),
        SIGNATURE,
        fill=(*SELECTIVE_YELLOW, 160),
        font=sigf,
        anchor="rb",
    )

    img.convert("RGB").save(output_path, "PNG", quality=95)
    print(f"OK {output_path}")
    return output_path


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python3 generate_quote_card.py "Ta citation" [sortie.png]')
        sys.exit(1)
    out = sys.argv[2] if len(sys.argv) > 2 else "quote_card.png"
    generate_quote_card(sys.argv[1], out)
