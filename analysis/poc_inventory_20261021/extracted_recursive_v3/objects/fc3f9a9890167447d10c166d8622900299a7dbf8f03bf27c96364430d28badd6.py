import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "Nonce reuse detection requires knowledge of the key or plaintext; ciphertexts alone are insufficient"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()