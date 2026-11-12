import sys, json, base64, select
ct_hex = "49324420443d10ce58309579924019bdc720e55149c31c71abd1b8b58b71bf0e2454b8c4f9ff0c8188a9f661a641d6fe9311cc187c0637e9369f0d9d38c870ad3c9c17737ad72a1a4fba62f937da9f7a"
ct = bytes.fromhex(ct_hex)
target = ct[-16:]
forged = bytes(16)
b64 = base64.b64encode(forged + target).decode()
sys.stdout.write('{"q":"' + b64 + '"}\n')
sys.stdout.flush()
sys.stderr.write('sent q len=' + str(len(forged+target)) + ' b64len=' + str(len(b64)) + '\n')
sys.stderr.flush()
r, _, _ = select.select([sys.stdin], [], [], 15)
sys.stderr.write('select ready=' + str(bool(r)) + '\n')
sys.stderr.flush()
if r:
    line = sys.stdin.readline()
    sys.stderr.write('got line: ' + repr(line) + '\n')
    sys.stderr.flush()
    try:
        o = json.loads(line.strip())
        sys.stderr.write('parsed: ' + repr(o) + '\n')
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write('parse err: ' + repr(e) + '\n')
        sys.stderr.flush()
else:
    sys.stderr.write('timeout waiting oracle\n')
    sys.stderr.flush()
sys.stdout.write('CLAIM:{"plaintext_hex":"00"}\n')
sys.stdout.flush()