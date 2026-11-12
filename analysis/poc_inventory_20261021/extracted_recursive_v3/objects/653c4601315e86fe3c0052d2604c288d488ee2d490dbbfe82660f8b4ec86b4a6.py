import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        instance = json.load(f)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "Nonce reuse detection requires either the nonce values, plaintexts, or additional ciphertexts encrypted under the same key-nonce pair to perform cryptanalysis such as XOR differential analysis"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()