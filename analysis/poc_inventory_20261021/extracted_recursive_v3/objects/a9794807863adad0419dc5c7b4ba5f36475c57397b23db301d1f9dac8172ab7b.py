import json, sys

c1_hex = '4fa5bba0121e1a59949fed21b878d31428830d8f6517649006a03ba4ce4f41ed3676e89cda75fd7244e5efe015b71f267584f2d0024c82e2298ce7c4bee49281'
c2_hex = '9a9bce168b7888cd30cae3ab8bd79aeb80ac3c42083166c01830a3631593c09d7c91be962408d3eefca724171385081cdb55b7612aec02383361e15b503249d0'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# RC4 reuse: c2 = RC4(key, 0x00*64) = keystream, c1 = P1 XOR keystream
# So P1 = c1 XOR c2
P1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = P1.hex()

claim = json.dumps({"plaintext_hex": plaintext_hex})
print(claim)
sys.stdout.flush()

# Also print OPSPAN_NS measurement
import time
start = time.monotonic_ns()
_ = bytes(a ^ b for a, b in zip(c1, c2))  # redo to measure
end = time.monotonic_ns()
print(f'OPSPAN_NS:{end - start}')
sys.stdout.flush()