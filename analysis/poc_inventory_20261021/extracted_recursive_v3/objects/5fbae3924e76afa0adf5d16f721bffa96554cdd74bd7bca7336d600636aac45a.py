import time, json, sys

c1_hex = "19b0d1181d3d9ce57e4e3f1e9318c25cb0bd34756b2aa34537ae2c6d8921781907819e61169ee2d6168192edeb0ad215e1d1f96a11b506a0862789486877827b"
c2_hex = "415b047b4b825946712897f72c712d6d2df388868179c87dcf8cf4280d5b7e8ea02a91de4ea92ea2851e16a0d05a37942e8a1358c6d31d5e6d2e9422cb0d6bcb"

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
assert len(c1) == 64 and len(c2) == 64

t0 = time.monotonic_ns()
# Same key => identical keystream K. c1 = P1 ^ K, c2 = 0x00*64 ^ K = K.
# Therefore P1 = c1 ^ c2.
p1 = bytes(a ^ b for a, b in zip(c1, c2))
t1 = time.monotonic_ns()

sys.stdout.write("OPSPAN_NS:%d\n" % (t1 - t0))
claim = {"plaintext_hex": p1.hex()}
assert len(claim["plaintext_hex"]) == 128
sys.stdout.write("CLAIM:" + json.dumps(claim, separators=(",", ":")) + "\n")
sys.stdout.flush()