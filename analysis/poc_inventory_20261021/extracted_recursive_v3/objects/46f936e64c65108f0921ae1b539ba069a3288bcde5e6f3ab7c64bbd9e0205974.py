import json
import sys
from typing import Dict, List, Tuple

def modinv(a: int, m: int) -> int:
    """Compute modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key_from_nonce_reuse(
    r: int, s1: int, s2: int, z1: int, z2: int, n: int
) -> int:
    """
    Recover private key from two signatures with the same nonce.
    
    From ECDSA equations:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    Solving for d:
    d = (s1*z2 - s2*z1) * (r*(s2 - s1))^(-1) mod n
    """
    # Calculate k first to verify
    # k = (z1 - z2) * (s1 - s2)^(-1) mod n
    s_diff = (s1 - s2) % n
    if s_diff == 0:
        return None
    
    z_diff = (z1 - z2) % n
    k = (z_diff * modinv(s_diff, n)) % n
    
    # Now calculate d from k
    # s1 = k^(-1) * (z1 + r*d) mod n
    # d = (s1*k - z1) * r^(-1) mod n
    k_inv = modinv(k, n)
    
    # Verify k is correct by checking s1
    computed_s1 = (k_inv * (z1 + r * 0)) % n  # We'll calculate d separately
    
    # Calculate d: d = (s1*k - z1) / r mod n
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    public_key = instance['public_key']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    sig_data: List[Dict] = []
    for sig in signatures:
        sig_data.append({
            'r': int(sig['r'], 16),
            's': int(sig['s'], 16),
            'z': int(sig['z'], 16)
        })
    
    # Find duplicate r values
    r_to_sigs = {}
    for i, sig in enumerate(sig_data):
        r = sig['r']
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append(i)
    
    # Find pairs with same r
    d = None
    k = None
    
    for r, indices in r_to_sigs.items():
        if len(indices) >= 2:
            # Found nonce reuse!
            i1, i2 = indices[0], indices[1]
            s1 = sig_data[i1]['s']
            s2 = sig_data[i2]['s']
            z1 = sig_data[i1]['z']
            z2 = sig_data[i2]['z']
            
            # Recover k from the two signatures
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            if s_diff != 0:
                k_recovered = (z_diff * modinv(s_diff, n)) % n
                
                # Recover d from k
                # s = k^(-1) * (z + r*d) mod n
                # s*k = z + r*d mod n
                # d = (s*k - z) * r^(-1) mod n
                d_recovered = ((s1 * k_recovered - z1) * modinv(r, n)) % n
                
                # Verify with second signature
                d_recovered2 = ((s2 * k_recovered - z2) * modinv(r, n)) % n
                
                if d_recovered == d_recovered2:
                    d = d_recovered
                    k = k_recovered
                    break
    
    # Format output
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()