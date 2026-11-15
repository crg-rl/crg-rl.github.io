#!/usr/bin/env python3
"""Check the existing project's download row at desktop and phone widths."""
from pathlib import Path
import argparse,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def run(out):
    out.mkdir(parents=True,exist_ok=True);checks=[];errors=[]
    with sync_playwright() as p:
        b=p.chromium.launch(channel='chrome',headless=True)
        for width in [1440,1024,768,390,320]:
            c=b.new_context(viewport={'width':width,'height':900});pg=c.new_page();pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto((ROOT/'index.html').as_uri());pg.wait_for_load_state('load')
            checks.append(dict(check=f'No horizontal overflow {width}',passed=pg.evaluate('document.documentElement.scrollWidth<=innerWidth')))
            for ext in ['pdf','pptx']:
                a=pg.locator('a[href="assets/slides/continual-reasoning-gym-slides.'+ext+'"]');box=a.bounding_box()
                checks.append(dict(check=f'{ext} link visible and inside viewport {width}',passed=a.count()==1 and a.is_visible() and box['x']>=0 and box['x']+box['width']<=width))
            for im in pg.locator('img').all():
                im.scroll_into_view_if_needed();im.evaluate('(e)=>e.loading="eager"');pg.wait_for_function('(e)=>e.complete&&e.naturalWidth>0',arg=im.element_handle())
            checks.append(dict(check=f'Figures load {width}',passed=pg.locator('img').evaluate_all('(a)=>a.every(e=>e.complete&&e.naturalWidth>0)')))
            pg.evaluate('scrollTo(0,0)');pg.screenshot(path=str(out/f'hero-{width}.png'));c.close()
        b.close()
    checks.append(dict(check='No JS errors',passed=not errors));res=dict(passed=all(x['passed'] for x in checks),checks=checks,errors=errors);(out/'browser-check.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res));return res['passed']
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();raise SystemExit(0 if run(a.out) else 1)
