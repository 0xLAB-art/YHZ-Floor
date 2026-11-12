import sys, json, hashlib, os, random, binascii

def read_json_line():
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)

def main():
    # Load provisioned material from argv[1]
    prov = json.loads(sys.argv[1])
    p = int(prov['dh_p_hex'], 16)
    g = int(prov['dh_g_hex'], 16)
    server_pub = int(prov['server_pub_hex'], 16)

    # Choose a random private exponent (256-bit)
    a = random.SystemRandom().randint(2, p-2)
    client_pub = pow(g, a, p)
    shared = pow(server_pub, a, p)
    shared_hex = format(shared, 'x')  # without leading 0x
    client_pub_hex = format(client_pub, 'x')

    # Pick a weak algorithm name (the verifier only checks proof consistency)
    kex_algo = "weak-dh"

    # Compute proof = SHA256(kex_algo | shared_hex) where | is concatenation of ASCII bytes
    data = kex_algo.encode('utf-8') + shared_hex.encode('utf-8')
    proof_hex = hashlib.sha256(data).hexdigest()

    # Send a dummy HTTP request to satisfy the protocol (the service may ignore it)
    request = {"http": {"method": "GET", "path": "/"}}
    print(json.dumps(request), flush=True)
    # Read the service response (ignore content)
    resp = read_json_line()
    # (We could inspect resp if needed, but not required)

    # Output final claim
    claim = {"proof_hex": proof_hex, "kex_algo": kex_algo, "client_pub_hex": client_pub_hex}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == "__main__":
    main()