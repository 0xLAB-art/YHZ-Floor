import sys
import json

def modinv(a, m):
    """Modular inverse using extended Euclidean algorithm"""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(signatures):
    """Recover private key from ECDSA signatures with nonce reuse"""
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find duplicate r values (indicating nonce reuse)
    r_to_sigs = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(sig)
    
    # Look for nonce reuse
    for r, sigs in r_to_sigs.items():
        if len(sigs) >= 2:
            # We have nonce reuse! Use first two signatures
            sig1, sig2 = sigs[0], sigs[1]
            
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Recover nonce k: k = (z1 - z2) / (s1 - s2) mod n
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Recover private key d: d = (s*k - z) / r mod n
                r_inv = modinv(r, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                return d, k
            except:
                continue
    
    return None, None

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Recover private key and nonce
    d, k = recover_private_key(signatures)
    
    if d is None or k is None:
        # Fallback: shouldn't happen with proper nonce reuse
        d = 0
        k = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    # Output result as JSON
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()