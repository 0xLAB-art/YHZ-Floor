import sys, json, base64

# Provisioned data (hard‑coded)
ct_hex = "a8ac22128816c9f04b998c1c25bbe0ab684ae667d95791c78a1bf45e34031d669a69b66b7cb70cab672fcda15f294c967af8bdb9efc3365feea9bd812764b24b71c7c22ebf3f964ef980e224f99187c6"
iv_hex = "3f751479bf95201d474e2ed280bd7042"
block_size = 16

# Convert hex to bytes (guard against errors)
try:
    ct = bytes.fromhex(ct_hex)
    iv = bytes.fromhex(iv_hex)
except Exception as e:
    sys.stderr.write(f"Hex decode error: {e}\n")
    sys.exit(1)

# Split ciphertext into 16‑byte blocks (C1..C5)
blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]

# Padding‑oracle query helper
def oracle_query(forged_prev: bytes, target: bytes) -> bool:
    payload = base64.b64encode(forged_prev + target).decode('ascii')
    print(json.dumps({"q": payload}), flush=True)
    line = sys.stdin.readline()
    if not line:
        sys.exit(1)
    resp = json.loads(line)
    return bool(resp.get('pad_ok'))

plaintext_blocks = []
# Recover each plaintext block sequentially
for idx, target_block in enumerate(blocks):
    prev_original = iv if idx == 0 else blocks[idx-1]
    # Intermediate value I = Dk(C) for this block
    I = [None] * block_size
    # Recover bytes from last to first
    for pos in range(block_size-1, -1, -1):
        pad_val = block_size - pos
        forged = bytearray(block_size)
        # Set already‑recovered bytes to enforce padding
        for j in range(pos+1, block_size):
            forged[j] = pad_val ^ I[j]
        # Bytes before pos can be any value; keep original to reduce false positives
        for j in range(0, pos):
            forged[j] = prev_original[j]
        found = False
        for guess in range(256):
            forged[pos] = guess
            if oracle_query(bytes(forged), target_block):
                # Extra check for pad_val == 1 to avoid the original‑padding false positive
                if pad_val == 1:
                    # Flip another byte and ensure padding fails
                    forged[pos] = guess ^ 1
                    if oracle_query(bytes(forged), target_block):
                        continue
                I[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            sys.stderr.write(f"Failed to recover byte at block {idx} position {pos}\n")
            sys.exit(1)
    # Derive plaintext block: P = I xor prev_original
    plain_block = bytes([I[i] ^ prev_original[i] for i in range(block_size)])
    plaintext_blocks.append(plain_block)

full_plain = b''.join(plaintext_blocks)
claim = {"plaintext_hex": full_plain.hex()}
print(f"CLAIM:{json.dumps(claim)}", flush=True)