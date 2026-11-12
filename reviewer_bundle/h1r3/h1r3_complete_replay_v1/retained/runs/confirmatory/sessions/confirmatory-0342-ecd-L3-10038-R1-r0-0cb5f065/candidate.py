import sys
import json

def modinv(a, m):
    """Compute modular inverse of a mod m using extended Euclidean algorithm."""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def recover_private_key(sig1, sig2, n):
    """Recover private key from two signatures with the same nonce."""
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Verify r values are the same
    assert r1 == r2, "r values must be the same"
    r = r1
    
    # Calculate k: k = (z1 - z2) / (s1 - s2) mod n
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d: d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    d = (r_inv * ((s1 * k - z1) % n)) % n
    
    return d, k

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with duplicate r values
    r_to_indices = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_to_indices:
            r_to_indices[r] = []
        r_to_indices[r].append(i)
    
    # Find a pair with the same r
    for r, indices in r_to_indices.items():
        if len(indices) >= 2:
            # Use the first two signatures with this r value
            sig1 = signatures[indices[0]]
            sig2 = signatures[indices[1]]
            
            d, k = recover_private_key(sig1, sig2, n)
            
            # Format as 64 lowercase hex characters
            d_hex = format(d, '064x')
            k_hex = format(k, '064x')
            
            result = {
                "d": d_hex,
                "k": k_hex
            }
            
            print(json.dumps(result))
            return
    
    # Should not reach here if the instance is valid
    raise ValueError("No duplicate r values found")

if __name__ == "__main__":
    main()
