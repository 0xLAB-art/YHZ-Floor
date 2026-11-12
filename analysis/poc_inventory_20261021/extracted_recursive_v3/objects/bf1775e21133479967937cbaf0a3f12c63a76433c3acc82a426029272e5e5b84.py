import json, time

c1_hex = "6b26fabb4fa5476670237b1dacac46d14615abe8e08599670f154e53ead5d524972ef749a94b4436466fc533386c77391b1db7d29dae500d7d20c1468e97aa99"
c2_hex = "fd6a15541c2cb3e9723b86e1ed04181a011602a26452415aa28cd20c4cc56e840275debd5f24d1fddc42c40ce0d47abcef456376f9c75333c47bf016527f379e"

start = time.monotonic_ns()
c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)
p1 = bytes(a ^ b for a, b in zip(c1, c2))
plaintext_hex = p1.hex()
end = time.monotonic_ns()

print(f"OPSPAN_NS:{end - start}")
print("CLAIM:" + json.dumps({"plaintext_hex": plaintext_hex}), flush=True)