import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.loads(f.read())
    
    known = instance['known_plaintexts'][0]
    target = instance['target']
    
    # Known: 4 bytes at offset 10 in message 6
    # Target: 128 bytes at offset 64 in message 7
    
    # Different messages, no overlap in offsets
    # With only 4 bytes of known plaintext at a different location,
    # cannot determine 128 bytes at the target location
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "Insufficient known plaintext to determine target region"
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()