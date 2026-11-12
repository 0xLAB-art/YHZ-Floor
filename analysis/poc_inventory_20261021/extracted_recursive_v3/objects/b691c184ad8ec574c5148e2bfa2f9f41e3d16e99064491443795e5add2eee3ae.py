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
    line = sys.stdin.readline()
    if not line:
        print("ERROR: Empty response from harness", file=sys.stderr)
        sys.exit(1)
    print(f"DEBUG: Got response line: {line[:200]}", file=sys.stderr)
    try:
        response = json.loads(line)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}", file=sys.stderr)
        print(f"Line was: {repr(line)}", file=sys.stderr)
        sys.exit(1)
    return response

# First, let's test the service with a simple encryption
plaintext = bytes([0] * 16)
print("Sending first encrypt request...", file=sys.stderr)
resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
print(f"Encrypt response: {resp}", file=sys.stderr)

# Get footprint
print("Getting footprint...", file=sys.stderr)
resp = http_request("GET", "/footprint")
print(f"Footprint response: {resp}", file=sys.stderr)

if resp["status"] == 200:
    body = base64.b64decode(resp["body_b64"])
    fp = json.loads(body)
    print(f"First footprint: {fp}", file=sys.stderr)

# Now let's understand the T-table structure
# Page = table * 256 + index
# There are 4 T-tables (T0, T1, T2, T3) each with 256 entries
# Each entry is on a separate 4KiB page
# So pages 0-255 = T0, 256-511 = T1, 512-767 = T2, 768-1023 = T3

def get_footprint_for_pt(pt):
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    if resp["status"] != 200:
        print(f"Encrypt failed: {resp}", file=sys.stderr)
        return None
    resp = http_request("GET", "/footprint")
    if resp["status"] == 200:
        body = base64.b64decode(resp["body_b64"])
        return json.loads(body)
    return None

# Test byte 0 (position 0) - this should use T0 table (pages 0-255)
print("\nProbing byte 0:", file=sys.stderr)
footprints_byte0 = {}
for val in range(256):
    pt = bytes([val]) + bytes([0] * 15)
    fp = get_footprint_for_pt(pt)
    if fp:
        pages = tuple(sorted(fp["pages"]))
        footprints_byte0[val] = pages
    if val % 32 == 0:
        print(f"  Progress: {val}/256", file=sys.stderr)

# Check how many unique footprints we get
unique_fps = set(footprints_byte0.values())
print(f"Unique footprints for byte 0: {len(unique_fps)}", file=sys.stderr)
for fp in sorted(unique_fps):
    print(f"  {fp}", file=sys.stderr)

# The key insight: for a fixed key byte k0, the index into T0 is pt[0] ^ k0
# So as we vary pt[0] from 0-255, we access T0[pt[0] ^ k0] which is all 256 entries of T0
# But wait - the footprint shows DISTINCT pages touched during the ENTIRE encryption
# First round has 16 T-table lookups (4 per column * 4 columns)
# Each byte position uses a specific T-table:
# Position 0,4,8,12 -> T0 (pages 0-255)
# Position 1,5,9,13 -> T1 (pages 256-511)
# Position 2,6,10,14 -> T2 (pages 512-767)
# Position 3,7,11,15 -> T3 (pages 768-1023)

# So when we vary byte 0, we change which T0 entry is accessed for position 0
# But positions 4,8,12 also use T0 with fixed values (since we fix those bytes)
# So the footprint for T0 will always include 3 fixed pages (for positions 4,8,12)
# plus 1 varying page (for position 0)
# Total T0 pages in footprint: 4 (but could be fewer if collisions)

# Let's analyze the footprints for byte 0
print("\nAnalyzing byte 0 footprints:", file=sys.stderr)
for val, pages in footprints_byte0.items():
    t0_pages = [p for p in pages if 0 <= p < 256]
    t1_pages = [p for p in pages if 256 <= p < 512]
    t2_pages = [p for p in pages if 512 <= p < 768]
    t3_pages = [p for p in pages if 768 <= p < 1024]
    print(f"  pt[0]={val}: T0={t0_pages}, T1={t1_pages}, T2={t2_pages}, T3={t3_pages}", file=sys.stderr)

# Now let's do this for all 16 byte positions to recover the key
# For each position i, we vary pt[i] 0-255, keep others fixed (e.g., 0)
# The varying page in the corresponding T-table tells us pt[i] ^ key[i]
# Since we know pt[i], we can compute key[i] = pt[i] ^ index

key_bytes = [None] * 16

