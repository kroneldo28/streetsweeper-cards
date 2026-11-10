#!/usr/bin/env python3
"""
Carte à liste numérotée — #TheStreetSweeper
===========================================

Variante de quote_card pour les citations en points numérotés, avec les
chiffres (« 1. », « 2. » …) en or et gras, le reste du texte en blanc.
Utilisée pour la carte « Deux pièges à éviter » (Les Stoïciens).

Même arborescence que quote_card.py : fonts/ et assets/ à côté du script.

Usage :

    import numbered_card as nc
    nc.make_numbered(
        intro="Deux pièges à éviter :",
        items=["Te soucier de ce qu'ils pensent.",
               "Penser qu'ils se soucient de toi."],
        author="Les Stoïciens",
        outfile="sortie.jpg")
"""

from PIL import Image, ImageDraw, ImageFont
import quote_card as qc

SIZE = qc.SIZE
GOLD = qc.GOLD
WHITE = qc.WHITE
MARGIN = qc.MARGIN


def make_numbered(intro,
                  items,
                  author,
                  outfile,
                  fsize=64,
                  line_gap=1.22,
                  item_gap=30,
                  author_gap=54,
                  v_shift=42,
                  max_w=760,
                  author_size=44,
                  tag_size=27):
    """
    intro   phrase d'introduction en blanc (peut être vide).
    items   liste des points ; ils sont numérotés 1., 2., 3. … en or/gras.
    author  signature, affichée « — Nom » en or/gras, alignée à droite.
    """
    qc.build_bg()

    img = Image.open(qc.BG_IMG).convert("RGB").resize((SIZE, SIZE))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([MARGIN, MARGIN, SIZE - MARGIN, SIZE - MARGIN],
                outline=GOLD, width=qc.BORDER_W)

    ft = ImageFont.truetype(qc.F_TAG, tag_size)
    d.text((SIZE - 55, MARGIN + 22), qc.HASHTAG, font=ft, fill=GOLD,
           anchor="ra")

    fb = ImageFont.truetype(qc.F_BODY, fsize)     # texte
    fn = ImageFont.truetype(qc.F_EMPH, fsize)     # numéros
    fa = ImageFont.truetype(qc.F_AUTHOR, author_size)
    lh = qc.line_h(fb) * line_gap

    x0 = MARGIN + qc.PAD

    blocks = []
    if intro:
        blocks.append(("intro", qc.wrap(d, qc.smart(intro), fb, max_w)))
    for i, it in enumerate(items, 1):
        num = f"{i}."
        nw = d.textlength(num + " ", font=fn)
        blocks.append((num, qc.wrap(d, qc.smart(it), fb, max_w - nw)))

    h = 0
    for kind, lines in blocks:
        h += lh * len(lines)
        if kind != "intro":
            h += item_gap
    h += item_gap                      # espace après l'intro
    h += author_gap + qc.line_h(fa)

    y = (SIZE - h) / 2 + v_shift
    for kind, lines in blocks:
        if kind == "intro":
            for ln in lines:
                d.text((x0, y), ln, font=fb, fill=WHITE, anchor="la")
                y += lh
            y += item_gap
        else:
            nw = d.textlength(kind + " ", font=fn)
            for j, ln in enumerate(lines):
                if j == 0:
                    d.text((x0, y), kind, font=fn, fill=GOLD, anchor="la")
                d.text((x0 + nw, y), ln, font=fb, fill=WHITE, anchor="la")
                y += lh
            y += item_gap

    y += author_gap
    d.text((SIZE - MARGIN - qc.PAD, y), f"— {author}", font=fa,
           fill=GOLD, anchor="ra")

    img.save(outfile, quality=95)
    print(f"Saved {outfile}")
    return outfile


if __name__ == "__main__":
    make_numbered(
        intro="Deux pièges à éviter :",
        items=["Te soucier de ce qu'ils pensent.",
               "Penser qu'ils se soucient de toi."],
        author="Les Stoïciens",
        outfile="test_numbered.jpg")
