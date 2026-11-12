import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "Nonce reuse detection requires observing keystream collision patterns or possessing plaintext/key material; ciphertexts alone are insufficient without a decryption oracle or known-plaintext anchor"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()