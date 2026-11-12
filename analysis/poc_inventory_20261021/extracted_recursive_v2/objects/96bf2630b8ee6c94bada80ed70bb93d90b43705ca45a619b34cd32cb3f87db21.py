import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(sigs, n):
    """
    Recover private key from ECDSA signatures with repeated nonce (k).
    
    For two signatures with the same r (same k):
    s1 = k^-1 * (z1 + r*d) mod n
    s2 = k^-1 * (z2 + r*d) mod n
    
    From these:
    s1 - s2 = k^-1 * (z1 - z2) mod n
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    
    # Group signatures by r value
    r_groups = {}
    for i, sig in enumerate(sigs):
        r = int(sig['r'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append((i, sig))
    
    # Find r values that appear multiple times (repeated k)
    for r, group in r_groups.items():
        if len(group) >= 2:
            # Use first two signatures with same r
            sig1 = group[0][1]
            sig2 = group[1][1]
            
            r = int(sig1['r'], 16)
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # Calculate k from the two signatures
            # k = (z1 - z2) / (s1 - s2) mod n
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            
            if s_diff == 0:
                continue
                
            k = (z_diff * modinv(s_diff, n)) % n
            
            # Calculate private key d from k
            # d = (s*k - z) / r mod n
            d = ((s1 * k - z1) * modinv(r, n)) % n
            
            return d, k
    
    return None, None

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Recover private key and nonce
    d, k = recover_private_key(signatures, n)
    
    if d is None:
        # Fallback: shouldn't happen with this instance
        d = 0
        k = 0
    
    # Format output as 64 lowercase hex characters
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
