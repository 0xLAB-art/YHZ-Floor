import sys, json, hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def main():
    # Read provisioned material from stdin (first non-empty line)
    provision = None
    for line in sys.stdin:
        line = line.strip()
        if line:
            try:
                provision = json.loads(line)
                break
            except json.JSONDecodeError:
                pass
    if provision is None:
        # Fallback to hardcoded values (should not happen)
        provision = {
            'sig1_hex': '6f8cc23bdc247e239635cfea89aca5dbf22c1b8e98b5af8b66d4b4dfeb499c5a5f8b02c264af1e4db79f6b43ab61356256bbcdb8a0bac9405c0327b1f2e63161',
            'sig2_hex': '6f8cc23bdc247e239635cfea89aca5dbf22c1b8e98b5af8b66d4b4dfeb499c5a9e7896ac22f015cbbe8615b5e9dd74d10d601418ec6e93ea4de3cb842f37a9b1',
            'z1_hex': '3fa937b2d07c772593d9a3aa7fb3a5b39c558b78c05d21360253480918908790',
            'z2_hex': 'f939528aa82ede5cd85f13540734fba37ededae077338fd3972bf7987717675b',
            'challenge_msg_hex': 'f6b93a1a5726095fad41523e0e6449b3a6012438eb16b8129aa6388818638f0b',
            'curve': 'NIST P-256'
        }
    
    sig1_hex = provision['sig1_hex']
    sig2_hex = provision['sig2_hex']
    z1_hex = provision['z1_hex']
    z2_hex = provision['z2_hex']
    challenge_msg_hex = provision['challenge_msg_hex']
    
    # Each signature is 64-byte r || 64-byte s (hex)
    r_hex = sig1_hex[:64]
    s1_hex = sig1_hex[64:]
    s2_hex = sig2_hex[64:]
    
    r = int(r_hex, 16)
    s1 = int(s1_hex, 16)
    s2 = int(s2_hex, 16)
    z1 = int(z1_hex, 16)
    z2 = int(z2_hex, 16)
    
    # Order of NIST P-256
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Compute nonce k = (z1 - z2) * (s1 - s2)^{-1} mod n
    delta_z = (z1 - z2) % n
    delta_s = (s1 - s2) % n
    inv_delta_s = pow(delta_s, -1, n)
    k = (delta_z * inv_delta_s) % n
    
    # Compute private key d = (s1 * k - z1) * r^{-1} mod n
    s1k = (s1 * k) % n
    d = ((s1k - z1) % n) * pow(r, -1, n) % n
    
    # Ensure low-s (if s > n/2, replace with n - s) but we already have low-s signatures.
    # For signing we will use the private key directly; the library will produce low-s.
    
    # Construct ECC key
    priv_key = ECC.construct(curve='P-256', d=d)
    signer = DSS.new(priv_key, 'fips-186-3')
    challenge_msg = bytes.fromhex(challenge_msg_hex)
    h = SHA256.new(challenge_msg)
    signature = signer.sign(h)
    sig_hex = signature.hex()
    
    # Output claim
    claim = {
        'd_hex': format(d, '064x'),
        'sig_hex': sig_hex
    }
    print('CLAIM:' + json.dumps(claim))
    sys.stdout.flush()

if __name__ == '__main__':
    main()