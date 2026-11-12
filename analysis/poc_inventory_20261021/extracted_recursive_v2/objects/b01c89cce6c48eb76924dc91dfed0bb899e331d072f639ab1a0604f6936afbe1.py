
import json, sys, base64

def call(path, data=None):
    req = {"method": "POST" if data is not None else "GET", "path": path}
    if data is not None:
        req["body_hex"] = data.hex()
    print(json.dumps({"http": req}), flush=True)
    resp = json.loads(sys.stdin.readline())
    return base64.b64decode(resp.get("body_b64", ""))

def footprint(pt):
    call("/encrypt", pt)
    fp = json.loads(call("/footprint"))
    return frozenset(fp["pages"])

def table_of(page): return page // 256
def index_of(page): return page % 256

key = bytearray(16)
for i in range(16):
    t_i = i % 4
    per_v = {}
    for v in range(256):
        pt = bytearray(16)
        pt[i] = v
        per_v[v] = footprint(bytes(pt))
    common = frozenset.intersection(*per_v.values())
    votes = {}
    for v in range(256):
        for pg in (per_v[v] - common):
            if table_of(pg) == t_i:
                votes[v ^ index_of(pg)] = votes.get(v ^ index_of(pg), 0) + 1
    key[i] = max(votes.items(), key=lambda kv: kv[1])[0]

print("CLAIM:" + json.dumps({"key_hex": bytes(key).hex()}))
