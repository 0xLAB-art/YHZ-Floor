import hashlib
import json
import base64

with open('README.md', 'rb') as f:
    data = f.read()

try:
    decoded = base64.b64decode(data).decode('utf-8')
except Exception:
    decoded = data.decode('utf-8')

hash_hex = 'a60458d2180258d47d7f7bef5236b33e86711ac926518ca4545ebf24cdc0b76c'

# Try common hash algorithms with lowercase names as salts
algorithms = [
    'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
    'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
    'blake2b', 'blake2s', 'sha512_224', 'sha512_256',
    'sha3_224', 'shake_128', 'shake_256',
    'ripemd128', 'ripemd160', 'whirlpool', 'tiger', 'md4',
    'md5-sha1', 'sha1', 'gost', 'gost-crypto', 'sm3',
]

for algo in algorithms:
    try:
        h = hashlib.new(algo)
        h.update(b'')
        # Try empty string as candidate
        if h.hexdigest() == hash_hex:
            print(f'flag{{{algo}}}')
            break
    except Exception:
        pass

# Also try common words as candidates with each algorithm
import string
common_words = ['password', 'password1', '123456', '12345678', 'qwerty', 'abc123',
                'letmein', 'monkey', 'dragon', 'master', 'login', 'admin',
                'example', 'test', 'pass', 'secret', 'hash', 'flag', 'ctf',
                'crack', 'me', 'hello', 'world', 'welcome', 'iloveyou',
                '123456789', '1234567890', '000000', '111111', '123123',
                'password123', 'admin123', 'root', 'toor', 'passw0rd',
                'shadow', 'matrix', 'trustno1', 'superman', 'batman',
                'football', 'baseball', 'soccer', 'hockey', 'starwars',
                'monkey', 'shadow', 'sunshine', 'princess', 'qwertyuiop',
                '1234567', '1234567890', '123456789', '12345678', '1234567',
                '123456', '12345', '1234', '123', '12', '1', '0',
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                'u', 'v', 'w', 'x', 'y', 'z',
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                'U', 'V', 'W', 'X', 'Y', 'Z',
                '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
                '-', '_', '=', '+', '[', ']', '{', '}', '|', '\\',
                ';', ':', "'", '"', ',', '.', '/', '?', '~', '`']

found = False
for algo in algorithms:
    if found:
        break
    try:
        h = hashlib.new(algo)
        for word in common_words:
            h.update(word.encode('utf-8'))
            if h.hexdigest() == hash_hex:
                print(f'flag{{{word}}}')
                found = True
                break
    except Exception:
        pass

if not found:
    # Try the algorithm name itself as the password
    for algo in algorithms:
        try:
            h = hashlib.new(algo)
            h.update(algo.encode('utf-8'))
            if h.hexdigest() == hash_hex:
                print(f'flag{{{algo}}}')
                found = True
                break
        except Exception:
            pass
