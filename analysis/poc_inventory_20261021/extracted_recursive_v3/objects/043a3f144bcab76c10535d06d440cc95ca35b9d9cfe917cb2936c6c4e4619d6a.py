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

# Let's first understand the structure better
# For key byte 0 (table 0), vary p[0] from 0-255, keep others fixed
fixed_bytes = bytes([0xAA] * 16)  # arbitrary fixed value

print("Collecting footprints for key byte 0...", file=sys.stderr)
footprints = []
for p0 in range(256):
    pt = bytes([p0]) + fixed_bytes[1:]
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    resp = http_request("GET", "/footprint")
    if resp.get('status') == 200:
        body = base64.b64decode(resp['body_b64'])
        footprint = json.loads(body)
        pages = set(footprint.get('pages', []))
        footprints.append(pages)
    else:
        print(f"Error at p0={p0}: {resp}", file=sys.stderr)
        footprints.append(set())
    if p0 % 32 == 0:
        print(f"  Progress: {p0}/256", file=sys.stderr)

print(f"Collected {len(footprints)} footprints", file=sys.stderr)

# Table for byte 0 is table 0 (pages 0-255)
table = 0
# For each key guess, count how many footprints contain the predicted page
best_count = -1
best_guess = -1
counts = []
for k_guess in range(256):
    count = 0
    for p0 in range(256):
        predicted_page = table * 256 + (p0 ^ k_guess)
        if predicted_page in footprints[p0]:
            count += 1
    counts.append(count)
    if count > best_count:
        best_count = count
        best_guess = k_guess
    if count == 256:
        print(f"Key byte 0 guess {k_guess}: count={count} (PERFECT)", file=sys.stderr)

print(f"Best guess for key byte 0: {best_guess} (count={best_count})", file=sys.stderr)
print(f"All counts: {counts}", file=sys.stderr)

# Let's also check the distribution
from collections import Counter
cnt = Counter(counts)
print(f"Count distribution: {sorted(cnt.items())}", file=sys.stderr)