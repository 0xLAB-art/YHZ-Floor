import sys, json, hashlib

p = int("c000e9d54cd6e6166eb0012b413708be02a5027f3104ab92407168a20950dbf9a8b177cbeda50b1047d892ca438092efee60691262f8ab28db6b4dcda0a178414be94b75c289e88f73c16f1a6e470def069a5d67c3956a7e036c578a4c2b2e41b83856044203e0add25e8ebebd6423085ea8071854cfcc47949cbfdcf466b311", 16)
g = int("2", 16)
Y = int("72b88583b6bec20670db24de1c7ecf2a35244f534e5334ec610afbb9cfda32f2ac4b9a00b7139406a7bedd2edcebe717a6a6e19c369ba6bc45ef4ddd4bdc30872fc0344300b962726d7aaf831884e2f3ca4d1f3311125ce51ce8357bd5fe9bd89628ae0521664bf34d3e9e1f2b74f702a15f78f3b0f9b97a66407eaf3af8fdf3", 16)

x = 0x5A17C0DE
X = pow(g, x, p)
shared = pow(Y, x, p)

xhex = format(X, "x")
shared_hex = format(shared, "x")

algos = ["diffie-hellman-group1-sha1"]

paths = ["/", "/info", "/kex", "/negotiate", "/ssh", "/algorithms", "/health", "/api", "/index.html"]
found = None
for pth in paths:
    print(json.dumps({"http": {"method": "GET", "path": pth}}), flush=True)
    line = sys.stdin.readline()
    if not line:
        break
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r.get("status") == 200:
        import base64
        try:
            body = base64.b64decode(r.get("body_b64", "")).decode("utf-8", "replace")
        except Exception:
            body = ""
        print("PROBE", pth, r.get("status"), body[:600], flush=True)
        import re
        for m in re.findall(r"[a-z0-9\-]*diffie[a-z0-9\-]*", body, re.I):
            found = m
            break

algo = found or algos[0]
proof = hashlib.sha256((algo + shared_hex).encode()).hexdigest()
print("ALGO", algo, "X", xhex, "S", shared_hex, flush=True)
print("CLAIM:" + json.dumps({"proof_hex": proof, "kex_algo": algo, "client_pub_hex": xhex}), flush=True)