#!/usr/bin/env python3
"""Build the editable CRG paper talk.

All charts, typography and explanatory diagrams are native PowerPoint shapes.
Original paper figures are embedded as high-resolution pictures; PDF retains their vectors. No GUI is launched.
"""
from __future__ import annotations
import argparse
import json
import hashlib
from slide_story import STORY, EXPERIMENT_DESIGNS, question_label, assert_slide_story
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

ROOT=Path(__file__).resolve().parents[1]
W,H=13.333333,7.5
INK,MUTED,LIGHT,LINE='17232D','596772','75818D','DCE2E9'
BLUE,PALE,GREY,RED,WHITE='235EC8','EAF1FF','AEBDCE','AA3B36','FFFFFF'
WASH='F5F7FA'
FONT='Arial'

def rgb(c):return RGBColor.from_string(c)

def text(s,content,x,y,w,h,size=22,color=INK,bold=False,align=PP_ALIGN.LEFT,font=FONT,valign=MSO_ANCHOR.TOP):
    b=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=b.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
    tf.vertical_anchor=valign
    for i,row in enumerate(str(content).split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text=row or ' ';p.alignment=align;p.line_spacing=1.12;p.space_after=Pt(0)
        for r in p.runs:r.font.name=font;r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=rgb(color)
    return b

def rect(s,x,y,w,h,fill=WHITE,stroke=LINE,width=.8,oval=False):
    r=s.shapes.add_shape(MSO_SHAPE.OVAL if oval else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    r.fill.solid();r.fill.fore_color.rgb=rgb(fill);r.line.color.rgb=rgb(stroke);r.line.width=Pt(width)
    return r

def line(s,x,y,x2,y2,color=LINE,width=1,arrow=False,dash=False):
    r=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x),Inches(y),Inches(x2),Inches(y2))
    r.line.color.rgb=rgb(color);r.line.width=Pt(width)
    if arrow:
        a=OxmlElement('a:tailEnd');a.set('type','triangle');a.set('w','med');a.set('len','med');r.line._get_or_add_ln().append(a)
    if dash:
        a=OxmlElement('a:prstDash');a.set('val','dash');r.line._get_or_add_ln().append(a)
    return r

def image(s,p,x,y,w,h):
    iw,ih=Image.open(p).size;scale=min(w/iw,h/ih);ww,hh=iw*scale,ih*scale
    return s.shapes.add_picture(str(p),Inches(x+(w-ww)/2),Inches(y+(h-hh)/2),Inches(ww),Inches(hh))

def note(s,body,source=''):
    s.notes_slide.notes_text_frame.text=body+('\n\n来源与口径：'+source if source else '')

def heading(s,title,n,source='',subtitle=None):
    row=STORY[n-1]
    t=text(s,row['title'],.63,.66,12.05,.58,size=30,bold=False);t.name='slide-title'
    image(s,ROOT/'assets/slides/pku-logo.png',12.08,.12,.46,.46)
    if row['phase']:
        nav=text(s,'04  Results & analysis',.65,.21,2.62,.22,size=11,color=BLUE,bold=True);nav.name='chapter-navigation:Results & analysis'
        q=text(s,question_label(row['phase']),3.38,.20,8.02,.25,size=14,color=BLUE,bold=True,align=PP_ALIGN.RIGHT);q.name='result-question:'+row['phase']
    elif row['chapter']:
        for i,(name,x,w) in enumerate([('Background',.65,1.75),('Environments',2.70,2.12),('Diagnosis & method',5.00,2.68),('Results & analysis',8.05,3.00)]):
            active=row['chapter']==name
            nav=text(s,f'{i+1:02}  {name}',x,.22,w,.22,size=11,color=BLUE if active else LIGHT,bold=active);nav.name='chapter-navigation:'+name
            if active:line(s,x,.49,x+w-.13,.49,BLUE,1.3)
    if row['experiment']:
        des=text(s,EXPERIMENT_DESIGNS[row['experiment']],.66,1.43,12.0,.44,size=17,color=MUTED);des.name='experiment-design:'+row['experiment']
    line(s,.64,6.99,12.68,6.99)
    if row['source']:
        t=text(s,row['source'],.65,7.13,11.2,.20,size=10,color=LIGHT);t.name='source-footer'
    t=text(s,f'{n:02}',12.11,7.11,.55,.23,size=11,color=LIGHT,align=PP_ALIGN.RIGHT);t.name='page-number'


