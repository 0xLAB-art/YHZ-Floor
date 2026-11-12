import sys
import json

def main():
    # Read instance
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    signatures = instance['signatures']
    
    # Check for nonce reuse (same r values)
    r_values = [sig['r'] for sig in signatures]
    r_set = set(r_values)
    
    # If we have duplicate r values, we could recover the private key
    if len(r_set) < len(r_values):
        # Found nonce reuse - this would be exploitable
        reason = "Nonce reuse detected but private key recovery not implemented"
    else:
        # No obvious nonce reuse
        # Check if we have enough signatures for lattice attack
        # Typically need many signatures and some bias
        
        # With 16 signatures and no obvious nonce reuse,
        # and without implementing full lattice attacks,
        # we cannot determine the private key
        reason = "No nonce reuse detected; insufficient information for private key recovery without advanced lattice techniques"
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": reason
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()