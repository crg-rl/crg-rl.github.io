#!/usr/bin/env python3
"""Positive rebuild plus deliberate source/shape/regression failures in a scratch copy."""
from pathlib import Path
import argparse,json,shutil,subprocess,sys,tempfile
import fitz
from pptx import Presentation
from validate_artifacts import check
ROOT=Path(__file__).resolve().parents[1];BASE='assets/slides/continual-reasoning-gym-slides'
def run():
    results=[]
    def test(name,ok):results.append(dict(test=name,passed=bool(ok)));assert ok,name
    test('Canonical release passes',check(ROOT)['passed'])
    with tempfile.TemporaryDirectory(prefix='crg-deck-test-') as tmp:
        r=Path(tmp)/'site';shutil.copytree(ROOT,r,ignore=shutil.ignore_patterns('.git','__pycache__'))
        for cmd in [['scripts/build_slides.py'],['scripts/render_slides_pdf.py',BASE+'.pptx',BASE+'.pdf']]:subprocess.run([sys.executable]+cmd,cwd=r,check=True,stdout=subprocess.DEVNULL)
        a=fitz.open(ROOT/(BASE+'.pdf'));b=fitz.open(r/(BASE+'.pdf'))
        test('Fresh rebuild preserves all page text',all(x.get_text()==y.get_text() for x,y in zip(a,b)))
        test('Fresh rebuild preserves every rendered page',all(x.get_pixmap().samples==y.get_pixmap().samples for x,y in zip(a,b)))
        shutil.copy2(ROOT/(BASE+'.pptx'),r/(BASE+'.pptx'));shutil.copy2(ROOT/(BASE+'.pdf'),r/(BASE+'.pdf'))
        def mutate(name,fn):
            p=r/(BASE+'.pptx');raw=p.read_bytes();deck=Presentation(p);fn(deck);deck.save(p);test(name,not check(r)['passed']);p.write_bytes(raw)
        mutate('Missing result design line is rejected',lambda d:setattr(next(s for s in d.slides[11].shapes if s.name.startswith('experiment-design:')),'text',''))
        mutate('Title drift is rejected',lambda d:setattr(next(s for s in d.slides[8].shapes if s.name=='slide-title'),'text','Changed headline'))
        mutate('Off-page text is rejected',lambda d:setattr(next(s for s in d.slides[1].shapes if s.name=='slide-title'),'left',-100000))
        p=r/'assets/slides/figures/case.pdf';raw=p.read_bytes();p.write_bytes(raw+b'changed');test('Source figure drift is rejected',not check(r)['passed']);p.write_bytes(raw)
        p=r/'index.html';raw=p.read_text();p.write_text(raw.replace(BASE+'.pptx','missing.pptx'));test('Broken editable-deck link is rejected',not check(r)['passed']);p.write_text(raw)
    return dict(passed=all(x['passed'] for x in results),tests=results)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);a=ap.parse_args();v=run()
    if a.output:a.output.write_text(json.dumps(v,indent=2)+'\n')
    print(json.dumps(v))
