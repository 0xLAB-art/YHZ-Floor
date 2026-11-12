import sys, time, json
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

# Provisioned material
provision = {
    "sig1_hex": "9c0b581bae769c94e4adc95ee9835487d9594685b5686ae0c30b419269c64683b254e115fa9d11923fff7fae60b7ba154c5126f76384a150f3d1dae7e64ca397",
    "sig2_hex": "9c0b581bae769c94e4adc95ee9835487d9594685b5686ae0c30b419269c64683b317e3c182eb5b96290cb20ee26bbd8cb1724fc3c2834d663b73abcc11028dc5",
    "z1_hex": "7d4e5c3a513a3a18d990c5fa91edd0c201c7e64de3391c08ff9a07bef91ed799",
    "z2_hex": "6b61940555d8299b59c9958a0308423c8718a8c9309422ec3ca0ae296ead1279",
    "challenge_msg_hex": "529c5822113481396e491294e9a0dfba97c6d5ff310f134602ddfafa70aa460f",
    "curve": "NIST P-256"
}

sig1_hex = provision["sig1_hex"]
sig2_hex = provision["sig2_hex"]
z1_hex = provision["z1_hex"]
z2_hex = provision["z2_hex"]
challenge_msg_hex = provision["challenge_msg_hex"]

# Extract r, s1, s2
r = int(sig1_hex[:64], 16)
s1 = int(sig1_hex[64:], 16)
s2 = int(sig2_hex[64:], 16)
z1 = int(z1_hex, 16)
z2 = int(z2_hex, 16)

# Curve order for NIST P-256
curve = ECC.construct(curve='P-256')
n = curve.order

# Compute k and private key d
delta_s = (s1 - s2) % n
delta_z = (z1 - z2) % n
k = (delta_z * pow(delta_s, -1, n)) % n
d = ((s1 * k - z1) % n) * pow(r, -1, n) % n

# Construct private key
private_key = ECC.construct(curve='P-256', d=d)

# Sign challenge message
msg = bytes.fromhex(challenge_msg_hex)
hash_obj = SHA256.new(msg)
signer = DSS.new(private_key, 'fips-186-3')
start = time.monotonic_ns()
signature = signer.sign(hash_obj)
end = time.monotonic_ns()

sig_hex = signature.hex()
d_hex = format(d, '064x')

# Output OPSPAN and CLAIM
print(f"OPSPAN_NS:{end-start}")
sys.stdout.flush()
claim = {"d_hex": d_hex, "sig_hex": sig_hex}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()