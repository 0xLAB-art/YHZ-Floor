import json
import sys
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

def modinv(a, n):
    return pow(a, -1, n)

def main():
    # Provisioned material
    sig1_hex = "7b73d20a6c56284d0d86d3e18e81634db5a28c79b54a174f7cc9cf3c302c1368baa965c733b1b10e58e2b647e3493f1c932dca0a0d45c840a420c831a38c504c"
    sig2_hex = "7b73d20a6c56284d0d86d3e18e81634db5a28c79b54a174f7cc9cf3c302c1368162c2a0c5c4d950e696ccb069c250a1a308e100c78ecd73182923047f44ff8e7"
    z1_hex = "73fdd77158acd11031d8b84b9a4dd7bd44b18d3b1e16fbe194d73c212d841006"
    z2_hex = "3721cc878449abbbf3dd199c8ad61723cb28c33b5b0e7d373a05e6ce65e90cf6"
    challenge_msg_hex = "7f242580f693f74981c4f9649e0bd7349c066f64cf383023916002e718beb174"
    
    # NIST P-256 curve order
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Parse signatures (64 bytes = 32 bytes r || 32 bytes s)
    sig1 = bytes.fromhex(sig1_hex)
    sig2 = bytes.fromhex(sig2_hex)
    
    r1 = int.from_bytes(sig1[:32], 'big')
    s1 = int.from_bytes(sig1[32:], 'big')
    r2 = int.from_bytes(sig2[:32], 'big')
    s2 = int.from_bytes(sig2[32:], 'big')
    
    # Verify r1 == r2 (same nonce)
    assert r1 == r2, f"r values differ: {r1} != {r2}"
    r = r1
    
    z1 = int(z1_hex, 16)
    z2 = int(z2_hex, 16)
    
    # Recover k: k = (z1 - z2) * (s1 - s2)^(-1) mod n
    k = ((z1 - z2) * modinv((s1 - s2) % n, n)) % n
    
    # Recover d: d = (s1 * k - z1) * r^(-1) mod n
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    # Convert d to 64-char hex
    d_hex = format(d, '064x')
    
    # Sign challenge message with recovered key
    key = ECC.construct(curve='NIST P-256', d=d)
    signer = DSS.new(key, 'fips-186-3')
    msg_hash = SHA256.new(bytes.fromhex(challenge_msg_hex))
    sig = signer.sign(msg_hash)
    sig_hex = sig.hex()
    
    # Output claim
    claim = {"d_hex": d_hex, "sig_hex": sig_hex}
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()