#!/usr/bin/env python3
"""TikTok #TheStreetSweeper — slides texte + vidéos verticales + montages lifestyle.

Reprise du système de juillet 2026 (discussion « Adapter textes en slides TikTok brandées »).

Slides texte (1080x1080) :
  - fond Rich Black + pattern Kouakep à 43 %, cadre or, police Bai Jamjuree
  - **mot** = en or (gras) ; un bloc qui commence par "@i " = italique
  - logo Ronel Kouakep en haut à gauche (230 px), #TheStreetSweeper en bas à droite (italique or, 27 px)
  - taille du texte selon la densité (62/54/46/40), espaces fines françaises automatiques

Vidéo texte (1080x1920) : pattern plein cadre, slide carrée au centre, cover en tête si fournie.
Durée par slide : 1,8 s + 0,30 s par mot, plancher 2,8 s, plafond 10 s ; fondu 0,35 s.

Montage lifestyle (1080x1920) : photos plein cadre avec léger zoom lent, légende « lieu · année »
en bas, logo discret. Sans son (le son se met dans TikTok).
"""
import os, re, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(ROOT, "myquotes", "fonts")
F_REG = os.path.join(FONTS, "BaiJamjuree-Regular.ttf")
F_BOLD = os.path.join(FONTS, "BaiJamjuree-Bold.ttf")
F_ITAL = os.path.join(FONTS, "BaiJamjuree-Italic.ttf")
F_BITAL = os.path.join(FONTS, "BaiJamjuree-BoldItalic.ttf")
F_MITAL = os.path.join(ROOT, "cartes", "fonts", "BaiJamjuree-MediumItalic.ttf")
PATTERN = os.path.join(ROOT, "cartes", "assets", "pattern01.jpg")
LOGO = os.path.join(HERE, "assets", "logo.png")

RICH_BLACK = (2, 25, 35)
GOLD = (249, 181, 19)
WHITE = (255, 255, 255)
S = 1080
TILE, TILE_ALPHA = 280, 110
MARGIN = 35
FPS = 30
BASE, RATE, MIN_D, MAX_D, XFADE = 1.8, 0.30, 2.8, 10.0, 0.35
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿️]")


# ------------------------------------------------------------------ fonds
def _tile():
    im = Image.open(PATTERN).convert("RGB")
    w = im.size[0]
    m = int(round(243 * w / 4167))
    p = np.asarray(im.crop((m, m, w - m, w - m)).convert("RGBA")).astype(int).copy()
    p[p[:, :, :3].sum(axis=2) > 200] = [*RICH_BLACK, 255]
    p = Image.fromarray(p.astype("uint8")).resize((TILE, TILE), Image.LANCZOS)
    p.putalpha(TILE_ALPHA)
    return p


def pattern_bg(w, h, y0=0):
    """Fond tuilé ; y0 cale les tuiles pour un raccord invisible."""
    t = _tile()
    c = Image.new("RGBA", (w, h), RICH_BLACK + (255,))
    start = y0 % TILE - TILE if y0 % TILE else 0
    for y in range(start, h, TILE):
        for x in range(0, w, TILE):
            c.alpha_composite(t, (x, y))
    return c.convert("RGB")


def logo(width):
    im = Image.open(LOGO).convert("RGB")
    a = np.asarray(im).max(axis=2)
    rgba = im.convert("RGBA")
    rgba.putalpha(Image.fromarray(np.clip(a * 1.4, 0, 255).astype("uint8")))
    h = int(im.size[1] * width / im.size[0])
    return rgba.resize((width, h), Image.LANCZOS)


# ------------------------------------------------------------------ texte
def fr_typo(s):
    s = s.replace("'", "’")
    s = re.sub(r"\s*([;:!?»])", " \\1", s)
    s = re.sub(r"«\s*", "« ", s)
    return s


def _tokens(text):
    """Mots avec statut or ; la ponctuation reste collée au mot précédent."""
    out, gold = [], False
    for part in re.split(r"(\*\*)", text):
        if part == "**":
            gold = not gold
            continue
        for w in part.split(" "):
            if not w:
                continue
            if out and re.fullmatch(r"[ ]?[;:!?»,.…)]+", w):
                out[-1] = (out[-1][0] + w, out[-1][1])
            else:
                out.append((w, gold))
    return out


def _wrap(d, toks, fonts, max_w):
    lines, cur, cw = [], [], 0
    sp = d.textlength(" ", font=fonts[0])
    for w, g in toks:
        tw = d.textlength(w, font=fonts[1] if g else fonts[0])
        if cur and cw + sp + tw > max_w:
            lines.append(cur); cur, cw = [], 0
        cw += (sp if cur else 0) + tw
        cur.append((w, g, tw))
    if cur:
        lines.append(cur)
    return lines


