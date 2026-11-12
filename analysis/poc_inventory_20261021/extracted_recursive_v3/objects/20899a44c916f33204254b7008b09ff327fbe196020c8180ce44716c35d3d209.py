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
    table_indices = {0: [], 1: [], 2: [], 3: []}
    for p in pages:
        table = p // 256
        index = p % 256
        if table in table_indices:
            table_indices[table].append(index)
    return table_indices

# First, identify which table corresponds to which byte position
# For byte position 0, vary it and see which table gets 256 distinct indices
print("Identifying table for byte position 0...", file=sys.stderr)
freq = {0: {}, 1: {}, 2: {}, 3: {}}
for t in range(4):
    for i in range(256):
        freq[t][i] = 0

for v in range(256):
    plaintext = bytes([v] + [0]*15)
    resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
    if resp['status'] != 200:
        continue
    ti = get_footprint()
    if ti is None:
        continue
    for t in range(4):
        for idx in ti[t]:
            freq[t][idx] += 1

for t in range(4):
    count1 = sum(1 for c in freq[t].values() if c == 1)
    print(f"  Table {t}: indices with count=1: {count1}", file=sys.stderr)

# Now recover all 16 key bytes
key_bytes = [0] * 16

for byte_pos in range(16):
    print(f"\nRecovering key byte {byte_pos}...", file=sys.stderr)
    
    # First, find which table this byte affects
    freq = {0: {}, 1: {}, 2: {}, 3: {}}
    for t in range(4):
        for i in range(256):
            freq[t][i] = 0
    
    # Also store the index for each plaintext value per table
    index_map = {0: {}, 1: {}, 2: {}, 3: {}}
    
    for v in range(256):
        pt = [0] * 16
        pt[byte_pos] = v
        plaintext = bytes(pt)
        resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
        if resp['status'] != 200:
            continue
        ti = get_footprint()
        if ti is None:
            continue
        for t in range(4):
            for idx in ti[t]:
                freq[t][idx] += 1
            # Store the first index seen for this value in this table
            if len(ti[t]) > 0 and v not in index_map[t]:
                index_map[t][v] = ti[t][0]
    
    # Find the table with 256 unique indices (count=1)
    target_table = None
    for t in range(4):
        count1 = sum(1 for c in freq[t].values() if c == 1)
        if count1 == 256:
            target_table = t
            break
    
    if target_table is None:
        print(f"  ERROR: Could not identify table for byte {byte_pos}", file=sys.stderr)
        continue
    
    print(f"  Byte {byte_pos} -> Table {target_table}", file=sys.stderr)
    
    # Now find key byte: index = plaintext_byte ^ key_byte
    # So key_byte = plaintext_byte ^ index
    key_candidates = set()
    for v in range(256):
        if v in index_map[target_table]:
            idx = index_map[target_table][v]
            key_candidates.add(v ^ idx)
    
    if len(key_candidates) == 1:
        key_byte = list(key_candidates)[0]
        key_bytes[byte_pos] = key_byte
        print(f"  Key byte {byte_pos} = {key_byte:02x}", file=sys.stderr)
    else:
        print(f"  ERROR: Multiple key candidates: {key_candidates}", file=sys.stderr)
        # Try to find the most consistent one
        # Count frequency of each candidate
        candidate_counts = {}
        for v in range(256):
            if v in index_map[target_table]:
                idx = index_map[target_table][v]
                cand = v ^ idx
                candidate_counts[cand] = candidate_counts.get(cand, 0) + 1
        best = max(candidate_counts.items(), key=lambda x: x[1])
        key_bytes[byte_pos] = best[0]
        print(f"  Using most frequent: {best[0]:02x} (count={best[1]})", file=sys.stderr)

key_hex = ''.join(f'{b:02x}' for b in key_bytes)
print(f"\nRecovered key: {key_hex}", file=sys.stderr)
print(f"CLAIM:{{\"key_hex\": \"{key_hex}\"}}")