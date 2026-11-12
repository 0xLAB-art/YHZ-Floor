import json, time
c1_hex = '9e19f6e795df1aa5c184333a9c5a6d5f6165024c51eaeae25890cd3f43f8bcf5af6b4956de29472b6bc099aa8d13ebb8e5733021954242a5d2d00303b63b786d'
c2_hex = '703963fb2dd982ea960320df2811159d0cc1ccb4bd17d310c93031b3f3c8b999cdb30c66b2fa70ef426de077bd2802be88f099ebf5df826ea43f633f0753a23d'
start = time.monotonic_ns()
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext2_hex = p1.hex()
end = time.monotonic_ns()
print('CLAIM:' + json.dumps({"plaintext2_hex": plaintext2_hex}), flush=True)