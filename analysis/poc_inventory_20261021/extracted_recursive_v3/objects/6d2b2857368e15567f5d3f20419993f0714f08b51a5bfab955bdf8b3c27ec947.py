import sys, json, hashlib, binascii

def main():
    # Load provisioned material from argv[1]
    provision = json.loads(sys.argv[1])
    p = int(provision['dh_p_hex'], 16)
    g = int(provision['dh_g_hex'], 16)
    server_pub = int(provision['server_pub_hex'], 16)
    # Choose a weak KEX algorithm name (any string accepted by verifier)
    kex_algo = 'diffie-hellman-group14-sha1'
    # Choose client private exponent a = 1 (simple, still valid)
    a = 1
    client_pub = pow(g, a, p)
    shared = pow(server_pub, a, p)
    shared_hex = format(shared, 'x')
    # Compute proof: SHA256(kex_algo | shared_hex)
    data = (kex_algo + shared_hex).encode()
    proof = hashlib.sha256(data).hexdigest()
    claim = {
        'proof_hex': proof,
        'kex_algo': kex_algo,
        'client_pub_hex': format(client_pub, 'x')
    }
    # Output final claim line
    print('CLAIM:' + json.dumps(claim, separators=(',', ':')))

if __name__ == '__main__':
    main()