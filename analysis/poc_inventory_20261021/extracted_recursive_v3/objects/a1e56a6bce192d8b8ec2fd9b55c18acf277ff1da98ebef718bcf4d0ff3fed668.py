import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key coordinates
    px = int(instance['public_key']['x'], 16)
    py = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Check for nonce reuse (same r value in different signatures)
    r_values = [sig[0] for sig in signatures]
    
    # Look for duplicate r values
    from collections import Counter
    r_counts = Counter(r_values)
    
    for r_val, count in r_counts.items():
        if count > 1:
            # Found nonce reuse - this is a critical vulnerability
            indices = [i for i, sig in enumerate(signatures) if sig[0] == r_val]
            result = {
                "status": "UNDERDETERMINED",
                "reason": f"Nonce reuse detected: r={hex(r_val)} appears {count} times at indices {indices}"
            }
            print(json.dumps(result))
            return
    
    # Check if we have enough signatures to attempt lattice attack
    num_sigs = len(signatures)
    
    # With 6 signatures and no obvious nonce reuse, we cannot determine
    # the private key without more information about the curve parameters
    # or additional cryptographic weaknesses
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": f"Insufficient information: {num_sigs} signatures with distinct r values, no nonce reuse detected, curve parameters unknown"
    }
    print(json.dumps(result))

if __name__ == '__main__':
    main()