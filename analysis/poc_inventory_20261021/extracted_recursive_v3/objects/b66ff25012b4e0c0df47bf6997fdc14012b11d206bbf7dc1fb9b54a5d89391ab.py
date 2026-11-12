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
    
    # ECDSA curve order (secp256k1)
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Since r1 == r2, nonce k was reused
    # ECDSA: s = k^-1 * (z + r*d) mod n
    # s1 = k^-1 * (z1 + r*d) mod n
    # s2 = k^-1 * (z2 + r*d) mod n
    # s1 - s2 = k^-1 * (z1 - z2) mod n
    # k = (z1 - z2) / (s1 - s2) mod n
    
    ds = (s1 - s2) % n
    dz = (z1 - z2) % n
    
    # Compute modular inverse
    ds_inv = pow(ds, -1, n)
    k = (dz * ds_inv) % n
    
    # Recover private key d
    # s1 = k^-1 * (z1 + r*d) mod n
    # s1 * k = z1 + r*d mod n
    # d = (s1*k - z1) / r mod n
    
    r_inv = pow(r1, -1, n)
    d = ((s1 * k - z1) % n * r_inv) % n
    
    result = {
        "d": f"{d:064x}",
        "k": f"{k:064x}"
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()