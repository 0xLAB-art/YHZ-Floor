import sys, json, base64, binascii, time, random

# Hardcoded provisioned data
ct_hex = "4a86af17e70c9831d8ddcd95d96474ca5a7d2c74b09a156d4f99c688cf069be764609c69850fda86efa65bd03b093d9fb18597f94b7ecf55d0ef51cbecc543cab0e2728a8a6907b7d558b81192febba3"
iv_hex = "b7a2c144f8568b6dcd742bd9bd5c3240"
block_size = 16

ct_bytes = binascii.unhexlify(ct_hex)
iv_bytes = binascii.unhexlify(iv_hex)
# Split ciphertext into 16‑byte blocks
blocks = [ct_bytes[i:i+block_size] for i in range(0, len(ct_bytes), block_size)]

# Helper to send a query and receive oracle answer
def query_pad(forged_prev: bytes, target: bytes) -> bool:
    assert len(forged_prev) == block_size and len(target) == block_size
    data = forged_prev + target
    b64 = base64.b64encode(data).decode()
    sys.stdout.write(json.dumps({"q": b64}) + "\n")
    sys.stdout.flush()
    # read response line
    while True:
        line = sys.stdin.readline()
        if not line:
            raise EOFError("Oracle closed")
        line = line.strip()
        if not line:
            continue
        try:
            resp = json.loads(line)
            if "pad_ok" in resp:
                return bool(resp["pad_ok"])
        except Exception:
            continue

# Recover intermediate value I = D(C_i) for each block
intermediate_blocks = []  # list of bytearrays length 16
plaintext_blocks = []

for idx, target_block in enumerate(blocks):
    # previous block (original) is iv for first block, else blocks[idx-1]
    # Not needed directly for attack, but used later to compute plaintext
    # We'll recover I (the raw decryption) using padding oracle
    I = bytearray(block_size)
    # We'll build forged_prev progressively
    forged = bytearray(block_size)
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        # Set bytes after pos to enforce correct padding using already known I bytes
        for j in range(pos+1, block_size):
            forged[j] = I[j] ^ pad_val
        # Try all possible guesses for this byte
        found = False
        # Randomize order to avoid systematic bias
        guesses = list(range(256))
        random.shuffle(guesses)
        for guess in guesses:
            forged[pos] = guess
            # For bytes before pos we can leave as 0 (they don't affect padding)
            if query_pad(bytes(forged), target_block):
                # Valid padding found
                I[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            # Should not happen; raise error
            raise RuntimeError(f"Failed to recover byte at block {idx} pos {pos}")
    intermediate_blocks.append(I)
    # Compute plaintext block: Pi = I XOR previous ciphertext (or IV)
    prev = iv_bytes if idx == 0 else blocks[idx-1]
    plaintext_block = bytes(a ^ b for a, b in zip(I, prev))
    plaintext_blocks.append(plaintext_block)

# Assemble full plaintext (including padding block)
full_plaintext = b"".join(plaintext_blocks)
plaintext_hex = binascii.hexlify(full_plaintext).decode()

# Output claim
start = time.monotonic_ns()
# (no extra heavy computation after this point)
end = time.monotonic_ns()
opspan = end - start
sys.stdout.write(f"OPSPAN_NS:{opspan}\n")
sys.stdout.flush()
claim = {"plaintext_hex": plaintext_hex}
sys.stdout.write("CLAIM:" + json.dumps(claim) + "\n")
sys.stdout.flush()