import sys, json, hashlib

def main():
    provision = json.loads(sys.argv[1])
    p_hex = provision['dh_p_hex']
    p_len = len(p_hex)  # number of hex digits for full modulus
    p = int(p_hex, 16)
    g = int(provision['dh_g_hex'], 16)
    server_pub = int(provision['server_pub_hex'], 16)
    # Choose a weak KEX algorithm name (any accepted string)
    kex_algo = 'diffie-hellman-group14-sha1'
    # Simple client private exponent a = 1
    a = 1
    client_pub = pow(g, a, p)
    # Shared secret = server_pub^{a} mod p = server_pub (since a=1)
    shared = server_pub
    # Hex representation padded to full modulus length (lowercase)
    shared_hex = format(shared, 'x').zfill(p_len)
    # Compute proof = SHA256(kex_algo || shared_hex) where both are ASCII bytes
    proof = hashlib.sha256(kex_algo.encode() + shared_hex.encode()).hexdigest()
    claim = {
        'proof_hex': proof,
        'kex_algo': kex_algo,
        'client_pub_hex': format(client_pub, 'x')
    }
    print('CLAIM:' + json.dumps(claim, separators=(',', ':')))

if __name__ == '__main__':
    main()