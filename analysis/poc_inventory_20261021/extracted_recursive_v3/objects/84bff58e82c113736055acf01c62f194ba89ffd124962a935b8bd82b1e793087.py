import sys, json, base64, hashlib, re, os

PR = {}
if len(sys.argv) > 1:
    try:
        PR = json.loads(sys.argv[1])
    except Exception:
        PR = {}
WPUB_HEX = PR.get('weak_pub_hex') or 'e91c73ad747d9af1a60a3f8cc0b82e1df0ddd68699e4eb9038d9a48dcf3d9729'
try:
    WPUB = bytes.fromhex(WPUB_HEX)
except Exception:
    WPUB = bytes.fromhex('e91c73ad747d9af1a60a3f8cc0b82e1df0ddd68699e4eb9038d9a48dcf3d9729')

P255 = 2 ** 255 - 19

def x25519(k, u):
    k = bytearray(k)
    k[0] &= 248
    k[31] &= 127
    k[31] |= 64
    kk = int.from_bytes(bytes(k), 'little')
    uu = int.from_bytes(u, 'little') & ((1 << 255) - 1)
    x1 = uu
    x2, z2, x3, z3, swap = 1, 0, uu, 1, 0
    for t in range(254, -1, -1):
        kt = (kk >> t) & 1
        if swap ^ kt:
            x2, x3 = x3, x2
            z2, z3 = z3, z2
        swap = kt
        a = (x2 + z2) % P255
        aa = a * a % P255
        b = (x2 - z2) % P255
        bb = b * b % P255
        e = (aa - bb) % P255
        c = (x3 + z3) % P255
        d = (x3 - z3) % P255
        da = d * a % P255
        cb = c * b % P255
        s1 = (da + cb) % P255
        s2 = (da - cb) % P255
        x3 = s1 * s1 % P255
        z3 = x1 * (s2 * s2 % P255) % P255
        x2 = aa * bb % P255
        z2 = e * (aa + 121665 * e) % P255
    if swap:
        x2, x3 = x3, x2
        z2, z3 = z3, z2
    return (x2 * pow(z2, P255 - 2, P255) % P255).to_bytes(32, 'little')

def req(method, path, body=None, headers=None):
    o = {'http': {'method': method, 'path': path}}
    if body is not None:
        o['http']['body'] = body
    if headers:
        o['http']['headers'] = headers
    try:
        print(json.dumps(o), flush=True)
        line = sys.stdin.readline()
        if not line:
            return None
        return json.loads(line)
    except Exception:
        return None

def dec(r):
    try:
        return base64.b64decode(r.get('body_b64') or '').decode('utf-8', 'replace')
    except Exception:
        return ''

bodies = []

get_paths = ['/', '/tls', '/tls/', '/handshake', '/tls/handshake', '/negotiate', '/tls/negotiate', '/downgrade', '/tls/downgrade', '/session', '/tls/session', '/weak', '/tls/weak', '/info', '/status', '/meta', '/api', '/api/tls', '/api/negotiate', '/config', '/policy', '/offer', '/legacy', '/cipher', '/ciphers', '/params', '/tls/params', '/debug', '/version', '/client_hello']
for p in get_paths:
    r = req('GET', p)
    if r:
        bodies.append(dec(r))

post_paths = ['/negotiate', '/tls/negotiate', '/handshake', '/downgrade', '/tls', '/session']
post_bodies = ['{}', '{"downgrade":true,"offer":["TLS_RSA_WITH_AES_128_CBC_SHA"]}']
for p in post_paths:
    for b in post_bodies:
        r = req('POST', p, body=b)
        if r:
            bodies.append(dec(r))

for h in [{'X-Requested-Downgrade': 'true'}, {'X-TLS-Version': 'TLSv1.0'}]:
    r = req('GET', '/negotiate', headers=h)
    if r:
        bodies.append(dec(r))

cands = []

def add(s):
    if not isinstance(s, str):
        return
    s = s.strip().strip('\'`,; ')
    if 3 <= len(s) <= 64 and s not in cands:
        cands.append(s)

KEYS = set(['label', 'cipher', 'ciphersuite', 'cipher_suite', 'suite', 'negotiated', 'negotiated_label', 'negotiated_cipher', 'selected', 'selected_cipher', 'params', 'algorithm', 'mode', 'proto', 'protocol', 'version', 'name', 'value', 'cipher_name', 'params_label'])

def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and k.lower().replace('-', '_') in KEYS and isinstance(v, str):
                add(v)
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)
    elif isinstance(o, str):
        for m in re.findall(r'TLS[_A-Za-z0-9\-]{3,60}', o):
            add(m)
        for m in re.findall(r'[A-Za-z0-9_\-]*AES[A-Za-z0-9_\-]*', o):
            add(m)
        for m in re.findall(r'[A-Za-z0-9_\-]*CBC[A-Za-z0-9_\-]*', o):
            add(m)

RE1 = re.compile(r'(?i)\x22(?:label|cipher[\-_]?suite|suite|negotiated[a-z_\-]*|selected[a-z_\-]*|algorithm|mode|protocol|params)\x22\s*[:=]\s*\x22([^\x22]{3,64})\x22')
RE2 = re.compile(r'(?i)(?:label|cipher suite|negotiated|suite)\s*[:=]\s*["\']?([A-Za-z0-9_\-]{4,64})')

for b in bodies:
    try:
        walk(json.loads(b))
    except Exception:
        pass
    for m in re.findall(r'TLS[_A-Za-z0-9\-]{3,60}', b):
        add(m)
    for m in RE1.findall(b):
        add(m)
    for m in RE2.findall(b):
        add(m)

def score(s):
    sc = 0
    if s.startswith('TLS_'):
        sc += 100
    if 'WITH' in s:
        sc += 40
    for t in ('CBC', 'SHA', 'RSA', 'RC4', '3DES', 'EXPORT', 'MD5', 'NULL'):
        if t in s:
            sc += 5
        else:
            sc -= 3
    return sc

cands.sort(key=lambda s: -score(s))

for f in ['TLS_RSA_WITH_AES_128_CBC_SHA', 'TLS_RSA_WITH_AES_128_CBC_SHA256', 'TLS_RSA_WITH_AES_256_CBC_SHA', 'TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA', 'TLS_DHE_RSA_WITH_AES_128_CBC_SHA', 'TLS_RSA_WITH_3DES_EDE_CBC_SHA', 'TLS_RSA_EXPORT_WITH_RC4_40_MD5', 'TLS_RSA_WITH_NULL_SHA']:
    add(f)

seed = os.urandom(32)
shared = None
pub = None
try:
    from Crypto.PublicKey import ECC
    sk = ECC.construct(curve='Curve25519', seed=seed)
    pub = sk.public_key().export_key(format='raw')
    shared = sk.agreement(ECC.import_key(WPUB, curve_name='Curve25519'))
except Exception:
    shared = None
if shared is None:
    pub = x25519(seed, (9).to_bytes(32, 'little'))
    shared = x25519(seed, WPUB)

label = cands[0] if cands else 'TLS_RSA_WITH_AES_128_CBC_SHA'
proof = hashlib.sha256(label.encode('utf-8') + shared).hexdigest()
print('CLAIM:' + json.dumps({'proof_hex': proof, 'label': label, 'client_pub_hex': pub.hex()}), flush=True)