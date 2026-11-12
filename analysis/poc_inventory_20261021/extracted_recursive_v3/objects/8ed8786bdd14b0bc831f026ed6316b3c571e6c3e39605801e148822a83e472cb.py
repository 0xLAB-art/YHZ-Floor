import json, time
c1_hex = "84764ccf7b3bcdc436b7c90c320a6c4e69cd71d192ecd4305a29139b2c0406885cecc5f667275393fd65c84f93eaf456bd18d8481cc3193ce46693e38a5fd471"
c2_hex = "35a70f5d4d5b905524a06f11382c224ddabe01143b1eb83ca1cc94367fb2cb5ecfc43ce90d94f4bdea0b870aabda091313d0d911da1d4197fbf749a05e15615f"
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
p1_hex = p1.hex()
# measure time
start = time.monotonic_ns
_ = bytes(a ^ b for a, b in zip(c1, c2))
end = time.monotonic_ns
# build claim
claim = json.dumps({"plaintext2_hex": p1_hex})
print(f"CLAIM:{claim}")
print(f"OPSPAN_NS:{end-start}")
sys.stdout.flush()