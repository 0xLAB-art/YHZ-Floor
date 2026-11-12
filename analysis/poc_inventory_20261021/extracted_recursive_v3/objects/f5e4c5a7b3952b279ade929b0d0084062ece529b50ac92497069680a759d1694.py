import sys, json, hashlib, time
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

def modinv(a, n):
    return pow(a, -1, n)

def parse_der_sig(sig_bytes):
    if sig_bytes[0] != 0x30:
        raise ValueError('Invalid SEQUENCE')
    length = sig_bytes[1]
    if length & 0x80:
        nlen = length & 0x7F
        length = int.from_bytes(sig_bytes[2:2+nlen], 'big')
        idx = 2 + nlen
    else:
        idx = 2
    if sig_bytes[idx] != 0x02:
        raise ValueError('Expected INTEGER')
    idx += 1
    rlen = sig_bytes[idx]
    idx += 1
    r = int.from_bytes(sig_bytes[idx:idx+rlen], 'big')
    idx += rlen
    if sig_bytes[idx] != 0x02:
        raise ValueError('Expected INTEGER')
    idx += 1
    slen = sig_bytes[idx]
    idx += 1
    s = int.from_bytes(sig_bytes[idx:idx+slen], 'big')
    return r, s

def main():
    data = json.loads(sys.stdin.read().strip())
    sig1_hex = data['sig1_hex']
    sig2_hex = data['sig2_hex']
    z1_hex = data['z1_hex']
    z2_hex = data['z2_hex']
    challenge_msg_hex = data['challenge_msg_hex']
    curve_name = data['curve']
    
    r = int(sig1_hex[:64], 16)
    s1 = int(sig1_hex[64:], 16)
    s2 = int(sig2_hex[64:], 16)
    z1 = int(z1_hex, 16)
    z2 = int(z2_hex, 16)
    
    n = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
    
    s1_minus_s2 = (s1 - s2) % n
    z1_minus_z2 = (z1 - z2) % n
    inv = modinv(s1_minus_s2, n)
    k = (z1_minus_z2 * inv) % n
    r_inv = modinv(r, n)
    d = ((s1 * k - z1) % n) * r_inv % n
    
    if d == 0 or d >= n:
        raise ValueError('Invalid private key')
    
    start = time.monotonic_ns()
    private_key = ECC.construct(curve='P-256', d=d)
    signer = DSS.new(private_key, 'fips-186-3')
    msg_hash = SHA256.new(bytes.fromhex(challenge_msg_hex))
    sig_der = signer.sign(msg_hash)
    end = time.monotonic_ns()
    
    r_sig, s_sig = parse_der_sig(sig_der)
    if s_sig > n // 2:
        s_sig = n - s_sig
    r_hex = format(r_sig, '064x')
    s_hex = format(s_sig, '064x')
    sig_hex = r_hex + s_hex
    d_hex = format(d, '064x')
    
    claim = json.dumps({'d_hex': d_hex, 'sig_hex': sig_hex})
    print('CLAIM:' + claim)
    print('OPSPAN_NS:' + str(end - start))
    sys.stdout.flush()

if __name__ == '__main__':
    main()