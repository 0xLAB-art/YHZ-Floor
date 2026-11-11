#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
ROOT=Path('/mnt/nvme5/ACTS-Attack')
BASE=ROOT/'sp2027/analysis/experiment_b_20261019/b2_2_stage01'
HERE=Path(__file__).resolve().parent
OUT=HERE/'raw_subprocess'
VAL=ROOT/'sp2027/analysis/contract_sound_stage01_validator_v2.py'
REF=ROOT/'sp2027/analysis/contract_sound_stage01_reference_verifier_v2.py'
WRAP=BASE/'external_candidate_binding_wrapper.py'
PROTECTED={
 ROOT/'sp2027/analysis/RESULTS_LOCK.json':'4b152f188d0781bada5e19f0f113067a7f1860ba98df6fd47862e974827d9e39',
 ROOT/'sp2027/analysis/RESULTS_LOCK_H1PC.json':'8221cb86dd9bd808854cc1f7d098bc3396a4ae53504ea6e8f9eb0ef80e655103',
 ROOT/'sp2027/paper/main.tex':'51f97748b7efca9e525140af5b5e82dbf9ffa8c65b62473c38cf9c8a154be461',
 ROOT/'sp2027/paper/main.pdf':'fd9a58894fa4e5b35a0980e47f488524f1099b6246c2207ff2900bbdf7dd887a',
}
CASES=['clean_control','a1_reproduction','a1b_reproduction','candidate_binding_mismatch','candidate_binding_match_control']
RUNNERS=[ROOT/'sp2027/analysis/run_contract_sound_stage01.py',ROOT/'sp2027/analysis/run_contract_sound_stage01_hardened.py',ROOT/'sp2027/analysis/run_contract_sound_agent_pilot.py',ROOT/'sp2027/analysis/run_contract_sound_agent_pilot_free_v2.py',ROOT/'sp2027/analysis/run_contract_sound_agent_replacement_v1.py']
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x): Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def last_json(s):
 for line in reversed(s.splitlines()):
  try:
   if line.lstrip().startswith('{'): return json.loads(line)
  except json.JSONDecodeError: pass
 return None
def invoke(argv,stdin=None):
 t=time.perf_counter()
 with (open(stdin,'rb') if stdin else open(os.devnull,'rb')) as f:
  p=subprocess.run(argv,stdin=f,capture_output=True,text=True,cwd=HERE)
 return {'argv':[str(x) for x in argv],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'elapsed_ms':round((time.perf_counter()-t)*1000,3),'verdict':last_json(p.stdout)}
def integrity(case):
 c=Path(case/'public_certificate.json'); cert=json.loads(c.read_text())
 rows=[]
 for item in cert.get('evidence',[]):
  p=Path(item['path']); rows.append({'kind':item.get('kind'),'path':str(p),'declared_sha256':item.get('sha256'),'actual_sha256':sha(p) if p.is_file() else None,'match':p.is_file() and item.get('sha256')==sha(p)})
 cp=Path(cert['agent_artifact']['path'])
 return {'evidence':rows,'candidate':{'path':str(cp),'declared_sha256':cert['agent_artifact'].get('sha256'),'actual_sha256':sha(cp) if cp.is_file() else None,'match':cp.is_file() and cert['agent_artifact'].get('sha256')==sha(cp)}}
def reachability(path):
 text=path.read_text(); lines=text.splitlines(); findings=[]
 try: tree=ast.parse(text)
 except SyntaxError as e: return {'path':str(path),'syntax_error':str(e),'external_interface':True,'findings':[]}
 for n in ast.walk(tree):
  if isinstance(n,(ast.Call,ast.Attribute,ast.Name)):
   s=ast.get_source_segment(text,n) or ''
   if any(x in s for x in ('argparse','sys.argv','stdin','json.load','json.loads','certificate','bundle','evidence')):
    findings.append({'line':getattr(n,'lineno',None),'kind':type(n).__name__,'source':s[:240]})
 cli=[{'line':i+1,'text':l} for i,l in enumerate(lines) if re.search(r'ArgumentParser|add_argument\(|sys\.argv|stdin',l)]
 writes=[{'line':i+1,'text':l} for i,l in enumerate(lines) if re.search(r'certificate|write_json|json\.dump|open\(',l,re.I)]
 external=bool(re.search(r'ArgumentParser|sys\.argv|json\.load\(\s*sys\.stdin|--(?:certificate|bundle|evidence)',text))
 return {'path':str(path),'sha256':sha(path),'external_interface_detected':external,'cli_or_input_lines':cli[:80],'ast_input_findings':findings[:120],'certificate_write_lines':writes[:120]}
def main():
 for p in PROTECTED:
  if not p.is_file(): raise SystemExit(f'missing protected {p}')
 before={str(p):sha(p) for p in PROTECTED}
 # Existing B2-2 cases are immutable inputs; copy byte-for-byte into audit evidence.
 copied=HERE/'input_case_snapshots'
 if copied.exists(): shutil.rmtree(copied)
 shutil.copytree(BASE/'cases',copied)
 results=[]
 for name in CASES:
  src=BASE/'cases'/name; pub=src/'public_certificate.json'; bundle=src/'reference_input.json'
  row={'name':name,'input_case':str(src),'input_case_files':{str(p.relative_to(src)):sha(p) for p in sorted(src.rglob('*')) if p.is_file()},'outer_integrity':integrity(src)}
  row['validator']=invoke([sys.executable,str(VAL)],pub)
  row['reference']=invoke([sys.executable,str(REF),str(bundle)])
  row['wrapper']=invoke([sys.executable,str(WRAP),str(pub)])
  dump(OUT/f'{name}.json',row); results.append(row)
 reach=[]
 for p in RUNNERS:
  reach.append(reachability(p))
 for r in reach: dump(HERE/'reachability'/(Path(r['path']).name+'.json'),r)
 v3=[]
 for p in [ROOT/'sp2027/analysis/experiment_b_20261019/iar_b/runs/20261019_112227/results.json',ROOT/'sp2027/analysis/experiment_b_20261019/iar_b_heldout/runs/20261019_114849/results.json',ROOT/'sp2027/analysis/experiment_b_20261019/iar_c/runs/20261019_121621/results.json']:
  v3.append({'path':str(p),'exists':p.is_file(),'sha256':sha(p) if p.is_file() else None,'mode':'read-only established result; not rerun'})
 after={str(p):sha(p) for p in PROTECTED}
 integrity_summary={'validator_sha256':sha(VAL),'reference_sha256':sha(REF),'wrapper_sha256':sha(WRAP),'protected_before':before,'protected_after':after,'protected_unchanged':before==after and after=={str(p):v for p,v in PROTECTED.items()},'provider_calls':0,'network_calls':0,'spend_usd':0.0}
 out={'schema':'b2-2-independent-audit/1','base_protocol':str(BASE/'B2_2_PROTOCOL.md'),'cases':results,'reachability':reach,'v3_full_established_results':v3,'integrity':integrity_summary,'determination':{'original_components':'reproduced from immutable B2-2 cases','binding_wrapper':'external wrapper only; not Stage01 repair','operational_exploitability':'NOT_DEMONSTRATED','novelty':'NOT_ESTABLISHED'}}
 dump(HERE/'B2_2_INDEPENDENT_AUDIT.json',out)
 print(json.dumps({'out':str(HERE/'B2_2_INDEPENDENT_AUDIT.json'),'protected_unchanged':integrity_summary['protected_unchanged'],'cases':len(results),'provider_calls':0,'network_calls':0},indent=2))
 if not integrity_summary['protected_unchanged']: raise SystemExit(3)
if __name__=='__main__': main()
