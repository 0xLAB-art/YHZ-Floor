import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "Nonce reuse detected but without plaintext, key, or additional oracle access, cannot determine which specific messages were encrypted or recover the keystream definitively."
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()