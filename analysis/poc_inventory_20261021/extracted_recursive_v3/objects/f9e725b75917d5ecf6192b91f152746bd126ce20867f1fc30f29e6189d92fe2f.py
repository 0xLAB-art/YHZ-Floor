import sys
import json
from collections import defaultdict

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # ECDSA curve parameters (secp256k1)
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Check for repeated r values (nonce reuse)
    r_to_sigs = defaultdict(list)
    for i, sig in enumerate(signatures):
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        r_to_sigs[r].append((i, r, s, z))
    
    # Look for nonce reuse
    for r, sigs in r_to_sigs.items():
        if len(sigs) >= 2:
            # Found nonce reuse - we can recover the private key
            i1, r1, s1, z1 = sigs[0]
            i2, r2, s2, z2 = sigs[1]
            
            # k = (z1 - z2) / (s1 - s2) mod n
            # d = (s*k - z) / r mod n
            
            s_diff = (s1 - s2) % n
            z_diff = (z1 - z2) % n
            
            # Compute modular inverse
            s_diff_inv = pow(s_diff, -1, n)
            k = (z_diff * s_diff_inv) % n
            
            # Recover private key
            r_inv = pow(r1, -1, n)
            d = ((s1 * k - z1) * r_inv) % n
            
            # Verify by computing public key
            # Public key = d * G (would need elliptic curve point multiplication)
            # For now, we've found the vulnerability
            
            result = {
                "status": "UNDERDETERMINED",
                "reason": f"nonce reuse detected: signatures {i1} and {i2} share r={hex(r)[:16]}..., private key recoverable"
            }
            print(json.dumps(result))
            return
    
    # Check for other vulnerabilities
    # Check if any s values are very small (could indicate weak randomness)
    small_threshold = n // 1000
    for i, sig in enumerate(signatures):
        s = int(sig['s'], 16)
        if s < small_threshold or (n - s) < small_threshold:
            result = {
                "status": "UNDERDETERMINED",
                "reason": f"signature {i} has suspiciously small s value, potential weak randomness"
            }
            print(json.dumps(result))
            return
    
    # No obvious vulnerability found
    result = {
        "status": "UNDERDETERMINED",
        "reason": "no nonce reuse or obvious vulnerabilities detected in signature set"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()