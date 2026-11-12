import sys
import json

def modinv(a, m):
    """Compute modular inverse of a modulo m using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m

def extended_gcd(a, b):
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    signatures = instance['signatures']
    
    # Look for nonce reuse: same r value in different signatures
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(i)
    
    # Check if any r value appears more than once
    for r, indices in r_to_sigs.items():
        if len(indices) >= 2:
            # Nonce reuse detected - we can recover the private key
            i1, i2 = indices[0], indices[1]
            sig1 = signatures[i1]
            sig2 = signatures[i2]
            
            s1 = int(sig1['s'], 16)
            s2 = int(sig2['s'], 16)
            z1 = int(sig1['z'], 16)
            z2 = int(sig2['z'], 16)
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s1 * k - z1) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            s_diff_inv = modinv(s_diff, n)
            if s_diff_inv is None:
                continue
            
            k = (z_diff * s_diff_inv) % n
            
            # Recover private key
            r_inv = modinv(r, n)
            if r_inv is None:
                continue
            
            d = (((s1 * k - z1) % n) * r_inv) % n
            
            result = {
                "status": "UNDERDETERMINED",
                "reason": f"Nonce reuse detected between signatures {i1} and {i2}, private key: {hex(d)[2:]}"
            }
            print(json.dumps(result))
            return
    
    # No obvious vulnerability found
    result = {
        "status": "UNDERDETERMINED",
        "reason": "No nonce reuse detected among signatures"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()