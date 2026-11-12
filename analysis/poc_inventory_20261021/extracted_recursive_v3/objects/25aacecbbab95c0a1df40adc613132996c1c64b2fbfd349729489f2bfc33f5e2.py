import json, hashlib, time, sys
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def main():
    start = time.monotonic_ns()
    data = json.loads('''{
  "sig1_hex": "cdb7a0aee0e2bcb8cb0573a9538ac4b5724d16678a7ff89cc4847ed3e680f92abb4b44e49e21ee0e438840b476e56e6a64fe2155eba9081b0e8822789bf633a5",
  "sig2_hex": "cdb7a0aee0e2bcb8cb0573a9538ac4b5724d16678a7ff89cc4847ed3e680f92a41ac7792fd7c66a0d13a1faa32790e6296e5775de07ab17b85544c63dc1b3206",
  "z1_hex": "df47f4baae47903e9c79298ca440406f348a8b646277691a4fed88e60ea04711",
  "z2_hex": "3b40c126738a6e115c260b756b819587ae2c2b03165ecf6f8ed213be11edd5c6",
  "challenge_msg_hex": "38b8313f98da7fa0124bfd82adb208ba02544f6212be4712e4f7c9089fd82303",
  "curve": "NIST P-256"
}''')
    sig1 = bytes.fromhex(data['sig1_hex'])
    sig2 = bytes.fromhex(data['sig2_hex'])
    z1 = int(data['z1_hex'], 16)
    z2 = int(data['z2_hex'], 16)
    challenge = bytes.fromhex(data['challenge_msg_hex'])
    # r is first 32 bytes, s is next 32 bytes
    r = int.from_bytes(sig1[:32], 'big')
    s1 = int.from_bytes(sig1[32:], 'big')
    s2 = int.from_bytes(sig2[32:], 'big')
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    s1_minus_s2 = (s1 - s2) % n
    z1_minus_z2 = (z1 - z2) % n
    k = (z1_minus_z2 * pow(s1_minus_s2, -1, n)) % n
    r_inv = pow(r, -1, n)
    d = ((s1 * k - z1) % n) * r_inv % n
    d = d % n
    priv_key = ECC.construct(curve='P-256', d=d)
    signer = DSS.new(priv_key, 'fips-186-3')
    h = SHA256.new(challenge)
    signature = signer.sign(h)
    sig_hex = signature.hex()
    d_hex = format(d, '064x')
    claim = {"d_hex": d_hex, "sig_hex": sig_hex}
    end = time.monotonic_ns()
    span = end - start
    print(f'OPSPAN_NS:{span}')
    print(f'CLAIM:{json.dumps(claim)}')
    sys.stdout.flush()

if __name__ == '__main__':
    main()