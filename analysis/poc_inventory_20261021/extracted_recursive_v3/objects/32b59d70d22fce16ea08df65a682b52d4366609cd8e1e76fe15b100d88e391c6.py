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

def get_footprint():
    resp = http_request("GET", "/footprint")
    if resp['status'] != 200:
        return None
    body = base64.b64decode(resp['body_b64'])
    data = json.loads(body)
    pages = data['pages']
    # Convert to table -> set of indices
    table_indices = {0: set(), 1: set(), 2: set(), 3: set()}
    for p in pages:
        table = p // 256
        index = p % 256
        if table in table_indices:
            table_indices[table].add(index)
    return table_indices

# Test: vary byte 0 through all 256 values, others fixed at 0
print("Testing byte position 0...", file=sys.stderr)
all_table_indices = {0: set(), 1: set(), 2: set(), 3: set()}
index_map = {0: {}, 1: {}, 2: {}, 3: {}}  # table -> {plaintext_byte: index}

for v in range(256):
    plaintext = bytes([v] + [0]*15)
    resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
    if resp['status'] != 200:
        print(f"Encrypt failed for v={v}", file=sys.stderr)
        continue
    ti = get_footprint()
    if ti is None:
        continue
    for t in range(4):
        all_table_indices[t].update(ti[t])
        # Record the index for this plaintext value (should be one per table per encryption)
        if len(ti[t]) == 1:
            idx = next(iter(ti[t]))
            index_map[t][v] = idx
    if v % 32 == 0:
        print(f"  Progress: {v}/256", file=sys.stderr)

print("\nResults for byte position 0:", file=sys.stderr)
for t in range(4):
    print(f"  Table {t}: {len(all_table_indices[t])} distinct indices", file=sys.stderr)
    if len(index_map[t]) > 0:
        # Check if index = plaintext ^ key_byte (i.e., index ^ plaintext is constant)
        key_candidates = set()
        for v, idx in index_map[t].items():
            key_candidates.add(v ^ idx)
        print(f"    Key candidates: {key_candidates}", file=sys.stderr)
        if len(key_candidates) == 1:
            print(f"    *** FOUND KEY BYTE: {list(key_candidates)[0]:02x} ***", file=sys.stderr)