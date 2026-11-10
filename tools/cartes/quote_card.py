#!/usr/bin/env python3
"""
Quote cards 1080x1080 — #TheStreetSweeper (charte Ronel Kouakep)
================================================================

Génère les cartes-citations carrées de la chaîne.

Arborescence attendue (tous les chemins sont relatifs à CE fichier) :

    quote_card.py
    fonts/
        BaiJamjuree-Regular.ttf
        BaiJamjuree-Bold.ttf
        BaiJamjuree-MediumItalic.ttf
    assets/
        pattern01.jpg          <- pattern-kouakep-variante-01.jpg
        bg_1080.jpg            <- généré automatiquement au 1er appel

Usage minimal :

    import quote_card
    quote_card.make_card("Ma citation.", author="Nom Auteur",
                         outfile="sortie.jpg")

Réglages par défaut validés : texte aligné à GAUCHE, auteur aligné à DROITE,
#TheStreetSweeper en HAUT à droite, bloc descendu (v_shift=42), tout le texte
en BLANC (pas de chute en or sauf demande explicite), auteur toujours en GRAS
et en or.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ---------------------------------------------------------------- chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")
ASSET_DIR = os.path.join(BASE_DIR, "assets")

PATTERN = os.path.join(ASSET_DIR, "pattern01.jpg")
BG_IMG = os.path.join(ASSET_DIR, "bg_1080.jpg")

F_BODY = os.path.join(FONT_DIR, "BaiJamjuree-Regular.ttf")
F_EMPH = os.path.join(FONT_DIR, "BaiJamjuree-Bold.ttf")
F_AUTHOR = os.path.join(FONT_DIR, "BaiJamjuree-Bold.ttf")
F_TAG = os.path.join(FONT_DIR, "BaiJamjuree-MediumItalic.ttf")

# ---------------------------------------------------------------- charte
SIZE = 1080                       # format carré
RICH_BLACK = (2, 25, 35)          # #021923
GOLD = (249, 181, 19)             # #F9B513 Selective Yellow
WHITE = (255, 255, 255)
MARGIN = 35                       # marge du cadre or
BORDER_W = 2                      # épaisseur du cadre
PAD = 48                          # retrait du texte par rapport au cadre
TILE = 280                        # taille de tuile du pattern
TILE_ALPHA = 110                  # ~43 % d'opacité
HASHTAG = "#TheStreetSweeper"


# ---------------------------------------------------------------- fond
def build_bg(force=False):
    """Construit assets/bg_1080.jpg : pattern tuilé à 43 % sur Rich Black."""
    if os.path.exists(BG_IMG) and not force:
        return
    import numpy as np

    im = Image.open(PATTERN).convert("RGB")
    w, _ = im.size
    # le pattern source a des marges blanches : crop proportionnel
    # (243 px de marge pour une source 4167x4167)
    m = int(round(243 * w / 4167))
    panel = im.crop((m, m, w - m, w - m)).convert("RGBA")

    # nettoyage des coins arrondis blancs résiduels -> bleu nuit
    pa = np.asarray(panel).astype(int).copy()
    pa[pa[:, :, :3].sum(axis=2) > 200] = [2, 25, 35, 255]
    panel = Image.fromarray(pa.astype("uint8"))

    canvas = Image.new("RGBA", (SIZE, SIZE), RICH_BLACK + (255,))
    panel = panel.resize((TILE, TILE), Image.LANCZOS)
    px = panel.load()
    for y in range(TILE):
        for x in range(TILE):
            r, g, b, _ = px[x, y]
            px[x, y] = (r, g, b, TILE_ALPHA)
    for ty in range(0, SIZE, TILE):
        for tx in range(0, SIZE, TILE):
            canvas.alpha_composite(panel, (tx, ty))
    canvas.convert("RGB").save(BG_IMG, quality=95)


# ---------------------------------------------------------------- texte
def smart(s):
    """Apostrophes et guillemets typographiques."""
    return s.replace("'", "’").replace('"', "”") if s else s


def wrap(d, text, font, max_w):
    """Découpe en lignes. Les '\\n' du texte sont des coupes forcées."""
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=font) <= max_w or not cur:
                cur = t
            else:
                out.append(cur)
                cur = w
        out.append(cur)
    return out


def line_h(f):
    asc, desc = f.getmetrics()
    return asc + desc


def tier(n):
    """Paliers lissés : (taille de départ, largeur max, interligne)."""
    if n <= 50:
        return 96, 800, 1.20
    if n <= 180:
        return 72, 660, 1.22
    if n <= 280:
        return 72, 660, 1.22
    return 60, 700, 1.28


def _layout(d, body, emph, author, fs, a_sz, max_w, lg,
            block_gap, author_gap, bf, ef, af):
    fb = ImageFont.truetype(bf, fs)
    fe = ImageFont.truetype(ef, fs)
    fa = ImageFont.truetype(af, a_sz)
    bl = wrap(d, body, fb, max_w) if body else []
    el = wrap(d, emph, fe, max_w) if emph else []
    lhb, lhe = line_h(fb) * lg, line_h(fe) * lg
    h = 0
    if bl:
        h += lhb * len(bl)
    if bl and el:
        h += block_gap
    if el:
        h += lhe * len(el)
    if author:
        h += author_gap + line_h(fa)
    return fb, fe, fa, bl, el, lhb, lhe, h


# ---------------------------------------------------------------- carte
def make_card(body,
              author,
              outfile,
              emphasis="",
              invert=False,
              author_bold=True,
              text_align="left",
              author_align="right",
              hashtag_pos="top",
              v_shift=42,
              author_size=44,
              tag_size=27,
              block_gap=52,
              author_gap=50,
              max_w=None,
              font_size=None):
    """
    body        texte principal (blanc par défaut). '\\n' = coupe forcée.
    author      signature, affichée « — Nom », toujours en or.
    outfile     chemin du JPG de sortie.
    emphasis    2e bloc mis en or + gras (la « chute »). Vide par défaut :
                par défaut TOUT le texte est blanc, sans chute.
    invert      inverse les rôles : bloc du haut en or/gras, bas en blanc.
    author_bold False pour un auteur en Regular (reste en or).
    text_align  'left' (défaut) | 'center' | 'right'
    author_align'right' (défaut) | 'center' | 'left'
    hashtag_pos 'top' (défaut, en haut à droite) | 'bottom'
    v_shift     décalage vertical du bloc texte+auteur (42 par défaut,
                pour équilibrer avec le hashtag en haut).
    max_w       largeur max de ligne, pour forcer une découpe en vers.
    font_size   force la taille du corps (sinon palier + auto-ajustement).
    """
    build_bg()

    body, emphasis = smart(body), smart(emphasis)
    cap, mw, lg = tier(len((body or "") + (emphasis or "")))
    if max_w:
        mw = max_w
    if font_size:
        cap = font_size

    # normal : haut blanc/Regular, bas or/Bold — invert : l'inverse,
    # l'ordre de lecture étant préservé.
    bfont, bcol = (F_EMPH, GOLD) if invert else (F_BODY, WHITE)
    efont, ecol = (F_BODY, WHITE) if invert else (F_EMPH, GOLD)
    afont = F_AUTHOR if author_bold else F_BODY

    img = Image.open(BG_IMG).convert("RGB").resize((SIZE, SIZE))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([MARGIN, MARGIN, SIZE - MARGIN, SIZE - MARGIN],
                outline=GOLD, width=BORDER_W)
    ft = ImageFont.truetype(F_TAG, tag_size)

    # auto-ajustement : on réduit jusqu'à tenir dans la zone sûre
    avail_h = SIZE - 2 * MARGIN - 150
    fsize = cap
    while fsize >= 28:
        a_sz = min(author_size, max(28, int(fsize * 0.6)))
        fb, fe, fa, bl, el, lhb, lhe, h = _layout(
            d, body, emphasis, author, fsize, a_sz, mw, lg,
            block_gap, author_gap, bfont, efont, afont)
        if h <= avail_h:
            break
        fsize -= 2

    y = (SIZE - h) / 2 + v_shift
    cx = SIZE / 2

    def anchor_x(align):
        if align == "right":
            return SIZE - MARGIN - PAD, "ra"
        if align == "left":
            return MARGIN + PAD, "la"
        return cx, "ma"

    tx, tanc = anchor_x(text_align)
    ax, aanc = anchor_x(author_align)

    for ln in bl:
        d.text((tx, y), ln, font=fb, fill=bcol, anchor=tanc)
        y += lhb
    if bl and el:
        y += block_gap
    for ln in el:
        d.text((tx, y), ln, font=fe, fill=ecol, anchor=tanc)
        y += lhe
    if author:
        y += author_gap
        d.text((ax, y), f"— {author}", font=fa, fill=GOLD, anchor=aanc)

    if hashtag_pos == "top":
        d.text((SIZE - 55, MARGIN + 22), HASHTAG, font=ft, fill=GOLD,
               anchor="ra")
    else:
        d.text((SIZE - 55, SIZE - 65), HASHTAG, font=ft, fill=GOLD,
               anchor="rs")

    img.save(outfile, quality=95)
    print(f"Saved {outfile} | taille texte {fsize}")
    return outfile


if __name__ == "__main__":
    make_card("Test de rendu", author="Test", outfile="test.jpg")
