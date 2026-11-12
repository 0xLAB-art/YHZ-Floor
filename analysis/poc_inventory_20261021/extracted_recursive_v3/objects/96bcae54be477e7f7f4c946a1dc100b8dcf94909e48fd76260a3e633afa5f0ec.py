import sys, json, base64

# Read provisioned JSON from stdin (consumes the initial material)
prov_line = sys.stdin.readline()
if not prov_line:
    sys.exit(1)
prov = json.loads(prov_line)
ct_hex = prov.get('ct_hex')
iv_hex = prov.get('iv_hex')
block_size = prov.get('block_size', 16)

# Convert hex strings to bytes
ct = bytes.fromhex(ct_hex)
iv = bytes.fromhex(iv_hex)

# Split ciphertext into 16‑byte blocks (C1..C5)
blocks = [ct[i:i+block_size] for i in range(0, len(ct), block_size)]

# Helper to query the padding oracle
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
    I = [0] * block_size
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
                # Extra check for pad_val == 1 to avoid original‑padding false positive
                if pad_val == 1:
                    forged[pos] = guess ^ 1
                    if oracle_query(bytes(forged), target_block):
                        continue
                I[pos] = guess ^ pad_val
                found = True
                break
        if not found:
            sys.exit(1)
    # Derive plaintext block: P = I xor prev_original
    plain_block = bytes([I[i] ^ prev_original[i] for i in range(block_size)])
    plaintext_blocks.append(plain_block)

full_plain = b''.join(plaintext_blocks)
claim = {"plaintext_hex": full_plain.hex()}
print(f"CLAIM:{json.dumps(claim)}", flush=True)