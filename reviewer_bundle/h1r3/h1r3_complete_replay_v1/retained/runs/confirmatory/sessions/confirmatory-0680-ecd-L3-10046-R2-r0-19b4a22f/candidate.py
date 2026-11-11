import sys
import json
import base64
import hashlib

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_bytes(n, length=32):
    return n.to_bytes(length, 'big')

def modinv(a, m):
    """Compute modular inverse using extended Euclidean algorithm."""
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# secp256k1 parameters
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Decode public key
    pub_x = bytes_to_int(base64.b64decode(instance['public_key']['x']))
    pub_y = bytes_to_int(base64.b64decode(instance['public_key']['y']))
    
    # Decode signatures
    signatures = []
    for sig in instance['signatures']:
        r = bytes_to_int(base64.b64decode(sig['r']))
        s = bytes_to_int(base64.b64decode(sig['s']))
        z = bytes_to_int(base64.b64decode(sig['z']))
        signatures.append((r, s, z))
    
    # Look for repeated r values (nonce reuse)
    r_map = {}
    for i, (r, s, z) in enumerate(signatures):
        if r not in r_map:
            r_map[r] = []
        r_map[r].append((i, s, z))
    
    # Find nonce reuse and recover private key
    d = None
    k = None
    
    for r, sigs in r_map.items():
        if len(sigs) >= 2:
            # Nonce reuse detected
            i1, s1, z1 = sigs[0]
            i2, s2, z2 = sigs[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s * k - z) / r mod n
            
            numerator = (z1 - z2) % n
            denominator = (s1 - s2) % n
            
            if denominator == 0:
                continue
            
            k_recovered = (numerator * modinv(denominator, n)) % n
            
            # Verify and compute d
            d_recovered = ((s1 * k_recovered - z1) * modinv(r, n)) % n
            
            # Verify the private key is correct by checking public key
            # In ECDSA, public key Q = d * G, but we can verify using all signatures
            valid = True
            for r_sig, s_sig, z_sig in signatures:
                # Verify: s * k = z + r * d (mod n)
                if r_sig == r:
                    lhs = (s_sig * k_recovered) % n
                    rhs = (z_sig + r_sig * d_recovered) % n
                    if lhs != rhs:
                        valid = False
                        break
            
            if valid:
                d = d_recovered
                k = k_recovered
                break
    
    # Convert to hex
    d_hex = format(d, '064x')
    k_hex = format(k, '064x')
    
    result = {
        "d": d_hex,
        "k": k_hex
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
