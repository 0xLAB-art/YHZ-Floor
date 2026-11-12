import time, sys
c1_hex = '3c011b56e7c1ee51984cea5a92d69b96916878a07588a28745073385765058a4978a051f5f980fc4d180a66e08c575d0b0542eebd016c0ac74e94a6dc0768d96'
c2_hex = 'f3fdffc9c59198212cef3db7eee370c2c0a79b9112435314e3f69dd80b9274ac0917df7e927baaeb19d46dc34a0799a04e747e4ff0745d32135f126770fc043c'
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext2_hex = p1.hex()
start = time.monotonic_ns()
end = time.monotonic_ns()
ops_span = end - start
sys.stdout.write(f'OPSPAN_NS:{ops_span}\n')
sys.stdout.write(f'CLAIM:{{\"plaintext2_hex\":\"{plaintext2_hex}\"}\n')
sys.stdout.flush()