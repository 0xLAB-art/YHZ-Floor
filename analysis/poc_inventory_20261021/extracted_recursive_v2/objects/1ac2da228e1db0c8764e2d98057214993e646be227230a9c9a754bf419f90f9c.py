import sys
import json
import base64

def b64_to_int(s):
    return int.from_bytes(base64.b64decode(s), 'big')

def main():
    with open(sys.argv[1]) as f:
        data = json.load(f)
    
    # Parse public key and signatures
    r1 = b64_to_int(data['signature_1']['r'])
    s1 = b64_to_int(data['signature_1']['s'])
    z1 = b64_to_int(data['signature_1']['z'])
    
    r2 = b64_to_int(data['signature_2']['r'])
    s2 = b64_to_int(data['signature_2']['s'])
    z2 = b64_to_int(data['signature_2']['z'])
    
    # secp256k1 order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Nonce reuse: r1 == r2
    # k = (z1 - z2) / (s1 - s2) mod n
    # d = (s1 * k - z1) / r1 mod n
    
    def modinv(a, m):
        return pow(a, -1, m)
    
    k = ((z1 - z2) * modinv(s1 - s2, n)) % n
    d = ((s1 * k - z1) * modinv(r1, n)) % n
    
    print(json.dumps({
        "d": f"{d:064x}",
        "k": f"{k:064x}"
    }))

if __name__ == "__main__":
    main()
