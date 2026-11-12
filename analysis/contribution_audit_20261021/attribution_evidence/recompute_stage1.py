import collections,csv,hashlib,json,pathlib,sys
ROOT=pathlib.Path('/mnt/nvme5/ACTS-Attack');OUT=pathlib.Path(__file__).resolve().parent;S=ROOT/'sp2027/analysis/acts_next_phase_20261019/stage1_attribution'
sys.dont_write_bytecode=True;sys.path.insert(0,str(S))
import s1_common
from s1_attribution_evaluator import AttributionEvaluator,RunExpectation
from s1_baseline_evaluators import BASELINE_EVALUATORS
from context_validator import ReplayState
def read(p): return json.loads(p.read_text())
def save(n,d): (OUT/n).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[p for p in S.rglob('*') if p.is_file() and '__pycache__' not in str(p)];before={str(p.relative_to(ROOT)):sha(p) for p in files}
old=read(S/'runs/results.json')['results'];rows=[];bad=[]
for r in old:
 bundle=S/r['bundle_path'];run=read(bundle)['run'];exp=RunExpectation(**{k:run[k] for k in RunExpectation.__annotations__})
 for name in [*BASELINE_EVALUATORS,'full','full_lenient']:
  ledger=ReplayState(max_uses=1)
  def ev():
   return BASELINE_EVALUATORS[name](S/'trust/public_bundle.json',exp,replay_state=ledger) if name in BASELINE_EVALUATORS else AttributionEvaluator(S/'trust/public_bundle.json',exp,replay_state=ledger,strict_execution=name=='full')
  first=ev().evaluate(bundle).as_dict();result=ev().evaluate(bundle).as_dict() if r['mutation']=='replay_shared_ledger' else first
  previous=r['observed']['decisions'][name]
  if previous!=result['decision']:bad.append({'case_id':r['case_id'],'system':name,'previous':previous,'current':result['decision']})
  rows.append({'case_id':r['case_id'],'family':r['family'],'system':name,'decision':result['decision'],'expected_strict':r['expected']['decision'],'expected_lenient':r['expected']['decision_lenient'],'crypto_success':r['expected']['crypto_success'],'replay_second_evaluation':r['mutation']=='replay_shared_ledger','details':result})
metrics={}
for name in [*BASELINE_EVALUATORS,'full','full_lenient']:
 rs=[r for r in rows if r['system']==name];metrics[name]={}
 for mode in ['crypto_success','expected_strict','expected_lenient']:
  pos=lambda r:r[mode] is True if mode=='crypto_success' else r[mode]=='ATTRIBUTED_SUCCESS'
  fail=[r for r in rs if not pos(r)];success=[r for r in rs if pos(r)]
  metrics[name][mode]={'false_attribution':[sum(r['decision']=='ATTRIBUTED_SUCCESS' for r in fail),len(fail)],'false_rejection':[sum(r['decision']!='ATTRIBUTED_SUCCESS' for r in success),len(success)]}
 metrics[name]['omission_decisions']=dict(collections.Counter(r['decision'] for r in rs if r['family']=='B'))
analogues=[r for r in old if r['stage01']['applicable']];non=[r for r in analogues if r['expected']['decision']!='ATTRIBUTED_SUCCESS']
metrics['stage01_archived_analogues']={'all_analogues':len(analogues),'unavailable':len(old)-len(analogues),'false_attribution':[sum(r['stage01']['stage01_final_decision']=='ACCEPTED' for r in non),len(non)],'evidence_class':'recomputed archived pair decisions; pair not re-executed here'}
manifest=read(S/'s1_integrity_manifest.json');checks=[]
def walk(x):
 if isinstance(x,dict):
  if 'path' in x and 'sha256' in x:
   p=ROOT/x['path'];checks.append({'path':str(p),'expected':x['sha256'],'actual':sha(p) if p.is_file() else None,'match':p.is_file() and sha(p)==x['sha256']})
  for v in x.values():walk(v)
 elif isinstance(x,list):
  for v in x:walk(v)
walk(manifest)
after={str(p.relative_to(ROOT)):sha(p) for p in files}
save('stage1_replay.json',rows);save('stage1_summary.json',metrics);save('stage1_integrity.json',{'input_hashes':before,'unchanged':before==after,'decision_disagreements':bad,'frozen_manifest_checks':checks})
print(json.dumps(metrics,indent=2));print('decision_disagreements',len(bad),'input_unchanged',before==after,'manifest_mismatches',[c['path'] for c in checks if not c['match']])
assert not bad and before==after
