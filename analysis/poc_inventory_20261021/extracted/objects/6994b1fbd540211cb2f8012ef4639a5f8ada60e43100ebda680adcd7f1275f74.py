import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    _, x, _ = extended_gcd(a % m, m)
    return (x % m + m) % m

def recover_key_from_reused_nonce(sig1, sig2, n):
    """Recover private key when nonce is reused (same r value)."""
    r1 = int(sig1['r'], 16)
    s1 = int(sig1['s'], 16)
    z1 = int(sig1['z'], 16)
    
    r2 = int(sig2['r'], 16)
    s2 = int(sig2['s'], 16)
    z2 = int(sig2['z'], 16)
    
    # Signatures must have same r (same k used)
    if r1 != r2:
        return None, None
    
    r = r1
    
    # Calculate k = (z1 - z2) / (s1 - s2) mod n
    z_diff = (z1 - z2) % n
    s_diff = (s1 - s2) % n
    
    if s_diff == 0:
        return None, None
    
    s_diff_inv = modinv(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Calculate d = (s*k - z) / r mod n
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d, k

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Find signatures with same r value (reused nonce)
    r_to_sigs = {}
    for idx, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(idx)
    
    # Find reused nonces
    for r, indices in r_to_sigs.items():
        if len(indices) >= 2:
            # Found reused nonce - recover key
            sig1 = signatures[indices[0]]
            sig2 = signatures[indices[1]]
            
            d, k = recover_key_from_reused_nonce(sig1, sig2, n)
            
            if d is not None and k is not None:
                # Format as 64 character hex strings
                d_hex = format(d, '064x')
                k_hex = format(k, '064x')
                
                result = {
                    "d": d_hex,
                    "k": k_hex
                }
                
                print(json.dumps(result))
                return
    
    # Should not reach here if instance is valid
    print(json.dumps({"d": "0" * 64, "k": "0" * 64}))

if __name__ == "__main__":
    main()
