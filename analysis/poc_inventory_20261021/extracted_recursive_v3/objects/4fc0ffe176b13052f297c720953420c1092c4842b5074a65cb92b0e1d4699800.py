import sys, json, hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.Util.asn1 import DerSequence

def main():
    data = json.load(sys.stdin)
    sig1_hex = data['sig1_hex']
    sig2_hex = data['sig2_hex']
    z1_hex = data['z1_hex']
    z2_hex = data['z2_hex']
    challenge_msg_hex = data['challenge_msg_hex']
    
    r_hex = sig1_hex[:64]
    s1_hex = sig1_hex[64:]
    s2_hex = sig2_hex[64:]
    
    r = int.from_bytes(bytes.fromhex(r_hex), 'big')
    s1 = int.from_bytes(bytes.fromhex(s1_hex), 'big')
    s2 = int.from_bytes(bytes.fromhex(s2_hex), 'big')
    z1 = int.from_bytes(bytes.fromhex(z1_hex), 'big')
    z2 = int.from_bytes(bytes.fromhex(z2_hex), 'big')
    
    curve = ECC.construct(curve='NIST P-256')
    n = curve.order
    
    diff_s = (s1 - s2) % n
    diff_z = (z1 - z2) % n
    k = (diff_z * pow(diff_s, -1, n)) % n
    
    d = ((s1 * k - z1) % n) * pow(r, -1, n) % n
    
    msg_bytes = bytes.fromhex(challenge_msg_hex)
    priv_key = ECC.construct(curve='NIST P-256', d=d)
    signer = DSS.new(priv_key, 'fips-186-3')
    h = SHA256.new(msg_bytes)
    sig_der = signer.sign(h)
    der_seq = DerSequence()
    der_seq.decode(sig_der)
    r_sig = der_seq[0]
    s_sig = der_seq[1]
    r_sig_bytes = r_sig.to_bytes((r_sig.bit_length() + 7) // 8, 'big').rjust(32, b'\x00')
    s_sig_bytes = s_sig.to_bytes((s_sig.bit_length() + 7) // 8, 'big').rjust(32, b'\x00')
    sig_bytes = r_sig_bytes + s_sig_bytes
    
    d_hex = format(d, '064x')
    sig_hex = sig_bytes.hex()
    claim = {"d_hex": d_hex, "sig_hex": sig_hex}
    print("CLAIM:" + json.dumps(claim))
    sys.stdout.flush()

if __name__ == "__main__":
    main()