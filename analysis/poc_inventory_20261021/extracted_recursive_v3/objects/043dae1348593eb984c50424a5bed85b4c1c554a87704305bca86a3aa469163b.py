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

def get_footprint_pages():
    resp = http_request("GET", "/footprint")
    if resp["status"] != 200:
        print(f"Footprint error: {resp}", file=sys.stderr)
        return []
    body = base64.b64decode(resp["body_b64"])
    data = json.loads(body)
    return data["pages"]

def encrypt(plaintext_bytes):
    body_hex = plaintext_bytes.hex()
    resp = http_request("POST", "/encrypt", body_hex=body_hex)
    if resp["status"] != 200:
        print(f"Encrypt error: {resp}", file=sys.stderr)
        return None
    body = base64.b64decode(resp["body_b64"])
    if body[0] != ord('E') or len(body) != 17:
        print(f"Unexpected response format: {body}", file=sys.stderr)
        return None
    return body[1:]

print("Testing service...")

# Test with zeros
ct = encrypt(bytes([0]*16))
print(f"Ciphertext: {ct.hex()}")
pages = get_footprint_pages()
print(f"Pages: {pages}")

# Test with different values for first byte
for i in range(4):
    pt = bytes([i]) + bytes([0]*15)
    ct = encrypt(pt)
    pages = get_footprint_pages()
    print(f"Byte 0={i}: pages={pages}")

# Now let's do the full attack: for each key byte position, try all 256 values
# The first round of AES does: state = plaintext XOR key, then SubBytes, then ShiftRows, then MixColumns
# The T-table lookups in the first round depend on (plaintext_byte XOR key_byte)
# So if we fix all plaintext bytes except one, and vary that one byte through 0-255,
# the footprint will change based on (pt_byte XOR key_byte)
# We can find the key byte by finding which value produces a unique footprint pattern

key_bytes = []

for key_pos in range(16):
    print(f"\n=== Recovering key byte {key_pos} ===")
    # We'll use a fixed plaintext with all zeros except we'll vary the byte at key_pos
    # Actually, due to ShiftRows, the byte positions get permuted.
    # Let me think about this more carefully.
    
    # In AES first round:
    # 1. AddRoundKey: state[i] = pt[i] XOR key[i]
    # 2. SubBytes: state[i] = SBox[state[i]]
    # 3. ShiftRows: row 0: no shift, row 1: shift 1, row 2: shift 2, row 3: shift 3
    # 4. MixColumns
    # 5. T-table lookups combine SubBytes+ShiftRows+MixColumns
    
    # The T-table index for each table lookup depends on specific state bytes.
    # With T-tables, each table corresponds to one column of the state after ShiftRows.
    # Table 0 uses bytes from column 0 after ShiftRows, etc.
    
    # The footprint shows which pages were accessed. Since each T-table entry is on a separate 4KB page,
    # the page number directly reveals the table index used.
    # page = table * 256 + index
    
    # For a given plaintext byte position, after AddRoundKey and SubBytes and ShiftRows,
    # it ends up in a specific table and row.
    
    # Let me just try the straightforward approach: fix all other bytes to 0,
    # vary the target byte through 0-255, collect footprints.
    # The key byte is the value that makes (pt_byte XOR key_byte) = some value.
    # Actually, we need to find which pt_byte value produces a specific footprint.
    # But we don't know the mapping from (pt_byte XOR key_byte) to footprint.
    # However, if we try all 256 values for pt_byte, we get 256 footprints.
    # The key byte is the one where (pt_byte XOR key_byte) = 0, i.e., pt_byte = key_byte.
    # But we don't know which footprint corresponds to index 0.
    
    # Wait - the task says: "chosen plaintexts with fixed non-key bytes isolate one key byte at a time
    # (probe all 256 values of one byte, keep the footprint signatures, match across queries)"
    # This suggests we need to do multiple queries with different fixed values for other bytes
    # and find the intersection/match.
    
    # Let me think: if we fix all other plaintext bytes to some value, and vary one byte,
    # the footprint for that byte position will cycle through all 256 possible table indices
    # as (pt_byte XOR key_byte) goes through 0-255.
    # But we don't know which footprint corresponds to which index.
    # However, if we do this with TWO different fixed values for the other bytes,
    # the footprint for the target byte will be the same when (pt_byte XOR key_byte) is the same.
    # So we can find the key byte by finding which pt_byte value produces the same footprint
    # in both experiments.
    
    # Actually, simpler: the footprint is a set of pages. For each pt_byte value, we get a set.
    # The key byte is the pt_byte value where the footprint matches some expected pattern.
    # But we don't know the expected pattern.
    
    # Let me re-read: "match across queries" - so we do multiple queries with different
    # fixed non-key bytes, and the key byte is the one that produces consistent footprints.
    
    # Let's try: for each candidate key byte k (0-255), we predict that when pt_byte = k,
    # then (pt_byte XOR k) = 0, so the SBox input is 0, SBox[0] = 0x63.
    # But we don't know the T-table mapping.
    
    # Actually, the simplest approach: collect footprints for all 256 values of one plaintext byte
    # with all other bytes fixed to 0. Then do it again with all other bytes fixed to 1.
    # The correct key byte is the one where the footprint is the same in both experiments
    # (because (pt_byte XOR key_byte) is the same, so the T-table index is the same).
    
    footprints_fixed0 = {}
    footprints_fixed1 = {}
    
    for pt_val in range(256):
        pt = bytearray([0]*16)
        pt[key_pos] = pt_val
        ct = encrypt(bytes(pt))
        pages = get_footprint_pages()
        footprints_fixed0[pt_val] = tuple(sorted(pages))
        
        pt = bytearray([1]*16)
        pt[key_pos] = pt_val
        ct = encrypt(bytes(pt))
        pages = get_footprint_pages()
        footprints_fixed1[pt_val] = tuple(sorted(pages))
    
    # Find pt_val where footprints match
    matches = []
    for pt_val in range(256):
        if footprints_fixed0[pt_val] == footprints_fixed1[pt_val]:
            matches.append(pt_val)
    
    print(f"Matches for key byte {key_pos}: {matches}")
    if len(matches) == 1:
        key_bytes.append(matches[0])
        print(f"Key byte {key_pos} = {matches[0]:02x}")
    else:
        # Try with fixed=2 as well
        footprints_fixed2 = {}
        for pt_val in range(256):
            pt = bytearray([2]*16)
            pt[key_pos] = pt_val
            ct = encrypt(bytes(pt))
            pages = get_footprint_pages()
            footprints_fixed2[pt_val] = tuple(sorted(pages))
        
        matches2 = []
        for pt_val in matches:
            if footprints_fixed0[pt_val] == footprints_fixed2[pt_val]:
                matches2.append(pt_val)
        print(f"Matches after fixed=2: {matches2}")
        if len(matches2) == 1:
            key_bytes.append(matches2[0])
            print(f"Key byte {key_pos} = {matches2[0]:02x}")
        else:
            key_bytes.append(matches[0])  # fallback
            print(f"Key byte {key_pos} = {matches[0]:02x} (fallback)")

print(f"\nRecovered key: {bytes(key_bytes).hex()}")
print(f"CLAIM:{{\"key_hex\": \"{bytes(key_bytes).hex()}\"}}")