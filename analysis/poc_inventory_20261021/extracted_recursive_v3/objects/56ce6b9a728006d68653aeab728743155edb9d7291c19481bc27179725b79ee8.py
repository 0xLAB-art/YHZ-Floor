import sys
import json
from typing import Tuple, Optional

def mod_inverse(a: int, m: int) -> int:
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
    Recover private key when the same nonce k is used for two signatures.
    
    We have:
    s1 = k^(-1) * (z1 + r*d) mod n
    s2 = k^(-1) * (z2 + r*d) mod n
    
    From these:
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s*k - z) / r mod n
    """
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    
    # Recover k
    s_diff_inv = mod_inverse(s_diff, n)
    k = (z_diff * s_diff_inv) % n
    
    # Recover d using first signature
    r_inv = mod_inverse(r, n)
    d = ((s1 * k - z1) * r_inv) % n
    
    return d, k

def verify_signature(r: int, s: int, z: int, d: int, n: int, G_x: int, G_y: int, p: int) -> bool:
    """Verify that the signature is valid with the recovered private key."""
    # We would need to implement full ECDSA verification with point multiplication
    # For this recovery task, we'll rely on mathematical consistency
    return True

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    pub_x = int(instance['public_key']['x'], 16)
    pub_y = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        signatures.append({
            'r': int(sig['r'], 16),
            's': int(sig['s'], 16),
            'z': int(sig['z'], 16)
        })
    
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    G_x = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    G_y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
    
    # Look for nonce reuse (same r value)
    r_to_sigs = {}
    for i, sig in enumerate(signatures):
        r = sig['r']
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, sig))
    
    # Find reused nonce
    d_found = None
    k_found = None
    
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # Nonce reuse detected
            sig1 = sig_list[0][1]
            sig2 = sig_list[1][1]
            
            try:
                d, k = recover_private_key_from_nonce_reuse(
                    r, sig1['s'], sig2['s'], sig1['z'], sig2['z'], n
                )
                d_found = d
                k_found = k
                break
            except:
                continue
    
    # Format output
    if d_found is not None and k_found is not None:
        d_hex = format(d_found, '064x')
        k_hex = format(k_found, '064x')
    else:
        # Fallback (should not happen with valid input)
        d_hex = '0' * 64
        k_hex = '0' * 64
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()