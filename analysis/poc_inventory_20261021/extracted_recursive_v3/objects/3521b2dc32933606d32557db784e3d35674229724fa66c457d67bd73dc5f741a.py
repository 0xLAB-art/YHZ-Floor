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

def recover_private_key(signatures):
    """Recover ECDSA private key from signatures with repeated nonces."""
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Look for duplicate r values (indicating nonce reuse)
    r_map = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_map:
            r_map[r] = []
        r_map[r].append(i)
    
    # Find pairs with same r value
    for r, indices in r_map.items():
        if len(indices) >= 2:
            # Use first two signatures with same r
            i, j = indices[0], indices[1]
            
            s1 = int(signatures[i]['s'], 16)
            s2 = int(signatures[j]['s'], 16)
            z1 = int(signatures[i]['z'], 16)
            z2 = int(signatures[j]['z'], 16)
            
            # From ECDSA: s = k^-1 * (z + r*d) mod n
            # s1 = k^-1 * (z1 + r*d) mod n
            # s2 = k^-1 * (z2 + r*d) mod n
            # 
            # s1 - s2 = k^-1 * (z1 - z2) mod n
            # k = (z1 - z2) / (s1 - s2) mod n
            
            ds = (s1 - s2) % n
            dz = (z1 - z2) % n
            
            if ds == 0:
                continue
            
            # k = dz / ds mod n
            k = (dz * modinv(ds, n)) % n
            
            # Now recover d from s1 = k^-1 * (z1 + r*d) mod n
            # s1 * k = z1 + r*d mod n
            # r*d = s1*k - z1 mod n
            # d = (s1*k - z1) / r mod n
            
            if r == 0:
                continue
            
            d = ((s1 * k - z1) % n * modinv(r, n)) % n
            
            return d
    
    return None

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Recover private key
    d = recover_private_key(signatures)
    
    if d is None:
        # Fallback: shouldn't happen with given data
        d = 0
    
    # Format as 64 lowercase hex characters
    d_hex = format(d, '064x')
    
    # Output exactly one JSON object
    result = {"d": d_hex}
    print(json.dumps(result))

if __name__ == "__main__":
    main()