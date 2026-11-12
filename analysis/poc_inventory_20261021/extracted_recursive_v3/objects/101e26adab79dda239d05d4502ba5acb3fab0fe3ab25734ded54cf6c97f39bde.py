import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean Algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(signatures, public_key, n):
    """
    Recover private key from ECDSA signatures with nonce reuse.
    
    When the same nonce k is used for two signatures:
    s1 = k^-1 * (z1 + r * d) mod n
    s2 = k^-1 * (z2 + r * d) mod n
    
    Then: k = (z1 - z2) / (s1 - s2) mod n
    And: d = (s * k - z) / r mod n
    """
    
    # Group signatures by r value (same r means same nonce k)
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append({'r': r, 's': s, 'z': z})
    
    # Find groups with multiple signatures (nonce reuse)
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1 = sigs[0]
            sig2 = sigs[1]
            
            r = sig1['r']
            s1 = sig1['s']
            z1 = sig1['z']
            s2 = sig2['s']
            z2 = sig2['z']
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            z_diff = (z1 - z2) % n
            s_diff = (s1 - s2) % n
            
            if s_diff == 0:
                continue
                
            s_diff_inv = modinv(s_diff, n)
            k = (z_diff * s_diff_inv) % n
            
            # Recover d: d = (s * k - z) / r mod n
            r_inv = modinv(r, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            return d, k
    
    return None, None

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # SECP256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    # Recover private key and nonce
    d, k = recover_private_key(signatures, public_key, n)
    
    if d is None or k is None:
        # Should not happen with the given instance
        result = {"d": "0" * 64, "k": "0" * 64}
    else:
        # Format as 64 lowercase hex characters
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
        
        result = {"d": d_hex, "k": k_hex}
    
    # Print exactly one JSON object
    print(json.dumps(result))

if __name__ == "__main__":
    main()