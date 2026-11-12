import json, sys, base64

c1_hex = 'e90ff997e3664f579f2425da2a610eaafa44e350a1230ecb4522be91b0403408067edc92704aee0ff0cc435b1d3384922f32d1b775fd4b983d3f6dda2ad86793'
c2_hex = '43369bc44bf34e000a9eee95086eeb5e3fc9b2cfb51fc8b6e2c6292ab6ee61b6fe9bf46503f5b81d5497d171fd48b48c06b869a50446909c6184b06443bbed36'

c1 = bytes.fromhex(c1_hex)
c2 = bytes.fromhex(c2_hex)

# XOR the two ciphertexts: c1 XOR c2 = ChaCha20(key, nonce, P1) XOR ChaCha20(key, nonce, 0x00*64)
# Since ChaCha20 with zero plaintext gives the keystream, we have:
# c2 = keystream (key, nonce, 0x00*64)
# c1 = ChaCha20(key, nonce, P1)
# We need to recover P1 from c1 and the keystream.

# Actually, ChaCha20(key, nonce, P1) XOR P1 = keystream for that nonce with that counter chain.
# But we don't have the keystream for P1 directly.
# However, we know c2 = ChaCha20(key, nonce, 0x00*64) which gives us the keystream for the zero plaintext.
# The key and nonce are the same, but the internal state differs based on the plaintext.

# Actually, ChaCha20 with zero plaintext of 64 bytes outputs the first 64 bytes of the keystream.
# Let's call this keystream K = ChaCha20(key, nonce, 0x00*64) = c2
# Then c1 = ChaCha20(key, nonce, P1)

# The key insight: ChaCha20 with a non-zero plaintext XORs the plaintext with the keystream.
# But we need to figure out how the keystream changes with different plaintexts.

# Actually, ChaCha20 always outputs the same keystream for the same key and nonce,
# regardless of the plaintext. The plaintext is XORed with the same keystream.
# So: c1 = P1 XOR keystream
# c2 = 0x00*64 XOR keystream = keystream
# Therefore: c1 XOR c2 = P1 XOR keystream XOR keystream = P1

# Wait, that's not right. Let me think again.
# ChaCha20(key, nonce, P) = P XOR keystream(key, nonce)
# So c1 = P1 XOR keystream
# c2 = 0x00*64 XOR keystream = keystream
# Therefore c1 XOR c2 = P1 XOR keystream XOR keystream = P1

# Actually wait - the ChaCha20 function takes the plaintext as input? No, ChaCha20 takes key, nonce, and counter.
# The plaintext is XORed with the output keystream.
# The verifier produces c1_hex = ChaCha20(key, nonce, P1) - this means ChaCha20(key, nonce, counter=0, plaintext=P1)
# And c2_hex = ChaCha20(key, nonce, 0x00*64) - but this is ambiguous.

# Let me re-read the task: "c1_hex = ChaCha20(key, nonce, P1) and c2_hex = ChaCha20(key, nonce, 0x00 * 64)"
# This means both are ChaCha20 encryption of the given plaintexts with the same key and nonce.

# ChaCha20(key, nonce, plaintext) = plaintext XOR keystream(key, nonce)
# So: c1 = P1 XOR keystream
# c2 = 0x00*64 XOR keystream = keystream
# Therefore: c1 XOR c2 = P1

p1 = bytes.fromhex(c1_hex) ^ c2  # XOR byte by byte
p1_hex = p1.hex()

claim = {"plaintext2_hex": p1_hex}
print(f"CLAIM:{json.dumps(claim)}")
sys.stdout.flush()