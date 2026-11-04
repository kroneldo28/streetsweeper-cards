# Générateur de cartes #TheStreetSweeper

Usage (Python 3 + Pillow) :

    import sys; sys.path.insert(0, "tools")
    from make_card import make_card
    make_card("Texte principal (blanc)", "Phrase forte (or)", "Auteur", "cards/NNN-slug.jpg")

Charte : 1080×1080, fond noir riche #021923 + motif, bordure et accent or #F9B513, police Bai Jamjuree, hashtag #TheStreetSweeper en bas à droite.
Nommage : cards/<n° du stock>-<slug>.jpg. URL publique : https://raw.githubusercontent.com/kroneldo28/streetsweeper-cards/main/cards/<fichier>
