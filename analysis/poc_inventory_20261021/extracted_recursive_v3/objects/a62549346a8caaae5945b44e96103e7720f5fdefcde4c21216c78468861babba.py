import sys
import json

def main():
    with open(sys.argv[1]) as f:
        instance = json.load(f)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "Nonce reuse detection requires known plaintext, the key, or multiple ciphertext pairs with structural correlation; none are provided in this instance"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()