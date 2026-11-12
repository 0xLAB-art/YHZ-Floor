import sys
import json
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import time

def modinv(a, n):
    return pow(a, -1, n)

def main():
    # Provisioned material
    sig1_hex = "07ed389c5a044913b6205d735eff120dc60e3035c37dd209fd24393db36c2be0d63b7f5f9bddf859dbb2873bde9a8b0b14e370b5a300475b8bb1cbf5b264d2cb"
    sig2_hex = "07ed389c5a044913b6205d735eff120dc60e3035c37dd209fd24393db36c2be0d26d4787c21fcf0e45c77d6f74a73dcd69d161f5fe712e2648ba68559ab24343"
    z1_hex = "bae7d09d4714fbacb2708a657b438af5b6976ae61434d754525b6eaada93a9b3"
    z2_hex = "f80ada615079dcaf05fe0473c25d45fcf0844200cd89e9ef91112b20ac838b8b"
    challenge_msg_hex = "880dfa1a2ce49fdf17d110d2897018d8c550c7c99f0b338c35e936ee0297db1b"
    
    # Parse signatures (64 bytes = r||s, 32 bytes each)
    sig1 = bytes.fromhex(sig1_hex)
    sig2 = bytes.fromhex(sig2_hex)
    
    r1 = int.from_bytes(sig1[:32], 'big')
    s1 = int.from_bytes(sig1[32:], 'big')
    r2 = int.from_bytes(sig2[:32], 'big')
    s2 = int.from_bytes(sig2[32:], 'big')
    
    # r should be the same for both signatures (same nonce k)
    assert r1 == r2, f"r values differ: {r1} != {r2}"
    r = r1
    
    z1 = int.from_bytes(bytes.fromhex(z1_hex), 'big')
    z2 = int.from_bytes(bytes.fromhex(z2_hex), 'big')
    
    # NIST P-256 curve order
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Recover k: k = (z1 - z2) * (s1 - s2)^(-1) mod n
    k = ((z1 - z2) % n) * modinv((s1 - s2) % n, n) % n
    
    # Recover d: d = (s1 * k - z1) * r^(-1) mod n
    d = ((s1 * k - z1) % n) * modinv(r, n) % n
    
    # Verify by creating signature for challenge message
    key = ECC.construct(curve='NIST P-256', d=d)
    signer = DSS.new(key, 'fips-186-3')
    challenge_hash = SHA256.new(bytes.fromhex(challenge_msg_hex))
    sig = signer.sign(challenge_hash)
    
    d_hex = format(d, '064x')
    sig_hex = sig.hex()
    
    # Output claim
    claim = {"d_hex": d_hex, "sig_hex": sig_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()