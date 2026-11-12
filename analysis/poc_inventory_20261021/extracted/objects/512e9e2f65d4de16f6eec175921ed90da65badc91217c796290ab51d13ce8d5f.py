import json
import sys

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Extract public key coordinates
    px = int(instance['public_key']['x'], 16)
    py = int(instance['public_key']['y'], 16)
    
    # Extract signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # ECDSA uses secp256k1 curve parameters
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Check for nonce reuse (same r value)
    r_values = [sig[0] for sig in signatures]
    
    for i in range(len(signatures)):
        for j in range(i + 1, len(signatures)):
            if r_values[i] == r_values[j]:
                # Same r means same k (nonce reuse)
                r, s1, z1 = signatures[i]
                _, s2, z2 = signatures[j]
                
                # k = (z1 - z2) / (s1 - s2) mod n
                # private_key = (s*k - z) / r mod n
                
                s_diff = (s1 - s2) % n
                z_diff = (z1 - z2) % n
                
                # Compute modular inverse
                s_diff_inv = pow(s_diff, -1, n)
                k = (z_diff * s_diff_inv) % n
                
                # Recover private key
                r_inv = pow(r, -1, n)
                d = ((s1 * k - z1) * r_inv) % n
                
                result = {
                    "status": "UNDERDETERMINED",
                    "reason": f"Nonce reuse detected: private key recovered as {hex(d)}"
                }
                print(json.dumps(result))
                return
    
    # Check for low s values or other weaknesses
    result = {
        "status": "UNDERDETERMINED",
        "reason": "No obvious nonce reuse detected; insufficient information to recover private key"
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
