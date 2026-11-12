import base64, hashlib

with open('README.md', 'rb') as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
except Exception:
    decoded = raw

text = decoded.decode('utf-8', errors='replace')

hash_hex = 'a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c'

# Try common hash algorithms with the algorithm name as salt
for algo in ['md5', 'sha1', 'sha256', 'sha512', 'sha224', 'sha384',
             'blake2b', 'blake2s', 'ripemd128', 'ripemd160', 'whirlpool',
             'tiger', 'gost', 'md4', 'md5-sha1', 'sha3_224', 'sha3_256',
             'sha3_384', 'sha3_512', 'shake_128', 'shake_256']:
    try:
        h = hashlib.new(algo)
    except ValueError:
        continue
    h.update(algo.encode('utf-8'))
    if h.hexdigest() == hash_hex:
        print('flag{{' + algo + '}}')
        break
else:
    print('flag{{' + hash_hex + '}}')