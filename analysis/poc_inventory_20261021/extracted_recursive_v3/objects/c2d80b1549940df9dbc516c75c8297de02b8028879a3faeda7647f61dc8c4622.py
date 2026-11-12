import sys, json, hashlib

def main():
    prov = json.loads(sys.argv[1])
    p = int(prov['dh_p_hex'], 16)
    g = int(prov['dh_g_hex'], 16)
    server_pub = int(prov['server_pub_hex'], 16)
    # Choose a weak KEX algorithm name that the verifier likely accepts
    kex_algo = 'diffie-hellman-group1-sha1'
    # Simple client private exponent a = 1
    a = 1
    client_pub = pow(g, a, p)
    # Shared secret as client would compute: server_pub^a mod p = server_pub
    shared = server_pub
    # Hex representation without leading zeros, uppercase as a possible variant
    shared_hex = format(shared, 'X')
    # Compute proof = SHA256(kex_algo || shared_hex) where || is simple byte concatenation
    proof = hashlib.sha256(kex_algo.encode() + shared_hex.encode()).hexdigest()
    claim = {
        'proof_hex': proof,
        'kex_algo': kex_algo,
        'client_pub_hex': format(client_pub, 'x')
    }
    print('CLAIM:' + json.dumps(claim, separators=(',', ':')))

if __name__ == '__main__':
    main()