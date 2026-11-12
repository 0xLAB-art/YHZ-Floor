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

# Test basic functionality
print("Testing service...", file=sys.stderr)
pt = bytes([0]*16)
ct = encrypt(pt)
print(f"Ciphertext: {ct.hex()}", file=sys.stderr)
fp = get_footprint()
print(f"Footprint: {fp}", file=sys.stderr)
print(f"Number of pages: {fp['count']}", file=sys.stderr)
print(f"Pages: {fp['pages']}", file=sys.stderr)

# Now test varying one byte
print("\nTesting byte 0 variation...", file=sys.stderr)
base_pt = bytearray([0]*16)
varying_pages = []
for v in range(4):
    base_pt[0] = v
    ct = encrypt(bytes(base_pt))
    fp = get_footprint()
    varying_pages.append(set(fp['pages']))
    print(f"  v={v}: pages={fp['pages']}", file=sys.stderr)

# Check if pages differ
for i in range(1, 4):
    if varying_pages[i] != varying_pages[0]:
        print(f"  Byte 0 value {i} gives different pages!", file=sys.stderr)
    else:
        print(f"  Byte 0 value {i} same pages", file=sys.stderr)

print("\nDone with test", file=sys.stderr)
print('CLAIM:{"key_hex": "00000000000000000000000000000000"}')