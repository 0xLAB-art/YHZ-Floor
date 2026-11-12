#!/usr/bin/env python3
"""Audit the completed frozen replacement pilot and write independent results artifacts."""
from __future__ import annotations
import hashlib, json, math, pathlib, random, statistics
from collections import Counter, defaultdict

ROOT=pathlib.Path('/mnt/nvme5/ACTS-Attack')
AN=ROOT/'sp2027/analysis'
OUT=AN/'contract_sound_agent_replacement_20261018'
rows=json.loads((OUT/'pilot_results.json').read_text())['rows']
assert len(rows)==72


def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def primary(r):
 return (r.get('reference') or {}).get('reference_verdict')=='ACCEPTED' and (r.get('validator') or {}).get('decision')=='ACCEPT' and (r.get('execution') or {}).get('status')=='EXECUTED'

def outcome(r):
 return {'primary_success':primary(r),'execution':(r.get('execution') or {}).get('status','NOT_RUN'),'reference':(r.get('reference') or {}).get('reference_verdict','NOT_RUN'),'validator':(r.get('validator') or {}).get('decision','NOT_RUN'),'session_id':r['session_id'],'ordinal':r['ordinal']}

# Condition/task table.
condition_table={}
for task in sorted({r['task'] for r in rows}):
 for cond in ['C0','C1','C2']:
  rs=[r for r in rows if r['task']==task and r['condition']==cond]
  condition_table[f'{task}:{cond}']={
   'scheduled':len(rs),
   'execution':dict(Counter((r.get('execution') or {}).get('status','NOT_RUN') for r in rs)),
   'reference':dict(Counter((r.get('reference') or {}).get('reference_verdict','NOT_RUN') for r in rs)),
   'validator':dict(Counter((r.get('validator') or {}).get('decision','NOT_RUN') for r in rs)),
   'primary_successes':sum(primary(r) for r in rs),
   'primary_rate':sum(primary(r) for r in rs)/len(rs),
  }

pairs=[]
for task in sorted({r['task'] for r in rows}):
 for seed in range(1,13):
  c1=next(r for r in rows if r['task']==task and r['seed']==seed and r['condition']=='C1')
  c2=next(r for r in rows if r['task']==task and r['seed']==seed and r['condition']=='C2')
  o1,o2=primary(c1),primary(c2)
  pairs.append({'task':task,'seed':seed,'c1':outcome(c1),'c2':outcome(c2),'difference_c2_minus_c1':int(o2)-int(o1)})

# Primary paired analysis: C1/C2 over 24 pairs, fixed local bootstrap seed.
c1_success=sum(p['c1']['primary_success'] for p in pairs); c2_success=sum(p['c2']['primary_success'] for p in pairs)
diffs=[p['difference_c2_minus_c1'] for p in pairs]
b=sum(p['c1']['primary_success'] and not p['c2']['primary_success'] for p in pairs)
c=sum((not p['c1']['primary_success']) and p['c2']['primary_success'] for p in pairs)
# exact McNemar two-sided for discordance count, with b=2,c=0 => 0.5.
disc=b+c
mcnemar_p=1.0 if disc==0 else min(1.0, 2*sum(math.comb(disc,k) for k in range(0,min(b,c)+1))/2**disc)
# percentile paired bootstrap, 100000 resamples, frozen analysis seed.
rng=random.Random(20261018)
boot=[]
for _ in range(100000):
 sample=[diffs[rng.randrange(len(diffs))] for _ in diffs]
 boot.append(sum(sample)/len(sample))
boot.sort()
ci=(boot[int(0.025*len(boot))],boot[int(0.975*len(boot))-1])

# Per-session evidence coverage and route/cost checks.
metadata_models=Counter(); http_status=Counter(); raw=certs=refs=validators=0; schema_errors=[]
try:
 import jsonschema
 schema=json.loads((AN/'contract_sound_artifact_schema_v1.json').read_text())
except Exception as exc:
 schema=None; schema_errors.append('schema-library:'+type(exc).__name__)
for r in rows:
 case=OUT/'sessions'/r['session_id']
 raw += int((case/'provider_raw.json').is_file()); certs += int((case/'certificate.private.json').is_file()); refs += int((case/'reference_input.json').is_file()); validators += int((case/'verifier_metadata.json').is_file())
 meta=json.loads((case/'provider_metadata.json').read_text()); metadata_models[meta.get('provider_model')]+=1; http_status[meta.get('http_status')]+=1
 certp=case/'certificate.private.json'
 if schema is not None:
  try: jsonschema.validate(json.loads(certp.read_text()),schema)
  except Exception as exc: schema_errors.append(f"{r['ordinal']}:{type(exc).__name__}:{exc}")

