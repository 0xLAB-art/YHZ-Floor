import sys, base64, os, select
ct_hex = '1f183c1a58d29333f0a5212c74339c348364861f54bde3f0c64797e9b96609a776e072356f6ee8d40e3b68bd0533113ab194df815b01bc1dbf13717cbeb710d79b1bdb0599aa16a0373e967d8453d560'
ct = bytes.fromhex(ct_hex)
tgt = ct[0:16]
fp = bytes(16)
s = base64.b64encode(fp + tgt).decode()
sys.stdout.write('{\u0022q\u0022:\u0022' + s + '\u0022}\n')
sys.stdout.flush()
sys.stderr.write('sent\n')
sys.stderr.flush()
r, _, _ = select.select([sys.stdin], [], [], 10)
sys.stderr.write('ready=' + str(bool(r)) + '\n')
sys.stderr.flush()
if r:
  d = os.read(0, 65536)
  sys.stderr.write('got=' + repr(d) + '\n')
  sys.stderr.flush()
else:
  sys.stderr.write('timeout\n')
  sys.stderr.flush()
sys.stdout.write('CLAIM:{\u0022plaintext_hex\u0022:\u002200' * 1 + '\n')