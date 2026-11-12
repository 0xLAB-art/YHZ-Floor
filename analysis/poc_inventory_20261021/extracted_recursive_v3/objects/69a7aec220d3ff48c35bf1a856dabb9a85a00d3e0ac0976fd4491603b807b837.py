import json
import sys

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

def recover_private_key_from_repeated_k(r1, s1, z1, r2, s2, z2, n):
    """
    Recover private key when the same k (nonce) is used for two signatures.
    
    From ECDSA equations:
    s1 = k^(-1) * (z1 + r1 * d) mod n
    s2 = k^(-1) * (z2 + r2 * d) mod n
    
    When r1 == r2 (same k used):
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1 * k - z1) / r1 mod n
    """
    # Calculate k
    numerator = (z1 - z2) % n
    denominator = (s1 - s2) % n
    
    if denominator == 0:
        return None
    
    k = (numerator * modinv(denominator, n)) % n
    
    # Calculate d (private key)
    numerator_d = (s1 * k - z1) % n
    denominator_d = r1 % n
    
    if denominator_d == 0:
        return None
    
    d = (numerator_d * modinv(denominator_d, n)) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Convert signatures to integers
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Look for repeated r values (indicating same k used)
    r_map = {}
    for i, (r, s, z) in enumerate(sigs):
        if r in r_map:
            # Found a repeated r! Try to recover the private key
            j, s_prev, z_prev = r_map[r]
            
            result = recover_private_key_from_repeated_k(
                r, s, z,
                r, s_prev, z_prev,
                n
            )
            
            if result:
                d, k = result
                
                # Format output
                d_hex = format(d, '064x')
                k_hex = format(k, '064x')
                
                output = {
                    "d": d_hex,
                    "k": k_hex
                }
                
                print(json.dumps(output))
                return
        else:
            r_map[r] = (i, s, z)
    
    # If no solution found
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()