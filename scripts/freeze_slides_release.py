#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
import fitz
from pptx import Presentation
from slide_story import STORY,assert_slide_story
ROOT=Path(__file__).resolve().parents[1]
BASE='assets/slides/continual-reasoning-gym-slides'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert_slide_story(Presentation(ROOT/(BASE+'.pptx')))
    with fitz.open(ROOT/(BASE+'.pdf')) as p:assert len(p)==len(STORY)
    names=['README.md','index.html','assets/slides/pku-logo.png','slides/outline.md','slides/speaker-notes.md','slides/figure-assets.json','slides/background-visuals.json']
    names += [str(p.relative_to(ROOT)) for folder in ['scripts','slides/sources','assets/slides/figures','assets/slides/background'] for p in (ROOT/folder).iterdir() if p.is_file() and p.suffix in ['.py','.json','.csv','.tex','.pdf','.png']]
    m=dict(schema=1,pages=len(STORY),talk_seconds=sum(x['seconds'] for x in STORY),inputs={n:sha(ROOT/n) for n in sorted(names)},outputs={BASE+ext:sha(ROOT/(BASE+ext)) for ext in ['.pdf','.pptx']})
    (ROOT/'slides/release-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'pages':m['pages'],'outputs':m['outputs']}))
if __name__=='__main__':main()
