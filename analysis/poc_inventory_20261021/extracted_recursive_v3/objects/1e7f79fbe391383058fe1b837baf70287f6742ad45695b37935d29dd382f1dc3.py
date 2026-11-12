import sys, json, time

c1_hex = '785ea420f277f58b4d301cd76e8dca84b0803c534abf86ba4f7069888bbdeb1fdd05d5681577ff91ed42838a40828adacc3cd70acf58bd08760a7126f57557ee'
c2_hex = '3707b8594897b9b15e9b27edbf443d6971f2adced26a94802caed3cba4feef91c1e58d55fb271e379a385c28152276ee035092ffa72c1e6448629de5ab42d8e8'

b1 = bytes.fromhex(c1_hex)
b2 = bytes.fromhex(c2_hex)

start = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(b1, b2))
duration = time.monotonic_ns() - start

plaintext2_hex = p1.hex()

print(f'OPSPAN_NS:{duration}')
sys.stdout.flush()

claim = json.dumps({'plaintext2_hex': plaintext2_hex})
print(f'CLAIM:{claim}')
sys.stdout.flush()