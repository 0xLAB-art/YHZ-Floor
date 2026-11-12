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

def encrypt(plaintext_bytes):
    body_hex = plaintext_bytes.hex()
    resp = http_request("POST", "/encrypt", body_hex=body_hex)
    if resp["status"] != 200:
        raise Exception(f"Encrypt failed: {resp}")
    body = base64.b64decode(resp["body_b64"])
    if body[0] != ord('E') or len(body) != 17:
        raise Exception(f"Unexpected encrypt response: {body}")
    return body[1:]

def get_footprint():
    resp = http_request("GET", "/footprint")
    if resp["status"] != 200:
        raise Exception(f"Footprint failed: {resp}")
    body = base64.b64decode(resp["body_b64"])
    return json.loads(body)

# AES inverse S-box
inv_sbox = [
    0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
    0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
    0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
    0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
    0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
    0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
    0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
    0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
    0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
    0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
    0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
    0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
    0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
    0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
    0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
]

# For each plaintext byte position, which T-table does it affect in first round?
# AES state is column-major: state[r][c] = input[r + 4*c]
# After ShiftRows: row r shifted left by r
# So state byte at (r, c) goes to T-table (c - r) mod 4
# Input byte at position p = r + 4*c affects T-table (c - r) mod 4
table_for_byte = [0, 3, 2, 1, 1, 0, 3, 2, 2, 1, 0, 3, 3, 2, 1, 0]

print("Starting key recovery...", file=sys.stderr)

key_bytes = [0] * 16

for target_byte in range(16):
    print(f"\nRecovering key byte {target_byte}...", file=sys.stderr)
    target_table = table_for_byte[target_byte]
    
    # Collect footprints for all 256 values
    footprints = []
    for v in range(256):
        pt = bytearray([0]*16)
        pt[target_byte] = v
        ct = encrypt(bytes(pt))
        fp = get_footprint()
        # Filter pages for the target table
        table_pages = set()
        for page in fp['pages']:
            table_idx = page // 256
            if table_idx == target_table:
                table_pages.add(page)
        footprints.append(frozenset(table_pages))
        if v % 32 == 0:
            print(f"  Progress: {v}/256", file=sys.stderr)
    
    # Extract the page for the target table from each footprint
    sbox_outputs = []
    for v in range(256):
        fp = footprints[v]
        table_page = None
        for page in fp:
            if page // 256 == target_table:
                table_page = page
                break
        if table_page is None:
            print(f"  ERROR: No page for table {target_table} at v={v}", file=sys.stderr)
            sbox_outputs.append(None)
        else:
            index = table_page % 256
            sbox_outputs.append(index)
    
    print(f"  S-box outputs sample: {sbox_outputs[:16]}", file=sys.stderr)
    
    # sbox_outputs[v] = S-box(v ^ k*) for true key k*
    # For candidate k, inv_sbox[sbox_outputs[v]] ^ v should equal k for all v
    candidate_counts = [0] * 256
    for v in range(256):
        s_out = sbox_outputs[v]
        if s_out is not None:
            k_candidate = inv_sbox[s_out] ^ v
            candidate_counts[k_candidate] += 1
    
    best_k = candidate_counts.index(max(candidate_counts))
    best_count = max(candidate_counts)
    print(f"  Key byte {target_byte} = {best_k:02x} (count={best_count}/256)", file=sys.stderr)
    key_bytes[target_byte] = best_k

key_hex = ''.join(f'{b:02x}' for b in key_bytes)
print(f"\nRecovered key: {key_hex}", file=sys.stderr)
print(f'CLAIM:{{"key_hex": "{key_hex}"}}')