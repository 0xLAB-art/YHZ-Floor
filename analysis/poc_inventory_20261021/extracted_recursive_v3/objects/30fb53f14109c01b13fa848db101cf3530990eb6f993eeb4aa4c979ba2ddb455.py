import json, sys, time
c1 = bytes.fromhex('96bb531d2a5303565f8c7e5a58995a59681b5883c742733aef294e9f474f193d092b9acec64e3bd81165954d036cd926620f6fa3b45611f9ddbc1b178d902b74')
c2 = bytes.fromhex('410b4f6fa1054121cc7156b5f6c2a74e65e7761060a3510ee98aa5aac99ba7b8a7a31e315f9ba5f8d6b6c8aa5672d02f26ba6d7792015e7be6ca15ea8c4a3a25')
start = time.monotonic_ns()
p1 = bytes(a ^ b for a, b in zip(c1, c2))
elapsed = time.monotonic_ns() - start
sys.stdout.write(f'OPSPAN_NS:{elapsed}\n')
claim = {"plaintext_hex": p1.hex()}
sys.stdout.write(f'CLAIM:{json.dumps(claim)}\n')
sys.stdout.flush()