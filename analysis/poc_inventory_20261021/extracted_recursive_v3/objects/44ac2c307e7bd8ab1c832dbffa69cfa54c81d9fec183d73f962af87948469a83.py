import sys
import json
import base64

def http_request(method, path, body_hex=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    if headers is not None:
        req["http"]["headers"] = headers
    print(json.dumps(req), flush=True)
    response = json.loads(sys.stdin.readline())
    return response

def encrypt_and_get_footprint(plaintext_bytes):
    resp = http_request("POST", "/encrypt", body_hex=plaintext_bytes.hex())
    if resp["status"] != 200:
        raise Exception(f"Encrypt failed: {resp}")
    resp2 = http_request("GET", "/footprint")
    if resp2["status"] != 200:
        raise Exception(f"Footprint failed: {resp2}")
    fp = json.loads(base64.b64decode(resp2["body_b64"]).decode())
    return set(fp["pages"])

# Probe key byte 0 (table 0)
print("Probing key byte 0...", file=sys.stderr)
fixed_template = bytes([0] * 16)
footprints = []
for v in range(256):
    pt = bytearray(fixed_template)
    pt[0] = v
    pages = encrypt_and_get_footprint(bytes(pt))
    footprints.append(pages)
    if v % 64 == 0:
        print(f"  v={v} done", file=sys.stderr)

# For each candidate key byte k (0-255), check how many v have page (v XOR k) in table 0
best_k = None
best_count = -1
for k in range(256):
    count = 0
    for v in range(256):
        page = 0 * 256 + (v ^ k)  # table 0, index = v XOR k
        if page in footprints[v]:
            count += 1
    if count > best_count:
        best_count = count
        best_k = k
    if count == 256:
        print(f"Found key byte 0 = {k} (0x{k:02x}) with perfect match!", file=sys.stderr)
        break

print(f"Best key byte 0: {best_k} (0x{best_k:02x}) with count {best_count}/256", file=sys.stderr)

# Show top candidates
candidates = []
for k in range(256):
    count = 0
    for v in range(256):
        page = 0 * 256 + (v ^ k)
        if page in footprints[v]:
            count += 1
    candidates.append((count, k))
candidates.sort(reverse=True)
print(f"Top 10 candidates: {candidates[:10]}", file=sys.stderr)