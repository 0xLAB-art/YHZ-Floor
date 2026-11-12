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