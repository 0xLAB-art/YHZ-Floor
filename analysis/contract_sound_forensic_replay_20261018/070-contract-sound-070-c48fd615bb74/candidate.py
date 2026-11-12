import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "ChaCha20 nonce reuse detection requires either the nonce values, the key, known plaintext, or a distinguisher oracle. With only two ciphertexts and no additional information, we cannot determine whether the same nonce was reused."
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
