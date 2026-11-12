import json
import sys

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        return None
    return (x % m + m) % m

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # secp256k1 curve order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signatures
    sigs = []
    for sig in signatures:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        sigs.append((r, s, z))
    
    # Find duplicate r values
    r_to_sigs = {}
    for i, (r, s, z) in enumerate(sigs):
        if r not in r_to_sigs:
            r_to_sigs[r] = []
        r_to_sigs[r].append((i, s, z))
    
    # Find a pair with the same r
    d = None
    k = None
    
    for r, sig_list in r_to_sigs.items():
        if len(sig_list) >= 2:
            # Use first two signatures with this r
            i1, s1, z1 = sig_list[0]
            i2, s2, z2 = sig_list[1]
            
            # Recover k: k = (z1 - z2) / (s1 - s2) mod n
            dz = (z1 - z2) % n
            ds = (s1 - s2) % n
            
            ds_inv = modinv(ds, n)
            if ds_inv is None:
                continue
            
            k = (dz * ds_inv) % n
            
            # Recover d: d = (s * k - z) / r mod n
            r_inv = modinv(r, n)
            if r_inv is None:
                continue
            
            d = ((s1 * k - z1) * r_inv) % n
            
            # Verify with second signature
            d_check = ((s2 * k - z2) * r_inv) % n
            
            if d == d_check:
                break
    
    # Format output
    if d is not None and k is not None:
        d_hex = format(d, '064x')
        k_hex = format(k, '064x')
        result = {"d": d_hex, "k": k_hex}
    else:
        # Fallback (shouldn't happen)
        result = {"d": "0" * 64, "k": "0" * 64}
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()