import base64, hashlib

with open('README.md', 'rb') as f:
    raw = f.read()

try:
    decoded = base64.b64decode(raw)
except Exception:
    decoded = raw

text = decoded.decode('utf-8', errors='replace')

hash_hex = 'a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c'

# The "salt" is the hash method name. Try common hash algorithms.
# The challenge says: if the hash is of the word `example`, submit `flag{{example}}`.
# So we need to find a word W such that hashlib.<method>(W).hexdigest() == hash_hex.

# Try standard algorithms with a small dictionary of common words.
words = ['example', 'password', 'test', 'secret', 'flag', 'ctf', 'challenge',
         'crack', 'hash', 'md5', 'sha1', 'sha256', 'ripemd128', 'ripemd160',
         'sha512', 'sha224', 'sha384', 'blake2b', 'blake2s', 'whirlpool',
         'tiger', 'md4', 'md2', 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
         'shake_128', 'shake_256', 'gost', 'sm3', 'crc32']

methods = [
    ('md5', hashlib.md5),
    ('sha1', hashlib.sha1),
    ('sha256', hashlib.sha256),
    ('sha512', hashlib.sha512),
    ('sha224', hashlib.sha224),
    ('sha384', hashlib.sha384),
    ('ripemd128', hashlib.new('ripemd128') if 'ripemd128' in hashlib.algorithms_available else None),
    ('ripemd160', hashlib.new('ripemd160') if 'ripemd160' in hashlib.algorithms_available else None),
    ('whirlpool', hashlib.new('whirlpool') if 'whirlpool' in hashlib.algorithms_available else None),
    ('blake2b', hashlib.blake2b),
    ('blake2s', hashlib.blake2s),
    ('sha3_224', hashlib.sha3_224),
    ('sha3_256', hashlib.sha3_256),
    ('sha3_384', hashlib.sha3_384),
    ('sha3_512', hashlib.sha3_512),
    ('md4', hashlib.md4),
    ('tiger192', hashlib.new('tiger192') if 'tiger192' in hashlib.algorithms_available else None),
    ('tiger160', hashlib.new('tiger160') if 'tiger160' in hashlib.algorithms_available else None),
    ('tiger', hashlib.new('tiger') if 'tiger' in hashlib.algorithms_available else None),
]

found = None
for method_name, method in methods:
    if method is None:
        continue
    for w in words:
        h = method(w.encode('utf-8')).hexdigest()
        if h == hash_hex:
            found = ('flag{{' + w + '}}', method_name)
            break
    if found:
        break

if found:
    print(found[0])
else:
    # Fallback: try all lowercase words from a larger list if available
    import string as _string
    more = []
    for w in words:
        more.append(w)
    # Try single and double letter combos
    for c1 in _string.ascii_lowercase:
        for c2 in _string.ascii_lowercase:
            more.append(c1 + c2)
    for c1 in _string.ascii_lowercase:
        for c2 in _string.ascii_lowercase:
            for c3 in _string.ascii_lowercase:
                more.append(c1 + c2 + c3)
    for method_name, method in methods:
        if method is None:
            continue
        for w in more:
            h = method(w.encode('utf-8')).hexdigest()
            if h == hash_hex:
                print('flag{{' + w + '}}')
                found = True
                break
        if found:
            break
    if not found:
        print('flag{{unknown}}')