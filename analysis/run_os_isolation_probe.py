#!/usr/bin/env python3
import json, os, pathlib, subprocess, tempfile
out=pathlib.Path('/mnt/nvme5/ACTS-Attack/sp2027/analysis/contract_sound_replacement_readiness_20261018')
case=out/'os_isolation_probe_trusted'
case.mkdir(parents=True, exist_ok=True)
(case/'probe.py').write_text('''import json, socket\nresult={}\ntry:\n open("/etc/acts_contract_sound_probe","w").write("x")\n result["host_write"]="UNEXPECTED_SUCCESS"\nexcept Exception as e: result["host_write"]=type(e).__name__\ntry:\n open("case-write.txt","w").write("ok")\n result["case_write"]="SUCCESS"\nexcept Exception as e: result["case_write"]=type(e).__name__\ntry:\n s=socket.socket(); s.settimeout(0.2); s.connect(("127.0.0.1",9)); result["network"]="UNEXPECTED_SUCCESS"\nexcept Exception as e: result["network"]=type(e).__name__\nprint(json.dumps(result,sort_keys=True))\n''')
cmd=['bwrap','--die-with-parent','--unshare-net','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--ro-bind','/bin','/bin','--ro-bind','/etc','/etc','--proc','/proc','--dev','/dev','--bind',str(case),str(case),'--chdir',str(case),'--','/usr/bin/python3','-I',str(case/'probe.py')]
proc=subprocess.run(cmd,capture_output=True,text=True,check=False)
(case/'stdout.txt').write_text(proc.stdout); (case/'stderr.txt').write_text(proc.stderr)
print(json.dumps({'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'case_write':(case/'case-write.txt').exists()},sort_keys=True))
if proc.returncode != 0: raise SystemExit(proc.returncode)
result=json.loads(proc.stdout.strip().splitlines()[-1])
assert result['host_write'] != 'UNEXPECTED_SUCCESS'
assert result['case_write'] == 'SUCCESS'
assert result['network'] != 'UNEXPECTED_SUCCESS'
assert not pathlib.Path('/etc/acts_contract_sound_probe').exists()
(case/'OS_ISOLATION_RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')