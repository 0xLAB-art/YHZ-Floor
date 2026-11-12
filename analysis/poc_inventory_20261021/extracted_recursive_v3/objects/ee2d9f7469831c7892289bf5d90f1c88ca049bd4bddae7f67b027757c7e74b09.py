import json, time, sys

c1_hex = "c2ea54f694360f0c47f58f874c77e618d1e7676766df187bc6aca966f1da71c1f3df0ab9051cede4d75493912affd26a4864de7ccbfa29d4f0d494355cc560c1"
c2_hex = "6dc861e3fabe34de8443cf371a6002db612868619710a62575f7d06abc2f6207aad23edce34f836ec73e62b852a20a64bb2f7f216909f161930323ffbd1ed825"

t0 = time.monotonic_ns()

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
assert len(c1) == len(c2) == 64

# RC4 keystream is identical for both messages under the same key.
# c1 = P1 ^ K , c2 = 0 ^ K = K  =>  P1 = c1 ^ c2
p1 = bytes(a ^ b for a, b in zip(c1, c2))
keystream = c2
assert bytes(x ^ y for x, y in zip(p1, keystream)) == c1

t1 = time.monotonic_ns()

sys.stdout.write("OPSPAN_NS:%d\n" % (t1 - t0))
sys.stdout.write("CLAIM:" + json.dumps({"plaintext_hex": p1.hex()}) + "\n")
sys.stdout.flush()