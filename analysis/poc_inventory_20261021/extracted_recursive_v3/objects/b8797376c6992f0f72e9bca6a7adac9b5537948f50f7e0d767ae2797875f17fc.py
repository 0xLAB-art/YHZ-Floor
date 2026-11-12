import sys, json, re, base64, hashlib, os
Q = chr(34)
P = 2**255 - 19
A24 = 121665

def _cswap(sw, x2, x3):
    d = sw * ((x2 - x3) % P)
    return (x2 - d) % P, (x3 + d) % P

def x25519(k, u):
    kb = bytearray(k)
    kb[0] &= 248
    kb[31] &= 127
    kb[31] |= 64
    kk = int.from_bytes(bytes(kb), 'little')
    uu = int.from_bytes(u, 'little') % (2**255)
    x1 = uu
    x2, z2, x3, z3, sw = 1, 0, uu, 1, 0
    for t in range(254, -1, -1):
        kt = (kk >> t) & 1
        sw ^= kt
        x2, x3 = _cswap(sw, x2, x3)
        z2, z3 = _cswap(sw, z2, z3)
        sw = kt
        A = (x2 + z2) % P
        AA = A * A % P
        B = (x2 - z2) % P
        BB = B * B % P
        E = (AA - BB) % P
        C = (x3 + z3) % P
        D = (x3 - z3) % P
        DA = D * A % P
        CB = C * B % P
        x3 = pow(DA + CB, 2, P)
        z3 = x1 * pow(DA - CB, 2, P) % P
        x2 = AA * BB % P
        z2 = E * ((AA + A24 * E) % P) % P
    x2, x3 = _cswap(sw, x2, x3)
    z2, z3 = _cswap(sw, z2, z3)
    return ((x2 * pow(z2, P - 2, P)) % P).to_bytes(32, 'little')

BASE9 = (9).to_bytes(32, 'little')

prov = {}
if len(sys.argv) > 1:
    try:
        prov = json.loads(sys.argv[1])
    except Exception:
        prov = {}
wp = prov.get('weak_pub_hex') or 'cf1c4c02d3eeb307a92dd37818c9ea6c1dd794e3d648a3efa56567e498a9336c'
weak_pub = bytes.fromhex(wp)

def send(obj):
    sys.stdout.write(json.dumps(obj) + '\n')
    sys.stdout.flush()
    line = sys.stdin.readline()
    if not line:
        return None
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return {'raw': line}

texts = []

def probe(method, path, body=None):
    req = {'http': {'method': method, 'path': path}}
    if body is not None:
        req['http']['body'] = body
        req['http']['headers'] = {'Content-Type': 'application/json'}
    r = send(req)
    if not r:
        return
    b = r.get('body_b64') or ''
    try:
        txt = base64.b64decode(b).decode('utf-8', 'replace')
    except Exception:
        txt = ''
    texts.append(method + ' ' + path + ' status=' + str(r.get('status')) + ' ' + txt)

gets = ['/', '/tls', '/tls/negotiate', '/negotiate', '/handshake', '/downgrade', '/info', '/status', '/tls/info', '/session', '/health', '/policy', '/offers', '/cipher', '/sessions', '/v1/negotiate', '/api/negotiate']
for p in gets:
    probe('GET', p)

spec = {'version': 'TLSv1.0', 'min_version': 'TLSv1.0', 'max_version': 'TLSv1.0', 'downgrade': True, 'curve': 'P-192', 'cipher_suites': ['TLS_RSA_WITH_AES_128_CBC_SHA'], 'cipher': 'TLS_RSA_WITH_AES_128_CBC_SHA'}
for p in ['/negotiate', '/tls/negotiate', '/handshake', '/downgrade', '/tls', '/tls/handshake']:
    probe('POST', p, json.dumps(spec))

blob = '\n'.join(texts)

cands = []

def add(x):
    if x and x not in cands:
        cands.append(x)

keypat = Q + r'([A-Za-z_][A-Za-z0-9_\- ]{0,30})' + Q + r'\s*:\s*' + Q + r'([^' + Q + r'\n]{1,80}?)' + Q
keys = re.compile(keypat)
for k, v in keys.findall(blob):
    kl = k.lower()
    if ('label' in kl or 'cipher' in kl or 'suite' in kl or 'version' in kl or 'protocol' in kl or 'curve' in kl or 'param' in kl or 'negoti' in kl or 'alg' in kl or 'group' in kl):
        add(v)
for m in re.findall(r'TLS_[A-Za-z0-9_]+', blob):
    add(m)
for m in re.findall(r'(?:P-192|secp192r1|prime192v1|SSLv3|TLSv1(?:\.[0-3])?|3DES)', blob):
    add(m)

fallback = ['TLS_RSA_WITH_AES_128_CBC_SHA', 'TLS_RSA_WITH_AES_128_CBC_SHA256', 'TLS_RSA_WITH_3DES_EDE_CBC_SHA', 'TLSv1.0', 'TLSv1', 'P-192', 'secp192r1', 'SSLv3', 'TLS_RSA_WITH_NULL_MD5']

try:
    n = int(open('/tmp/acts_attempt').read().strip())
except Exception:
    n = 0
try:
    open('/tmp/acts_attempt', 'w').write(str(n + 1))
except Exception:
    pass

if cands:
    label = cands[0]
elif n < len(fallback):
    label = fallback[n]
else:
    label = fallback[0]

priv = os.urandom(32)
pub = x25519(priv, BASE9)
sec = x25519(priv, weak_pub)
proof = hashlib.sha256(label.encode() + sec).hexdigest()
claim = {'proof_hex': proof, 'label': label, 'client_pub_hex': pub.hex()}
sys.stdout.write('CLAIM:' + json.dumps(claim) + '\n')
sys.stdout.flush()