import sys, time, json
start = time.monotonic_ns()
c1_hex = '...'
c2_hex = '...'
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext2_hex = p1.hex()
elapsed = time.monotonic_ns() - start
print('OPSPAN_NS:%d' % elapsed)
print('CLAIM:' + json.dumps({'plaintext2_hex': plaintext2_hex}))
sys.stdout.flush()