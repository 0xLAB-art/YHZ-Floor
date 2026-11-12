import sys, json, base64, hashlib, secrets

# Try more endpoints
for path in ['/ssh/kex', '/ssh/negotiate', '/ssh/connect', '/ssh/session', '/kex/init', '/kex/dh', '/dh', '/diffie-hellman', '/weak', '/legacy', '/v1', '/v1/kex', '/v1/ssh']:
    print(json.dumps({"http": {"method": "GET", "path": path}}), flush=True)
    resp = json.loads(sys.stdin.readline())
    print(f"{path}: {resp}", file=sys.stderr)
    if resp['status'] != 404:
        body = base64.b64decode(resp['body_b64'])
        print(f"  Body: {body}", file=sys.stderr)