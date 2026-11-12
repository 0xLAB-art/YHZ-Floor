import sys, json, base64, hashlib, select

PROV = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
P = int(PROV.get('dh_p_hex', '0'), 16)
G = int(PROV.get('dh_g_hex', '2'), 16)
SP = int(PROV.get('server_pub_hex', '0'), 16)

def log(s):
    sys.stdout.write(str(s) + '\n')
    sys.stdout.flush()

def send(obj):
    sys.stdout.write(json.dumps(obj) + '\n')
    sys.stdout.flush()

def recv(timeout=10):
    try:
        r, _, _ = select.select([sys.stdin], [], [], timeout)
    except Exception:
        return None
    if not r:
        return None
    try:
        line = sys.stdin.readline()
    except Exception:
        return None
    if not line:
        return None
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return {'raw': line[:4000]}

def http(method, path, body=None, headers=None, body_hex=None):
    msg = {'http': {'method': method, 'path': path}}
    if body is not None:
        msg['http']['body'] = body
    if body_hex is not None:
        msg['http']['body_hex'] = body_hex
    if headers:
        msg['http']['headers'] = headers
    send(msg)
    return recv()

def btext(rep):
    if not isinstance(rep, dict):
        return ''
    if 'body_b64' in rep:
        try:
            return base64.b64decode(rep['body_b64']).decode('utf-8', 'replace')
        except Exception:
            return ''
    if 'body' in rep:
        return str(rep['body'])
    return json.dumps(rep)[:4000]

def leaves(o, path='', out=None):
    if out is None:
        out = []
    if isinstance(o, dict):
        for k, v in o.items():
            leaves(v, path + '/' + str(k), out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            leaves(v, path + '/[%d]' % i, out)
    else:
        out.append((path, str(o)))
    return out

def hx(i):
    s = '%x' % i
    return s

B = 0x2a2a2a2a2a
PUB = pow(G, B, P)
SHARED = pow(SP, B, P)
PUB_HEX = hx(PUB)
SHARED_HEX = hx(SHARED)

WEAK = ['diffie-hellman-group1-sha1', 'diffie-hellman-group-exchange-sha1',
        'diffie-hellman-group-exchange-sha256', 'diffie-hellman-group14-sha1',
        'diffie-hellman-group14-sha256', 'diffie-hellman-group15-sha512',
        'diffie-hellman-group14-sha256@ssh.com', 'curve25519-sha256',
        'diffie-hellman-group1-sha1@openssh.com']

body = json.dumps({'kex_algos': WEAK, 'client_algos': WEAK, 'algorithms': WEAK,
                   'proposed_algorithms': WEAK, 'kex_algorithms': WEAK,
                   'server_algos': WEAK, 'algorithms_by_key': WEAK,
                   'client_pub_hex': PUB_HEX, 'client_public_key_hex': PUB_HEX,
                   'client_public': PUB_HEX, 'e': PUB_HEX, 'y': PUB_HEX,
                   'dh_p_hex': PROV.get('dh_p_hex'), 'dh_g_hex': PROV.get('dh_g_hex'),
                   'b_hex': hx(B), 'username': 'user', 'service': 'ssh-connection'})

log('PUB_HEX=' + PUB_HEX)
log('SHARED_HEX=' + SHARED_HEX)
log('PROV=' + json.dumps(PROV))

found_kex = None
found_shared = None

for pth in ['/', '/health', '/api', '/ssh', '/kex', '/version', '/openapi.json', '/docs', '/status']:
    r = http('GET', pth)
    if r is None:
        log('OBS GET ' + pth + ' -> NOREPLY')
        break
    log('OBS GET ' + pth + ' -> ' + json.dumps(r)[:1500])
    t = btext(r)
    try:
        o = json.loads(t)
    except Exception:
        o = None
    if isinstance(o, dict):
        for kp, v in leaves(o):
            kk = kp.lower()
            if found_kex is None and ('kex_algo' in kk or 'negotiated' in kk) and 'sha' in v:
                found_kex = v
            if found_shared is None and 'shared' in kk:
                try:
                    found_shared = '%x' % int(v, 16)
                except Exception:
                    found_shared = v

if found_kex is None:
    for pth in ['/kex', '/ssh/kex', '/api/kex', '/handshake', '/ssh/handshake', '/negotiate',
                '/ssh', '/api/handshake', '/session', '/exchange', '/kexinit', '/api/v1/kex',
                '/ssh/kexinit', '/connect', '/api/ssh/kex', '/negotiate/kex']:
        r = http('POST', pth, body=body, headers={'Content-Type': 'application/json'})
        if r is None:
            log('OBS POST ' + pth + ' -> NOREPLY')
            break
        log('OBS POST ' + pth + ' -> ' + json.dumps(r)[:2500])
        t = btext(r)
        try:
            o = json.loads(t)
        except Exception:
            o = None
        if isinstance(o, dict):
            for kp, v in leaves(o):
                kk = kp.lower()
                if found_kex is None and ('kex' in kk or 'negotiat' in kk) and 'sha' in v:
                    found_kex = v
                if 'shared' in kk and found_shared is None:
                    try:
                        found_shared = '%x' % int(v, 16)
                    except Exception:
                        found_shared = v
        if found_kex and found_shared:
            log('HIT at ' + pth)
            break

log('FOUND_KEX=' + str(found_kex))
log('FOUND_SHARED=' + str(found_shared))

if found_kex and found_shared:
    proof = hashlib.sha256((found_kex + found_shared).encode()).hexdigest()
    log('CLAIM:{"proof_hex": "%s", "kex_algo": "%s", "client_pub_hex": "%s"}' % (proof, found_kex, PUB_HEX))
else:
    log('NO_CLAIM_RECON_ONLY')