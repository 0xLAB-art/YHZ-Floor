import sys
import json

def main():
    # Read instance from command line argument
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Extract all r values to check for nonce reuse
    r_values = [sig['r'] for sig in signatures]
    
    # Check if any r values are duplicated (nonce reuse)
    seen_r = set()
    has_duplicate = False
    for r in r_values:
        if r in seen_r:
            has_duplicate = True
            break
        seen_r.add(r)
    
    if has_duplicate:
        reason = "Duplicate nonce detected but exploitation not implemented in this analysis"
    else:
        # No nonce reuse detected
        # Without implementing sophisticated lattice-based attacks or finding other
        # weaknesses, we cannot recover the private key from these signatures
        reason = "No exploitable weakness found; standard ECDSA signatures without nonce reuse"
    
    # Output the required JSON format
    result = {
        "status": "UNDERDETERMINED",
        "reason": reason
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()