import time
c1 = bytes.fromhex('41eb9609d823272c2516a288954010c4b6dfe4d0ad87ba4a1680504ce8ed7cf2a74faf13c4d771ee766b38dde8fe877297a3f5714e2275383e2e94f57fc0a2c9')
c2 = bytes.fromhex('97e4e16f41e91bf9d31607f116b9dbde80d943493f800c939e9ea75527b9ae88b31a1b4ab01f8b1518d717e21611dc949d7ffdf30d5f656682d00c2dd53a2d80')
t0 = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(c1, c2))
dt = time.monotonic_ns() - t0
print('OPSPAN_NS:%d' % dt)
print('CLAIM:' + __import__('json').dumps({'plaintext_hex': p1.hex()}))