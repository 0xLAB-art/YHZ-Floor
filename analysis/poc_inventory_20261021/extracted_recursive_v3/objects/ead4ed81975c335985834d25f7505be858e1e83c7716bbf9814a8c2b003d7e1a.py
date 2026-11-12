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

def get_footprint():
    resp = http_request("GET", "/footprint")
    body = base64.b64decode(resp['body_b64'])
    return json.loads(body)

# Test with different plaintexts to see which tables are accessed
print("=== Testing different plaintexts ===", file=sys.stderr)

# Test 1: All zeros
resp = http_request("POST", "/encrypt", body_hex=bytes([0]*16).hex())
fp = get_footprint()
tables = set(p // 256 for p in fp['pages'])
print(f"Plaintext all 0: tables={tables}, count={fp['count']}", file=sys.stderr)

# Test 2: All 1s
resp = http_request("POST", "/encrypt", body_hex=bytes([1]*16).hex())
fp = get_footprint()
tables = set(p // 256 for p in fp['pages'])
print(f"Plaintext all 1: tables={tables}, count={fp['count']}", file=sys.stderr)

# Test 3: Single byte variation - byte 0
for val in [0, 1, 2, 3, 4, 5, 255]:
    pt = bytes([val] + [0]*15)
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    fp = get_footprint()
    tables = set(p // 256 for p in fp['pages'])
    indices = sorted(p % 256 for p in fp['pages'])
    print(f"Byte 0={val}: tables={tables}, indices={indices[:10]}... (count={fp['count']})", file=sys.stderr)

# Test 4: Single byte variation - byte 1
for val in [0, 1, 2, 3]:
    pt = bytes([0, val] + [0]*14)
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    fp = get_footprint()
    tables = set(p // 256 for p in fp['pages'])
    indices = sorted(p % 256 for p in fp['pages'])
    print(f"Byte 1={val}: tables={tables}, indices={indices[:10]}... (count={fp['count']})", file=sys.stderr)

# Test 5: Single byte variation - byte 4
for val in [0, 1, 2, 3]:
    pt = bytes([0]*4 + [val] + [0]*11)
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    fp = get_footprint()
    tables = set(p // 256 for p in fp['pages'])
    indices = sorted(p % 256 for p in fp['pages'])
    print(f"Byte 4={val}: tables={tables}, indices={indices[:10]}... (count={fp['count']})", file=sys.stderr)

# Test 6: Single byte variation - byte 8
for val in [0, 1, 2, 3]:
    pt = bytes([0]*8 + [val] + [0]*7)
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    fp = get_footprint()
    tables = set(p // 256 for p in fp['pages'])
    indices = sorted(p % 256 for p in fp['pages'])
    print(f"Byte 8={val}: tables={tables}, indices={indices[:10]}... (count={fp['count']})", file=sys.stderr)

# Test 7: Single byte variation - byte 12
for val in [0, 1, 2, 3]:
    pt = bytes([0]*12 + [val] + [0]*3)
    resp = http_request("POST", "/encrypt", body_hex=pt.hex())
    fp = get_footprint()
    tables = set(p // 256 for p in fp['pages'])
    indices = sorted(p % 256 for p in fp['pages'])
    print(f"Byte 12={val}: tables={tables}, indices={indices[:10]}... (count={fp['count']})", file=sys.stderr)