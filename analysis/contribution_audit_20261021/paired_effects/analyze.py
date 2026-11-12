import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / 'sp2027/analysis/h1r3_20261019'
sys.dont_write_bytecode = True
sys.path.insert(0, str(SOURCE))
from h1r3_contract import qualify_source
import h1r3_analyze as original
import h1r3_stats as original_stats

ARMS = ('R0', 'R1', 'R2')
METRICS = ('current', 'legacy_admission', 'policy_change_legacy_minus_current')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index_rows(rows):
    index = {}
    for row in rows:
        if row['kind'] != 'primary':
            continue
        if row['arm'] not in ARMS:
            raise ValueError('unexpected primary arm')
        key = (row['family'], row['level'], row['instance_id'])
        arms = index.setdefault(key, {})
        if row['arm'] in arms:
            raise ValueError('duplicate primary cell')
        arms[row['arm']] = row
    for key, arms in index.items():
        if set(arms) != set(ARMS):
            raise ValueError('missing arm: ' + str(key))
        if len({r['seed'] for r in arms.values()}) != 1:
            raise ValueError('inconsistent matched seed')
        if any(r['terminal'] in {'PROVIDER_FAILURE', 'EXTRACTION_EMPTY'} for r in arms.values()):
            raise ValueError('excluded terminal requires explicit denominator revision')
    return index


def vector(arms, arm):
    ref, treatment = arms['R0'], arms[arm]
    current = int(treatment['terminal_success']) - int(ref['terminal_success'])
    legacy = (int(treatment['terminal_success']) * int(treatment['qualification_legacy']['qualified'])
              - int(ref['terminal_success']) * int(ref['qualification_legacy']['qualified']))
    return (current, legacy, legacy - current)


def bootstrap(values, groups, resamples, seed, mode='stratified_instance'):
    rng = np.random.default_rng(seed)
    groups = np.asarray(groups)
    if mode == 'unstratified_instance':
        ix = rng.integers(0, len(values), (resamples, len(values)))
        return values[ix].mean(axis=1)
    strata = [np.flatnonzero(groups == g) for g in sorted(set(groups))]
    answer = np.zeros((resamples, values.shape[1]))
    for ix in strata:
        draws = rng.integers(0, len(ix), (resamples, len(ix)))
        answer += values[ix][draws].sum(axis=1) / len(values)
    return answer


def interval(draws, alpha=.05):
    return [float(x) for x in np.quantile(draws, [alpha/2, 1-alpha/2])]


def describe(values, draws):
    n = len(values)
    nonzero = int(np.count_nonzero(values))
    return {'estimate': float(np.mean(values)), 'ci95_percentile': interval(draws),
            'ci_bonferroni54_percentile': interval(draws, .05/54),
            'negative_pairs': int(sum(values < 0)), 'positive_pairs': int(sum(values > 0)),
            'zero_pairs': int(sum(values == 0)),
            'zero_nonzero_event_upper95': float(1-.05**(1/n)) if not nonzero else None,
            'zero_nonzero_event_upper97_5': float(1-.025**(1/n)) if not nonzero else None,
            'zero_nonzero_event_upper_bonferroni54': float(1-(.05/54)**(1/n)) if not nonzero else None}


