import concurrent.futures,csv,hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path('/mnt/nvme5/ACTS-Attack')
OUT=pathlib.Path(__file__).resolve().parent
A=ROOT/'sp2027/analysis'
H=A/'heb1_crossboundary_20261019'
B=A/'experiment_b_20261019'
def read(p): return json.loads(p.read_text())
def save(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def invoke(cmd):
 p=subprocess.run([sys.executable,'-B',*map(str,cmd)],capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=90)
 try: v=json.loads(p.stdout.strip().splitlines()[-1])
 except Exception: v=None
 return {'command':[sys.executable,'-B',*map(str,cmd)],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'verdict':v}
configs=[('heb1_dev',H/'build/cases/dev',H/'build/private/dev',H/'build/labels/dev_labels.json',None,H/'build/runs/dev_run_20261019_073337/results.json'),('heb1_heldout',H/'build/cases/heldout',H/'build/private/heldout',H/'build/labels/heldout_labels.json',None,H/'heldout/heldout_results.json'),('iar_b_dev',B/'iar_b/cases/dev',B/'iar_b/private/dev',B/'iar_b/labels/dev_labels.json',B/'iar_b/trust/dev_run_keys.json',B/'iar_b/runs/20261019_112227/results.json'),('iar_b_heldout',B/'iar_b_heldout/cases/dev',B/'iar_b_heldout/private/dev',B/'iar_b_heldout/labels/heldout_labels.json',B/'iar_b_heldout/trust/heldout_run_keys.json',B/'iar_b_heldout/runs/20261019_114849/results.json'),('iar_c_preserved',B/'iar_c/data/cases',B/'iar_c/data/private',B/'iar_c/data/labels/iar_c_labels.json',B/'iar_c/data/trust/iar_c_run_keys.json',B/'iar_c/runs/20261019_121621/results.json')]
files=set()
for _,cases,private,labels,trust,result in configs:
 files.update(p for d in (cases,private) for p in d.rglob('*') if p.is_file());files.update([labels,result]);files.update([trust] if trust else [])
for d in (H/'build',H/'heldout',H/'freeze',B,B/'iar_c',A/'acts_next_phase_20261019/stage1_attribution'):
 files.update(p for p in d.glob('*') if p.is_file())
files.update((A/'acts_next_phase_20261019/stage1_attribution').glob('work/**/*'))
files={p for p in files if p.is_file() and '__pycache__' not in str(p)}
before={str(p.relative_to(ROOT)):sha(p) for p in sorted(files)}
save('input_hashes_before.json',before)
rows=[];summaries={};mismatches=[];invocations=[]
for name,cases,private,labels,trust,archive in configs:
 labs=read(labels); old=read(archive); heb=name.startswith('heb1')
 prior=old['cases'] if heb else {r['cid']:r for r in old['per_case']}
 systems={'V0':H/'build/heb1_v0_schema_reference.py','V1':H/'build/heb1_v1_hash_integrity.py','V2':H/'build/heb1_v2_claim_binding.py'} if heb else {'v2':H/'build/heb1_v2_claim_binding.py','v3-sig':B/'eb_v3_sig.py','v3-full':B/'eb_v3_full.py'}
 adj=H/'build/heb1_adjudicator.py' if heb else B/('iar_c/eb_independent_adj.py' if name=='iar_c_preserved' else 'eb_adjudicator.py')
 jobs=[]
 for cid in sorted(labs):
  pub=cases/cid/'public';priv=private/cid
  for system,script in systems.items(): jobs.append((cid,system,[script,pub]+([trust] if trust and system!='v2' else [])))
  jobs.append((cid,'adj',[adj,pub,priv]+([trust] if trust else [])))
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
  responses=list(ex.map(lambda j:invoke(j[2]),jobs))
 grouped={cid:{} for cid in labs}
 for (cid,system,_),res in zip(jobs,responses):
  invocations.append({'population':name,'case_id':cid,'system':system,**res});grouped[cid][system]=res['verdict']
  if res['returncode'] or res['verdict'] is None: mismatches.append({'population':name,'case_id':cid,'system':system,'error':'invocation failure'})
 pop=[]
 for cid,lab in sorted(labs.items()):
  got=grouped[cid];truth=got['adj'];requested=['artifact_authorship','execution_identity','target_effect','reference_oracle_acceptance','boundary_enforcement','attribution'].index(read(cases/cid/'public/request.json')['claimed']['claim_level'])+1
  fam=lab['family'];attack=(fam in {'B1','B2','B3','B4a','B4b','B5'} if heb else fam not in ({'S1','S2','S3','S13'} if name=='iar_c_preserved' else {'H0','H7'}))
  level=truth.get('level',truth.get('supported'));honest=(not truth['malformed'] and level>=1 and requested<=level)
  for s in systems:
   v=got[s];accept=v.get('decision') in {'EMIT','ACCEPT'};emitted=v.get('level',v.get('supported')) if accept else None
   previous=prior[cid]['systems'][s]
   prevdec=previous['decision'] if heb else previous
   if v['decision']!=prevdec or (not heb and emitted!=prior[cid]['asserted'][s]): mismatches.append({'population':name,'case_id':cid,'system':s,'current':v,'previous':previous})
   prevadj=prior[cid]['adjudicator'] if heb else prior[cid]['adj']
   for k,val in prevadj.items():
    if k!='ms' and truth.get(k)!=val: mismatches.append({'population':name,'case_id':cid,'adjudicator_key':k})
   r={'population':name,'case_id':cid,'family':fam,'primitive':lab['primitive'],'requested_level':requested,'supported_level':level,'truth_strong':truth['truth_strong'],'malformed':truth['malformed'],'attack_family':attack,'honest_within_evidence':honest,'system':s,'decision':v['decision'],'emitted_level':emitted,'false_promotion':emitted==6 and not truth['truth_strong'],'rejected_honest':honest and emitted!=level,'input_dir':str(cases/cid/'public'),'archive':str(archive)}
   rows.append(r);pop.append(r)
 summaries[name]={'cases':len(labs),'family_counts':{f:sum(l['family']==f for l in labs.values()) for f in sorted({l['family'] for l in labs.values()})},'systems':{}}
 for s in systems:
  rs=[r for r in pop if r['system']==s];att=[r for r in rs if r['attack_family']];hon=[r for r in rs if r['honest_within_evidence']]
  summaries[name]['systems'][s]={'false_promotion_attack':[sum(r['false_promotion'] for r in att),len(att)],'false_promotion_all':[sum(r['false_promotion'] for r in rs),len(rs)],'honest_rejected':[sum(r['rejected_honest'] for r in hon),len(hon)],'fp_by_family':{f:sum(r['false_promotion'] for r in rs if r['family']==f) for f in summaries[name]['family_counts']}}
 print(name,json.dumps(summaries[name]),flush=True)
 save('raw_invocations.json',invocations);save('recomputed_summary.json',summaries);save('case_ledger.json',rows);save('archive_disagreements.json',mismatches)
with (OUT/'case_ledger.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
after={str(p.relative_to(ROOT)):sha(p) for p in sorted(files)}
save('input_hashes_after.json',after);save('input_integrity.json',{'files':len(before),'unchanged':before==after,'changed':[p for p in before if before[p]!=after[p]],'invocations':len(invocations),'archive_disagreements':len(mismatches)})
assert not mismatches and before==after
