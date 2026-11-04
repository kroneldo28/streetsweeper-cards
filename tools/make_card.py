#!/usr/bin/env python3
"""Cartes-citations 1080x1080 — #TheStreetSweeper (charte INSTRUCTIONS-quote-cards v2)."""
import sys
from PIL import Image, ImageDraw, ImageFont
import os
D = os.path.dirname(os.path.abspath(__file__)) + "/"
SIZE=1080; RICH_BLACK=(2,25,35); GOLD=(249,181,19); WHITE=(255,255,255); MARGIN=35; BORDER_W=2
PATTERN=D+"pattern.jpg"; CROP=(66,66,1026,1026)  # pattern source 1092px (équivalent du crop 243/3924 sur 4167px)
F_BODY=D+"fonts/BaiJamjuree-Regular.woff"; F_EMPH=D+"fonts/BaiJamjuree-Bold.woff"
F_AUTHOR=F_EMPH; F_TAG=D+"fonts/BaiJamjuree-MediumItalic.woff"; HASHTAG="#TheStreetSweeper"

def build_bg():
    canvas=Image.new("RGBA",(SIZE,SIZE),RICH_BLACK+(255,))
    tile=280
    pat=Image.open(PATTERN).convert("RGBA").crop(CROP).resize((tile,tile),Image.LANCZOS)
    pat.putalpha(110)
    for ty in range(0,SIZE,tile):
        for tx in range(0,SIZE,tile): canvas.alpha_composite(pat,(tx,ty))
    return canvas.convert("RGB")

def smart(s): return s.replace("'","’").replace('"','”') if s else s
def wrap(d,text,font,max_w):
    out,cur=[],""
    for w in text.split(" "):
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=max_w or not cur: cur=t
        else: out.append(cur); cur=w
    if cur: out.append(cur)
    return out
def lh(f): a,dsc=f.getmetrics(); return a+dsc
def tier(n):
    if n<=50: return 96,800,1.20
    if n<=180: return 72,660,1.22
    if n<=280: return 48,760,1.30
    return 36,820,1.35
def _layout(d,body,emph,author,fs,asz,max_w,lg,bg,ag):
    fb=ImageFont.truetype(F_BODY,fs); fe=ImageFont.truetype(F_EMPH,fs); fa=ImageFont.truetype(F_AUTHOR,asz)
    bl=wrap(d,body,fb,max_w) if body else []; el=wrap(d,emph,fe,max_w) if emph else []
    lhb,lhe=lh(fb)*lg,lh(fe)*lg; h=0
    if bl: h+=lhb*len(bl)
    if bl and el: h+=bg
    if el: h+=lhe*len(el)
    if author: h+=ag+lh(fa)
    return fb,fe,fa,bl,el,lhb,lhe,h
def make_card(body,emph,author,outfile,author_size=44,tag_size=27,block_gap=52,author_gap=50):
    body,emph=smart(body),smart(emph)
    cap,max_w,lg=tier(len((body or "")+(emph or "")))
    img=build_bg(); d=ImageDraw.Draw(img,"RGBA")
    d.rectangle([MARGIN,MARGIN,SIZE-MARGIN,SIZE-MARGIN],outline=GOLD,width=BORDER_W)
    ft=ImageFont.truetype(F_TAG,tag_size)
    avail=SIZE-2*MARGIN-150; fs=cap
    while fs>=28:
        asz=min(author_size,max(28,int(fs*0.6)))
        fb,fe,fa,bl,el,lhb,lhe,h=_layout(d,body,emph,author,fs,asz,max_w,lg,block_gap,author_gap)
        if h<=avail: break
        fs-=2
    y=(SIZE-h)/2-12; cx=SIZE/2
    for ln in bl: d.text((cx,y),ln,font=fb,fill=WHITE,anchor="ma"); y+=lhb
    if bl and el: y+=block_gap
    for ln in el: d.text((cx,y),ln,font=fe,fill=GOLD,anchor="ma"); y+=lhe
    if author: y+=author_gap; d.text((cx,y),f"— {author}",font=fa,fill=GOLD,anchor="ma")
    d.text((SIZE-55,SIZE-65),HASHTAG,font=ft,fill=GOLD,anchor="rs")
    img.save(outfile,quality=95)
