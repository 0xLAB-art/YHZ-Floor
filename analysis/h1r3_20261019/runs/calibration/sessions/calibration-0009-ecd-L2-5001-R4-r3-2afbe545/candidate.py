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
    """Extended Euclidean Algorithm."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def recover_private_key(public_key, signatures):
    """Recover private key from ECDSA signatures with nonce reuse."""
    # secp256k1 parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse public key
    x = int(public_key['x'], 16)
    y = int(public_key['y'], 16)
    
    # Parse signatures
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Find two signatures with the same r value (nonce reuse)
    r_to_sigs = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((s, z, i))
    
    # Look for nonce reuse
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # We have nonce reuse! Use first two signatures with same r
            s1, z1, _ = sig_list[0]
            s2, z2, _ = sig_list[1]
            
            # Recover nonce k: k = (z1 - z2) / (s1 - s2) mod n
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            try:
                s_diff_inv = modinv(s_diff, n)
                k = (z_diff * s_diff_inv) % n
                
                # Recover private key d: d = (s*k - z) / r mod n
                r_inv = modinv(r, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                # Verify with second signature
                d_check = ((s2 * k - z2) * r_inv) % n
                
                if d == d_check and d != 0:
                    # Format as 64 lowercase hex characters
                    d_hex = format(d, '064x')
                    return d_hex
            except ValueError:
                continue
    
    # If no solution found, return empty (shouldn't happen with valid input)
    return "0" * 64

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Recover private key
    private_key = recover_private_key(instance['public_key'], instance['signatures'])
    
    # Output result as JSON
    result = {"d": private_key}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
