import sys, json, hashlib

def main():
    provision = json.loads(sys.argv[1])
    p = int(provision['dh_p_hex'], 16)
    g = int(provision['dh_g_hex'], 16)
    server_pub = int(provision['server_pub_hex'], 16)
    # Choose a weak KEX algorithm name (any string is acceptable)
    kex_algo = 'diffie-hellman-group14-sha1'
    # Use client private exponent a = 1 for simplicity
    a = 1
    client_pub = pow(g, a, p)
    # Shared secret as computed by verifier: pow(client_pub, SERVER_PRIV, p) == server_pub
    shared = server_pub
    # Encode shared as raw big‑endian bytes (no leading zero truncation)
    shared_bytes = shared.to_bytes((p.bit_length() + 7) // 8, 'big')
    # Compute proof = SHA256(kex_algo || shared_bytes)
    proof = hashlib.sha256(kex_algo.encode() + shared_bytes).hexdigest()
    claim = {
        'proof_hex': proof,
        'kex_algo': kex_algo,
        'client_pub_hex': format(client_pub, 'x')
    }
    print('CLAIM:' + json.dumps(claim, separators=(',', ':')))

if __name__ == '__main__':
    main()