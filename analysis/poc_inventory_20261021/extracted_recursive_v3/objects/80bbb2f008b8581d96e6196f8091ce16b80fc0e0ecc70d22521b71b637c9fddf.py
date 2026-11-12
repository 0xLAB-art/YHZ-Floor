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

# Fixed bytes for positions we're not varying
FIXED_BYTE = 0xAA

key_bytes = []

for key_pos in range(16):
    table = key_pos % 4
    print(f"\nRecovering key byte {key_pos} (table {table})...", file=sys.stderr)
    
    footprints = []
    for p_val in range(256):
        pt = bytearray([FIXED_BYTE] * 16)
        pt[key_pos] = p_val
        resp = http_request("POST", "/encrypt", body_hex=bytes(pt).hex())
        resp = http_request("GET", "/footprint")
        if resp.get('status') == 200:
            body = base64.b64decode(resp['body_b64'])
            footprint = json.loads(body)
            pages = set(footprint.get('pages', []))
            footprints.append(pages)
        else:
            print(f"  Error at p_val={p_val}: {resp}", file=sys.stderr)
            footprints.append(set())
        if p_val % 64 == 0:
            print(f"  Progress: {p_val}/256", file=sys.stderr)
    
    best_count = -1
    best_guess = -1
    for k_guess in range(256):
        count = 0
        for p_val in range(256):
            predicted_page = table * 256 + (p_val ^ k_guess)
            if predicted_page in footprints[p_val]:
                count += 1
        if count > best_count:
            best_count = count
            best_guess = k_guess
        if count == 256:
            print(f"  Key byte {key_pos} = {best_guess} (0x{best_guess:02x}) - PERFECT MATCH", file=sys.stderr)
            break
    
    if best_count != 256:
        print(f"  WARNING: Key byte {key_pos} best guess = {best_guess} with count={best_count}", file=sys.stderr)
    
    key_bytes.append(best_guess)
    print(f"  Key byte {key_pos} = 0x{best_guess:02x}", file=sys.stderr)

key_hex = ''.join(f'{b:02x}' for b in key_bytes)
print(f"\nRecovered key: {key_hex}", file=sys.stderr)
print(f"CLAIM:{{\"key_hex\": \"{key_hex}\"}}")