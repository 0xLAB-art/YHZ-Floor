import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    # Parse public key coordinates
    x = int(instance['public_key']['x'], 16)
    y = int(instance['public_key']['y'], 16)
    
    # Parse signatures
    signatures = []
    for sig in instance['signatures']:
        r = int(sig['r'], 16)
        s = int(sig['s'], 16)
        z = int(sig['z'], 16)
        signatures.append((r, s, z))
    
    # Check for nonce reuse (same r value in different signatures)
    r_values = [sig[0] for sig in signatures]
    r_counts = {}
    for r in r_values:
        r_counts[r] = r_counts.get(r, 0) + 1
    
    # If we find repeated r values, we could potentially recover the private key
    repeated_r = [r for r, count in r_counts.items() if count > 1]
    
    if repeated_r:
        result = {
            "status": "UNDERDETERMINED",
            "reason": "nonce reuse detected but curve order unknown"
        }
    else:
        # Without repeated nonces and without knowing the curve parameters,
        # we cannot recover the private key from ECDSA signatures
        result = {
            "status": "UNDERDETERMINED",
            "reason": "insufficient information without curve parameters"
        }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()