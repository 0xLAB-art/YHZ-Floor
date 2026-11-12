import sys
import json
import base64
from collections import Counter

def http_request(method, path, body_hex=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    if headers is not None:
        req["http"]["headers"] = headers
    print(json.dumps(req), flush=True)
    line = sys.stdin.readline()
    if not line.strip():
        return {"status": 0, "body_b64": "", "content_type": ""}
    return json.loads(line)

print("=== Starting key recovery ===", file=sys.stderr, flush=True)

# Quick test
pt = bytes([0] * 16)
resp = http_request("POST", "/encrypt", body_hex=pt.hex())
print(f"Test encrypt: {resp.get('status')}", file=sys.stderr, flush=True)
resp = http_request("GET", "/footprint")
print(f"Test footprint: {resp.get('status')}", file=sys.stderr, flush=True)

key_bytes = [0] * 16

for byte_pos in range(16):
    print(f"\n=== Probing byte position {byte_pos} ===", file=sys.stderr, flush=True)
    footprints = {}
    
    for val in range(256):
        pt = [0] * 16
        pt[byte_pos] = val
        pt = bytes(pt)
        resp = http_request("POST", "/encrypt", body_hex=pt.hex())
        if resp.get("status") != 200:
            print(f"  Encrypt failed at val={val}: {resp}", file=sys.stderr, flush=True)
            continue
        resp = http_request("GET", "/footprint")
        if resp.get("status") != 200:
            print(f"  Footprint failed at val={val}: {resp}", file=sys.stderr, flush=True)
            continue
        body = base64.b64decode(resp["body_b64"])
        footprint = json.loads(body)
        footprints[val] = set(footprint['pages'])
    
    print(f"  Got {len(footprints)} footprints", file=sys.stderr, flush=True)
    
    if len(footprints) == 0:
        key_bytes[byte_pos] = 0
        continue
    
    # Count page frequencies
    page_counts = Counter()
    for pages in footprints.values():
        for p in pages:
            page_counts[p] += 1
    
    # Varying pages appear exactly once
    varying_pages = [p for p, c in page_counts.items() if c == 1]
    print(f"  Varying pages: {len(varying_pages)}", file=sys.stderr, flush=True)
    
    if len(varying_pages) != 256:
        print(f"  WARNING: Expected 256 varying pages, got {len(varying_pages)}", file=sys.stderr, flush=True)
        varying_pages = [p for p, c in page_counts.items() if c < len(footprints)]
        print(f"  Using pages with count < {len(footprints)}: {len(varying_pages)}", file=sys.stderr, flush=True)
    
    varying_set = set(varying_pages)
    
    # Map each val to its varying page
    val_to_page = {}
    for val, pages in footprints.items():
        varying = pages & varying_set
        if len(varying) == 1:
            val_to_page[val] = varying.pop()
        elif len(varying) > 1:
            indices = [p % 256 for p in varying]
            if len(set(indices)) == 1:
                val_to_page[val] = varying.pop()
            else:
                val_to_page[val] = min(varying)
        else:
            pass  # skip
    
    # Compute key byte
    key_candidates = []
    for val, page in val_to_page.items():
        index = page % 256
        key_byte = val ^ index
        key_candidates.append(key_byte)
    
    if key_candidates:
        most_common = Counter(key_candidates).most_common(1)[0]
        key_bytes[byte_pos] = most_common[0]
        print(f"  Recovered key byte {byte_pos}: {key_bytes[byte_pos]:02x} (count={most_common[1]}/{len(key_candidates)})", file=sys.stderr, flush=True)
    else:
        print(f"  ERROR: No candidates for byte {byte_pos}", file=sys.stderr, flush=True)
        key_bytes[byte_pos] = 0

key_hex = bytes(key_bytes).hex()
print(f"\n=== Final key: {key_hex} ===", file=sys.stderr, flush=True)
print(f"CLAIM:{{\"key_hex\": \"{key_hex}\"}}", flush=True)