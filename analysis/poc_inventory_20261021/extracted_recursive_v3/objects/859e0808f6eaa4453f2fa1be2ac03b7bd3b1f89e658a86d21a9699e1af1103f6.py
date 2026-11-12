import base64, hashlib, json, sys

def read_reply():
    line = sys.stdin.readline()
    return json.loads(line) if line else {}

def relay(method, path, body=None):
    obj = {'http': {'method': method, 'path': path, 'headers': {'Content-Type': 'application/json'}}}
    if body is not None:
        obj['http']['body'] = json.dumps(body)
    sys.stdout.write(json.dumps(obj) + '\n')
    sys.stdout.flush()
    return read_reply()

argv = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
p = int(argv['dh_p_hex'], 16)
g = int(argv['dh_g_hex'], 16)
server_pub = int(argv['server_pub_hex'], 16)
algo = 'diffie-hellman-group1-sha1'
cpriv = int.from_bytes(hashlib.sha256(b'acts-ssh-weak-client-v1').digest(), 'big') % (p - 3) + 2
cpub = pow(g, cpriv, p)
client_pub_hex = format(cpub, 'x')
relay('POST', '/exchange', {'kex_algo': algo, 'client_pub_hex': client_pub_hex})
shared = pow(server_pub, cpriv, p)
shared_hex = format(shared, 'x')
proof = hashlib.sha256((algo + '|' + shared_hex).encode()).hexdigest()
print('CLAIM:' + json.dumps({'proof_hex': proof, 'kex_algo': algo, 'client_pub_hex': client_pub_hex}, separators=(',', ':')))