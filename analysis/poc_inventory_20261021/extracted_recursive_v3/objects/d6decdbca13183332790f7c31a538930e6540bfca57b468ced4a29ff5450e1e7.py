import sys, json, hashlib, random

def read_json_line():
    line = sys.stdin.readline()
    return json.loads(line) if line else None

def main():
    prov = json.loads(sys.argv[1])
    p_hex = prov['dh_p_hex']
    p = int(p_hex, 16)
    g = int(prov['dh_g_hex'], 16)
    server_pub = int(prov['server_pub_hex'], 16)

    # Generate client private exponent
    a = random.SystemRandom().randint(2, p-2)
    client_pub = pow(g, a, p)
    shared = pow(server_pub, a, p)

    # Pad hex strings to full length of p (in hex digits)
    hex_len = len(p_hex)
    client_pub_hex = format(client_pub, 'x').zfill(hex_len)
    shared_hex = format(shared, 'x').zfill(hex_len)

    # Choose a weak algorithm name (any string is acceptable)
    kex_algo = "weak-dh"

    # Compute proof = SHA256(kex_algo | shared_hex)
    data = kex_algo.encode('utf-8') + shared_hex.encode('utf-8')
    proof_hex = hashlib.sha256(data).hexdigest()

    # Send a dummy HTTP request as required by the protocol
    request = {"http": {"method": "GET", "path": "/"}}
    print(json.dumps(request), flush=True)
    _ = read_json_line()  # ignore response

    claim = {"proof_hex": proof_hex, "kex_algo": kex_algo, "client_pub_hex": client_pub_hex}
    print(f"CLAIM:{json.dumps(claim)}")

if __name__ == '__main__':
    main()