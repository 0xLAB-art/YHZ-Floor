import sys
import time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def main():
    start = time.monotonic_ns()
    # Provisioned material (hardcoded from prompt)
    sig1_hex = "a586998ba8c1e597b372331f2fe0bfa4345629356f9e1e6369a2e14cde193af8a718b8139b608aef51236ccc27bd34368f0ac1bd55a9e54d939ff798c1fc4f4f"
    sig2_hex = "a586998ba8c1e597b372331f2fe0bfa4345629356f9e1e6369a2e14cde193af8542bfad60f8c5c66965c1d7ad6b50e2c5c2b851477334bdc08450d9eab4b29e3"
    z1_hex = "4c97c73e22a34a7478852c8eb16e0cabc9aa294de8658e00361d6b93f9650411"
    z2_hex = "75a8e5c34c2280d4273112c0a38f5cc100a5c5fd88c0cf884f12a5d3795e648c"
    challenge_msg_hex = "a22ad8a4aeaf1d4b580e56225cb0c7793814c6c48ad1c5d0f2a6b032ea11a767"
    
    # Helper to convert hex to int
    def h2i(h): return int(h, 16)
    
    r1 = h2i(sig1_hex[:64])
    s1 = h2i(sig1_hex[64:])
    r2 = h2i(sig2_hex[:64])
    s2 = h2i(sig2_hex[64:])
    z1 = h2i(z1_hex)
    z2 = h2i(z2_hex)
    challenge_msg = bytes.fromhex(challenge_msg_hex)
    
    # Sanity check: r should be equal
    if r1 != r2:
        sys.stderr.write("Error: r values differ\n")
        sys.exit(1)
    r = r1
    
    # Curve order for NIST P-256
    # We'll get it from a temporary key
    tmp_key = ECC.construct(curve='p256')
    n = tmp_key.order
    
    # Compute nonce k
    s1_minus_s2 = (s1 - s2) % n
    z1_minus_z2 = (z1 - z2) % n
    inv_s_diff = pow(s1_minus_s2, -1, n)
    k = (z1_minus_z2 * inv_s_diff) % n
    
    # Compute private key d
    s1_k = (s1 * k) % n
    d = ((s1_k - z1) % n) * pow(r, -1, n) % n
    
    # Ensure d is in correct range
    if not (1 <= d < n):
        sys.stderr.write("Error: d out of range\n")
        sys.exit(1)
    
    # Create signature over challenge message
    priv_key = ECC.construct(curve='p256', d=d)
    signer = DSS.new(priv_key, 'fips-186-3')
    signature = signer.sign(SHA256.new(challenge_msg))
    sig_hex = signature.hex()
    
    end = time.monotonic_ns()
    
    # Output claim
    claim = {"d_hex": format(d, '064x'), "sig_hex": sig_hex}
    print(f"CLAIM:{claim}", flush=True)
    print(f"OPSPAN_NS:{end - start}", flush=True)

if __name__ == "__main__":
    main()