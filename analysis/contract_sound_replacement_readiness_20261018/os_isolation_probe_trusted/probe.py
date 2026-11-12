import json, socket
result={}
try:
 open("/etc/acts_contract_sound_probe","w").write("x")
 result["host_write"]="UNEXPECTED_SUCCESS"
except Exception as e: result["host_write"]=type(e).__name__
try:
 open("case-write.txt","w").write("ok")
 result["case_write"]="SUCCESS"
except Exception as e: result["case_write"]=type(e).__name__
try:
 s=socket.socket(); s.settimeout(0.2); s.connect(("127.0.0.1",9)); result["network"]="UNEXPECTED_SUCCESS"
except Exception as e: result["network"]=type(e).__name__
print(json.dumps(result,sort_keys=True))
