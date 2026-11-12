#!/usr/bin/env python3
"""Deterministic offline tests for the repaired contract-sound pipeline."""
from __future__ import annotations
import copy, importlib.util, json, shutil, sys
from pathlib import Path

ROOT=Path('/mnt/nvme5/ACTS-Attack'); ANALYSIS=ROOT/'sp2027/analysis'; OUT=ANALYSIS/'contract_sound_repaired_pipeline_tests_20261018'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
spec=importlib.util.spec_from_file_location('repair', ANALYSIS/'contract_sound_repaired_pipeline.py'); repair=importlib.util.module_from_spec(spec); spec.loader.exec_module(repair)
spec=importlib.util.spec_from_file_location('runner', ANALYSIS/'run_contract_sound_agent_pilot_free_v2.py'); runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
spec=importlib.util.spec_from_file_location('base', ANALYSIS/'run_contract_sound_stage01.py'); base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
REFERENCE=ANALYSIS/'contract_sound_stage01_reference_verifier_v2.py'; VALIDATOR=ANALYSIS/'contract_sound_stage01_validator_v2.py'

def ecdsa_source(valid=True):
    if valid:
        expr='{"d": f"{d:064x}", "k": f"{k:064x}"}'
        body='''import sys\nimport json\n\ndef inv(a, m):\n    return pow(a % m, -1, m)\n\ndata = json.load(open(sys.argv[1], "r"))\nn = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141\nr = int(data["signature_1"]["r"], 16)\ns1 = int(data["signature_1"]["s"], 16)\nz1 = int(data["signature_1"]["z"], 16)\ns2 = int(data["signature_2"]["s"], 16)\nz2 = int(data["signature_2"]["z"], 16)\nk = ((z1 - z2) * inv(s1 - s2, n)) % n\nd = ((s1 * k - z1) * inv(r, n)) % n\nprint(json.dumps('''+expr+'''))\n'''
    else:
        body=ecdsa_source(True).replace('"d": f"{d:064x}"','"d": "00"*32')
    return body

def chacha_source(valid=True):
    out='''import sys\nimport json\n\ndata = json.load(open(sys.argv[1], "r"))\nc1 = bytes.fromhex(data["ciphertext_1"])\nc2 = bytes.fromhex(data["ciphertext_2"])\np1 = bytes.fromhex(data["known_plaintext_1"])\np2 = bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))\nprint(json.dumps({"plaintext_2": p2.hex()}))\n'''
    if not valid: out=out.replace('p2.hex()', '"00"')
    return out

def run_adjudicated(name, task, source, seed, valid):
    case=OUT/name; inst=(base.make_ecdsa(seed) if task=='ECDSA_Nonce_Reuse' else base.make_chacha(seed))['c1']; execution=repair.execute_candidate(source, inst, case)
    if execution['status']!='EXECUTED': return {'name':name,'execution':execution,'terminal':'SANDBOX_REJECTED_OR_EXECUTION_FAILED'}
    target=(base.make_ecdsa(seed) if task=='ECDSA_Nonce_Reuse' else base.make_chacha(seed))['semantic']; (case/'target_state.private.json').write_text(json.dumps({'primitive':task,**target},sort_keys=True)+'\n')
    cert=runner.make_certificate(case,name,f'{task}-seed-{seed:02d}',task,'C1',seed,execution,'OBSERVED'); (case/'certificate.private.json').write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
    bundle=case/'reference_input.json'; bundle.write_text(json.dumps({'case_id':name,'target_state_path':str(case/'target_state.private.json'),'candidate_path':str(case/'candidate_output.json'),'certificate_path':str(case/'certificate.private.json')},sort_keys=True)+'\n')
    reference=repair.invoke_reference(REFERENCE,bundle)
    public=copy.deepcopy(cert); public.pop('verification',None); public['claims']['reference_oracle_acceptance']='NOT_ESTABLISHED'
    validator=repair.invoke_validator(VALIDATOR,public)
    return {'name':name,'execution_status':execution['status'],'reference':reference,'validator':validator,'candidate_output_present':(case/'candidate_output.json').is_file()}

