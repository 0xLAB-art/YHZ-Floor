import sys
import json
import base64
import itertools

def http_request(method, path, body=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body is not None:
        req["http"]["body"] = body
    if headers is not None:
        req["http"]["headers"] = headers
    print(json.dumps(req), flush=True)
    response = json.loads(sys.stdin.readline())
    return response

def encrypt(plaintext):
    # plaintext is 16 bytes
    resp = http_request("POST", "/encrypt", body=base64.b64encode(plaintext).decode())
    if resp["status"] != 200:
        raise Exception(f"Encrypt failed: {resp}")
    body = base64.b64decode(resp["body_b64"])
    if body[0] != ord('E') or len(body) != 17:
        raise Exception(f"Unexpected response: {body}")
    return body[1:]

def get_footprint():
    resp = http_request("GET", "/footprint")
    if resp["status"] != 200:
        raise Exception(f"Footprint failed: {resp}")
    data = json.loads(base64.b64decode(resp["body_b64"]).decode())
    return set(data["pages"])

def main():
    # We need to recover 16 key bytes.
    # For each key byte position i (0-15), we can fix all other plaintext bytes
    # and vary the i-th byte across 0-255.
    # The first round T-table lookups depend on plaintext XOR key.
    # Each T-table entry is on a separate 4KB page.
    # The footprint tells us which pages were accessed.
    # For a fixed key byte k_i, as we vary p_i, the T-table index = p_i ^ k_i varies.
    # Each index maps to a unique page (table*256 + index).
    # So the set of pages accessed for byte position i will be exactly the set of
    # pages corresponding to the 256 possible indices for that T-table.
    # But wait - there are 4 T-tables (T0, T1, T2, T3) used in first round.
    # Each byte of state goes through one T-table depending on position.
    # Actually, AES first round: state = plaintext XOR key, then SubBytes, ShiftRows, MixColumns.
    # With T-tables: each column of state uses 4 T-table lookups (one per byte).
    # T0, T1, T2, T3 correspond to the 4 bytes of a column.
    # For a given plaintext byte position, it maps to a specific T-table.
    # Let's map plaintext byte index to T-table:
    # After XOR with key, byte at position 0,1,2,3 (column 0) use T0,T1,T2,T3 respectively.
    # Position 4,5,6,7 (column 1) use T0,T1,T2,T3 but shifted by ShiftRows.
    # Actually standard T-table implementation:
    # For each column c in 0..3:
    #   t0 = T0[s[0][c] ^ k[0][c]]
    #   t1 = T1[s[1][c] ^ k[1][c]]
    #   t2 = T2[s[2][c] ^ k[2][c]]
    #   t3 = T3[s[3][c] ^ k[3][c]]
    # But with ShiftRows, the indices are permuted.
    # Let's think: state is 4x4 matrix, row-major: s[0][0], s[1][0], s[2][0], s[3][0], s[0][1], ...
    # Plaintext bytes 0-15 map to state[row][col] where row = i % 4, col = i // 4.
    # After AddRoundKey: state[row][col] ^= key[row][col]
    # Then SubBytes, then ShiftRows shifts row r by r positions left.
    # Then MixColumns combines columns.
    # T-table implementation combines SubBytes+ShiftRows+MixColumns:
    # For each column c, output column = T0[s[0][c]] ^ T1[s[1][c]] ^ T2[s[2][c]] ^ T3[s[3][c]] (with appropriate shifts)
    # Actually standard T-tables:
    # T0[x] = [S[x], S[x]<<1, S[x], S[x]<<1^S[x]] (column)
    # T1[x] = [S[x]<<1, S[x], S[x]<<1^S[x], S[x]] (shifted)
    # etc.
    # The key insight: each plaintext byte position i maps to exactly one T-table (0,1,2,3)
    # and the index into that T-table is plaintext_byte ^ key_byte.
    # So for each key byte position, we can determine which T-table it uses.
    # Let's determine the mapping by testing.
    # But we can also just brute force: for each key byte position, try all 256 key values,
    # and see which one produces a consistent footprint pattern.
    # Actually, the footprint for a single encryption is the set of 16 pages accessed
    # (4 T-tables * 4 bytes per column * 4 columns? No, each encryption does 16 T-table lookups:
    # 4 columns * 4 T-tables per column = 16 lookups).
    # Each lookup accesses one page (since each T-table entry is on its own page).
    # So each encryption touches exactly 16 pages (one per state byte).
    # The page ID = table*256 + index, where index = state_byte ^ key_byte.
    # For a fixed key, as we vary one plaintext byte, only one of the 16 pages changes
    # (the one corresponding to that byte position).
    # So we can isolate each key byte by varying one plaintext byte at a time
    # and observing which page changes.
    
    # Strategy:
    # 1. Choose a base plaintext (all zeros).
    # 2. For each position i (0-15):
    #    - For each value v in 0..255:
    #        - Create plaintext with base but position i = v
    #        - Encrypt and get footprint
    #    - We get 256 footprints, each a set of 16 pages.
    #    - 15 of the pages are constant across all 256 queries (the other 15 bytes fixed).
    #    - 1 page varies across the 256 queries - this is the page for position i.
    #    - The varying page IDs will be table*256 + (v ^ key_byte) for v=0..255.
    #    - So the set of varying pages = {table*256 + (v ^ key_byte) | v in 0..255}
    #      = {table*256 + x | x in 0..255} (just a permutation)
    #    - But we need to find key_byte. We know the table number from the page ID // 256.
    #    - The index = page_id % 256 = v ^ key_byte.
    #    - So for each v, we get index = page_id % 256.
    #    - Then key_byte = v ^ index.
    #    - This should be constant for all v.
    
    base_pt = bytes([0]*16)
    key_bytes = [None]*16
    
    for pos in range(16):
        print(f"Recovering key byte {pos}", file=sys.stderr, flush=True)
        footprints = []
        for v in range(256):
            pt = bytearray(base_pt)
            pt[pos] = v
            ct = encrypt(bytes(pt))
            fp = get_footprint()
            footprints.append(fp)
        
        # Find which page varies
        # Intersection of all footprints = constant pages
        constant_pages = set.intersection(*footprints)
        # The varying page for each query is the one in fp but not in constant_pages
        varying_pages = []
        for fp in footprints:
            diff = fp - constant_pages
            if len(diff) != 1:
                print(f"Warning: pos={pos}, v={v}, diff={diff}", file=sys.stderr)
            varying_pages.append(list(diff)[0] if diff else None)
        
        # Now varying_pages[v] = table*256 + (v ^ key_byte)
        # Compute key_byte from first few
        key_candidates = []
        for v in range(256):
            page = varying_pages[v]
            if page is None:
                continue
            index = page % 256
            table = page // 256
            kb = v ^ index
            key_candidates.append(kb)
        
        # All should be the same
        if len(set(key_candidates)) != 1:
            print(f"Error: multiple key candidates for pos {pos}: {set(key_candidates)}", file=sys.stderr)
            # Take most common
            from collections import Counter
            kb = Counter(key_candidates).most_common(1)[0][0]
        else:
            kb = key_candidates[0]
        
        key_bytes[pos] = kb
        print(f"Key byte {pos} = {kb:02x}", file=sys.stderr, flush=True)
    
    key_hex = ''.join(f'{b:02x}' for b in key_bytes)
    print(f"CLAIM:{json.dumps({{'key_hex': key_hex}})}", flush=True)

if __name__ == "__main__":
    main()