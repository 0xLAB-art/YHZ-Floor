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

def recover_private_key(signatures, public_key, p, n):
    """
    Recover private key from ECDSA signatures with nonce reuse.
    If two signatures share the same r value, they used the same nonce k.
    """
    # Group signatures by r value
    r_groups = {}
    for sig in signatures:
        r = int(sig['r'], 16)
        if r not in r_groups:
            r_groups[r] = []
        r_groups[r].append(sig)
    
    # Find r values that appear more than once (nonce reuse)
    for r, sigs in r_groups.items():
        if len(sigs) >= 2:
            # Use first two signatures with same r
            sig1, sig2 = sigs[0], sigs[1]
            
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # From ECDSA: s = k^(-1) * (z + r*d) mod n
            # s1 = k^(-1) * (z1 + r*d) mod n
            # s2 = k^(-1) * (z2 + r*d) mod n
            # 
            # s1 - s2 = k^(-1) * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff == 0:
                continue
            
            try:
                k = (z_diff * modinv(s_diff, n)) % n
                
                # Now recover d from: s1 = k^(-1) * (z1 + r*d) mod n
                # s1 * k = z1 + r*d mod n
                # d = (s1*k - z1) / r mod n
                
                k_inv = modinv(k, n)
                d = ((s1 * k - z1) * modinv(r, n)) % n
                
                # Verify with the second signature
                d_check = ((s2 * k - z2) * modinv(r, n)) % n
                
                if d == d_check and d > 0:
                    return d
                
                # Try negative k
                k = (-z_diff * modinv(s_diff, n)) % n
                d = ((s1 * k - z1) * modinv(r, n)) % n
                d_check = ((s2 * k - z2) * modinv(r, n)) % n
                
                if d == d_check and d > 0:
                    return d
                    
            except ValueError:
                continue
    
    return None

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    public_key = instance['public_key']
    signatures = instance['signatures']
    
    # Recover private key
    d = recover_private_key(signatures, public_key, p, n)
    
    if d is None:
        # Fallback: try all pairs
        for i in range(len(signatures)):
            for j in range(i + 1, len(signatures)):
                sig1, sig2 = signatures[i], signatures[j]
                r1 = int(sig1['r'], 16)
                r2 = int(sig2['r'], 16)
                
                if r1 == r2:
                    s1 = int(sig1['s'], 16)
                    s2 = int(sig2['s'], 16)
                    z1 = int(sig1['z'], 16)
                    z2 = int(sig2['z'], 16)
                    
                    s_diff = (s1 - s2) % n
                    z_diff = (z1 - z2) % n
                    
                    if s_diff != 0:
                        try:
                            k = (z_diff * modinv(s_diff, n)) % n
                            d = ((s1 * k - z1) * modinv(r1, n)) % n
                            if d > 0:
                                break
                        except ValueError:
                            continue
            if d is not None and d > 0:
                break
    
    # Format output
    d_hex = format(d, '064x')
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
