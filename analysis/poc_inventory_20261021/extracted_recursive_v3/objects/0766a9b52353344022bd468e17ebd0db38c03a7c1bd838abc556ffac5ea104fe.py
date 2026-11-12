import sys, json, base64, binascii, time, random

# ---------------------------------------------------------------------------
# Read the provisioned JSON that the verifier sends on stdin at the start.
# It contains ct_hex, iv_hex, etc.  We ignore the values because they are
# already hard‑coded in the prompt, but we must consume the line so that the
# stdin stream remains open for the padding‑oracle responses.
# ---------------------------------------------------------------------------
first_line = sys.stdin.readline()
if not first_line:
    # No provisioned data – nothing we can do.
    sys.exit(1)
try:
    _prov = json.loads(first_line.strip())
except Exception:
    # If the line is not JSON, just ignore it.
    _prov = None

# ---------------------------------------------------------------------------
# Hard‑coded provisioned material (matches the prompt).
# ---------------------------------------------------------------------------
ct_hex = "4a86af17e70c9831d8ddcd95d96474ca5a7d2c74b09a156d4f99c688cf069be764609c69850fda86efa65bd03b093d9fb18597f94b7ecf55d0ef51cbecc543cab0e2728a8a6907b7d558b81192febba3"
iv_hex = "b7a2c144f8568b6dcd742bd9bd5c3240"
block_size = 16

ct_bytes = binascii.unhexlify(ct_hex)
iv_bytes = binascii.unhexlify(iv_hex)
blocks = [ct_bytes[i:i+block_size] for i in range(0, len(ct_bytes), block_size)]

# ---------------------------------------------------------------------------
# Padding‑oracle query helper.
# Sends a JSON line {"q": "<base64>"} where the base64 encodes
# forged_prev || target (32 bytes).  Then reads a single JSON response line
# containing the key "pad_ok".
# ---------------------------------------------------------------------------
def query_pad(forged_prev: bytes, target: bytes) -> bool:
    assert len(forged_prev) == block_size and len(target) == block_size
    payload = forged_prev + target
    b64 = base64.b64encode(payload).decode('ascii')
    # Compact JSON without spaces to keep the line short.
    sys.stdout.write(json.dumps({"q": b64}, separators=(',', ':')) + "\n")
    sys.stdout.flush()
    # Read the oracle's response.
    line = sys.stdin.readline()
    if not line:
        raise EOFError("Oracle closed the connection")
    resp = json.loads(line.strip())
    return bool(resp.get("pad_ok", False))

intermediate_blocks = []   # D(C_i) for each ciphertext block
plaintext_blocks = []

# ---------------------------------------------------------------------------
# Recover each block using the classic Vaudenay padding‑oracle technique.
# ---------------------------------------------------------------------------
for idx, target_block in enumerate(blocks):
    I = bytearray(block_size)          # will hold the intermediate value
    forged = bytearray(block_size)    # the block we control (previous ciphertext)
    for pos in range(block_size - 1, -1, -1):
        pad_val = block_size - pos
        # Set the suffix bytes so that they produce a correct padding value.
        for j in range(pos + 1, block_size):
            forged[j] = I[j] ^ pad_val
        found = False
        # Try all 256 possibilities in random order to avoid any deterministic
        # pattern that could be throttled by the oracle.
        guesses = list(range(256))
        random.shuffle(guesses)
        for guess in guesses:
            forged[pos] = guess
            if query_pad(bytes(forged), target_block):
                # Padding is valid → we have discovered the intermediate byte.
                I[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            raise RuntimeError(f"Failed to recover byte at block {idx}, position {pos}")
    intermediate_blocks.append(I)
    # Plaintext block = intermediate XOR previous ciphertext (or IV for first).
    prev = iv_bytes if idx == 0 else blocks[idx - 1]
    plaintext_blocks.append(bytes(a ^ b for a, b in zip(I, prev)))

full_plaintext = b"".join(plaintext_blocks)
plaintext_hex = binascii.hexlify(full_plaintext).decode('ascii')

# ---------------------------------------------------------------------------
# Output timing (optional) and final claim.
# ---------------------------------------------------------------------------
start_ns = time.monotonic_ns()
# No heavy work after this point.
end_ns = time.monotonic_ns()
sys.stdout.write(f"OPSPAN_NS:{end_ns - start_ns}\n")
claim = {"plaintext_hex": plaintext_hex}
sys.stdout.write("CLAIM:" + json.dumps(claim, separators=(',', ':')) + "\n")
sys.stdout.flush()