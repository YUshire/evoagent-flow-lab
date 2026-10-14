import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
OUT=ROOT/'output'/'github-flow'
OUT.mkdir(parents=True,exist_ok=True)
REPOSITORY='YUshire/evoagent-flow-lab'
def load(name): return json.loads((ROOT/'records'/'github-flow'/(name+'.json')).read_text(encoding='utf-8'))
def save(name,value): (OUT/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

from evoagent.evolution_proof import run_prompt_evolution_proof, write_report
from evoagent.evolution import EvolutionEngine
from evoagent.store import TaskStore
from evoagent.evaluation_harness import RULE_TO_CWE

out=OUT/'controlled-activation'
out.mkdir(exist_ok=True)
assert not (OUT/'controlled-activation.db').exists(), 'Use a fresh output directory; existing experiment evidence must not be overwritten'
cases=[]
for split in ['validation','holdout']:
    samples=[
        ('SEC-EVAL','def read_payload(raw):\n    return eval(raw)\n','return eval'),
        ('SEC-YAML-LOAD','import yaml\ndef read_yaml(raw):\n    return yaml.load(raw, Loader=yaml.Loader)\n','return yaml.load'),
        ('SEC-ASSERT-AUTH','def privileged_action(user):\n    assert user.is_admin\n    return "privileged"\n','assert user.is_admin'),
        (None,'import json\ndef read_payload(raw):\n    return json.loads(raw)\n',None),
        (None,'import yaml\ndef read_yaml(raw):\n    return yaml.safe_load(raw)\n',None),
        (None,'def privileged_action(user):\n    if not user.is_admin:\n        raise PermissionError("denied")\n    return "privileged"\n',None)]
    for index,(rule,code,marker) in enumerate(samples,1):
        path=split+'/'+str(index)+'.py'
        compile(code,path,'exec')
        lines=code.splitlines()
        diff='--- /dev/null\n+++ b/'+path+'\n@@ -0,0 +1,'+str(len(lines))+' @@\n'+''.join('+'+line+'\n' for line in lines)
        line=next((i+1 for i,s in enumerate(lines) if marker and marker in s),0)
        expected=[] if not rule else [{'path':path,'start_line':line,'end_line':line,'cwe':RULE_TO_CWE[rule],'rule_id':rule,'severity':'medium' if rule=='SEC-ASSERT-AUTH' else 'high'}]
        cases.append({'id':split+'-'+str(index),'repository':'authored-proof/'+split,'pull_request':None,'split':split,'diff':diff,'expected_findings':expected,'source':{'kind':'new-authored-controlled','note':'Mechanism proof with a deterministic reviewer; not real-model improvement.'}})
dataset=out/'cases.jsonl'
dataset.write_text(''.join(json.dumps(case,ensure_ascii=False)+'\n' for case in cases),encoding='utf-8')
db=str(OUT/'controlled-activation.db')
report=run_prompt_evolution_proof(str(dataset),db)
write_report(report,str(out))
store=TaskStore(db)
versions=store.list_skill_versions('llm-review')
base=min(versions,key=lambda v:v['version'])
active_before=store.get_active_skill_version('llm-review')['version']
rolled_back=EvolutionEngine(store,seed_defaults=False).rollback('llm-review',base['version'])
save('controlled-rollback',{'active_before':active_before,'restored_version':base['version'],'passed':rolled_back and store.get_active_skill_version('llm-review')['version']==base['version'],'scope':'isolated deterministic proof database; no production change'})
assert report['evolution_run']['decision']=='activated'
print(json.dumps({'decision':report['evolution_run']['decision'],'validation':report['validation']['delta'],'holdout':report['holdout']['delta'],'rollback':rolled_back}),flush=True)
