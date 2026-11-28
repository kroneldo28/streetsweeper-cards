# Générateurs de cartes #TheStreetSweeper (versions validées par Ronel le 10/11/2026)

RÈGLE : choisir le générateur selon l'auteur des mots.

## 1. Les propres mots de Ronel → My quotes (tools/myquotes/)
Format « tweet » : photo, Ronel Kouakep + badge, @RonelKouakep, citation, https://ronelkouakep.com, #TheStreetSweeper en bas à droite.

    cd tools/myquotes && python3 generate_quote_card.py "Texte avec [[passage en jaune]]." /chemin/sortie.png

- [[...]] = passage en jaune (mettre la chute en jaune), \n = nouveau paragraphe.
- Convertir en JPG (Pillow, qualité 95) dans cards/<n°>-<slug>.jpg.

## 2. Citations d'autres personnes → Cartes 1080 v2 (tools/cartes/)
Texte à gauche, tout en blanc, auteur en or à droite, hashtag en haut à droite.

    import sys; sys.path.insert(0, "tools/cartes"); import quote_card
    quote_card.make_card("Citation.", author="Auteur", outfile="cards/<n°>-<slug>.jpg")

- Options : emphasis, invert, hashtag_pos="bottom", \n pour forcer les coupes. Liste numérotée : numbered_card.py.

URL publique : https://raw.githubusercontent.com/kroneldo28/streetsweeper-cards/main/cards/<fichier>

## 3. TikTok → tools/tiktok/tiktok.py (repris le 28/11/2026)
Vidéos texte : `text_video(slides, out, cover=None)`. Chaque slide est une liste de blocs ; `**mot**` = or ; "@i " = italique. 1080x1920, durée calculée par mot, cover en tête si fournie.
Montages lifestyle : `lifestyle_frame(photo, out, "Lieu · année", crop_x, crop_y)` puis `render(frames, [2.8]*n, out, zoom=True)`. Photos « utilisable » seulement, jamais d'enfants. Mélanger un même contexte à des époques différentes.
