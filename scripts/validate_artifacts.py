#!/usr/bin/env python3
"""Verify CRG story, exact numbers, native shapes, source figures and release identity."""
from pathlib import Path
import argparse,csv,hashlib,json,re,statistics,unicodedata
from urllib.parse import urlparse,unquote
from html.parser import HTMLParser
import fitz
from pptx import Presentation
from slide_story import STORY,assert_slide_story
ROOT=Path(__file__).resolve().parents[1]
BASE='assets/slides/continual-reasoning-gym-slides'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s))
class Links(HTMLParser):
    def __init__(self):super().__init__();self.urls=[];self.ids=[]
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if t in ('a','img','script','link'):
            u=a.get('href',a.get('src'))
            if u:self.urls.append(u)
def check(root=ROOT):
    checks=[]
    def expect(ok,name):checks.append(dict(check=name,pass_=bool(ok)))
    page=Links();page.feed((root/'index.html').read_text())
    expect(len(page.ids)==len(set(page.ids)),'Unique web IDs')
    for url in page.urls:
        u=urlparse(url)
        if u.scheme:continue
        if url.startswith('#'):expect(url[1:] in page.ids,'Web anchor '+url)
        else:expect((root/unquote(u.path)).is_file(),'Web local asset '+url)
    expect(BASE+'.pdf' in page.urls and BASE+'.pptx' in page.urls,'Both deck formats linked on website')
    ppt=Presentation(root/'assets/slides/continual-reasoning-gym-slides.pptx');pdf=fitz.open(root/'assets/slides/continual-reasoning-gym-slides.pdf')
    expect(len(ppt.slides)==len(pdf)==len(STORY),'PPTX/PDF match the 17-slide story')
    try:
        assert_slide_story(ppt);story_ok=True
    except AssertionError:
        story_ok=False
    expect(story_ok,'Story, chapter navigation, design lines and genuine Takeaways')
    numeric_wraps=[];bounds=[];mismatches=[];overlaps=[];picture_slides=[]
    for i,(slide,p) in enumerate(zip(ppt.slides,pdf),1):
        txt=p.get_text();normalized=norm(txt)
        expect('来源与口径' in slide.notes_slide.notes_text_frame.text,f'Slide {i} source and Chinese speaker notes')
        picture_boxes=[fitz.Rect(*[v/12700 for v in [b.left,b.top,b.left+b.width,b.top+b.height]]) for b in slide.shapes if b.shape_type==13]
        for shape in slide.shapes:
            x,y,w,h=[v/12700 for v in [shape.left,shape.top,shape.width,shape.height]]
            if x<-.1 or y<-.1 or x+w>p.rect.width+.1 or y+h>p.rect.height+.1:
                bounds.append([i,shape.name,x,y,w,h])
            if shape.shape_type==13:picture_slides.append(i)
            if not shape.has_text_frame or not shape.text.strip():continue
            for box in picture_boxes:
                inter=fitz.Rect(x,y,x+w,y+h)&box
                if not inter.is_empty and inter.width>2 and inter.height>2:overlaps.append([i,'Native text overlaps paper figure',shape.text])
            if norm(shape.text) not in normalized:mismatches.append([i,shape.text])
            if re.fullmatch(r'[+−-]?\d+\.\d+%?',shape.text):
                clipped=p.get_text('text',clip=fitz.Rect(x-1,y-3,x+w+1,y+h+3))
                if shape.text not in clipped.splitlines():numeric_wraps.append([i,shape.text,clipped])
        spans=[s for b in p.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans'] if s['text'].strip()]
        all_spans=spans
        spans=[s for s in all_spans if not any(box.contains(fitz.Point((s['bbox'][0]+s['bbox'][2])/2,(s['bbox'][1]+s['bbox'][3])/2)) for box in picture_boxes)]
        for sp in all_spans:
            if not p.rect.contains(fitz.Rect(sp['bbox'])):bounds.append([i,sp['text'],sp['bbox']])
        for a in range(len(spans)):
            ra=fitz.Rect(spans[a]['bbox'])
            if not p.rect.contains(ra):bounds.append([i,spans[a]['text'],list(ra)])
            for b in range(a+1,len(spans)):
                rb=fitz.Rect(spans[b]['bbox']);inter=ra & rb
                if not inter.is_empty and inter.width>2 and inter.height>2 and inter.width*inter.height>min(ra.width*ra.height,rb.width*rb.height)*.15:
                    overlaps.append([i,spans[a]['text'],spans[b]['text']])
    expect(not mismatches,'Every native PPTX text box survives PDF rendition')
    expect(not numeric_wraps,'Numeric data labels remain on one line')
    expect(not bounds,'No slide/text content outside the page')
    expect(not overlaps,'No material native-text overlaps')
    expect(sorted(set(picture_slides))==list(range(1,18)), 'Institution mark appears on every slide')
    fonts={f[0]:f for p in pdf for f in p.get_fonts()}
    expect(all(f[2]!='Type3' and bool(pdf.extract_font(x)[3]) for x,f in fonts.items()),'All PDF fonts embedded; zero Type 3')
    expected_figures={6:['gym'],7:['tasks'],9:['gap'],11:['method'],14:['gradients','alignment'],15:['case']}
    actual={}
    for i,s in enumerate(ppt.slides,1):
        keys=[b.name.split(':',1)[1] for b in s.shapes if b.name.startswith('paper-figure:')]
        if keys:actual[i]=keys
    expect(actual==expected_figures,'Original exhibits on intended pages')
    assets=json.loads((root/'slides/figure-assets.json').read_text())
    for key,a in assets.items():
        for kind in ('pdf','png'):expect(sha(root/a[kind])==a[kind+'_sha256'],'Figure hash '+key+' '+kind)
    rows=list(csv.DictReader((root/'slides/sources/fig_ctm_by_suite.csv').open()))
    expected={'CPR':'1.03','Muon':'0.97','KL-to-old-policy':'0.95','Seq. RLVR':'0.88','EWC':'0.87','ReDo':'0.78','OSFT':'0.65','FIRE':'0.29'}
    pairs=[(b.text, ppt.slides[11].shapes[i+2].text) for i,b in enumerate(ppt.slides[11].shapes) if b.has_text_frame and b.text in expected]
    for name,v in expected.items():
        mean=statistics.mean(float(r['ctm']) for r in rows if r['display_method']==name)
        expect(f'{mean:.2f}'==v,'Mean CTM recomputed '+name)
        expect((name,v) in pairs,'Native bar label/value pair '+name)
    expect('+2.4' in pdf[12].get_text() and '+4.9' in pdf[12].get_text() and '-0.9' in pdf[12].get_text() and '+6.4' in pdf[12].get_text(),'Signed weighted source gains')
    expect(all(v in pdf[15].get_text() for v in ['47.5','49.9','63.3','65.3','+13.5']),'Regeneration ablation values')
    algo={r['display_method']:float(r['final_avg']) for r in rows if r['group']=='LLM algorithmic'}
    exact_gain=(algo['CPR']-algo['Seq. RLVR'])*100
    expect(f'{exact_gain:+.1f}' in pdf[15].get_text(),'Regeneration gain uses unrounded source values')
    expect('Seq. RLVR' in pdf[14].get_text(),'Case is correctly scoped to sequential RLVR')
    expect('fixed base model' in pdf[13].get_text(),'Gradient-mixing checkpoint scope visible')
    expect('33.2%' in pdf[11].get_text() and '34.7%' in pdf[11].get_text(),'Positional trade-off retained')
    expect('JD.com' not in pdf[0].get_text() and all(n in pdf[0].get_text() for n in ['Lirui Luo','Guoxi Zhang','Hongming Xu','Rongqing Li','Cong Fang','Lifeng Fan','Peking University','BIGAI','Beijing Institute of Technology']),'Original CRG authorship retained')
    expect(all('\ufffd' not in p.get_text() and '\x00' not in p.get_text() for p in pdf),'No missing-glyph text markers')
    m=root/'slides/release-manifest.json';expect(m.is_file(),'Release manifest exists')
    if m.is_file():
        manifest=json.loads(m.read_text());expect(manifest['pages']==len(STORY),'Manifest page count')
        for group in ['inputs','outputs']:
            for path,digest in manifest[group].items():expect((root/path).is_file() and sha(root/path)==digest,'Release binding '+path)
    return dict(passed=all(c['pass_'] for c in checks),checks=checks,text_mismatches=mismatches,numeric_wraps=numeric_wraps,out_of_bounds=bounds,text_overlaps=overlaps)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--output',type=Path);a=ap.parse_args();r=check(a.root)
    if a.output:a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(r,ensure_ascii=False));raise SystemExit(0 if r['passed'] else 1)
