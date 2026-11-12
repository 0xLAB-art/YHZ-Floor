import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    signatures = data['signatures']
    
    # Check for duplicate r values (nonce reuse)
    r_values = [sig['r'] for sig in signatures]
    r_counts = {}
    for r in r_values:
        r_counts[r] = r_counts.get(r, 0) + 1
    
    # Find any repeated r values
    repeated_r = [r for r, count in r_counts.items() if count > 1]
    
    if repeated_r:
        # Nonce reuse detected - private key can be recovered
        result = {
            "status": "UNDERDETERMINED",
            "reason": "nonce reuse detected allowing private key recovery"
        }
    else:
        # Check if there are enough signatures for other attacks
        # With 16 unique signatures, lattice attacks might be possible
        # but require more complex analysis
        if len(signatures) >= 10:
            result = {
                "status": "UNDERDETERMINED", 
                "reason": "multiple signatures present, potential lattice attack vector"
            }
        else:
            result = {
                "status": "UNDERDETERMINED",
                "reason": "insufficient information for cryptanalysis"
            }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()