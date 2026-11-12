import collections,csv,hashlib,json,pathlib
R=pathlib.Path('/mnt/nvme5/ACTS-Attack');A=R/'sp2027/analysis';O=pathlib.Path(__file__).resolve().parent;V=A/'acts_next_phase_20261019_v2';B=A/'experiment_b_20261019';H=A/'heb1_crossboundary_20261019'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):(O/n).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
sources=[]
def source(p):
 sources.append({'path':str(p.relative_to(R)),'sha256':sha(p),'size':p.stat().st_size});return read(p)
p=V/'stage6_matched_translation/translation_results_v2.json';d=source(p);rows=d['rows'];arms={}
for arm in ['in_toto_default','in_toto_policy','in_toto_policy_stateful','in_toto_acts_integration','slsa']:
 pos=[r for r in rows if r['acts']['output']['decision']=='ATTRIBUTED_SUCCESS'];neg=[r for r in rows if r not in pos]
 arms[arm]={'accepted':sum(r[arm]['accepted'] for r in rows),'total':len(rows),'false_promotion':[sum(r[arm]['accepted'] for r in neg),len(neg)],'false_rejection':[sum(not r[arm]['accepted'] for r in pos),len(pos)],'agreement':sum(r[arm]['accepted']==(r in pos) for r in rows),'stages':dict(collections.Counter(r[arm].get('stage','not_recorded') for r in rows))}
sound=[]
for p in sorted((V/'heb2_contract_v1').glob('soundness_*.json')):
 d=source(p);sound.append({'path':str(p.relative_to(R)),'corpus_size':d['corpus_size'],'evaluations':sum(d['decision_census'].values()),'reported_evaluations':d['evaluations'],'accepted_evaluations':sum(n for k,n in d['decision_census'].items() if k.endswith('ATTRIBUTED_SUCCESS')),'accepted_operators':d['accepted_mutant_operators'],'genuine_cases':len(d['genuine_baseline'])//2,'violations':len(d['soundness_violations']),'seed':d['seed'],'evidence_class':'aggregate census reconstruction; no retained per-mutant decision table or fresh soundness execution'})
cal=source(B/'iar_c/runs/20261019_121420/results.json');pres=source(B/'iar_c/runs/20261019_121621/results.json')
ind={'iar_c_calibration_and_preserved_same_ids':[r['cid'] for r in cal['per_case']]==[r['cid'] for r in pres['per_case']],'iar_c_calibration_and_preserved_identical_case_results':cal['per_case']==pres['per_case'],'calibration_cases':len(cal['per_case']),'preserved_cases':len(pres['per_case']),'heldout_generator_imports':{str(p.relative_to(R)):[l for l in p.read_text().splitlines() if l.startswith(('import ','from '))] for p in [H/'heldout/heb1_heldout_gen.py',B/'heldout/eb_iar_b_heldout.py',B/'iar_c/eb_independent_gen.py',B/'iar_c/eb_independent_adj.py']}}
freeze=[]
for p in (H/'freeze').glob('*.json'):
 for rel,expected in source(p)['files'].items():
  f=H/rel;freeze.append({'manifest':str(p.relative_to(R)),'file':str(f.relative_to(R)),'expected':expected,'actual':sha(f),'match':sha(f)==expected})
for p in [B/'iar_c/freeze/IAR_C_FREEZE.json',B/'iar_c/freeze/IAR_C_CASE_MANIFEST.json',B/'freeze/HEB_IARB_FREEZE.json']:
 source(p)
for base in [H,A/'heb1_independent_adversarial_audit_20261019',B,B/'iar_c',A/'acts_next_phase_20261019/stage1_attribution',V/'research/deliverables',V/'stage6_matched_translation',V/'heb2_contract_v1']:
 for p in base.glob('*.md'):sources.append({'path':str(p.relative_to(R)),'sha256':sha(p),'size':p.stat().st_size})
save('supplementary_census.json',{'translation_archived_row_recomputation':arms,'mutation_census':sound,'total_mutation_evaluations':sum(x['evaluations'] for x in sound),'independence':ind,'heb1_frozen_current_checks':freeze,'sources':sources})
claims=[]
def c(cid,claim,n,d,unit,pop,artifact,limit):claims.append({'claim_id':cid,'allowed_claim':claim,'numerator':n,'denominator':d,'unit':unit,'population':pop,'recomputed_artifact':artifact,'qualification':limit})
c('H01','Schema and hash baselines emitted unsupported attribution on HEB1 heldout defects',36,36,'constructed bundle','heb1_heldout B1-B5','recomputed_summary.json','64 total; excludes28 coherent/control bundles; six patterns, two primitives; synthetic')
c('H02','Join-only blocked all HEB1 heldout defect promotions',0,36,'constructed bundle','heb1_heldout B1-B5','recomputed_summary.json','Not authenticated composition or general soundness')
c('C01','Join-only emitted unsupported level6 claims',10,28,'constructed bundle','iar_c_preserved attack families','recomputed_summary.json','Calibration saw same cases before freeze;44 total;not28 independent attacks')
c('C02','Signature-only emitted unsupported level6 claims',14,28,'constructed bundle','iar_c_preserved attack families','recomputed_summary.json','Authentic record origin does not imply claim-specific coherence')
c('C03','Combined validator emitted no unsupported level6 claim',0,28,'constructed bundle','iar_c_preserved attack families','recomputed_summary.json','Trust anchor and uncorrupted relevant signers assumed; known joins tested')
c('C04','Join-only rejected honest-within-evidence bundles',14,16,'constructed bundle','iar_c_preserved honest','recomputed_summary.json','14 are lower-level requests outside V2 full-attribution acceptance contract;not comparative FR evidence')
c('B01','Join-only emitted unsupported level6 claims',16,44,'constructed bundle','iar_b_heldout non-H0/H7','recomputed_summary.json','58 total;44 attack/control-negative cases includes8 malformed H8')
c('B02','Signature-only emitted unsupported level6 claims',28,44,'constructed bundle','iar_b_heldout non-H0/H7','recomputed_summary.json','Different population from44-case IAR-C')
c('S01','Stage1 full strict emitted no false attribution under posthoc attribution truth',0,25,'constructed bundle','TOEEA-1 strict non-success','stage1_summary.json','Preregistered crypto truth is different:0/6 FA and19/21 crypto-positive not attributed')
c('S02','Historical Stage01 falsely attributed two direct-analogue non-successes',2,11,'applicable constructed analogue','TOEEA-1 Stage01','stage1_summary.json','13 analogues total;14 N/A;archived component decisions recomputed not rerun')
c('P01','Configured stateful in-toto inspection agrees with ACTS decisions',22,22,'constructed bundle','stage6 matched translation','supplementary_census.json','Archived upstream outcomes recounted;implementation agreement,not superiority;policy arms added after review')
c('M01','Four aggregate mutation censuses report zero soundness violations',0,11256,'mutant-semantic evaluation','four HEB2 corpora x1407 mutants x2 semantics','supplementary_census.json','Not11256 unique attacks;archived aggregates,no fresh proof;property and evaluator share contract module')
save('claim_ledger.json',claims)
with (O/'claim_ledger.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(claims[0]));w.writeheader();w.writerows(claims)
print(json.dumps({'translation':arms,'mutation_evaluations':sum(x['evaluations'] for x in sound),'calibration_same_cases':ind['iar_c_calibration_and_preserved_same_ids'],'calibration_same_results':ind['iar_c_calibration_and_preserved_identical_case_results'],'heb1_freeze_match':all(x['match'] for x in freeze)},indent=2))