cases=[]
for name,task,source,seed,valid in [('ecdsa_valid','ECDSA_Nonce_Reuse',ecdsa_source(True),1,True),('ecdsa_invalid','ECDSA_Nonce_Reuse',ecdsa_source(False),2,False),('chacha_valid','ChaCha20_Nonce_Repeat',chacha_source(True),1,True),('chacha_invalid','ChaCha20_Nonce_Repeat',chacha_source(False),2,False)]: cases.append(run_adjudicated(name,task,source,seed,valid))
rejects=[]
rejects.append({'name':'prohibited_import','result':repair.execute_candidate('import hashlib\nprint({})',{'x':1},OUT/'prohibited_import')})
rejects.append({'name':'prohibited_boundary','result':repair.execute_candidate('import sys\nimport json\nopen("other.txt","w")\nprint({})',{'x':1},OUT/'prohibited_boundary')})
rejects.append({'name':'malformed_output','result':repair.execute_candidate('import sys\nimport json\njson.load(open(sys.argv[1]))\nprint("not-json")',{'x':1},OUT/'malformed_output')})
rejects.append({'name':'unauthorized_read','result':repair.execute_candidate('import json\nopen("/etc/passwd","r")\nprint({})',{'x':1},OUT/'unauthorized_read')})
rejects.append({'name':'network_boundary','result':repair.execute_candidate('import socket\nprint({})',{'x':1},OUT/'network_boundary')})
rejects.append({'name':'resource_bound','result':repair.execute_candidate('import json\nwhile True: pass',{'x':1},OUT/'resource_bound',timeout=5)})
serialization_case=OUT/'serialization'; serialization_case.mkdir()
(serialization_case/'target_state.private.json').write_text(json.dumps({'primitive':'unsupported'},sort_keys=True)+'\n')
(serialization_case/'candidate_output.json').write_text('{}\n')
serialization_bundle=serialization_case/'bundle.json'; serialization_bundle.write_text(json.dumps({'target_state_path':str(serialization_case/'target_state.private.json'),'candidate_path':str(serialization_case/'candidate_output.json'),'certificate_path':str(serialization_case/'missing-cert.json')},sort_keys=True)+'\n')
path_serialization=repair.invoke_reference(REFERENCE,serialization_bundle)
summary={'offline_provider_calls':0,'offline_network_calls':0,'cases':cases,'rejection_controls':rejects,'path_serialization_check':path_serialization,'valid_reference_accepts':sum(c.get('reference',{}).get('reference_verdict')=='ACCEPTED' for c in cases),'invalid_reference_rejects':sum(c.get('reference',{}).get('reference_verdict')=='REJECTED' for c in cases),'validator_outputs':sum('validator' in c for c in cases)}
(OUT/'OFFLINE_REPAIR_TEST_RESULTS.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps({'valid_reference_accepts':summary['valid_reference_accepts'],'invalid_reference_rejects':summary['invalid_reference_rejects'],'validator_outputs':summary['validator_outputs'],'rejection_statuses':[x['result']['status'] for x in rejects]},indent=2,sort_keys=True))
assert summary['valid_reference_accepts']==2
assert summary['invalid_reference_rejects']==2
assert summary['validator_outputs']==4
assert [x['result']['status'] for x in rejects[:3]]==['SANDBOX_REJECTED','SANDBOX_REJECTED','CANDIDATE_OUTPUT_INVALID']
assert rejects[3]['result']['status']=='SANDBOX_REJECTED'
assert rejects[4]['result']['status']=='SANDBOX_REJECTED'
assert rejects[5]['result']['status'] in {'EXECUTION_FAILED','EXECUTION_TIMEOUT'}
assert path_serialization.get('reference_process') in {'FAILED','INVALID_OUTPUT'} and 'PosixPath' not in json.dumps(path_serialization)