for pos in range(16):
    print(f"\nProbing byte position {pos}:", file=sys.stderr)
    # Determine which T-table this position uses
    table_idx = pos % 4  # 0=T0, 1=T1, 2=T2, 3=T3
    table_base = table_idx * 256
    
    # We'll vary this byte and see which page in the corresponding table is accessed
    # But we need to isolate the varying page from the fixed ones
    # Strategy: use a base plaintext where all bytes are 0
    # Then for each value of pt[pos], the index into T_table is pt[pos] ^ key[pos]
    # The page accessed will be table_base + (pt[pos] ^ key[pos])
    # Other positions in the same table will access fixed pages
    
    # Let's collect all footprints
    footprints = {}
    for val in range(256):
        pt = bytearray([0] * 16)
        pt[pos] = val
        fp = get_footprint_for_pt(bytes(pt))
        if fp:
            pages = tuple(sorted(fp["pages"]))
            footprints[val] = pages
    
    # Find which page in the target table varies
    # For each value, look at pages in the target table range
    varying_pages = {}
    for val, pages in footprints.items():
        target_pages = [p for p in pages if table_base <= p < table_base + 256]
        varying_pages[val] = target_pages
    
    # The varying page should be the one that changes with val
    # Fixed pages (from other positions in same table) will be constant
    # Let's find the page that takes all 256 values (or at least varies)
    all_target_pages = set()
    for pages in varying_pages.values():
        all_target_pages.update(pages)
    
    print(f"  All pages in table {table_idx} seen: {sorted(all_target_pages)}", file=sys.stderr)
    
    # For each val, the varying page is the one in target_pages that's not always present
    # Actually, there should be 4 positions per table, so 4 pages per table in footprint
    # 3 are fixed (from the 3 positions we keep at 0), 1 varies
    # Let's find the fixed pages first
    page_counts = {}
    for pages in varying_pages.values():
        for p in pages:
            page_counts[p] = page_counts.get(p, 0) + 1
    
    fixed_pages = {p for p, c in page_counts.items() if c == 256}
    varying_page_candidates = {p for p, c in page_counts.items() if c < 256}
    
    print(f"  Fixed pages: {fixed_pages}", file=sys.stderr)
    print(f"  Varying page candidates: {varying_page_candidates}", file=sys.stderr)
    
    # For each val, the varying page is the one in target_pages not in fixed_pages
    key_byte = None
    for val in range(256):
        target_pages = varying_pages[val]
        varying = [p for p in target_pages if p not in fixed_pages]
        if len(varying) == 1:
            page = varying[0]
            index = page - table_base
            # index = pt[pos] ^ key[pos] = val ^ key[pos]
            # So key[pos] = val ^ index
            kb = val ^ index
            if key_byte is None:
                key_byte = kb
            elif key_byte != kb:
                print(f"  CONFLICT at val={val}: expected {key_byte}, got {kb}", file=sys.stderr)
        elif len(varying) == 0:
            # All target pages are fixed - this means the varying page collided with a fixed page
            # The index must be one of the fixed page indices
            # We need to figure out which one
            pass
        else:
            print(f"  Multiple varying pages at val={val}: {varying}", file=sys.stderr)
    
    if key_byte is not None:
        key_bytes[pos] = key_byte
        print(f"  Recovered key[{pos}] = {key_byte:02x}", file=sys.stderr)
    else:
        print(f"  FAILED to recover key[{pos}]", file=sys.stderr)
        # Try alternative approach
        # For each val, the set of target pages should have size 4 (or less if collision)
        # The index = page - table_base for the page that corresponds to this position
        # Since we know pt[pos] = val, and index = val ^ key[pos]
        # We can try all possible key bytes and see which one makes the mapping consistent
        
        # Build mapping from val to the set of indices accessed in this table
        val_to_indices = {}
        for val, pages in varying_pages.items():
            indices = [p - table_base for p in pages]
            val_to_indices[val] = set(indices)
        
        # Try each possible key byte
        for kb in range(256):
            consistent = True
            for val in range(256):
                expected_index = val ^ kb
                if expected_index not in val_to_indices[val]:
                    consistent = False
                    break
            if consistent:
                key_bytes[pos] = kb
                print(f"  Recovered key[{pos}] = {kb:02x} (via consistency check)", file=sys.stderr)
                break
        
        if key_bytes[pos] is None:
            print(f"  STILL FAILED for position {pos}", file=sys.stderr)

print(f"\nRecovered key bytes: {key_bytes}", file=sys.stderr)
key_hex = ''.join(f'{b:02x}' for b in key_bytes)
print(f"Key hex: {key_hex}", file=sys.stderr)

# Submit claim
print(f'CLAIM:{{"key_hex": "{key_hex}"}}', flush=True)