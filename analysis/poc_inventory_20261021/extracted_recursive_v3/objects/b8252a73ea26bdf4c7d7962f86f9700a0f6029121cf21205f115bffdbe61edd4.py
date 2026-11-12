import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "Nonce reuse detection requires plaintext, key, nonce, or keystream distinguisher; ciphertexts alone are insufficient"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
