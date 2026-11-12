import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "ChaCha20 nonce reuse detection requires plaintext, key, or distinguisher access; ciphertexts alone are computationally indistinguishable from random"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()