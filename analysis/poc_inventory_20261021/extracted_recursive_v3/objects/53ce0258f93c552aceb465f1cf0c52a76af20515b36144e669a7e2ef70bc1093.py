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
    """Encrypt plaintext and return footprint pages set."""
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
    if v % 32 == 0:
        print(f"  v={v}: {len(pages)} pages", file=sys.stderr)

# Find pages that vary across footprints
all_pages = set()
for fp in footprints:
    all_pages.update(fp)

# Count how many times each page appears
page_counts = {}
for fp in footprints:
    for p in fp:
        page_counts[p] = page_counts.get(p, 0) + 1

# Pages that appear in all 256 footprints are from fixed bytes
# Pages that appear in only 1 footprint are from the varying byte
varying_pages = [p for p, count in page_counts.items() if count == 1]
constant_pages = [p for p, count in page_counts.items() if count == 256]

print(f"Total unique pages: {len(all_pages)}", file=sys.stderr)
print(f"Constant pages (count=256): {len(constant_pages)}", file=sys.stderr)
print(f"Varying pages (count=1): {len(varying_pages)}", file=sys.stderr)

# Map v -> varying page
v_to_page = {}
for v in range(256):
    fp = footprints[v]
    # Find the page in this footprint that's in varying_pages
    for p in fp:
        if p in varying_pages:
            v_to_page[v] = p
            break

print(f"Mapped {len(v_to_page)} values", file=sys.stderr)

# Check if all varying pages belong to same table
if v_to_page:
    tables = set(p // 256 for p in v_to_page.values())
    print(f"Tables used: {tables}", file=sys.stderr)
    # For v=0, the index = page % 256 = 0 XOR k_0 = k_0
    page_0 = v_to_page[0]
    key_byte_0 = page_0 % 256
    print(f"Key byte 0 = {key_byte_0} (0x{key_byte_0:02x})", file=sys.stderr)
    print(f"Page for v=0: {page_0} (table={page_0//256}, index={page_0%256})", file=sys.stderr)
    
    # Verify: for each v, index should be v XOR key_byte_0
    for v in [0, 1, 2, 3, 4, 5, 10, 100, 200, 255]:
        p = v_to_page[v]
        idx = p % 256
        expected = v ^ key_byte_0
        print(f"  v={v}: page={p}, idx={idx}, expected={expected}, match={idx==expected}", file=sys.stderr)