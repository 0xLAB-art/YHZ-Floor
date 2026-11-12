import sys
import json
import base64

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
    # plaintext is 16 bytes, send as latin-1 string
    body_str = plaintext.decode('latin-1')
    resp = http_request("POST", "/encrypt", body=body_str)
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
    body = base64.b64decode(resp["body_b64"]).decode()
    data = json.loads(body)
    return set(data["pages"])

def main():
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
        constant_pages = set.intersection(*footprints)
        varying_pages = []
        for fp in footprints:
            diff = fp - constant_pages
            if len(diff) != 1:
                print(f"Warning: pos={pos}, v={v}, diff={diff}", file=sys.stderr)
            varying_pages.append(list(diff)[0] if diff else None)
        
        key_candidates = []
        for v in range(256):
            page = varying_pages[v]
            if page is None:
                continue
            index = page % 256
            kb = v ^ index
            key_candidates.append(kb)
        
        if len(set(key_candidates)) != 1:
            print(f"Error: multiple key candidates for pos {pos}: {set(key_candidates)}", file=sys.stderr)
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