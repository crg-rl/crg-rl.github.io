"""Story contract for the CRG 15-minute talk."""
EXPERIMENT_DESIGNS={
'gap':'Seq. RLVR vs MTRL · same task pool and training budget · five task sequences.',
'main':'Eight continual methods · 500 optimizer steps per sequence · mean CTM over five sequences.',
'sources':'CPR minus Seq. RLVR · decompose the final-score difference across five task sequences.',
'gradients':'LLM algorithmic · task-pair cosines under Seq. RLVR; gradient mixing at a fixed base model.',
'case':'Seq. RLVR on LLM algorithmic · jugs success across stages, with one question traced throughout.',
'replay':'LLM algorithmic · same training budget; replace fresh responses with stored trajectories.'}
Q={'Q1':'Q1  Can CPR reach joint-training performance?','Q2.1':'Q2.1  Where does the improvement come from?','Q2.2':'Q2.2  Why can previous tasks help?','Q2.3':'Q2.3  What does shared reasoning look like?','Q3':'Q3  Is replay alone enough?'}
def question_label(p):return Q[p]
rows=[
('Beyond Forgetting','',None,None,25),
('Roadmap','',None,None,20),
('New capabilities arrive after deployment','Background',None,None,50),
('Can task-by-task RLVR match joint training?','Background',None,None,45),
('An environment, a diagnosis, and a method','',None,None,40),
('CRG makes continual RLVR an executable environment','Environments',None,None,65),
('Five task sequences across text and visual reasoning','Environments',None,None,45),
('Evaluate every task after every stage','Environments',None,None,60),
('Modest forgetting still leaves a multitask gap','Diagnosis & method',None,'gap',60),
('Final performance depends on more than retention','Diagnosis & method',None,None,65),
('CPR replays prompts and regenerates responses','Diagnosis & method',None,None,75),
('Only CPR reaches MTRL-level performance on average','Results & analysis','Q1','main',75),
('The gain comes from learning, not less forgetting','Results & analysis','Q2.1','sources',65),
('Shared reasoning offers a useful update direction','Results & analysis','Q2.2','gradients',65),
('Other tasks help jugs before and after its own stage','Results & analysis','Q2.3','case',65),
('Fresh responses turn replay into a learning benefit','Results & analysis','Q3','replay',60),
('Takeaways','',None,None,35)]
STORY=[dict(index=i+1,title=t,chapter=c,phase=p,experiment=e,seconds=s,source='') for i,(t,c,p,e,s) in enumerate(rows)]

def assert_slide_story(prs):
    assert len(prs.slides)==len(STORY)==17
    for i,(s,row) in enumerate(zip(prs.slides,STORY)):
        titles=[x for x in s.shapes if x.name=='slide-title']
        if i:assert len(titles)==1 and titles[0].text==row['title'],f'Title drift on {i+1}'
        des=[x for x in s.shapes if x.name.startswith('experiment-design:')]
        assert len(des)==int(bool(row['experiment'])),f'Design line drift on {i+1}'
        if des:assert des[0].text==EXPERIMENT_DESIGNS[row['experiment']]
        for x in s.shapes:
            if x.name.startswith(('chapter-navigation:','result-question:')):assert x.top<titles[0].top
        body='\n'.join(x.text for x in s.shapes if x.has_text_frame)
        if row['chapter']=='Background':assert all(x not in body for x in ['Continual Prompt Replay','CPR','replay previous'])
        assert not any(x in body.lower() for x in ['evidence version','multi-seed','illustrative only','frozen task executor','camp-ii'])
    assert STORY[-1]['title']=='Takeaways'