def paper_figure(s,key,x,y,w,root=ROOT):
    a=json.loads((root/'slides/figure-assets.json').read_text())[key]
    for kind in ('pdf','png'):
        assert hashlib.sha256((root/a[kind]).read_bytes()).hexdigest()==a[kind+'_sha256'],f'Figure drift: {key}'
    x0,y0,x1,y1=a.get('clip_pt',[0,0,a['width_pt'],a['height_pt']]);h=w*(y1-y0)/(x1-x0)
    p=s.shapes.add_picture(str(root/a['png']),Inches(x),Inches(y),Inches(w),Inches(h))
    p.crop_left=x0/a['width_pt'];p.crop_right=1-x1/a['width_pt'];p.crop_top=y0/a['height_pt'];p.crop_bottom=1-y1/a['height_pt'];p.name='paper-figure:'+key
    return p


def conclusion(s,copy,y=6.47,size=24):
    line(s,.64,y-.22,12.68,y-.22,color=LINE)
    text(s,copy,.67,y,12,.62,size=size,color=BLUE,bold=True)

def file(s,x,y,w,h,title='notes.md',lines=None):
    rect(s,x,y,w,h,WHITE,'B4C8EB');rect(s,x,y,.055,h,BLUE,BLUE)
    text(s,title,x+.22,y+.17,w-.43,.3,size=16,color=BLUE,bold=True,font='Menlo')
    line(s,x+.05,y+.64,x+w,y+.64)
    if lines:text(s,lines,x+.22,y+.88,w-.44,h-.97,size=17,color=INK)

def barplot(s,rows,x,y,w,h,maxv=80,labelw=2.8,highlight=None,size=17,axis=True,colors=None):
    # Native geometry and data labels; axis begins at zero.
    n=len(rows);step=(h-.45)/n;plotw=w-labelw-.95;plotx=x+labelw
    if axis:
        ticks=[0,20,40,60,80] if maxv==80 else ([0,25,50,75,100] if maxv==100 else ([0,25,50] if maxv==50 else [0,5,10,15,20,25]))
        for tick in ticks:
            xx=plotx+plotw*tick/maxv;line(s,xx,y-.02,xx,y+step*n-.05,width=.5)
            text(s,str(tick),xx-.16,y+step*n+.06,.38,.2,size=10,color=LIGHT,align=PP_ALIGN.CENTER)
    for i,(lab,val) in enumerate(rows):
        yy=y+i*step
        col=(colors[i] if colors else BLUE if lab==highlight else GREY)
        text(s,lab,x,yy+.015,labelw-.15,step-.02,size=size,color=BLUE if lab==highlight else INK,bold=lab==highlight,valign=MSO_ANCHOR.MIDDLE)
        bh=min(.32,step*.65)
        if val:rect(s,plotx,yy+(step-bh)/2,plotw*val/maxv,bh,col,col,width=.1)
        text(s,f'{val:.1f}',plotx+plotw*val/maxv+.10,yy+.015,.86,step-.02,size=size,color=BLUE if lab==highlight else MUTED,bold=lab==highlight,valign=MSO_ANCHOR.MIDDLE)


