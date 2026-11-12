import sys
import json
import base64

def b64_to_int(s):
    return int.from_bytes(base64.b64decode(s), 'big')

def main():
    with open(sys.argv[1]) as f:
        data = json.load(f)
    
    # secp256k1 parameters
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Parse signature data
    r = b64_to_int(data['signature_1']['r'])
    s1 = b64_to_int(data['signature_1']['s'])
    z1 = b64_to_int(data['signature_1']['z'])
    s2 = b64_to_int(data['signature_2']['s'])
    z2 = b64_to_int(data['signature_2']['z'])
    
    # Nonce reuse attack: same r means same k
    # s1 = (z1 + r*d) / k mod n
    # s2 = (z2 + r*d) / k mod n
    # s1 - s2 = (z1 - z2) / k mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
    
    # d = (s*k - z) / r mod n
    d = ((s1 * k - z1) * pow(r, -1, n)) % n
    
    result = {
        "d": f"{d:064x}",
        "k": f"{k:064x}"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()
