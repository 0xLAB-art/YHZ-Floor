import sys, json, hashlib, os, select, base64

prov = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
p = int(prov["dh_p_hex"], 16)
g = int(prov["dh_g_hex"], 16)
B = int(prov["server_pub_hex"], 16)

candidates = [
    "diffie-hellman-group-exchange-sha1",
    "diffie-hellman-group-exchange-sha256",
    "diffie-hellman-group1-sha1",
    "diffie-hellman-group14-sha1",
    "diffie-hellman-group14-sha256",
]

kex_algo = None

def probe(path):
    global kex_algo
    try:
        sys.stdout.write(json.dumps({"http": {"method": "GET", "path": path}}) + "\n")
        sys.stdout.flush()
        r, _, _ = select.select([sys.stdin], [], [], 4.0)
        if not r:
            return
        line = sys.stdin.readline()
        if not line:
            return
        resp = json.loads(line)
        body = base64.b64decode(resp.get("body_b64", "") or b"").decode("utf-8", "ignore")
        for name in candidates:
            if name in body:
                kex_algo = name
                return
    except Exception:
        pass

for path in ["/", "/kex", "/ssh", "/algorithms", "/transcript", "/info"]:
    if kex_algo is None:
        probe(path)

if kex_algo is None:
    kex_algo = "diffie-hellman-group-exchange-sha1"

a = int.from_bytes(os.urandom(32), "big") % (p - 3) + 2
A = pow(g, a, p)
K = pow(B, a, p)
shared_hex = format(K, "x")
proof = hashlib.sha256((kex_algo + shared_hex).encode()).hexdigest()
claim = {"proof_hex": proof, "kex_algo": kex_algo, "client_pub_hex": format(A, "x")}
sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
sys.stdout.flush()