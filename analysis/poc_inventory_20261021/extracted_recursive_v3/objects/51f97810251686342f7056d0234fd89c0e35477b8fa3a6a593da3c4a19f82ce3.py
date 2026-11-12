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
    response = json.loads(sys.stdin.readline())
    return response

# First, let's understand the varying pages for byte 0
print("Testing byte 0 variation (all 256 values):", file=sys.stderr)
footprints = {}
for val in range(256):
    pt = bytes([val] + [0]*15)
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    resp = http_request("GET", "/footprint")
    if resp["status"] == 200:
        body = base64.b64decode(resp["body_b64"])
        footprint = json.loads(body)
        footprints[val] = set(footprint['pages'])
    else:
        print(f"  Error at val={val}: {resp}", file=sys.stderr)
        footprints[val] = set()

# Find pages that vary
all_pages = set()
for s in footprints.values():
    all_pages.update(s)

print(f"Total distinct pages across all 256 queries: {len(all_pages)}", file=sys.stderr)

# For each page, count how many queries it appears in
page_counts = Counter()
for val, pages in footprints.items():
    for p in pages:
        page_counts[p] += 1

# Pages that appear in exactly 1 query are the varying ones (first round for byte 0)
varying_pages = [p for p, c in page_counts.items() if c == 1]
constant_pages = [p for p, c in page_counts.items() if c == 256]
partial_pages = [p for p, c in page_counts.items() if 1 < c < 256]

print(f"Varying pages (count=1): {len(varying_pages)}", file=sys.stderr)
print(f"Constant pages (count=256): {len(constant_pages)}", file=sys.stderr)
print(f"Partial pages (1<count<256): {len(partial_pages)}", file=sys.stderr)

if varying_pages:
    varying_pages.sort()
    print(f"First 10 varying pages: {varying_pages[:10]}", file=sys.stderr)
    # Decode table and index
    for p in varying_pages[:10]:
        table = p // 256
        index = p % 256
        print(f"  Page {p} -> table={table}, index={index}", file=sys.stderr)
    
    # Map each val to its varying page
    val_to_varying_page = {}
    for val, pages in footprints.items():
        varying = pages & set(varying_pages)
        if len(varying) == 1:
            val_to_varying_page[val] = varying.pop()
        else:
            print(f"  WARNING: val={val} has {len(varying)} varying pages: {varying}", file=sys.stderr)
    
    print(f"\nMapping val -> page:", file=sys.stderr)
    key_candidates = []
    for val in range(256):
        if val in val_to_varying_page:
            page = val_to_varying_page[val]
            index = page % 256
            table = page // 256
            key_byte = val ^ index
            key_candidates.append(key_byte)
            if val < 10:
                print(f"  val={val:3d} -> page={page} (table={table}, index={index}) -> key_byte={key_byte:02x}", file=sys.stderr)
    
    if key_candidates:
        most_common = Counter(key_candidates).most_common(1)[0]
        print(f"\nKey byte 0 candidates: {Counter(key_candidates).most_common(5)}", file=sys.stderr)
        print(f"Recovered key byte 0: {most_common[0]:02x} (count={most_common[1]})", file=sys.stderr)

# Now do the same for all 16 bytes
key_bytes = [None] * 16

for byte_pos in range(16):
    print(f"\n=== Probing byte position {byte_pos} ===", file=sys.stderr)
    footprints = {}
    
    for val in range(256):
        pt = [0] * 16
        pt[byte_pos] = val
        pt = bytes(pt)
        resp = http_request("POST", "/encrypt", body_hex=pt.hex())
        resp = http_request("GET", "/footprint")
        if resp["status"] == 200:
            body = base64.b64decode(resp["body_b64"])
            footprint = json.loads(body)
            footprints[val] = set(footprint['pages'])
        else:
            print(f"  Error at val={val}: {resp}", file=sys.stderr)
            footprints[val] = set()
    
    # Count page frequencies
    page_counts = Counter()
    for pages in footprints.values():
        for p in pages:
            page_counts[p] += 1
    
    # Varying pages appear exactly once
    varying_pages = [p for p, c in page_counts.items() if c == 1]
    print(f"  Varying pages: {len(varying_pages)}", file=sys.stderr)
    
    if len(varying_pages) != 256:
        print(f"  WARNING: Expected 256 varying pages, got {len(varying_pages)}", file=sys.stderr)
        # Maybe some pages appear 0 times? No, each query should have one varying page.
        # Let's check pages with count < 256
        candidate_pages = [p for p, c in page_counts.items() if c < 256]
        print(f"  Pages with count < 256: {len(candidate_pages)}", file=sys.stderr)
        varying_pages = candidate_pages
    
    # Map each val to its varying page
    val_to_page = {}
    varying_set = set(varying_pages)
    for val, pages in footprints.items():
        varying = pages & varying_set
        if len(varying) == 1:
            val_to_page[val] = varying.pop()
        elif len(varying) > 1:
            # Pick the one that makes sense (same table)
            tables = [p // 256 for p in varying]
            if len(set(tables)) == 1:
                # All same table, pick any
                val_to_page[val] = varying.pop()
            else:
                print(f"  WARNING: val={val} has varying pages from different tables: {varying}", file=sys.stderr)
        else:
            print(f"  WARNING: val={val} has no varying page", file=sys.stderr)
    
    # Compute key byte candidates
    key_candidates = []
    for val, page in val_to_page.items():
        index = page % 256
        table = page // 256
        key_byte = val ^ index
        key_candidates.append(key_byte)
    
    if key_candidates:
        most_common = Counter(key_candidates).most_common(1)[0]
        key_bytes[byte_pos] = most_common[0]
        print(f"  Recovered key byte {byte_pos}: {key_bytes[byte_pos]:02x} (count={most_common[1]}/{len(key_candidates)})", file=sys.stderr)
        # Verify consistency
        if most_common[1] != len(key_candidates):
            print(f"  WARNING: Not all candidates agree! Distribution: {Counter(key_candidates).most_common()}", file=sys.stderr)
    else:
        print(f"  ERROR: No key candidates for byte {byte_pos}", file=sys.stderr)
        key_bytes[byte_pos] = 0

print(f"\n=== Final key: {bytes(key_bytes).hex()} ===", file=sys.stderr)
print(f"CLAIM:{{\"key_hex\": \"{bytes(key_bytes).hex()}\"}}")