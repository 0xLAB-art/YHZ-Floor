import sys
import time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def main():
    # Provisioned material
    sig1_hex = '1a906d18e9d6f5fe0ad675b377d4f62fca73082c9f079afe03204a36f98f2df5a34a9827a6388c5cce91588e771a51a594fa2aa930cc5146e078d7bb3b7ef477'
    sig2_hex = '1a906d18e9d6f5fe0ad675b377d4f62fca73082c9f079afe03204a36f98f2df5b8ca47f1c21d974070e20ca83ee68123aa111196739a1147be8aefa47466e4a2'
    z1_hex = 'c76f0af6d627ce7b94f37d6b535e2666bdf73c79682e3dad69030d4c47a1f576'
    z2_hex = '3c631fced634f827737e1eb2e5cbc1af396d8f25ec2ee16cf1e544e693670cff'
    challenge_msg_hex = '46ecf87ce0cf1096ca0ff82b6c5220d75ae097ed445d069a246fdb21ed7f3341'
    
    # Curve order for NIST P-256
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    # Parse signatures
    r1 = int(sig1_hex[:64], 16)
    s1 = int(sig1_hex[64:], 16)
    r2 = int(sig2_hex[:64], 16)
    s2 = int(sig2_hex[64:], 16)
    # r should be equal
    if r1 != r2:
        raise ValueError('r values differ')
    r = r1
    
    # Parse message hashes
    z1 = int(z1_hex, 16)
    z2 = int(z2_hex, 16)
    
    # Compute nonce k
    s_diff = (s1 - s2) % n
    z_diff = (z1 - z2) % n
    k = (z_diff * pow(s_diff, -1, n)) % n
    
    # Compute private key d
    d = ((s1 * k - z1) * pow(r, -1, n)) % n
    
    # Recover signature over challenge message
    start = time.monotonic_ns()
    key = ECC.construct(curve='NIST P-256', d=d)
    signer = DSS.new(key, 'fips-186-3')
    challenge_msg = bytes.fromhex(challenge_msg_hex)
    signature = signer.sign(SHA256.new(challenge_msg))
    end = time.monotonic_ns()
    
    # Format outputs
    d_hex = format(d, '064x')
    sig_hex = signature.hex()
    
    # Optional opspan
    print(f'OPSPAN_NS:{end - start}')
    sys.stdout.flush()
    
    # Final claim
    claim = {'d_hex': d_hex, 'sig_hex': sig_hex}
    print(f'CLAIM:{json.dumps(claim)}')
    sys.stdout.flush()

if __name__ == '__main__':
    import json
    main()