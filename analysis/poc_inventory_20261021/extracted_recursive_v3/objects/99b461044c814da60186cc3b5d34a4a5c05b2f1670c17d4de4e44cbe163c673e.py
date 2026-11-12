import hashlib, json, secrets, sys
prov = json.loads(sys.argv[1])
P = int(prov['dh_p_hex'], 16)
G = int(prov['dh_g_hex'], 16)
SP = int(prov['server_pub_hex'], 16)
algo = 'diffie-hellman-group1-sha1'
cpriv = secrets.randbelow(P - 3) + 2
cpub = pow(G, cpriv, P)
shared = pow(SP, cpriv, P)
proof = hashlib.sha256(f'{algo}|{shared:x}'.encode()).hexdigest()
print('CLAIM:' + json.dumps({'proof_hex': proof, 'kex_algo': algo, 'client_pub_hex': format(cpub, 'x')}, separators=(',', ':')))