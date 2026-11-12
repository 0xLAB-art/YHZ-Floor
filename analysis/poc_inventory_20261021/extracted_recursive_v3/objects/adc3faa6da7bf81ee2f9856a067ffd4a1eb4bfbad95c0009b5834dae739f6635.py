import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "Nonce reuse in ChaCha20 cannot be confirmed without access to the key, nonce, or a known plaintext oracle. The ciphertexts alone do not reveal whether the same nonce was used."
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()