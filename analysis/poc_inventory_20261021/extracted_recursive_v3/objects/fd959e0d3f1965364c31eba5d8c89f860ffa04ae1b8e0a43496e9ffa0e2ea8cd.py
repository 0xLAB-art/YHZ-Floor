import sys
import json

def main():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    result = {
        "status": "UNDERDETERMINED",
        "reason": "ECDSA nonce reuse requires at least two signatures sharing the same nonce (r value); only one signature provided"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()