def make_slide(blocks, out, hashtag="#TheStreetSweeper"):
    img = pattern_bg(S, S)
    d = ImageDraw.Draw(img)
    d.rectangle([MARGIN, MARGIN, S - MARGIN, S - MARGIN], outline=GOLD, width=2)
    lg = logo(230)
    img.paste(lg, (MARGIN + 32, MARGIN + 30), lg)
    ft = ImageFont.truetype(F_MITAL, 27)
    tw = d.textlength(hashtag, font=ft)
    d.text((S - MARGIN - 32 - tw, S - MARGIN - 62), hashtag, font=ft, fill=GOLD)

    n = sum(len(b) for b in blocks)
    for fs in ([62, 54, 46, 40] if n < 120 else [54, 46, 40] if n < 220 else [46, 40, 36]):
        maxw, top, bot = S - 2 * (MARGIN + 70), MARGIN + 150, S - MARGIN - 110
        laid, h = [], 0
        for i, b in enumerate(blocks):
            ital = b.startswith("@i ")
            txt = fr_typo(b[3:] if ital else b)
            if '"' in txt or "“" in txt:
                ital = True
            fonts = (ImageFont.truetype(F_ITAL if ital else F_REG, fs),
                     ImageFont.truetype(F_BITAL if ital else F_BOLD, fs))
            lines = _wrap(d, _tokens(txt), fonts, maxw)
            lh = int(fs * 1.38)
            laid.append((lines, fonts, lh))
            h += lh * len(lines) + (int(fs * 0.9) if i else 0)
        if h <= bot - top:
            break
    y = top + (bot - top - h) // 2
    for i, (lines, fonts, lh) in enumerate(laid):
        if i:
            y += int(fs * 0.9)
        for ln in lines:
            x = MARGIN + 70
            for w, g, wpx in ln:
                d.text((x, y), w, font=fonts[1] if g else fonts[0], fill=GOLD if g else WHITE)
                x += wpx + d.textlength(" ", font=fonts[0])
            y += lh
    img.save(out)
    return out


def duration_txt(txt):
    txt = EMOJI_RE.sub("", re.sub(r"(@i |\*\*)", "", txt))
    n = len([w for w in txt.split() if any(c.isalnum() for c in w)])
    return round(min(MAX_D, max(MIN_D, BASE + RATE * n)), 2)


