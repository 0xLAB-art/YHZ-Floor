import sys, json, hashlib

PROV = {
    "dh_p_hex": "c0007cca3bd948636d759b8959aceed2f2a4bb836f8ec79a0eb07fe98e66583887ea5a30a238ea5525c1ed4333ac9ff8b86feb312927a5dd440f0fa356400a9fb2abe401cb99be971fdb0c8adbbd1a663baedc9e8aba86bf87ec8759ce4ed75d681699a1b30dd44514898321f33b254b2840673d3fdffd732f4f91ad57a9e23f",
    "dh_g_hex": "2",
    "server_pub_hex": "7c0054fa1414cd7f111a2be568017311e01e3d1960bc1325f5e1c0476ad13c2b59733efafda471b00f81312a5417bef8d3e438663512315e8c4252cbd7f52f6ae9d71ed038addb3a88435ad27eb1b8b0748716391b6e7f1ce57ded6a432aa8b7ee929c645a6e537dec74d625933b1dbdb229c856542d861b83d36b6c3ed27f2c",
}

prov = PROV
try:
    if len(sys.argv) > 1 and sys.argv[1]:
        loaded = json.loads(sys.argv[1])
        if isinstance(loaded, dict):
            prov.update(loaded)
except Exception:
    pass

p = int(prov["dh_p_hex"], 16)
g = int(prov.get("dh_g_hex", "2"), 16)
server_pub = int(prov["server_pub_hex"], 16)

# 1024-bit MODP group == RFC 2409 group1 == diffie-hellman-group1-sha1
kex_algo = "diffie-hellman-group1-sha1"

# Deterministic ephemeral private exponent (in [2, p-2])
x = int.from_bytes(hashlib.sha256(b"acts-weak-kex-client-eph").digest(), "big") % (p - 3) + 2

client_pub = pow(g, x, p)
shared = pow(server_pub, x, p)

shared_hex = format(shared, "x")
proof = hashlib.sha256((kex_algo + "|" + shared_hex).encode()).hexdigest()

claim = {
    "proof_hex": proof,
    "kex_algo": kex_algo,
    "client_pub_hex": format(client_pub, "x"),
}
sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
sys.stdout.flush()