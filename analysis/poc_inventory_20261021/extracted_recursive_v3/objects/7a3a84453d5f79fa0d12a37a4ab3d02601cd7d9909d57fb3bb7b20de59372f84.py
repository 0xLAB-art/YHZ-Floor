import json
import sys
import hashlib
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

def recover_private_key():
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    
    sig1_der = bytes.fromhex(data['signature_one_der'])
    sig2_der = bytes.fromhex(data['signature_two_der'])
    
    r1, s1 = decode_dss_signature(sig1_der)
    r2, s2 = decode_dss_signature(sig2_der)
    
    # secp256k1 order
    n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    
    # Nonce reuse: same r value means same k
    # r1 == r2, so k was reused
    # s1 = k^-1 * (H(m1) + r * d) mod n
    # s2 = k^-1 * (H(m2) + r * d) mod n
    # s1 - s2 = k^-1 * (H(m1) - H(m2)) mod n
    # k = (H(m1) - H(m2)) / (s1 - s2) mod n
    
    h1 = int.from_bytes(hashlib.sha256(data['message_one'].encode()).digest(), 'big')
    h2 = int.from_bytes(hashlib.sha256(data['message_two'].encode()).digest(), 'big')
    
    # Recover k
    k = ((h1 - h2) * pow(s1 - s2, -1, n)) % n
    
    # Recover private key d
    # s1 = k^-1 * (h1 + r * d) mod n
    # s1 * k = h1 + r * d mod n
    # d = (s1 * k - h1) / r mod n
    d = ((s1 * k - h1) * pow(r1, -1, n)) % n
    
    result = {"private_key_hex": hex(d)[2:].zfill(64)}
    print(json.dumps(result))

recover_private_key()