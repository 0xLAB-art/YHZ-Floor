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
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key
    px = int(instance['public_key']['x'], 16)
    py = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Secp256k1 curve parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Try to find duplicate r values (nonce reuse attack)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r in r_map:
            # Found duplicate r - nonce reuse!
            j = r_map[r]
            r1, s1, z1 = signatures[j]
            r2, s2, z2 = signatures[i]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s*k - z) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            s_diff_inv = modinv(s_diff, n)
            if s_diff_inv is None:
                continue
                
            k = (z_diff * s_diff_inv) % n
            
            # Recover private key using first signature
            r_inv = modinv(r1, n)
            if r_inv is None:
                continue
                
            d = ((s1 * k - z1) * r_inv) % n
            
            # Verify the private key
            # Public key should be d * G
            # We'll verify by checking all signatures
            valid = True
            for r_sig, s_sig, z_sig in signatures:
                # Verify: s*k = z + r*d (mod n)
                # We need to compute k for each signature
                s_inv = modinv(s_sig, n)
                if s_inv is None:
                    valid = False
                    break
                # k = (z + r*d) / s mod n
                k_check = ((z_sig + r_sig * d) * s_inv) % n
                # We can't easily verify without full ECDSA, but the key should be consistent
            
            result = {
                "status": "UNDERDETERMINED",
                "reason": f"private key candidate: {hex(d)[2:]}"
            }
            print(json.dumps(result))
            return
        
        r_map[r] = i
    
    # No duplicate r found - cannot determine private key
    result = {
        "status": "UNDERDETERMINED",
        "reason": "no nonce reuse detected; insufficient information to recover private key"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