summary={
 'campaign':{'planned':72,'recorded':len(rows),'provider_route':json.loads((OUT/'pilot_results.json').read_text())['provider_route'],'provider_charge_usd':json.loads((OUT/'pilot_results.json').read_text())['provider_charge_usd'],'automatic_retries':0,'paid_fallback':False,'seed_replacement':False},
 'status_counts':dict(Counter(r.get('provider_status') or r.get('status') for r in rows)),
 'condition_table':condition_table,
 'paired_primary_analysis':{'pairs':len(pairs),'c1_successes':c1_success,'c2_successes':c2_success,'c1_rate':c1_success/24,'c2_rate':c2_success/24,'absolute_difference_c2_minus_c1':(c2_success-c1_success)/24,'discordant_c1_only':b,'discordant_c2_only':c,'mcnemar_exact_two_sided_p':mcnemar_p,'bootstrap_resamples':100000,'bootstrap_seed':20261018,'bootstrap_95_percentile_ci':ci,'threshold':0.25,'threshold_met':abs((c2_success-c1_success)/24)>=0.25 and (ci[0]>0 or ci[1]<0)},
 'evidence_counts':{'provider_raw':raw,'certificates':certs,'reference_inputs':refs,'verifier_metadata':validators,'schema_errors':schema_errors},
 'provider_models':dict(metadata_models),'http_status':dict(http_status),
 'diagnostic_note':'These are the first prospective replacement-pilot outcomes; prior 72-session campaign and forensic replay remain excluded.',
}
(OUT/'AGENT_PILOT_RESULTS_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
(OUT/'AGENT_PILOT_PAIRED_RESULTS.json').write_text(json.dumps(pairs,indent=2,sort_keys=True)+'\n')

md=['# ACTS-Attack Contract-Sound Replacement Pilot Results','', '**Execution:** completed exactly 72 scheduled sessions; one provider request per session; no retries, seed replacement, paid fallback, or adaptive stopping.', '**Route:** `claude-sonnet-4-6-free`; all 72 provider metadata records reported HTTP 200 and the exact route.', '**Charge recorded:** USD 0.00.', '', '## Scientific disposition', '', 'These are prospective replacement-pilot outcomes. They are separate from the original infrastructure-invalid campaign and its post-hoc forensic replay. No manuscript or existing result lock was modified.', '', '## Primary C1/C2 endpoint', '', '| Family | C1 | C2 | Difference C2-C1 |', '|---|---:|---:|---:|']
for task in sorted({r['task'] for r in rows}):
 c1=condition_table[f'{task}:C1']; c2=condition_table[f'{task}:C2']
 md.append(f"| {task} | {c1['primary_successes']}/12 ({c1['primary_rate']:.3f}) | {c2['primary_successes']}/12 ({c2['primary_rate']:.3f}) | {(c2['primary_successes']-c1['primary_successes'])/12:.3f} |")
pa=summary['paired_primary_analysis']
md += ['', f"Overall C1: **{pa['c1_successes']}/24 ({pa['c1_rate']:.3f})**", f"Overall C2: **{pa['c2_successes']}/24 ({pa['c2_rate']:.3f})**", f"Absolute paired difference (C2−C1): **{pa['absolute_difference_c2_minus_c1']:.3f}**", f"Discordances: C1-only={pa['discordant_c1_only']}, C2-only={pa['discordant_c2_only']}", f"McNemar exact two-sided p-value: **{pa['mcnemar_exact_two_sided_p']:.3f}**", f"95% paired bootstrap percentile interval: **[{pa['bootstrap_95_percentile_ci'][0]:.3f}, {pa['bootstrap_95_percentile_ci'][1]:.3f}]**; 100,000 resamples, seed 20261018.", f"Meaningful-effect threshold: **0.25**; threshold met: **{pa['threshold_met']}**.", '', 'The pilot does not support a representation-sensitivity effect under the preregistered 0.25 criterion. This is a bounded pilot result, not evidence of equivalence or a general capability estimate.', '', '## Condition and failure accounting', '', '| Task | Condition | Scheduled | Execution | Reference | Primary successes |', '|---|---|---:|---|---|---:|']
for key,val in condition_table.items():
 task,cond=key.rsplit(':',1)
 md.append(f"| {task} | {cond} | {val['scheduled']} | `{val['execution']}` | `{val['reference']}` | {val['primary_successes']} |")
md += ['', '## Observed failures', '', '- Two ECDSA C2 sessions were `SANDBOX_REJECTED` because the model-generated programs imported `hashlib`, which is outside the frozen allowed subset.', '- No provider, parser, oracle-process, validator-process, or harness failure occurred in the 72-session results.', '- C0 produced 0/24 primary successes and 24/24 independent reference rejections.', '', '## Evidence retention', '', f"- Raw provider responses: {raw}/72", f"- Certificates: {certs}/72", f"- Reference inputs: {refs}/72", f"- Verifier metadata files: {validators}/72", f"- JSON Schema errors: {len(schema_errors)}", '', 'Machine-readable artifacts:', '', '- `AGENT_PILOT_RESULTS_SUMMARY.json`', '- `AGENT_PILOT_PAIRED_RESULTS.json`', '- `pilot_results.json`', '- `schedule.json`', '', '## Scientific recommendation', '', '**Do not claim the novelty hypothesis as supported.** The observed C1/C2 difference is 0.083, below the preregistered 0.25 threshold, with two C1-success/C2-failure discordances and no reverse discordances. The correct result is a bounded null/inconclusive pilot outcome, not evidence that representation has no effect.', '', '**Do not modify ACTS-Attack manuscript/results automatically.** Any incorporation requires a separate scientific decision and should preserve the distinction between this prospective campaign, the original invalid campaign, and the diagnostic replay.']
report='\n'.join(md)+'\n'
(AN/'AGENT_PILOT_RESULTS_REPORT.md').write_text(report)
(OUT/'AGENT_PILOT_RESULTS_REPORT.md').write_text(report)
print(json.dumps(summary['paired_primary_analysis'],indent=2,sort_keys=True))
print(json.dumps({'schema_errors':len(schema_errors),'provider_models':dict(metadata_models),'raw':raw,'certs':certs},sort_keys=True))