def analyze(rows, resamples=50000, seed=20261021):
    index = index_rows(rows)
    outputs, paired = [], []
    for level in ('L1','L2','L3'):
        families = sorted({k[0] for k in index if k[1] == level})
        for family in families + ['pooled']:
            keys = sorted(k for k in index if k[1] == level and (family == 'pooled' or k[0] == family))
            for arm in ('R1','R2'):
                values = np.array([vector(index[k], arm) for k in keys])
                boot = bootstrap(values, [k[0] for k in keys], resamples, seed)
                out = {'level': level, 'family': family, 'contrast': arm+'-R0', 'n_pairs': len(keys),
                       'metrics': {name: describe(values[:,j], boot[:,j]) for j,name in enumerate(METRICS)}}
                for policy in ('current', 'legacy_admission'):
                    sub = out['metrics'][policy]
                    ref = [int(index[k]['R0']['terminal_success']) * (int(index[k]['R0']['qualification_legacy']['qualified']) if policy != 'current' else 1) for k in keys]
                    tx = [int(index[k][arm]['terminal_success']) * (int(index[k][arm]['qualification_legacy']['qualified']) if policy != 'current' else 1) for k in keys]
                    sub.update(ref_success=sum(ref), treatment_success=sum(tx),
                               both_success=sum(r and t for r,t in zip(ref,tx)),
                               both_failure=sum(not r and not t for r,t in zip(ref,tx)))
                    discordance = sub['positive_pairs'] + sub['negative_pairs']
                    sub['mcnemar_p'] = float(binomtest(sub['positive_pairs'],discordance,.5).pvalue) if discordance else 1.
                if family == 'pooled':
                    unstrat = bootstrap(values,[k[0] for k in keys],resamples,seed,'unstratified_instance')
                    by_seed = defaultdict(list)
                    for key,v in zip(keys,values):
                        by_seed[index[key]['R0']['seed']].append(v)
                    if not all(len(v)==len(families) for v in by_seed.values()):
                        raise ValueError('seed-cluster sensitivity requires complete family blocks')
                    seed_values = np.array([np.mean(by_seed[s],axis=0) for s in sorted(by_seed)])
                    seed_boot = bootstrap(seed_values,['one']*len(seed_values),resamples,seed)
                    weights = {}
                    fam_means = [values[np.array([k[0] == fam for k in keys])].mean(axis=0) for fam in families]
                    for weight in (0.,.25,.5,.75,1.):
                        weights[str(weight)] = dict(zip(METRICS,(weight*fam_means[0]+(1-weight)*fam_means[1]).tolist()))
                    out['pooling_sensitivity'] = {'fixed_families': families, 'first_family_weight_estimates':weights,
                        'unstratified_instance_ci95':{name: interval(unstrat[:,j]) for j,name in enumerate(METRICS)},
                        'shared_seed_cluster_n':len(seed_values),
                        'shared_seed_zero_event_upper95':{name:float(1-.05**(1/len(seed_values))) if not np.count_nonzero(seed_values[:,j]) else None for j,name in enumerate(METRICS)},
                        'shared_seed_cluster_ci95':{name:interval(seed_boot[:,j]) for j,name in enumerate(METRICS)}}
                    for key, vals in zip(keys,values):
                        item = dict(family=key[0],level=key[1],instance_id=key[2],seed=index[key]['R0']['seed'],contrast=arm+'-R0')
                        item.update(dict(zip(METRICS,vals.tolist())))
                        for a in ('R0',arm):
                            item[a+'_session_id'] = index[key][a]['session_id']
                            item[a+'_current'] = index[key][a]['terminal_success']
                            item[a+'_legacy_admitted'] = index[key][a]['qualification_legacy']['qualified']
                        paired.append(item)
                outputs.append(out)
    tests = sorted((o['metrics'][p]['mcnemar_p'], i,p) for i,o in enumerate(outputs) for p in ('current','legacy_admission'))
    running = 0.
    for rank,(p,i,policy) in enumerate(tests):
        running = max(running,min(1.,(len(tests)-rank)*p))
        outputs[i]['metrics'][policy]['mcnemar_holm36'] = running
    return outputs, paired


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w') as f:
        w = csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resamples',type=int,default=50000)
    parser.add_argument('--seed',type=int,default=20261021)
    parser.add_argument('--out',type=Path,default=HERE)
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(HERE):
        raise ValueError('outputs must remain inside assigned directory')
    out.mkdir(parents=True,exist_ok=True)
    raw = SOURCE/'runs/confirmatory/results.jsonl'
    before = digest(raw)
    rows = [json.loads(s) for s in raw.read_text().splitlines()]
    assert len(rows)==852
    assert Counter(r['kind'] for r in rows)=={'primary':768,'noise':64,'c0':20}
    assert len({r['session_id'] for r in rows})==852
    audits = []
    for row in rows:
        assert row['terminal_success'] in (0,1)
        if row['kind'] != 'c0':
            assert bool(row['terminal_success']) == (row['terminal']=='SUCCESS')
        candidate = SOURCE/'runs/confirmatory/sessions'/row['session_id']/'candidate.py'
        source = candidate.read_text()
        sha_match = digest(candidate)==row['source_sha256']
        fresh = qualify_source(source,'legacy')
        qualified_match = fresh['qualified'] == row['qualification_legacy']['qualified']
        reject_match = (not fresh['qualified']) == row['legacy_would_reject']
        assert sha_match and qualified_match and reject_match, row['session_id']
        audits.append({'session_id':row['session_id'],'source_sha256':digest(candidate),
                       'source_hash_match':sha_match,'legacy_admission_recomputed_match':qualified_match,
                       'legacy_rejection_flag_match':reject_match})
    contrasts,pairs = analyze(rows,args.resamples,args.seed)
    primary = [r for r in rows if r['kind']=='primary']
    cells = []
    for family in sorted({r['family'] for r in primary})+['pooled']:
        for level in ('L1','L2','L3'):
            for arm in ARMS:
                group = [r for r in primary if r['level']==level and r['arm']==arm and (family=='pooled' or r['family']==family)]
                success = sum(r['terminal_success'] for r in group)
                legacy = sum(r['terminal_success']*r['qualification_legacy']['qualified'] for r in group)
                cells.append(dict(family=family,level=level,arm=arm,n=len(group),current_success=success,
                                  legacy_admission_success=legacy,successes_removed=success-legacy,
                                  current_failure_headroom=len(group)-success))
    oi=original.primary_index(rows)
    reproduction={}
    for arm in ('R1','R2'):
        op,drop=original.collect_pairs(oi,'L3',None,arm)
        reproduction[arm]=original.contrast(op,drop)
    holm=original_stats.holm([(a,v['mcnemar']['p_value']) for a,v in reproduction.items()])
    assert all(v['equivalence']['status']=='EQUIVALENT_WITHIN_MARGIN' for v in reproduction.values())
    assert before==digest(raw)
    metadata = {'status':'EXPLORATORY_NO_NEW_EQUIVALENCE_DECISION','source_path':str(raw),'source_sha256':before,
        'rows':len(rows),'primary_rows':len(primary),'matched_instances':len(index_rows(rows)),
        'resamples':args.resamples,'seed':args.seed,'rng':'numpy default_rng PCG64',
        'versions':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__},
        'source_admission_rechecks':len(audits),'models':dict(Counter(r['provider_model'] for r in rows)),
        'kind_counts':dict(Counter(r['kind'] for r in rows)),
        'separate_controls':{'R4':{'n':64,'success':sum(r['terminal_success'] for r in rows if r['kind']=='noise')},
                             'C0':{'n':20,'correct_abstention':sum(r.get('c0_correct_abstention',0) for r in rows if r['kind']=='c0')}},
        'inputs':{str(p.relative_to(ROOT)):digest(p) for p in [raw,SOURCE/'H1R3_PREREGISTRATION.md',SOURCE/'h1r3_stats.py',SOURCE/'h1r3_analyze.py',SOURCE/'h1r3_contract.py',ROOT/'sp2027/paper/capability_revision_20261020/main_sections/04_capability.tex']},
        'main_bootstrap':'joint matched-instance resampling within fixed family strata, both outcomes and contrast changes retained in each draw',
        'multiplicity':'36 McNemar p values Holm-adjusted together; 54 main intervals have unadjusted 95% and Bonferroni54 percentile bounds; exploratory coverage only; sensitivity intervals unadjusted',
        'policy_change_definition':'(legacy treatment - legacy R0) - (current treatment - current R0); negative means legacy admission widens treatment disadvantage'}
    (out/'results.json').write_text(json.dumps({'metadata':metadata,'contrasts':contrasts,'cells':cells},indent=2)+'\n')
    (out/'preregistered_L3_reproduction.json').write_text(json.dumps({'contrasts':reproduction,'holm':holm,'note':'Original 20000 resamples/20261019 and decision code, unchanged.'},indent=2)+'\n')
    write_csv(out/'cells.csv',cells)
    write_csv(out/'paired_instances.csv',pairs)
    write_csv(out/'source_admission_audit.csv',audits)
    flat=[]
    for c in contrasts:
        for metric,result in c['metrics'].items():
            flat.append({**{k:c[k] for k in ('family','level','contrast','n_pairs')},'metric':metric,**result})
    write_csv(out/'contrasts.csv',flat)
    print(json.dumps({'status':'PASS','raw_sha256':before,'source_rechecks':len(audits),'primary_rows':len(primary),'paired_rows':len(pairs),'contrasts':len(contrasts),'metrics':len(flat),'seed':args.seed,'resamples':args.resamples}))

if __name__=='__main__':
    main()
