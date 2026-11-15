#!/usr/bin/env python3
"""Headless full-page previews and contact sheets; output outside the source repo."""
import argparse
from pathlib import Path
import fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def render(source,out):
    out.mkdir(parents=True,exist_ok=True);thumbs=[]
    with fitz.open(source) as doc:
        for i,page in enumerate(doc):
            pix=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6));pix.save(out/f'slide-{i+1:02}.png')
            im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((640,360));thumbs.append(im)
    for start in range(0,len(thumbs),9):
        group=thumbs[start:start+9];sheet=Image.new('RGB',(1980,((len(group)+2)//3)*395),'#e6e9ec');dr=ImageDraw.Draw(sheet)
        for i,im in enumerate(group):
            x=(i%3)*660+10;y=(i//3)*395+25;sheet.paste(im,(x,y));dr.text((x,y-18),f'Slide {start+i+1}',fill='black')
        sheet.save(out/f'contact-{start+1:02}.jpg',quality=92)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--pdf',type=Path,default=ROOT/'assets/slides/continual-reasoning-gym-slides.pdf');ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();render(a.pdf,a.out)
