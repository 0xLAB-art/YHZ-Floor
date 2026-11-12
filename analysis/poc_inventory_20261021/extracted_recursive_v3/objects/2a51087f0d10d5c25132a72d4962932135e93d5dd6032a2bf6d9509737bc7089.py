import sys, json, os, hashlib
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.Util.asn1 import DerSequence

def main():
    # Debug: print stderr info
    sys.stderr.write('DEBUG: stdin raw: ')
    try:
        raw = sys.stdin.read()
        sys.stderr.write(repr(raw) + '\n')
    except Exception as e:
        sys.stderr.write('Error reading stdin: ' + str(e) + '\n')
    sys.stderr.write('DEBUG: argv: ' + str(sys.argv) + '\n')
    # Filter env to avoid huge output
    relevant = {k:v for k,v in os.environ.items() if 'PROV' in k or 'SIG' in k or 'Z' in k or 'CHAL' in k}
    sys.stderr.write('DEBUG: relevant env: ' + str(relevant) + '\n')
    
    # If we got raw JSON, use it
    data = None
    if raw.strip():
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            pass
    
    # If not, try to parse from environment variables
    if data is None:
        # Look for individual vars
        data = {}
        for key in ['sig1_hex','sig2_hex','z1_hex','z2_hex','challenge_msg_hex','curve']:
            if key in os.environ:
                data[key] = os.environ[key]
            else:
                # maybe they are prefixed
                pass
        if data:
            # check if we got all
            if len(data) == 6:
                pass
            else:
                data = None
    
    # If still None, use hardcoded values from the prompt (as fallback)
    if data is None:
        data = {
            'sig1_hex': '850c93459a5bc96cf089277618f8555e582eb6fb031136b5791d55a158bd7abe1bb024f0c796d41655683d9ea2b38a5741d1052dc1786bc258de324f8b339a21',
            'sig2_hex': '850c93459a5bc96cf089277618f8555e582eb6fb031136b5791d55a158bd7abe8c8e2204dff8c67f682189f396979293290e563a18920f844766fa1511e816d4',
            'z1_hex': '368010379fb7462d60c5c23d953a1efee4a40f884ab1a400f02b530ed42fdb4e',
            'z2_hex': 'e9883b9da1a5b2fbc3f04a00600f01a1f777252c26dbef16cac08bbcb152b774',
            'challenge_msg_hex': '0b819afde6ccabcefc120021215f83b3d71e976177d247312c2ee7eb610a43d2',
            'curve': 'NIST P-256'
        }
        sys.stderr.write('DEBUG: Using hardcoded values\n')
    
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
    sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()