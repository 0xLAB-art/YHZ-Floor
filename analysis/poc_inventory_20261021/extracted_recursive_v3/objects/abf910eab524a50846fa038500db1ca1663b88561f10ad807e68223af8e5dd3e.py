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

# Test with all-zero plaintext
plaintext = bytes([0] * 16)
resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
print(f"Encrypt status: {resp['status']}", file=sys.stderr)
if resp['status'] == 200:
    body = base64.b64decode(resp['body_b64'])
    print(f"Ciphertext: {body.hex()}", file=sys.stderr)

resp = http_request("GET", "/footprint")
print(f"Footprint status: {resp['status']}", file=sys.stderr)
if resp['status'] == 200:
    body = base64.b64decode(resp['body_b64'])
    data = json.loads(body)
    pages = data['pages']
    print(f"Count: {data['count']}", file=sys.stderr)
    print(f"Pages: {pages}", file=sys.stderr)
    
    # Analyze page distribution by table
    tables = {}
    for p in pages:
        table = p // 256
        index = p % 256
        if table not in tables:
            tables[table] = []
        tables[table].append(index)
    for t in sorted(tables.keys()):
        print(f"Table {t}: {len(tables[t])} indices: {sorted(tables[t])}", file=sys.stderr)

# Test with all-0xFF plaintext
plaintext = bytes([0xFF] * 16)
resp = http_request("POST", "/encrypt", body_hex=plaintext.hex())
resp = http_request("GET", "/footprint")
if resp['status'] == 200:
    body = base64.b64decode(resp['body_b64'])
    data = json.loads(body)
    pages = data['pages']
    print(f"\nAll-FF Count: {data['count']}", file=sys.stderr)
    tables = {}
    for p in pages:
        table = p // 256
        index = p % 256
        if table not in tables:
            tables[table] = []
        tables[table].append(index)
    for t in sorted(tables.keys()):
        print(f"Table {t}: {len(tables[t])} indices: {sorted(tables[t])}", file=sys.stderr)