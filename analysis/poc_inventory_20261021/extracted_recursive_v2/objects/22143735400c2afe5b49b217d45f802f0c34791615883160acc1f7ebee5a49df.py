import sys
import json
import base64

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

def int_to_hex(n):
    return format(n % (2**256), '064x')

data = json.load(open(sys.argv[1]))

Qx = bytes_to_int(base64.b64decode(data['public_key'][0]))
Qy = bytes_to_int(base64.b64decode(data['public_key'][1]))

r1 = bytes_to_int(base64.b64decode(data['signature_1']['r']))
s1 = bytes_to_int(base64.b64decode(data['signature_1']['s']))
z1 = bytes_to_int(base64.b64decode(data['signature_1']['z']))

r2 = bytes_to_int(base64.b64decode(data['signature_2']['r']))
s2 = bytes_to_int(base64.b64decode(data['signature_2']['s']))
z2 = bytes_to_int(base64.b64decode(data['signature_2']['z']))

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

s1_minus_s2 = (s1 - s2) % n
z1_minus_z2 = (z1 - z2) % n

k = (z1_minus_z2 * pow(s1_minus_s2, -1, n)) % n
d = ((s1 * k - z1) * pow(r1, -1, n)) % n

print(json.dumps({"d": int_to_hex(d), "k": int_to_hex(k)}))