# ------------------------------------------------------------------ vidéo
def to_vertical(src, dst, bg=None, fit="square"):
    bg = bg or pattern_bg(S, 1920, y0=-420)
    c = bg.copy()
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    if fit == "square":
        im = im.resize((S, int(im.size[1] * S / im.size[0])), Image.LANCZOS)
        c.paste(im, (0, (1920 - im.size[1]) // 2))
    c.save(dst)
    return dst


def render(frames, durs, out, zoom=False):
    tmp = tempfile.mkdtemp()
    segs = []
    for i, (f, dur) in enumerate(zip(frames, durs)):
        seg = os.path.join(tmp, f"s{i:02d}.mp4")
        vf = "scale=1080:1920,setsar=1"
        if zoom:
            nf = int(dur * FPS)
            vf = (f"scale=2160:3840,zoompan=z='min(1+0.06*on/{nf},1.06)':"
                  f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nf}:s=1080x1920:fps={FPS},setsar=1")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", f, "-t", str(dur),
                        "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", seg], check=True)
        segs.append(seg)
    cmd, filt, prev, off = ["ffmpeg", "-y", "-loglevel", "error"], [], "0:v", 0.0
    for s in segs:
        cmd += ["-i", s]
    for i in range(1, len(segs)):
        off += durs[i - 1] - XFADE
        filt.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XFADE}:offset={off:.2f}[x{i}]")
        prev = f"x{i}"
    if filt:
        cmd += ["-filter_complex", ";".join(filt), "-map", f"[{prev}]"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    return round(sum(durs) - XFADE * (len(durs) - 1), 1)


def text_video(slides, out, cover=None, cover_dur=4.0, workdir=None):
    wd = workdir or tempfile.mkdtemp()
    bg = pattern_bg(S, 1920, y0=-420)
    frames, durs = [], []
    if cover:
        frames.append(to_vertical(cover, os.path.join(wd, "v_cover.png"), bg)); durs.append(cover_dur)
    for i, blocks in enumerate(slides, 1):
        sq = make_slide(blocks, os.path.join(wd, f"slide_{i:02d}.png"))
        frames.append(to_vertical(sq, os.path.join(wd, f"v_{i:02d}.png"), bg))
        durs.append(duration_txt(" ".join(blocks)))
    return render(frames, durs, out), durs


# ------------------------------------------------------------------ habillage (projet RAP237)
W, H = 1080, 1920
F_MED = os.path.join(FONTS, "BaiJamjuree-Medium.ttf")


def brand_overlay(out=None):
    """Habillage permanent du projet RAP237 : cadre or (3 px, marge 35), logo Ronel Kouakep
    en bas à gauche et #TheStreetSweeper en bas à droite, alignés sur la même ligne de base.
    Centre transparent. Le dégradé du pattern est dans chaque image (voir photo_frame)."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([MARGIN, MARGIN, W - MARGIN, H - MARGIN], outline=GOLD + (255,), width=3)
    lg = logo(int(78 * Image.open(LOGO).size[0] / Image.open(LOGO).size[1]))
    base = H - MARGIN - 60
    ov.alpha_composite(lg, (MARGIN + 40, base - lg.size[1]))
    ft = ImageFont.truetype(F_ITAL, 30)
    bb = d.textbbox((0, 0), "#TheStreetSweeper", font=ft)
    d.text((W - MARGIN - 40, base - (bb[3] - bb[1]) - bb[1]), "#TheStreetSweeper", font=ft,
           fill=GOLD + (255,), anchor="ra")
    if out:
        ov.save(out)
    return ov


def _bottom_gradient(h=620, top_alpha=0, bottom_alpha=235):
    bg = pattern_bg(W, h).convert("RGBA")
    a = np.linspace(0, 1, h) ** 1.4 * (bottom_alpha - top_alpha) + top_alpha
    bg.putalpha(Image.fromarray(np.repeat(a[:, None], W, axis=1).astype("uint8")))
    return bg


def photo_frame(src, dst, caption=None, crop_x=0.5, crop_y=0.5, scale=2, subtitle=None, caption_top=False, tight=1.0):
    """Photo plein cadre 9:16 (centre réglable) + dégradé du pattern en bas + légende « Ville · année »."""
    from pillow_heif import register_heif_opener
    register_heif_opener()
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = im.size
    tw, th = (w, int(w * 16 / 9)) if w / h < 9 / 16 else (int(h * 9 / 16), h)
    tw, th = int(tw * tight), int(th * tight)
    x = int(max(0, min(w - tw, crop_x * w - tw / 2)))
    y = int(max(0, min(h - th, crop_y * h - th / 2)))
    im = im.crop((x, y, x + tw, y + th)).resize((W * scale, H * scale), Image.LANCZOS).convert("RGBA")
    g = _bottom_gradient().resize((W * scale, 620 * scale))
    im.alpha_composite(g, (0, (H - 620) * scale))
    if caption:
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype(F_BOLD, 62 * scale)
        cy = (H - MARGIN - 60 - 78 - 150) * scale if not caption_top else (MARGIN + 220) * scale
        if not subtitle:
            d.rectangle([(MARGIN + 40) * scale, cy - 22 * scale, (MARGIN + 130) * scale, cy - 16 * scale], fill=GOLD)
        if subtitle:
            f = ImageFont.truetype(F_BOLD, 84 * scale)
            cy -= 70 * scale
            d.rectangle([(MARGIN + 40) * scale, cy - 34 * scale, (MARGIN + 130) * scale, cy - 28 * scale], fill=GOLD)
        d.text(((MARGIN + 40) * scale, cy), caption, font=f, fill=WHITE)
        if subtitle:
            fs = ImageFont.truetype(F_MED, 44 * scale)
            d.text(((MARGIN + 42) * scale, cy + 104 * scale), subtitle, font=fs, fill=GOLD)
    im.convert("RGB").save(dst, quality=95)
    return dst


def finish(video, out, track=None, overlay=True, volume=1.0, track_start=0):
    """Ajoute l'habillage (fixe, ne zoome pas) et la musique (fondu d'entrée et de sortie)."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                               capture_output=True, text=True).stdout)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", video]
    filt, vmap = [], "0:v"
    if overlay:
        ov = os.path.join(tempfile.mkdtemp(), "ov.png"); brand_overlay(ov)
        cmd += ["-i", ov]; filt.append("[0:v][1:v]overlay=0:0[v]"); vmap = "[v]"
    if track:
        cmd += ["-ss", str(track_start), "-i", track]
        ai = 2 if overlay else 1
        filt.append(f"[{ai}:a]atrim=0:{dur:.2f},afade=t=in:d=0.4,afade=t=out:st={max(0, dur - 1.5):.2f}:d=1.5,volume={volume}[a]")
    if filt:
        cmd += ["-filter_complex", ";".join(filt)]
    cmd += ["-map", vmap] + (["-map", "[a]", "-c:a", "aac", "-b:a", "160k"] if track else ["-an"])
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-t", f"{dur:.2f}", out]
    subprocess.run(cmd, check=True)
    return out


MUSIC_DIR = os.path.join(HERE, "music")


