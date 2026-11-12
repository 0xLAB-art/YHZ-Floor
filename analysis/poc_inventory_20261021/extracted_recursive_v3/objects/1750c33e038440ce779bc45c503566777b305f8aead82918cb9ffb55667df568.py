import sys
import json
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def modinv(a, n):
    return pow(a, -1, n)

def main():
    # Provisioned material
    sig1_hex = "7136ab52b98673240454cfcc52cfdf9e98910e7627d95a088708c6df9251512e3cecdce3cfc1df6f0f211c059ae91b67fe4d72801a68735ecdb11a95ab09b52f"
    sig2_hex = "7136ab52b98673240454cfcc52cfdf9e98910e7627d95a088708c6df9251512e549136d28bdb3ae1682524939ce01bec614060eb9dca0e79565ab03ac5666d22"
    z1_hex = "3adb250e4e3e0cabef3ee1aaf328c569a3b07e2da6f8954deafbbfabae5923f8"
    z2_hex = "c6dbdca23d06f752bd382fe1a55b194be3e39f9e4e3d8ffd69b424d5820861ec"
    challenge_msg_hex = "0d4a9b9253da0f28f900efa59a8ed160f09d30b8ad252ff71b6f659de133e07a"
    
    # Parse signatures (r || s, each 32 bytes = 64 hex chars)
    r_hex = sig1_hex[:64]
    s1_hex = sig1_hex[64:]
    s2_hex = sig2_hex[64:]
    
    r = int(r_hex, 16)
    s1 = int(s1_hex, 16)
    s2 = int(s2_hex, 16)
    z1 = int(z1_hex, 16)
    z2 = int(z2_hex, 16)
    
    # NIST P-256 order
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Recover k: k = (z1 - z2) * (s1 - s2)^-1 mod n
    k = ((z1 - z2) * modinv((s1 - s2) % n, n)) % n
    
    # Recover d: d = (s1 * k - z1) * r^-1 mod n
    d = ((s1 * k - z1) * modinv(r, n)) % n
    
    d_hex = format(d, '064x')
    
    # Create signature for challenge message
    key = ECC.construct(curve='NIST P-256', d=d)
    signer = DSS.new(key, 'fips-186-3')
    msg_hash = SHA256.new(bytes.fromhex(challenge_msg_hex))
    sig = signer.sign(msg_hash)
    sig_hex = sig.hex()
    
    # Output claim
    claim = {
        "d_hex": d_hex,
        "sig_hex": sig_hex
    }
    print(f"CLAIM:{json.dumps(claim)}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()