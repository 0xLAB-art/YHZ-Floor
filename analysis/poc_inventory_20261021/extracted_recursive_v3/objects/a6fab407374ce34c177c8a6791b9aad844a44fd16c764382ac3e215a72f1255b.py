import sys, time, json

c1_hex = "45f3f611a981d2c6b8d89e5b2e78effe71346c6f05b91d88392c12757748d21af5d25d7372e76733afeb4b898aa6716669992591bbdd18cd9d242c97a63bc99c"
c2_hex = "b040918e0f603957bad4f5be16a0396831f1769d8c9f90be4d6fd8d463117b7dd2383de5d90c301e4c70d6d60d85ea9b7efe7f9d03a488865867c2fab7c116ac"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# Recover P1: since both are encrypted with same key/nonce, keystream is same.
# c2 = keystream XOR 0x00*64 = keystream
# c1 = keystream XOR P1
# Therefore P1 = c1 XOR c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext2_hex = p1.hex()

elapsed = time.monotonic_ns() - time.monotonic_ns()  # placeholder, but I'll measure properly

# Actually, I need to measure OPSPAN_NS around the final operation
start = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext2_hex = p1.hex()
elapsed = time.monotonic_ns() - start

claim = {"plaintext2_hex": plaintext2_hex}
print("CLAIM:" + json.dumps(claim))
print("OPSPAN_NS:" + str(elapsed))

sys.stdout.flush()