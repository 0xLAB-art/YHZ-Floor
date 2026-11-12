import json, sys

c1_hex = 'e90ff997e3664f579f2425da2a610eaafa44e350a1230ecb4522be91b0403408067edc92704aee0ff0cc435b1d3384922f32d1b775fd4b983d3f6dda2ad86793'
c2_hex = '43369bc44bf34e000a9eee95086eeb5e3fc9b2cfb51fc8b6e2c6292ab6ee61b6fe9bf46503f5b81d5497d171fd48b48c06b869a50446909c6184b06443bbed36'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# XOR two byte strings of equal length
def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

p1 = xor_bytes(c1, c2)
p1_hex = p1.hex()

claim = {"plaintext2_hex": p1_hex}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()