def build(out,site_root):
    prs=Presentation();prs.slide_width=Inches(W);prs.slide_height=Inches(H)
    prs.core_properties.title='Beyond Forgetting: Diagnosing and Harnessing Shared Reasoning in Continual RLVR'
    prs.core_properties.author='Lirui Luo; Guoxi Zhang; Hongming Xu; Rongqing Li; Cong Fang; Lifeng Fan'
    prs.core_properties.subject='Continual Reasoning Gym and Continual Prompt Replay'
    def slide():
        s=prs.slides.add_slide(prs.slide_layouts[6]);n=len(prs.slides)
        if n>1:heading(s,STORY[n-1]['title'],n)
        return s
    def box(s,lab,x,y,w=2.05,h=.67,fill=PALE,col=BLUE,size=21):
        rect(s,x,y,w,h,fill,LINE);text(s,lab,x+.10,y+.12,w-.20,h-.16,size=size,color=col,align=PP_ALIGN.CENTER)
    def picture(s,key,x,y,w,h):
        a=json.loads((ROOT/'slides/figure-assets.json').read_text())[key];scale=min(w/a['width_pt'],h/a['height_pt']);ww=a['width_pt']*scale;hh=a['height_pt']*scale
        return paper_figure(s,key,x+(w-ww)/2,y+(h-hh)/2,ww)
    def notes(s,body,source):note(s,body,source+'；约 '+str(STORY[len(prs.slides)-1]['seconds'])+' 秒。')
    # Cover.
    s=slide();text(s,'CONTINUAL REASONING GYM',.72,.43,8,.30,size=16,color=BLUE,bold=True)
    image(s,ROOT/'assets/slides/pku-logo.png',11.80,.34,.73,.73)
    text(s,'Beyond Forgetting',.70,1.30,11.9,.83,size=45,bold=True)
    text(s,'Diagnosing and Harnessing Shared Reasoning\nin Continual RLVR',.75,2.35,11.8,1.08,size=29,color=MUTED)
    text(s,'Lirui Luo [1,2] · Guoxi Zhang [2] · Hongming Xu [2]\nRongqing Li [4] · Cong Fang [1,3] · Lifeng Fan [2]',.77,4.02,11.8,.73,size=18)
    text(s,'[1] State Key Lab of General AI, School of Intelligence Science and Technology, Peking University\n[2] State Key Laboratory of General Artificial Intelligence, BIGAI\n[3] Institute for Artificial Intelligence, Peking University    [4] Beijing Institute of Technology',.78,5.06,11.8,.87,size=12,color=MUTED)
    line(s,.77,6.26,12.50,6.26)
    text(s,'Learning new tasks should expand the whole model’s capability.',.77,6.48,11.8,.46,size=24,color=BLUE,bold=True)
    for label,x,w,url in [('crg-rl.github.io',.78,7.0,'https://crg-rl.github.io/'),('Paper',9.36,.9,'https://arxiv.org/abs/2608.18574'),('Code',11.26,1.1,'https://github.com/crg-rl/crg')]:
        p=text(s,label,x,7.12,w,.21,size=11,color=BLUE);p.text_frame.paragraphs[0].runs[0].hyperlink.address=url
    notes(s,'核心问题是持续扩展推理能力。不是只看旧任务有没有掉分，而是看逐个学习任务后，整体能不能接近同时学所有任务的模型。','公开论文完整标题、作者与单位')
    # Roadmap.
    s=slide()
    ch=[('01','Background','Why learn tasks continually?'),('02','Environments','How does CRG make the question measurable?'),('03','Diagnosis & method','What is missing, and how can replay help?'),('04','Results & analysis','Does it work, and where do the gains come from?')]
    for i,(num,title,desc) in enumerate(ch):
        y=1.90+i*1.13;text(s,num,.89,y,.64,.45,size=25,color=BLUE);text(s,title,1.91,y,4.22,.50,size=27,bold=True);text(s,desc,6.29,y+.04,6.25,.62,size=20,color=MUTED)
        if i<3:line(s,1.91,y+.77,12.50,y+.77)
    notes(s,'先讲任务为什么会连续到来，再介绍 CRG 的环境和比较方式。随后诊断“少遗忘但落后”的矛盾，提出 CPR。实验用三个问题回答效果、增益来源和关键设计。','讲述路线')
    # Background: explanatory scenes, not text columns. No proposed solution.
    bg=json.loads((ROOT/'slides/background-visuals.json').read_text())
    s=slide();a=bg['growing-tasks'];assert hashlib.sha256((ROOT/a['png']).read_bytes()).hexdigest()==a['sha256']
    visual=image(s,ROOT/a['png'],.82,1.47,11.69,4.84);visual.name='background-illustration:growing-tasks'
    conclusion(s,'Can capability expansion avoid repeated joint training?',y=6.49,size=24)
    notes(s,'用图直接对比两种设置。上排随着新任务到来，联合训练不断重新访问更大的任务集合；下排把现有模型传给下一个阶段，只接收当前新任务。图中的题目是推理场景图标，不对应实测成绩。RLVR 用可验证奖励训练推理，MTRL 指多任务联合 RLVR。本页只解释研究需要，不引入 CPR。','Introduction 动机；背景场景图由内置 image_gen 生成')
    s=slide();a=bg['learning-relations'];assert hashlib.sha256((ROOT/a['png']).read_bytes()).hexdigest()==a['sha256']
    visual=image(s,ROOT/a['png'],1.57,1.43,10.20,4.78);visual.name='background-illustration:learning-relations'
    conclusion(s,'Learn the new task. Retain earlier skills. Help future tasks.',y=6.49,size=24)
    notes(s,'橙色向下箭头表示只在当前任务上做训练更新；蓝色向上的三条路径表示更新后要检查的三种能力：当前任务能否学会，旧任务能否保留，未来任务能否获益。问号保留研究问题，不在背景提前宣布结果。整体目标是逐个学习后尽量接近同任务集合的联合训练。','研究问题；关系图由内置 image_gen 生成，不含 CPR 解法')
    # Contributions.
    s=slide()
    for i,(a,b,c) in enumerate([('CRG','A reusable continual-RLVR environment','Task sequences, verifiable rewards and stage-wise evaluation.'),('Shared reasoning','A diagnosis beyond forgetting','Separate transfer, direct learning and retention.'),('CPR','Continual Prompt Replay','Reuse earlier prompts to improve current-policy learning.')]):
        y=1.80+i*1.50;text(s,f'0{i+1}',.83,y,.70,.45,size=27,color=BLUE);text(s,a,1.89,y,3.40,.48,size=27,bold=True);text(s,b,5.56,y,6.85,.43,size=23,bold=True);text(s,c,5.56,y+.61,6.90,.70,size=19,color=MUTED)
        if i<2:line(s,1.88,y+1.17,12.48,y+1.17)
    notes(s,'贡献分三层：CRG 是可执行、可复用的环境；共享推理给出为什么不能只看遗忘的解释；CPR 把已有任务提示带回当前策略的训练。这里只给预览，细节随后展开。','Introduction 三项贡献')
    # Environment overview original paper figure.
    s=slide();picture(s,'gym',.65,1.48,7.66,5.12)
    for i,(a,b) in enumerate([('Task sequences','Train through related but distinct tasks.'),('Verifiable rewards','Generate responses; check them with task verifiers.'),('Stage-wise evaluation','Evaluate all tasks at every stage boundary.')]):
        y=1.97+i*1.54;text(s,a,8.68,y,3.85,.42,size=24,bold=True,color=BLUE);text(s,b,8.68,y+.57,3.85,.90,size=21,color=MUTED)
    notes(s,'直接用论文原图讲环境。上方是算法推理的任务序列，中间是 prompt、生成、验证、更新的循环；每个阶段完成后对所有任务评测。CRG 不只是结果榜单，而是训练和诊断可共用的持续 RLVR 环境。','当前 CRG 原始环境图；只保留 PKU 标识，不移植 CAMP 的机构')
    # Concrete tasks.
    s=slide();text(s,'Two text sequences from Reasoning Gym; three visual sequences from VisuLogic.',.73,1.53,11.95,.70,size=22,color=MUTED)
    picture(s,'tasks',.70,2.69,11.94,2.82)
    text(s,'Text reasoning',.84,5.73,5.0,.40,size=24,bold=True);text(s,'Visual reasoning',5.72,5.73,6.3,.40,size=24,bold=True)
    text(s,'Qwen3-4B',.84,6.25,5.0,.37,size=21,color=BLUE);text(s,'Qwen2.5-VL-7B',5.72,6.25,6.3,.37,size=21,color=BLUE)
    notes(s,'五条序列分属两个模态：文本算法、代数，视觉空间、位置和数量推理。原图给出每类具体任务，听众不需要记住所有任务名。训练模型分别是 Qwen3-4B 和 Qwen2.5-VL-7B。','当前作者论文 task-example 原图；旧版主结果与当前表格一致')
    # Evaluation matrix and CTM definition.
    s=slide();text(s,'A score matrix separates when each task benefits from training.',.74,1.51,11.94,.45,size=22,color=MUTED)
    x,y=2.28,2.48;cw,ch=1.36,.73
    for j,lab in enumerate(['Task 1','Task 2','…','Task T']):text(s,lab,x+j*cw,y-.42,cw,.28,size=16,align=PP_ALIGN.CENTER)
    for i,lab in enumerate(['Before training','After stage 1','After stage 2','After stage T']):
        text(s,lab,.74,y+i*ch+.20,1.40,.50,size=14,color=MUTED)
        for j in range(4):
            col=PALE if i==3 else ('DBE8FA' if i>0 and j<i else WASH)
            rect(s,x+j*cw,y+i*ch,cw-.05,ch-.06,col,WHITE);text(s,'score',x+j*cw,y+i*ch+.22,cw-.05,.28,size=15,color=BLUE if i==3 else MUTED,align=PP_ALIGN.CENTER)
    text(s,'FinalAvg = average of the final row',2.28,5.68,5.4,.38,size=20,color=BLUE,bold=True)
    line(s,8.20,2.35,8.20,6.03)
    text(s,'Continual-to-multitask ratio',8.62,2.49,3.98,.70,size=21,bold=True)
    text(s,'CTM =',8.64,3.63,1.43,.44,size=24,color=BLUE,bold=True)
    text(s,'FinalAvg',10.14,3.35,2.22,.35,size=23,align=PP_ALIGN.CENTER);line(s,10.07,3.85,12.42,3.85,INK,1.1);text(s,'MTRL FinalAvg',10.04,4.04,2.40,.39,size=20,align=PP_ALIGN.CENTER)
    text(s,'1.0 = joint-training performance',8.65,5.13,3.90,.84,size=23,color=BLUE,bold=True)
    notes(s,'矩阵每行对应一个训练边界，每列对应任务；每个 score 都来自实际任务评测，图中只显示结构而不填造数。最后一行平均值是 FinalAvg。为了跨不同难度的任务序列比较，使用 FinalAvg 除以同任务集合的 MTRL FinalAvg，得到 CTM；1 表示到达联合训练水平。','Evaluation quantities；CTM 用各序列 ratio 再等权平均，不是 aggregate 分数比')
    # Observation.
    s=slide();picture(s,'gap',.72,2.12,7.50,4.55)
    text(s,'2.47 pp',8.80,2.33,3.56,.72,size=43,color=BLUE,bold=True);text(s,'mean drop on earlier tasks',8.85,3.20,3.65,.75,size=21,color=MUTED)
    line(s,8.85,4.13,12.43,4.13);text(s,'0.88×',8.80,4.47,3.60,.74,size=43,color=RED,bold=True);text(s,'joint-training performance',8.85,5.35,3.62,.80,size=21,color=MUTED)
    notes(s,'关键现象是：平均旧任务只掉 2.47 个百分点，但整体 CTM 只有 0.88。原图每个点是一条任务序列，横轴 BWT，纵轴 CTM。尤其算法任务有正向 BWT，仍明显低于 MTRL。这促使我们把剩余差距拆开，而不是只降低遗忘。','公开论文 Figure 3；当前同内容原图，数值不变')
    # Exact decomposition in readable native type.
    s=slide();text(s,'Track a task before, during and after its own training stage.',.73,1.52,11.95,.45,size=22,color=MUTED)
    terms=[('BaseAvg',.90,INK),('+',3.09,MUTED),('w × FWT',3.69,BLUE),('+',6.04,MUTED),('TLG',6.75,BLUE),('+',8.39,MUTED),('w × BWT',9.07,RED)]
    text(s,'FinalAvg =',.85,2.43,11.7,.48,size=29,bold=True)
    for val,x,col in terms:text(s,val,x,3.23,2.50 if val!='+' else .50,.53,size=28,color=col,bold=val!='+')
    text(s,'w = (T − 1) / T     ·     T = number of tasks',.90,4.01,11.5,.35,size=17,color=MUTED)
    for x,a,b,c in [(1.00,'FWT','Before its own stage','Transfer from earlier tasks'),(5.15,'TLG','During its own stage','Learning the current task'),(9.24,'BWT','After its own stage','Effect of later-task training')]:
        line(s,x,4.75,x+3.17,4.75,BLUE if a!='BWT' else RED,1.2);text(s,a,x,5.02,3.18,.40,size=25,color=BLUE if a!='BWT' else RED,bold=True);text(s,b,x,5.56,3.18,.38,size=18,bold=True);text(s,c,x,6.10,3.18,.64,size=17,color=MUTED)
    notes(s,'这个恒等式将最终分数分成初始能力，加上学本任务之前、直接训练本任务、以及后续训练三个阶段的变化。FWT 与 BWT 按论文定义排除首尾没有对应阶段的任务，因此有 (T-1)/T 的系数。只改善 BWT，可能同时损失 FWT 和 TLG；少遗忘并不自动等于高最终分数。','Proposition 1；正式 FWT/TLG/BWT 定义，非单个任务案例的近似量')
    # Method: original authored figure dominates.
    s=slide();picture(s,'method',.68,1.51,7.83,5.22)
    for i,(a,b) in enumerate([('Keep the prompts','Select previous prompts with intermediate pass rates.'),('Generate with today’s policy','Fresh responses receive their own task’s verified reward.'),('Mix within the same budget','Replace part of the current batch; keep rollouts fixed.')]):
        y=1.84+i*1.66;text(s,a,8.82,y,3.75,.77,size=23,color=BLUE,bold=True);text(s,b,8.82,y+.83,3.75,.88,size=19,color=MUTED)
    notes(s,'CPR 的核心不是重放旧答案：存的是之前任务的题目，重放时让当前策略重新解答，再由该任务验证器给奖励。选择中间通过率的旧题，替换当前 batch 的一部分，保持每次更新的 prompt 和 rollout 预算。右上对照旧轨迹重放，下面是完整一次更新。目标是让先前任务提供对全任务集合更有用的训练方向。','当前原始 CPR 图；对应论文方法和 Algorithm 1')
    # Q1 editable bar chart with every comparison method.
    s=slide();text(s,'Mean CTM',.77,1.98,3.5,.30,size=14,color=MUTED)
    rows=[('CPR',1.03),('Muon',.97),('KL-to-old-policy',.95),('Seq. RLVR',.88),('EWC',.87),('ReDo',.78),('OSFT',.65),('FIRE',.29)]
    plotx=3.70;plotw=4.75;y=2.45;step=.45
    for tick in [0,.25,.5,.75,1.0]:
        xx=plotx+plotw*tick/1.1;line(s,xx,y-.10,xx,y+step*8-.05,BLUE if tick==1 else LINE,1.2 if tick==1 else .5,dash=tick==1);text(s,f'{tick:g}',xx-.20,y+step*8+.10,.44,.20,size=11,color=MUTED,align=PP_ALIGN.CENTER)
    for i,(name,v) in enumerate(rows):
        yy=y+i*step;text(s,name,.77,yy+.02,2.73,.29,size=19,bold=name=='CPR',color=BLUE if name=='CPR' else INK);rect(s,plotx,yy+.06,plotw*v/1.1,.24,BLUE if name=='CPR' else GREY,BLUE if name=='CPR' else GREY,.1);text(s,f'{v:.2f}',plotx+plotw*v/1.1+.10,yy+.015,.72,.32,size=18,color=BLUE if name=='CPR' else MUTED,bold=name=='CPR')
    text(s,'1.03×',9.46,2.55,2.84,.77,size=46,color=BLUE,bold=True);text(s,'MTRL-level performance\non average',9.50,3.48,2.93,1.16,size=23)
    line(s,9.49,4.72,12.41,4.72);text(s,'Four of five sequences\nimprove over Seq. RLVR.',9.49,5.05,3.03,.81,size=19,color=MUTED);text(s,'Positional: 33.2% vs 34.7%.',9.49,6.03,3.03,.52,size=15,color=MUTED)
    notes(s,'看五序列 CTM 的等权平均，所有比较方法都展示。CPR 为 1.03，Seq.RLVR 为 0.88；在所比较的持续学习方法里只有 CPR 达到 MTRL 水平。注意这不是每条序列都更高：四条高于 Seq.RLVR，位置推理低 1.5 个百分点。Muon 是不同优化器的控制项，MTRL 仍是固定参照，不称 optimizer-matched。','公开论文 Table 2；CTM=序列内比值再平均；数字按论文显示精度')
    # Q2.1 source deltas: signed, weighted contributions.
    s=slide();text(s,'Contribution to the FinalAvg improvement (percentage points)',.77,2.00,10.4,.32,size=16,color=MUTED)
    base=5.30;scale=.50
    line(s,.94,base,8.44,base,INK,1)
    for i,(label,val,col) in enumerate([('Forward transfer',2.4,BLUE),('Direct task learning',4.9,BLUE),('Backward transfer',-.9,RED)]):
        x=1.42+i*2.47;h=abs(val)*scale;rect(s,x,base-h if val>0 else base,1.35,h,col,col,.1)
        text(s,f'{val:+.1f}',x-.04,base-h-.55 if val>0 else base+h+.13,1.44,.49,size=28,color=col,bold=True,align=PP_ALIGN.CENTER)
        text(s,label,x-.52,6.41,2.39,.40,size=16,align=PP_ALIGN.CENTER)
    line(s,8.83,2.48,8.83,6.40);text(s,'+6.4 pp',9.23,2.95,3.25,.80,size=44,color=BLUE,bold=True);text(s,'higher final performance',9.27,3.97,3.20,.74,size=22)
    text(s,'Transfer and direct learning\nmore than offset the\nretention trade-off.',9.27,5.02,3.20,1.40,size=21,color=MUTED)
    notes(s,'同一初始策略下，CPR 的最终平均分高 6.4 点。加权后的 FWT 贡献 +2.4，TLG +4.9，BWT -0.9，三者恰好相加为6.4。因此收益不是“旧任务忘得更少”，而是更好地学当前任务与迁移到未来任务。这些已经是对 FinalAvg 的贡献，不再乘一次系数。','公开论文 Table 2；对 Seq.RLVR 的加权百分点差，表中四舍五入')
    # Q2.2 separate diagnostic contexts, one argument.
    s=slide();text(s,'Tasks share useful directions',.80,2.05,5.62,.40,size=24,bold=True);text(s,'Replay can exploit those directions',6.86,2.05,5.73,.40,size=24,bold=True)
    picture(s,'gradients',.80,2.68,5.62,3.22);picture(s,'alignment',6.91,2.68,5.60,3.22)
    text(s,'82.2% positive task-pair cosines',.88,6.15,5.55,.40,size=22,color=BLUE,bold=True)
    text(s,'Mean alignment: 0.43 → 0.79',6.98,6.15,5.50,.40,size=22,color=BLUE,bold=True)
    notes(s,'两幅图回答相关但不同的问题。左图在 Seq.RLVR 下测算法任务两两梯度，平均 cosine 0.345，82.2% 为正，支持共享结构。右图在冻结 Qwen3-4B base 上，对 stage2到10 比较当前任务梯度和当前/以前任务梯度各占一半的组合；对全任务平均方向的 alignment 从0.43到0.79，九个阶段都更高。这是局部梯度诊断，不把 cosine 当作长期性能保证。','公开梯度热图 + 当前作者九阶段梯度诊断；右图固定base，左图Seq.RLVR')
    # Full original case figure, no reconstructed narrative graphic.
    s=slide();picture(s,'case',.78,2.03,11.78,4.88)
    notes(s,'完整论文案例图，保留性能曲线和真实推理摘录。Jugs 在自己的训练阶段之前从0到24%，直接训练后39%，后续其他任务训练后44%。同一问题的推理从反复检查、不输出答案，到正确答案，再到更直接的推理。这里研究的是 Seq.RLVR 内的共享推理现象，不是 CPR 与基线配对个例。图中的早期/直接/后期增益是单任务区间变化，不称全序列平均 FWT/TLG/BWT。','当前原始 jugs 图，完整保留；推理长度按图中有效 think 内容')
    # Q3 current policy regeneration.
    s=slide();text(s,'Final average task success (%)',.80,2.03,7.82,.31,size=15,color=MUTED)
    vals=[('Stored trajectories',47.5),('No replay',49.9),('CPR: fresh responses',63.3),('MTRL',65.3)]
    for i,(lab,v) in enumerate(vals):
        y=2.74+i*.78;col=BLUE if i==2 else ('7C8B9E' if i==3 else GREY);text(s,lab,.80,y+.07,3.14,.51,size=21,bold=i==2,color=BLUE if i==2 else INK);rect(s,4.11,y+.12,4.07*v/70,.34,col,col,.1);text(s,f'{v:.1f}',4.11+4.07*v/70+.15,y+.07,.85,.41,size=23,bold=i==2,color=BLUE if i==2 else MUTED)
    line(s,4.11,6.08,8.18,6.08)
    for v in [0,20,40,60]:text(s,str(v),4.11+4.07*v/70-.14,6.27,.42,.22,size=11,color=MUTED,align=PP_ALIGN.CENTER)
    text(s,'+13.5 pp',9.38,2.96,3.10,.76,size=42,color=BLUE,bold=True);text(s,'over no replay',9.42,3.94,3.08,.43,size=23)
    text(s,'Old prompts remain useful.\nOld answers can become stale.',9.42,5.13,3.08,1.44,size=22,color=MUTED)
    notes(s,'不是“加 replay 就行”。在算法序列同预算对照中，旧轨迹重放47.5，甚至低于不重放49.9；保持题目但用当前策略重新生成，达到63.3，接近MTRL65.3。CPR相对不重放高13.5点（按未四舍五入值计算）。结论是题目可以复用，但训练答案应跟上当前策略。','公开论文 regeneration 消融；不把算法序列数字写成跨序列平均')
    # Takeaways: insights that survive removal of method names.
    s=slide()
    take=[('Low forgetting is not the same as good continual learning.','The final score also depends on transfer and learning the arriving task.'),('Earlier tasks can be a resource for learning new ones.','Shared reasoning gives replay a role beyond protecting old performance.'),('Replay quality depends on the current policy.','Old prompts can remain useful after their stored answers become stale.')]
    for i,(a,b) in enumerate(take):
        y=1.85+i*1.54;text(s,f'0{i+1}',.85,y,.69,.49,size=29,color=BLUE);text(s,a,1.97,y,10.50,.83,size=27,bold=True);text(s,b,1.99,y+.91,10.45,.52,size=21,color=MUTED)
        if i<2:line(s,1.98,y+1.32,12.46,y+1.32)
    notes(s,'收尾留三个 insight。第一，不遗忘只是持续学习的一部分；第二，旧任务不是只能被保护，也可以成为学习新任务的资源；第三，RLVR 重放应复用问题、刷新答案。到这里停住，可直接进入问答，不追加 references 或 thank-you。','综合分解、梯度/行为观察与生成消融；不把操作步骤当 insight')
    assert_slide_story(prs);out.parent.mkdir(parents=True,exist_ok=True);prs.save(out)
    outline=['# Beyond Forgetting — talk outline','','17 slides · approximately 15–16 minutes · English slides / Chinese notes','']
    notes_out=['# 讲稿：Beyond Forgetting','']
    for row,s in zip(STORY,prs.slides):
        outline+= [f"## {row['index']:02} · {row['title']}",f"{row['chapter'] or 'Talk structure'} · {row['seconds']} s",'']
        notes_out += [f"## {row['index']:02} · {row['title']}",s.notes_slide.notes_text_frame.text,'']
    (ROOT/'slides/outline.md').write_text('\n'.join(outline));(ROOT/'slides/speaker-notes.md').write_text('\n'.join(notes_out))
    print(json.dumps({'slides':len(prs.slides),'seconds':sum(r['seconds'] for r in STORY),'pptx':str(out)}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'assets/slides/continual-reasoning-gym-slides.pptx');a=ap.parse_args();build(a.out,ROOT)
