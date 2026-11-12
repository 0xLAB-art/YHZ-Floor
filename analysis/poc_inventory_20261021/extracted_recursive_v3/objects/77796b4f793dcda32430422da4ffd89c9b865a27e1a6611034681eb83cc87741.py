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

# Test: probe key byte 0 with all 256 values, others fixed to 0
print("Probing key byte 0...", file=sys.stderr)
fixed_template = bytes([0] * 16)
footprints = []
for v in range(256):
    pt = bytearray(fixed_template)
    pt[0] = v
    pages = encrypt_and_get_footprint(bytes(pt))
    footprints.append(pages)

# Count how many times each page appears
page_counts = {}
for fp in footprints:
    for p in fp:
        page_counts[p] = page_counts.get(p, 0) + 1

# Distribution of counts
count_dist = {}
for p, count in page_counts.items():
    count_dist[count] = count_dist.get(count, 0) + 1

print(f"Count distribution: {sorted(count_dist.items())}", file=sys.stderr)

# Pages that appear in all 256 footprints
constant_pages = [p for p, count in page_counts.items() if count == 256]
print(f"Constant pages (256): {len(constant_pages)}", file=sys.stderr)

# Let's look at pages with count != 256
varying = [(p, c) for p, c in page_counts.items() if c != 256]
print(f"Varying pages count: {len(varying)}", file=sys.stderr)

# Group by table
table_pages = {}
for p, c in varying:
    t = p // 256
    if t not in table_pages:
        table_pages[t] = []
    table_pages[t].append((p, c))

for t in sorted(table_pages.keys()):
    pages = table_pages[t]
    print(f"Table {t}: {len(pages)} pages, counts: {sorted(set(c for _, c in pages))}", file=sys.stderr)
    # Show first few
    for p, c in sorted(pages)[:10]:
        print(f"  page {p} (idx {p%256}): count={c}", file=sys.stderr)

# The first round uses 4 tables (T0, T1, T2, T3) for the 16 bytes
# Byte 0 uses T0, byte 1 uses T1, byte 2 uses T2, byte 3 uses T3, byte 4 uses T0, etc.
# So for byte 0, the first-round table is T0 (table 0)
# Let's check table 0 pages
if 0 in table_pages:
    print("\nTable 0 pages:", file=sys.stderr)
    for p, c in sorted(table_pages[0]):
        print(f"  page {p} (idx {p%256}): count={c}", file=sys.stderr)