def pick_track(mood, used=()):
    """Choisit un morceau du catalogue (CC0) selon l'ambiance, en évitant ceux déjà utilisés."""
    import json
    cat = json.load(open(os.path.join(MUSIC_DIR, "catalogue.json")))
    c = [t for t in cat if t["mood"] == mood and t["file"] not in used] or [t for t in cat if t["mood"] == mood]
    return os.path.join(MUSIC_DIR, c[0]["file"])


# ------------------------------------------------------------------ lifestyle
def lifestyle_frame(src, dst, caption=None, crop_x=0.5, crop_y=0.5):
    """Photo recadrée 9:16 (centre réglable), légende « lieu · année », logo discret."""
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = im.size
    tw, th = (w, int(w * 16 / 9)) if w / h < 9 / 16 else (int(h * 9 / 16), h)
    x = int(max(0, min(w - tw, crop_x * w - tw / 2)))
    y = int(max(0, min(h - th, crop_y * h - th / 2)))
    im = im.crop((x, y, x + tw, y + th)).resize((2160, 3840), Image.LANCZOS)
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 3840 - 700, 2160, 3840], fill=(2, 25, 35, 0))
    grad = Image.new("L", (1, 700))
    for i in range(700):
        grad.putpixel((0, i), int(190 * (i / 700) ** 1.6))
    shade = Image.new("RGBA", (2160, 700), RICH_BLACK + (0,))
    shade.putalpha(grad.resize((2160, 700)))
    im.paste(shade, (0, 3840 - 700), shade)
    if caption:
        f = ImageFont.truetype(F_BOLD, 96)
        d.text((120, 3840 - 330), caption, font=f, fill=WHITE)
        d.rectangle([120, 3840 - 360, 300, 3840 - 350], fill=GOLD)
    lg = logo(420)
    im.paste(lg, (2160 - 420 - 110, 150), lg)
    im.save(dst, quality=95)
    return dst


# ------------------------------------------------------------------ légendes animées
def _text_png(text, font_path, size, color, out, bar=False):
    """Texte avec ombre portée douce, fond transparent (pour les légendes animées)."""
    from PIL import ImageFilter
    f = ImageFont.truetype(font_path, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = tmp.textbbox((0, 0), text, font=f)
    pad, top = 30, (40 if bar else 0)
    wpx, hpx = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad + top
    sh = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((pad - bb[0] + 3, pad + top - bb[1] + 4), text, font=f, fill=(0, 0, 0, 200))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    d = ImageDraw.Draw(sh)
    if bar:
        d.rectangle([pad, pad, pad + 90, pad + 6], fill=GOLD + (255,))
    d.text((pad - bb[0], pad + top - bb[1]), text, font=f, fill=color + (255,))
    sh.save(out)
    return out, wpx, hpx


def animated_segment(photo_png, out, dur, title, subtitle, y_title=1150, slide=0.7):
    """Photo (zoom lent) + titre qui arrive de la gauche + sous-titre qui arrive de la droite."""
    wd = tempfile.mkdtemp()
    t1, w1, h1 = _text_png(title, F_BOLD, 104, WHITE, os.path.join(wd, "t.png"), bar=True)
    t2, w2, h2 = _text_png(subtitle, F_MED, 52, GOLD, os.path.join(wd, "s.png")) if subtitle else (None, 0, 0)
    x0 = MARGIN + 40 - 30
    nf = int(dur * FPS)
    ease = lambda st: f"(1-pow(1-min(max((t-{st})/{slide},0),1),3))"
    f = (f"[0:v]scale=2160:3840,zoompan=z='min(1+0.06*on/{nf},1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
         f"d={nf}:s={W}x{H}:fps={FPS},setsar=1[bg];"
         f"[bg][1:v]overlay=x='-w+({x0}+w)*{ease(0.15)}':y={y_title}:eval=frame[a]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(dur), "-i", photo_png,
           "-loop", "1", "-t", str(dur), "-i", t1]
    if t2:
        cmd += ["-loop", "1", "-t", str(dur), "-i", t2]
        f += f";[a][2:v]overlay=x='W-(W-{x0 + 2})*{ease(0.35)}':y={y_title + h1 - 22}:eval=frame[o]"
        last = "[o]"
    else:
        last = "[a]"
    cmd += ["-filter_complex", f, "-map", last, "-t", str(dur), "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", out]
    subprocess.run(cmd, check=True)
    return out


def concat_xfade(segs, durs, out):
    cmd, filt, prev, off = ["ffmpeg", "-y", "-loglevel", "error"], [], "0:v", 0.0
    for s_ in segs:
        cmd += ["-i", s_]
    for i in range(1, len(segs)):
        off += durs[i - 1] - XFADE
        filt.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XFADE}:offset={off:.2f}[x{i}]")
        prev = f"x{i}"
    if filt:
        cmd += ["-filter_complex", ";".join(filt), "-map", f"[{prev}]"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", out]
    subprocess.run(cmd, check=True)
    return round(sum(durs) - XFADE * (len(durs) - 1), 1)
