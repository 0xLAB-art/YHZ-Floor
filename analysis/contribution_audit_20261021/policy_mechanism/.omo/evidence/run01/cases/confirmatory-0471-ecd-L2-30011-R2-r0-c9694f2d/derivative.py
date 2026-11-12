import json
import sys

from typing import List, Tuple

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

def bytes_to_int(b: bytes) -> int:
    """Convert bytes to integer."""
    return int.from_bytes(b, 'big')

def int_to_hex(n: int) -> str:
    """Convert integer to 64-character hex string."""
    return format(n, '064x')

def recover_private_key_from_nonce_reuse(r: int, s1: int, s2: int, z1: int, z2: int, n: int) -> int:
    """
    Recover private key from two signatures sharing the same nonce (r value).
    k = (z1 - z2) / (s1 - s2) mod n
    d = (s1*k - z1) / r mod n
    """
    # Calculate k
    k = (z1 - z2) * modinv(s1 - s2, n) % n
    
    # Calculate private key d
    d = (s1 * k - z1) * modinv(r, n) % n
    
    return d

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # ECDSA parameters for secp256k1
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Decode signatures
    import base64
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Look for duplicate r values (nonce reuse)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find nonce reuse
    private_key = None
    for r, sig_list in r_map.items():
        if len(sig_list) >= 2:
            # We have nonce reuse!
            i1, s1, z1 = sig_list[0]
            i2, s2, z2 = sig_list[1]
            
            try:
                private_key = recover_private_key_from_nonce_reuse(r, s1, s2, z1, z2, n)
                break
            except:
                continue
    
    if private_key is None:
        # Fallback: try all pairs
        for i in range(len(signatures)):
            for j in range(i + 1, len(signatures)):
                r1, s1, z1 = signatures[i]
                r2, s2, z2 = signatures[j]
                if r1 == r2:
                    try:
                        private_key = recover_private_key_from_nonce_reuse(r1, s1, s2, z1, z2, n)
                        break
                    except:
                        continue
            if private_key is not None:
                break
    
    # Output result
    result = {"d": int_to_hex(private_key)}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
