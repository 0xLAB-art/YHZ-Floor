import json, time, hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def main():
    start = time.monotonic_ns()
    # provisioned material
    sig1_hex = "b44f9b22dfcae120b4c05b2f7733cedbe268dfeb1be85857cfa3fb768afbb45c4e39124bb5bc0cd3aee54665bc850a5c81aebb0449f1e5f382f5e06ff6d43967"
    sig2_hex = "b44f9b22dfcae120b4c05b2f7733cedbe268dfeb1be85857cfa3fb768afbb45c2621a70afa47fb91f4b9b2532d1b7e5f3d64a1b145298a69d05c9c5430e9001a"
    z1_hex = "2b1a0bd50311474fa18eb86b5faa79378c09b8ad36fc2eacd5e55f99e98ecfc1"
    z2_hex = "0172b8c1bc428fef72dc360102907553c855c3d90c617cd98aef85214fe6be30"
    challenge_msg_hex = "fb2bce9e91c47d1597b119e4841e1ff0eb3f5eb3f7c97dff11a4fc5c9b78d462"
    
    # curve order for NIST P-256
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    r = int(sig1_hex[:64], 16)
    s1 = int(sig1_hex[64:], 16)
    s2 = int(sig2_hex[64:], 16)
    z1 = int(z1_hex, 16)
    z2 = int(z2_hex, 16)
    
    # compute k
    k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
    # compute d
    d = ((s1 * k - z1) * pow(r, -1, n)) % n
    
    # create signature over challenge message
    priv_key = ECC.construct(curve='p256', d=d)
    signer = DSS.new(priv_key, 'fips-186-3')
    sig = signer.sign(SHA256.new(bytes.fromhex(challenge_msg_hex)))
    sig_hex = sig.hex()
    
    end = time.monotonic_ns()
    
    claim = {"d_hex": format(d, '064x'), "sig_hex": sig_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    print(f"OPSPAN_NS:{end - start}")
    sys.stdout.flush()

if __name__ == "__main__":
    import sys
    main()