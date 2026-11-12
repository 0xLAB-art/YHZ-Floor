import csv
import hashlib
import json
from pathlib import Path

here=Path(__file__).resolve().parent
base='sp2027/analysis/contribution_audit_20261021/paired_effects'
evidence=here/'.omo/evidence'
r=json.loads((here/'results.json').read_text())
log=json.loads((evidence/'analysis.log').read_text())
assert log['status']=='PASS' and log['source_rechecks']==852
assert 'Ran 9 tests' in (evidence/'tests.log').read_text() and (evidence/'tests.log').read_text().rstrip().endswith('OK')
assert (evidence/'report.log').read_text().startswith('PASS:')
assert len(list(csv.DictReader((here/'paired_instances.csv').open())))==512
assert len(list(csv.DictReader((here/'source_admission_audit.csv').open())))==852
assert len(r['contrasts'])==18 and r['metadata']['primary_rows']==768
assert all('shared_seed_zero_event_upper95' in c['pooling_sensitivity'] for c in r['contrasts'] if c['family']=='pooled')
rep=json.loads((here/'preregistered_L3_reproduction.json').read_text())
assert all(v['equivalence']['status']=='EQUIVALENT_WITHIN_MARGIN' for v in rep['contrasts'].values())
cmd=f'python {base}/analyze.py > {base}/.omo/evidence/analysis.log 2>&1'
criteria=[
 ('Cohort and recomputed source admission',cmd,'PASS; 852 source hash/admission checks; 768 primary rows; 256 complete triplets',['results.json','source_admission_audit.csv','.omo/evidence/analysis.log']),
 ('Paired current/legacy and policy interactions',cmd,'18 contrasts, 54 metrics, 512 contrast-instance ledger rows; 50000 resamples seed20261021',['results.json','contrasts.csv','paired_instances.csv','cells.csv']),
 ('Family pooling, shared-seed, zero discordance and multiplicity sensitivity',cmd,'Each of 6 pooled contrasts has instance and seed cluster sensitivity; all 54 metrics have Bonferroni intervals; all 36 McNemar tests have Holm values',['results.json','contrasts.csv']),
 ('Original preregistered L3 retained',cmd,'Original code produces both original EQUIVALENT_WITHIN_MARGIN labels; original seed20261019/20000 draws',['preregistered_L3_reproduction.json']),
 ('Pairing and estimand adversarial/synthetic tests',f'PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s {base} -p test_analysis.py -v > {base}/.omo/evidence/tests.log 2>&1','Ran 9 tests; OK',['test_analysis.py','.omo/evidence/tests.log']),
 ('Bounded scientific interpretation',f'python {base}/render_report.py > {base}/.omo/evidence/report.log 2>&1','PASS: REPORT.md generated; explicit exploratory/counterfactual/ceiling limits',['REPORT.md','render_report.py','.omo/evidence/report.log'])]
files=['analyze.py','test_analysis.py','render_report.py','record_evidence.py','results.json','contrasts.csv','paired_instances.csv','cells.csv','source_admission_audit.csv','preregistered_L3_reproduction.json','REPORT.md','.omo/evidence/analysis.log','.omo/evidence/tests.log','.omo/evidence/report.log']
manifest={}
for name in files:
 p=here/name
 assert p.is_file() and p.stat().st_size>0
 manifest[str(p)]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
report={'status':'PASS','cwd':str(here.parents[3]),'attempt_status':'No active ULW plan; evidence kept under assigned directory/.omo/evidence',
        'criteria':[{'scenario':s,'invocation':c,'binary_observable':o,'artifact_paths':[str(here/p) for p in paths]} for s,c,o,paths in criteria],
        'artifacts':manifest,'validation_invocation':f'python {base}/record_evidence.py > {base}/.omo/evidence/validation.log 2>&1'}
(evidence/'EVIDENCE.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'PASS','nonempty_hashed_artifacts':len(manifest),'criteria':len(criteria),'source_sha256':r['metadata']['source_sha256']}))
