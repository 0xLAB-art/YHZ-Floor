import time
t0 = time.monotonic_ns()
c1 = bytes.fromhex('e0f585a5b799754e75fef040a82011892feed1b8a5d6adb671e2e22c46a1be630c8a3b73a03967cb4ae04a1a6d77564098f101eeeefd6159412de93b52ee4351')
c2 = bytes.fromhex('cbd90e141becfa3027d209210f8306f55c45c702fd38d5367423d639a932c0da5699aaa8769e544107ad80ce0b77299fce4d9486f7864fab3d349310b598271e')
assert len(c1) == len(c2) == 64
p1 = bytes(a ^ b for a, b in zip(c1, c2))
t1 = time.monotonic_ns()
print('OPSPAN_NS:' + str(t1 - t0))
print('CLAIM:' + '{"plaintext2_hex": "' + p1.hex() + '"}')